"""Input sanitization utilities."""

from __future__ import annotations

import html
import re
import unicodedata
from collections.abc import Mapping
from html.parser import HTMLParser

__all__ = ["sanitize_html", "sanitize_sql_identifier", "sanitize_filename"]

# Tags that can execute script, load active content or change how the rest of
# the page is parsed. They are never allowed, even if a caller lists them.
_FORBIDDEN_TAGS = frozenset(
    {
        "script", "style", "iframe", "frame", "frameset", "object", "embed",
        "applet", "svg", "math", "template", "base", "link", "meta", "form",
        "input", "button", "textarea", "select", "option", "noscript",
    }
)

# Elements with no closing tag; emitted without a matching </tag>.
_VOID_TAGS = frozenset({"br", "hr", "img", "wbr", "col", "area", "source", "track"})

# Attributes whose values are URLs and must pass the scheme check.
_URL_ATTRIBUTES = frozenset(
    {"href", "src", "cite", "action", "formaction", "poster", "background", "xlink:href"}
)
_SAFE_URL_SCHEMES = frozenset({"http", "https", "mailto"})
_SCHEME_RE = re.compile(r"^([a-z][a-z0-9+.\-]*):", re.IGNORECASE)
_URL_NOISE_RE = re.compile(r"[\x00-\x20\x7f]+")


def _is_safe_url(value: str) -> bool:
    """Allow relative URLs and http(s)/mailto; reject javascript:, data:, etc."""
    # Browsers ignore embedded whitespace/control characters in the scheme
    # ("java\tscript:"), so strip them before checking.
    cleaned = _URL_NOISE_RE.sub("", value)
    match = _SCHEME_RE.match(cleaned)
    return match is None or match.group(1).lower() in _SAFE_URL_SCHEMES


def _is_forbidden_attribute(name: str) -> bool:
    return name.startswith("on") or name in {"style", "srcdoc", "formaction"}


class _AllowlistSanitizer(HTMLParser):
    """Re-serializes HTML, keeping only allowlisted tags and attributes.

    All text is escaped. Disallowed tags are escaped and shown as text, as in
    devkitx 2.0. Comments, doctypes and processing instructions are dropped.
    """

    def __init__(self, allowed_tags: frozenset[str], allowed_attributes: Mapping[str, frozenset[str]]):
        super().__init__(convert_charrefs=True)
        self._tags = allowed_tags
        self._attrs = allowed_attributes
        self._out: list[str] = []
        self._open: list[str] = []

    def _render_attrs(self, tag: str, attrs: list[tuple[str, str | None]]) -> str:
        permitted = self._attrs.get(tag, frozenset()) | self._attrs.get("*", frozenset())
        parts: list[str] = []
        for name, value in attrs:
            name = name.lower()
            if name not in permitted or _is_forbidden_attribute(name):
                continue
            value = value or ""
            if name in _URL_ATTRIBUTES and not _is_safe_url(value):
                continue
            parts.append(f' {name}="{html.escape(value, quote=True)}"')
        return "".join(parts)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._tags:
            self._out.append(f"<{tag}{self._render_attrs(tag, attrs)}>")
            if tag not in _VOID_TAGS:
                self._open.append(tag)
        else:
            self._out.append(html.escape(self.get_starttag_text() or f"<{tag}>"))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._tags:
            self._out.append(f"<{tag}{self._render_attrs(tag, attrs)}>")
        else:
            self._out.append(html.escape(self.get_starttag_text() or f"<{tag} />"))

    def handle_endtag(self, tag: str) -> None:
        if tag in self._tags and tag not in _VOID_TAGS:
            if tag in self._open:
                # Close any allowed tags left open inside this one.
                while self._open:
                    current = self._open.pop()
                    self._out.append(f"</{current}>")
                    if current == tag:
                        break
            # A stray closing tag for an allowed element is dropped.
        else:
            self._out.append(html.escape(f"</{tag}>"))

    def handle_data(self, data: str) -> None:
        self._out.append(html.escape(data))

    def result(self) -> str:
        self.close()
        while self._open:
            self._out.append(f"</{self._open.pop()}>")
        return "".join(self._out)


def sanitize_html(
    text: str,
    allowed_tags: set[str] | None = None,
    allowed_attributes: Mapping[str, set[str]] | None = None,
) -> str:
    """Sanitize HTML input to prevent XSS attacks.

    With no ``allowed_tags`` every character is HTML-escaped. With an
    allowlist, the input is parsed and rebuilt: allowed tags are kept
    *without attributes* unless listed in ``allowed_attributes``, all other
    markup is escaped, and all text is escaped. Event-handler (``on*``),
    ``style`` and ``srcdoc`` attributes are always removed, and URL
    attributes only keep relative, ``http``, ``https`` and ``mailto`` URLs.

    Args:
        text: HTML text to sanitize.
        allowed_tags: Tags to keep, e.g. ``{"b", "i", "a"}``.
        allowed_attributes: Per-tag attribute allowlist, e.g.
            ``{"a": {"href", "title"}}``. Use ``"*"`` for attributes allowed
            on every allowed tag.

    Returns:
        Sanitized HTML.

    Raises:
        ValueError: If ``allowed_tags`` contains a tag that can run script
            or load active content (``script``, ``iframe``, ``svg``, ...).

    Example:
        >>> sanitize_html("<script>alert('xss')</script>Hello")
        '&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;Hello'
        >>> sanitize_html('<b onclick="x()">Hi</b>', allowed_tags={"b"})
        '<b>Hi</b>'
        >>> sanitize_html('<a href="javascript:x()">y</a>', {"a"}, {"a": {"href"}})
        '<a>y</a>'
    """
    if allowed_tags is None:
        return html.escape(text)

    tags = frozenset(tag.lower() for tag in allowed_tags)
    forbidden = sorted(tags & _FORBIDDEN_TAGS)
    if forbidden:
        raise ValueError(f"These tags can never be allowed: {', '.join(forbidden)}")
    attrs = {
        tag.lower(): frozenset(name.lower() for name in names)
        for tag, names in (allowed_attributes or {}).items()
    }

    parser = _AllowlistSanitizer(tags, attrs)
    parser.feed(text)
    return parser.result()


def sanitize_sql_identifier(identifier: str) -> str:
    """Sanitize SQL identifier to prevent injection.

    Args:
        identifier: SQL identifier (table name, column name, etc.)

    Returns:
        Sanitized identifier

    Raises:
        ValueError: If identifier contains invalid characters

    Example:
        >>> sanitize_sql_identifier("user_table")
        'user_table'
        >>> sanitize_sql_identifier("users; DROP TABLE users;")
        Traceback (most recent call last):
        ValueError: Invalid SQL identifier: contains disallowed characters
    """
    # Allow only alphanumeric characters and underscores
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", identifier):
        raise ValueError("Invalid SQL identifier: contains disallowed characters")

    # Check for SQL keywords (basic list)
    sql_keywords = {
        "select", "insert", "update", "delete", "drop", "create", "alter",
        "table", "database", "index", "view", "trigger", "procedure", "function",
        "union", "join", "where", "having", "group", "order", "limit", "offset"
    }

    if identifier.lower() in sql_keywords:
        raise ValueError(f"Invalid SQL identifier: '{identifier}' is a reserved keyword")

    return identifier


# Device names Windows treats specially regardless of extension.
_WINDOWS_RESERVED = frozenset(
    {"con", "prn", "aux", "nul"}
    | {f"com{i}" for i in range(1, 10)}
    | {f"lpt{i}" for i in range(1, 10)}
)
_MAX_FILENAME_BYTES = 255


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename so it is safe to use as a single path component.

    Removes path separators, traversal sequences, control characters and
    characters Windows forbids; avoids Windows device names; and limits the
    result to 255 bytes (UTF-8).

    Args:
        filename: Filename to sanitize

    Returns:
        Sanitized filename (never empty)

    Example:
        >>> sanitize_filename("../../../etc/passwd")
        '______etc_passwd'
        >>> sanitize_filename("normal_file.txt")
        'normal_file.txt'
        >>> sanitize_filename("CON.txt")
        '_CON.txt'
    """
    # Normalize so look-alike separators (e.g. fullwidth slash) become ASCII.
    sanitized = unicodedata.normalize("NFKC", filename)

    # Remove control characters, including NUL.
    sanitized = "".join(ch for ch in sanitized if unicodedata.category(ch) != "Cc")

    # Replace directory separators and characters Windows forbids
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", sanitized)

    # Remove path traversal attempts
    sanitized = sanitized.replace("..", "_")

    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(". ")

    if sanitized.split(".")[0].lower() in _WINDOWS_RESERVED:
        sanitized = f"_{sanitized}"

    # Keep within the common 255-byte filesystem limit, preserving the extension.
    if len(sanitized.encode("utf-8")) > _MAX_FILENAME_BYTES:
        stem, dot, ext = sanitized.rpartition(".")
        if not dot or len(ext.encode("utf-8")) > 16:
            stem, ext = sanitized, ""
        budget = _MAX_FILENAME_BYTES - len(ext.encode("utf-8")) - (1 if ext else 0)
        stem = stem.encode("utf-8")[:budget].decode("utf-8", errors="ignore")
        sanitized = f"{stem}.{ext}" if ext else stem

    # Ensure filename is not empty
    if not sanitized:
        sanitized = "unnamed_file"

    return sanitized
