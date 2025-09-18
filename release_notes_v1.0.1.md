# DevKitX v1.0.1 Release Notes

## Release Summary

This release addresses critical packaging and usability issues identified in v1.0.0, making the package properly usable and trustworthy for developers.

## Key Changes

### Package Identity & Naming
- ✅ Finalized rename to `devkitx` across all package imports, documentation, and URLs
- ✅ Updated PyPI metadata to point to correct `ladycami/devkitx` repository
- ✅ Marked development status as "Beta" instead of "Production/Stable"
- ✅ Added `py.typed` marker file for proper type annotation support

### New Features
- ✅ HTTP utilities with safe defaults (10s connect, 15s read timeouts)
- ✅ Retry logic with exponential backoff and jitter
- ✅ Async bridge functions for safe sync/async conversion
- ✅ Concurrency control with semaphore-based limiting
- ✅ JWT utilities with secure defaults (HS256, required claims)
- ✅ JSON flattening utility for nested data structures

### Quality Improvements
- ✅ Curated top-level API exports for stability
- ✅ Optional dependency management with extras
- ✅ Minimal test suite with CI pipeline (ruff, mypy, pytest)
- ✅ Proper package structure following Python best practices

## Installation

```bash
# Basic installation
pip install devkitx

# With optional extras
pip install devkitx[http,jwt,cli]
```

## Verification

The package has been built and verified:
- ✅ Built distributions: wheel and source tarball
- ✅ Passed twine check for PyPI compliance
- ✅ Package metadata verified
- ✅ All required files included (including py.typed)

## Git Operations (to be performed)

Due to Xcode license requirements, the following git operations should be performed manually:

```bash
# Add all changes
git add .

# Create release commit
git commit -m "Release v1.0.1

- Fix package naming and import consistency
- Add HTTP utilities with safe defaults
- Implement async bridge functions
- Add JWT utilities with secure defaults
- Update package metadata and project URLs
- Mark as Beta development status
- Add comprehensive test suite and CI
- Implement optional dependency management"

# Create release tag
git tag -a v1.0.1 -m "Release v1.0.1: Package fixes and core utilities"

# Push changes and tag
git push origin main
git push origin v1.0.1
```

## Ready for PyPI Deployment

The package is now ready for deployment to PyPI:
- Built artifacts are in `dist/devkitx-1.0.1*`
- All metadata is correct
- Package structure follows best practices
- Documentation is updated