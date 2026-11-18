# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-11-17

### Security
- `sanitize_html` with `allowed_tags` no longer passes attributes through. Allowed
  tags are rebuilt from a parse with no attributes unless listed in the new
  `allowed_attributes` argument; `on*`, `style` and `srcdoc` are always removed and
  URL attributes only keep relative, `http`, `https` and `mailto` URLs. Previously
  `<b onmouseover=...>` and `<a href="javascript:...">` survived (XSS).
  Tags such as `script`, `iframe` and `svg` can no longer be allowlisted.
- Audit log chain hashes now cover each event's full content (previously only the
  event ID and timestamp, so actor, action, outcome and metadata could be edited
  undetected). Optional `hmac_key` makes the chain keyed (HMAC-SHA256). New
  `verify_chain()` and `AuditChainError`. File logs continue their chain after a
  restart, and logging is thread-safe.
- `secure_hash` only accepts SHA-2, SHA-3 and BLAKE2; `md5` and `sha1` raise
  `ValueError`.
- `sanitize_filename` also removes control characters (including NUL), avoids
  Windows device names (`CON`, `NUL`, ...) and limits names to 255 bytes. Now
  exported from `devkitx.security`.

### Changed
- `asyncbridge`, `httpx-defaults` and `configmerge` are now part of devkitx
  (`devkitx.async_bridge`, `devkitx.http_client`, `devkitx.config`). The only
  runtime dependency is `httpx`. New extras: `yaml`, `toml`, `http2`.
- Line endings normalized to LF.

### Fixed
- README told users to `pip install confmerge`, an unrelated third-party package.
- `SecureClient.request()` crashed when given an `httpx.URL` object instead of a string.
- Plain-HTTP warning now checks the parsed host (so `http://localhost.evil.com`
  warns) and also fires for `SecureAsyncClient`, which never warned before.
- PII detector missed the opening parenthesis of numbers like `(555) 987-6543`;
  the email pattern accepted `|` in the top-level domain.
- Config files whose top level is not a mapping now raise `ValueError` instead of
  returning a non-dict.
- `bcrypt` (needed for `hash_password`/`verify_password`) is now declared as the
  `crypto` extra and included in `all`.
- `devkitx audit deps` runs pip-audit via the current interpreter instead of
  resolving `pip-audit` from `PATH`.
- Project URLs pointed at a `SerityOps/devkitx` repository and a Read the Docs
  site that do not exist; they now point at `ladycami/devkitx`.

### Internal
- Releases: pushing a `vX.Y.Z` tag publishes to PyPI from CI via trusted
  publishing (`.github/workflows/release.yml`); `scripts/publish.py` publishes
  locally using tokens from a gitignored `.env` (format in `.env.example`).
- CI runs on `develop` and pull requests (the old workflow targeted a `main`
  branch that does not exist): ruff, ruff format, strict mypy on 3.10 and 3.13
  semantics, tests on Python 3.10-3.13 with a coverage floor, doctests, bandit,
  pip-audit, and a build + clean-install check. Actions are pinned by commit SHA.
- ruff and mypy (strict) are clean; ruff's security rules (`S`) are enabled.

## [2.0.1] - 2025-12-31

Source restored from the PyPI release; no separate changelog was kept for 2.0.x.

## [2.0.0] - 2025-12-31

Security- and compliance-focused rewrite: audit logging, PII detection, secrets
scanning, input sanitization, NIST 800-53 control mapping and a Typer CLI.

## [1.0.1] - 2025-09-16

### Changed
- Finalized rename to `devkitx` across package, imports, docs, and URLs
- Marked package Development Status: Beta (instead of Production/Stable)
- Curated top-level exports; added `py.typed` marker file
- Updated project URLs to point to correct `ladycami/devkitx` repository

### Added
- HTTP clients with sensible defaults (10s connect, 15s read timeouts)
- Retry helper with exponential backoff and jitter
- Async bridges for safe sync/async conversion with event loop detection
- Concurrency limiter for async operations using semaphores
- JWT utilities with safe defaults (HS256, required exp/iat claims)
- JSON flattening utility for nested structures
- Minimal test suite with CI pipeline (ruff, mypy, pytest)
- Optional dependency extras: http, cli, jwt, bcrypt, yaml, toml, dev

### Fixed
- Import/package name mismatches in documentation and examples
- Incorrect project links in PyPI metadata
- Missing type annotation marker file
- Package structure to follow Python best practices

## [1.0.0] - 2025-09-15

### Added
- Initial release of DevKitX
- 16 comprehensive utility modules:
  - `string_utils`: Case conversions, validation, sanitization
  - `json_utils`: JSON processing, flatten/unflatten, pretty printing
  - `file_utils`: Atomic writes, file finding, cross-platform operations
  - `data_utils`: Deep merge/diff, collection processing, transformations
  - `config_utils`: Multi-format config loading, type-safe getters
  - `system_utils`: System info, command execution, process management
  - `security_utils`: Password hashing, JWT tokens, secure generation
  - `time_utils`: Date parsing, timezone handling, business days
  - `validation_utils`: Schema validation, input validation, custom rules
  - `cli_utils`: Interactive prompts, progress bars, colored output
  - `http_utils`: API clients, retry logic, async support
  - `async_utils`: Async file ops, sync/async bridges, concurrency
  - `dev_utils`: Performance profiling, debugging, test data generation
  - `log_utils`: Enhanced logging setup, timing contexts
- 200+ utility functions with comprehensive type annotations
- 50+ CLI commands across 8 categories
- Comprehensive test suite with 89% coverage (740+ test cases)
- Cross-platform compatibility (Windows, macOS, Linux)
- Async/await support throughout
- Security best practices with bcrypt and JWT
- Performance optimizations and benchmarking tools

### Security
- Secure password hashing using bcrypt
- JWT token generation and verification
- Input sanitization and validation
- Cryptographically secure random generation

### Documentation
- Complete API documentation with examples
- Comprehensive README with usage examples
- Real-world usage scenarios and demos
- CLI command documentation

## [1.0.1] - 2025-09-16

### Changed
- Finalized rename to `devkitx` across package, imports, docs, and URLs
- Updated package development status from "Production/Stable" to "Beta" 
- Curated top-level exports with graceful handling of optional dependencies
- Added `py.typed` marker file for proper type annotation support

### Added
- HTTP clients with sensible defaults (10s connect, 15s read timeouts)
- Connection limits to prevent resource exhaustion (10 keepalive, 100 total)
- Retry helper with exponential backoff and jitter
- Async bridge functions for safe sync/async conversion with event loop detection
- Async concurrency limiter using semaphore-based control
- JSON flattening utility with configurable separators
- JWT utilities with secure defaults (HS256, required exp/iat claims)
- Optional dependency groups (extras): http, cli, jwt, bcrypt, yaml, toml
- Minimal test suite with CI/CD pipeline (ruff, mypy, pytest)
- Security documentation with clear scope and limitations

### Fixed
- Import/package name mismatches - all examples now use correct `devkitx` imports
- Project URLs now point to correct `ladycami/devkitx` repository
- Changelog entries now have proper dates instead of "Upcoming" status
- Package structure follows Python packaging best practices

### Security
- JWT tokens now require exp and iat claims by default
- HTTP clients use secure connection limits to prevent resource exhaustion
- Clear documentation of security feature scope and limitations

## [Unreleased]

### Planned for v1.1.0
- Enhanced property-based testing with Hypothesis
- Additional timeout and retry configurations
- Expanded async utilities and concurrency helpers

---

## Security Policy

If you discover a security vulnerability, please send an email to the maintainers. All security vulnerabilities will be promptly addressed.

## Migration Guide

### From v0.x to v1.0.0
This is the initial stable release. No migration needed.

### Future Migrations
Breaking changes will be clearly documented here with migration instructions.