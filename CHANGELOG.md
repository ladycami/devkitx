# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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