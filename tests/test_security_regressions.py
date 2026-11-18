"""Regression tests for security fixes after the 2.0.1 release."""

from __future__ import annotations

import json
import threading
from html.parser import HTMLParser
from io import StringIO
from pathlib import Path

import pytest

from devkitx.compliance import AuditChainError, AuditLogger, verify_chain
from devkitx.security import sanitize_filename, sanitize_html
from devkitx.security.crypto import secure_hash

# --------------------------------------------------------------------------
# sanitize_html
# --------------------------------------------------------------------------

XSS_PAYLOADS = [
    '<b onmouseover="alert(1)">x</b>',
    "<b ONCLICK=alert(1)>x</b>",
    "<b/onmouseover=alert(1)>x</b>",
    "<b\nonclick=alert(1)>x</b>",
    '<b style="background:url(javascript:alert(1))">x</b>',
    '<a href="javascript:alert(1)">x</a>',
    '<a href="JaVaScRiPt:alert(1)">x</a>',
    '<a href="java\tscript:alert(1)">x</a>',
    '<a href=" javascript:alert(1)">x</a>',
    '<a href="\x01javascript:alert(1)">x</a>',
    '<a href="javascript&#58;alert(1)">x</a>',
    '<a href="javascript&colon;alert(1)">x</a>',
    '<a href="&#x6A;avascript:alert(1)">x</a>',
    '<a href="javascript://%0aalert(1)">x</a>',
    '<a href="data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==">x</a>',
    '<a href="vbscript:msgbox(1)">x</a>',
    "<img src=x onerror=alert(1)>",
    "<IMG SRC=JaVaScRiPt:alert(1)>",
    '<img src="x" alt="&quot; onerror=&quot;alert(1)">',
    '<a title="&quot;><script>alert(1)</script>">x</a>',
    "<script>alert(1)</script>",
    "<svg onload=alert(1)>",
    "<iframe src=javascript:alert(1)>",
    '<math><mi xlink:href="javascript:alert(1)">x</mi></math>',
    "<b><script>alert(1)</script></b>",
    "<!--<script>alert(1)</script>-->",
    '"><script>alert(1)</script>',
    "<scr<script>ipt>alert(1)</script>",
    "<<script>script>alert(1)<</script>/script>",
]

_ALLOWED_TAGS = {"b", "i", "a", "img"}
_ALLOWED_ATTRS = {"a": {"href", "title"}, "img": {"src", "alt"}}


class _TagCollector(HTMLParser):
    """Parses sanitizer output the way a browser would, collecting real tags."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[tuple[str, list[tuple[str, str | None]]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag, attrs))

    handle_startendtag = handle_starttag


@pytest.mark.parametrize("payload", XSS_PAYLOADS)
def test_sanitize_html_blocks_xss(payload: str) -> None:
    out = sanitize_html(payload, _ALLOWED_TAGS, _ALLOWED_ATTRS)
    collector = _TagCollector()
    collector.feed(out)
    for tag, attrs in collector.tags:
        assert tag in _ALLOWED_TAGS, out
        for name, value in attrs:
            assert name in _ALLOWED_ATTRS.get(tag, set()), out
            if name in {"href", "src"}:
                scheme = "".join(ch for ch in (value or "") if ch > " ").split(":")[0].lower()
                assert ":" not in (value or "") or scheme in {"http", "https", "mailto"}, out


def test_sanitize_html_keeps_allowed_markup() -> None:
    assert sanitize_html("Hello <b>world</b>", {"b"}) == "Hello <b>world</b>"
    assert sanitize_html("<i>a</i><b>b</b>", {"b", "i"}) == "<i>a</i><b>b</b>"
    assert sanitize_html("line<br>break", {"br"}) == "line<br>break"


def test_sanitize_html_strips_attributes_by_default() -> None:
    assert sanitize_html('<b class="x" id="y">t</b>', {"b"}) == "<b>t</b>"


def test_sanitize_html_keeps_safe_allowlisted_attributes() -> None:
    out = sanitize_html(
        '<a href="https://example.com/?a=1&b=2" title="T">x</a>',
        {"a"},
        {"a": {"href", "title"}},
    )
    assert out == '<a href="https://example.com/?a=1&amp;b=2" title="T">x</a>'
    assert sanitize_html('<a href="/docs">x</a>', {"a"}, {"a": {"href"}}) == '<a href="/docs">x</a>'
    assert sanitize_html('<a href="mailto:a@b.c">x</a>', {"a"}, {"a": {"href"}}) == (
        '<a href="mailto:a@b.c">x</a>'
    )


def test_sanitize_html_event_handlers_cannot_be_allowlisted() -> None:
    out = sanitize_html('<b onclick="x()" style="color:red">t</b>', {"b"}, {"b": {"onclick", "style"}})
    assert out == "<b>t</b>"


@pytest.mark.parametrize("tag", ["script", "style", "iframe", "svg", "object", "SCRIPT"])
def test_sanitize_html_refuses_dangerous_allowlist(tag: str) -> None:
    with pytest.raises(ValueError):
        sanitize_html("x", allowed_tags={tag})


def test_sanitize_html_escapes_text_and_disallowed_tags() -> None:
    out = sanitize_html("<script>alert('x')</script><u>u</u>&<b>b</b>", {"b"})
    assert out == "&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;&lt;u&gt;u&lt;/u&gt;&amp;<b>b</b>"


def test_sanitize_html_closes_unclosed_tags() -> None:
    assert sanitize_html("<b>bold", {"b"}) == "<b>bold</b>"
    assert sanitize_html("</b>stray", {"b"}) == "stray"


def test_sanitize_html_no_allowlist_unchanged_behaviour() -> None:
    assert sanitize_html("<b>x</b>") == "&lt;b&gt;x&lt;/b&gt;"


# --------------------------------------------------------------------------
# Audit log chain
# --------------------------------------------------------------------------


def _write_log(key: bytes | None = None, n: int = 3) -> list[str]:
    out = StringIO()
    logger = AuditLogger(service="svc", output=out, hmac_key=key)
    for i in range(n):
        logger.log_access("read", resource_type="doc", resource_id=f"d{i}", user_id=f"u{i}")
    return out.getvalue().splitlines()


def test_chain_verifies_untampered_log() -> None:
    assert verify_chain(_write_log()) == 3


@pytest.mark.parametrize("field", ["user_id", "action", "outcome", "resource_id", "source_ip"])
def test_chain_detects_content_edit(field: str) -> None:
    lines = _write_log()
    record = json.loads(lines[1])
    record[field] = "tampered"
    lines[1] = json.dumps(record, separators=(",", ":"))
    with pytest.raises(AuditChainError) as info:
        verify_chain(lines)
    assert info.value.line_number == 2


def test_chain_detects_metadata_edit() -> None:
    out = StringIO()
    logger = AuditLogger(service="svc", output=out)
    logger.log_change("update", "user", "1", changes={"role": {"old": "user", "new": "admin"}})
    record = json.loads(out.getvalue())
    record["metadata"]["changes"]["role"]["new"] = "user"
    with pytest.raises(AuditChainError):
        verify_chain([json.dumps(record)])


def test_chain_detects_deleted_and_reordered_lines() -> None:
    lines = _write_log()
    with pytest.raises(AuditChainError):
        verify_chain([lines[0], lines[2]])
    with pytest.raises(AuditChainError):
        verify_chain([lines[1], lines[0], lines[2]])


def test_chain_rejects_non_audit_lines() -> None:
    with pytest.raises(AuditChainError):
        verify_chain(["not json"])


def test_hmac_chain_needs_the_right_key() -> None:
    lines = _write_log(key=b"k1")
    assert verify_chain(lines, hmac_key=b"k1") == 3
    with pytest.raises(AuditChainError):
        verify_chain(lines, hmac_key=b"k2")
    with pytest.raises(AuditChainError):
        verify_chain(lines)  # unkeyed verification of a keyed log


def test_unkeyed_forgery_fails_against_hmac_log() -> None:
    """An attacker who edits a line and recomputes a plain SHA-256 chain is caught."""
    import hashlib

    from devkitx.compliance.audit_logger import _canonical

    lines = _write_log(key=b"secret")
    previous = "0" * 64
    forged = []
    for i, line in enumerate(lines):
        record = json.loads(line)
        if i == 1:
            record["user_id"] = "attacker"
        record["metadata"]["_chain_hash"] = hashlib.sha256(
            previous.encode() + b"\n" + _canonical(record)
        ).hexdigest()
        previous = record["metadata"]["_chain_hash"]
        forged.append(json.dumps(record))
    with pytest.raises(AuditChainError):
        verify_chain(forged, hmac_key=b"secret")


def test_chain_continues_across_restart(tmp_path: Path) -> None:
    path = tmp_path / "audit.log"
    AuditLogger(service="svc", output=path).log_auth("login", user_id="a")
    AuditLogger(service="svc", output=path).log_auth("login", user_id="b")
    assert verify_chain(path) == 2


def test_chain_is_thread_safe(tmp_path: Path) -> None:
    path = tmp_path / "audit.log"
    logger = AuditLogger(service="svc", output=path, hmac_key=b"k")

    def worker(n: int) -> None:
        for i in range(25):
            logger.log_access("read", "doc", f"{n}-{i}")

    threads = [threading.Thread(target=worker, args=(n,)) for n in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert verify_chain(path, hmac_key=b"k") == 200


def test_reused_event_object_is_rechained() -> None:
    from devkitx.compliance import AuditEvent

    out = StringIO()
    logger = AuditLogger(service="svc", output=out)
    event = AuditEvent(event_type="t", action="a")
    logger.log(event)
    logger.log(event)
    assert verify_chain(out.getvalue().splitlines()) == 2


def test_timestamp_format_unchanged() -> None:
    record = json.loads(_write_log(n=1)[0])
    ts = record["timestamp"]
    assert ts.endswith("Z") and "+" not in ts and "T" in ts


# --------------------------------------------------------------------------
# secure_hash
# --------------------------------------------------------------------------


@pytest.mark.parametrize("algorithm", ["md5", "sha1", "MD5", "sha224", "nonexistent"])
def test_secure_hash_rejects_weak_algorithms(algorithm: str) -> None:
    with pytest.raises(ValueError):
        secure_hash("x", algorithm)


@pytest.mark.parametrize("algorithm", ["sha256", "SHA-256", "sha512", "sha3_256", "blake2b"])
def test_secure_hash_accepts_strong_algorithms(algorithm: str) -> None:
    assert secure_hash("x", algorithm)


def test_secure_hash_default_unchanged() -> None:
    assert secure_hash("hello world") == (
        "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
    )


# --------------------------------------------------------------------------
# sanitize_filename
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "name",
    ["../../etc/passwd", "..\\..\\windows\\win.ini", "a\x00b.txt", "a\nb", "∕etc∕passwd", "..", "/"],
)
def test_sanitize_filename_is_single_safe_component(name: str) -> None:
    out = sanitize_filename(name)
    assert out
    assert "/" not in out and "\\" not in out and "\x00" not in out and "\n" not in out
    assert ".." not in out
    assert out not in {".", ".."}


@pytest.mark.parametrize("name", ["CON", "con.txt", "NUL", "com1.log", "LPT9"])
def test_sanitize_filename_avoids_windows_device_names(name: str) -> None:
    assert sanitize_filename(name).startswith("_")


def test_sanitize_filename_limits_length_and_keeps_extension() -> None:
    out = sanitize_filename("a" * 400 + ".pdf")
    assert len(out.encode()) <= 255 and out.endswith(".pdf")
    out = sanitize_filename("é" * 300)
    assert len(out.encode()) <= 255
