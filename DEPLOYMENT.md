# Deployment Guide for devtools-py

This guide explains how to deploy the devtools-py package to PyPI.

## Prerequisites

1. **Install deployment dependencies:**
   ```bash
   pip install build twine
   ```

2. **Configure PyPI credentials:**
   
   Create a `.pypirc` file in your home directory with your PyPI API tokens:
   ```bash
   cp .pypirc.template ~/.pypirc
   ```
   
   Then edit `~/.pypirc` and replace the placeholder tokens with your actual API tokens:
   - Get PyPI token from: https://pypi.org/manage/account/token/
   - Get TestPyPI token from: https://test.pypi.org/manage/account/token/

   Alternatively, you can set environment variables:
   ```bash
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=<your-pypi-api-token>
   ```

## Deployment Process

### 1. Prepare for Release

1. **Update version** (if needed):
   ```bash
   python scripts/version_manager.py bump patch  # or minor/major
   ```

2. **Run validation:**
   ```bash
   python scripts/build_validate_simple.py
   ```

### 2. Test Deployment (Recommended)

Deploy to TestPyPI first to verify everything works:

```bash
python scripts/deploy.py --test-pypi
```

Verify the test deployment:
```bash
python scripts/verify_deployment.py --test-pypi --version <version>
```

### 3. Production Deployment

Deploy to PyPI:
```bash
python scripts/deploy.py
```

Verify the production deployment:
```bash
python scripts/verify_deployment.py --version <version>
```

## Manual Deployment (Alternative)

If you prefer to deploy manually:

1. **Build the package:**
   ```bash
   python -m build
   ```

2. **Check the build:**
   ```bash
   python -m twine check dist/*
   ```

3. **Upload to TestPyPI:**
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

4. **Upload to PyPI:**
   ```bash
   python -m twine upload dist/*
   ```

## Using Makefile

The project includes a Makefile with convenient targets:

```bash
# Build and validate
make build

# Release with patch version bump
make release-patch

# Release with minor version bump
make release-minor

# Release with major version bump
make release-major
```

## Troubleshooting

### Common Issues

1. **Authentication errors:**
   - Verify your API tokens are correct
   - Check that `.pypirc` file has correct permissions (600)
   - Ensure you're using `__token__` as username

2. **Version conflicts:**
   - PyPI doesn't allow re-uploading the same version
   - Bump the version number and try again

3. **Package validation errors:**
   - Run `python -m twine check dist/*` to see specific issues
   - Fix any metadata or content issues

4. **Upload timeouts:**
   - Large packages may timeout on slow connections
   - Try uploading again or use a faster connection

### Getting Help

- Check the [Twine documentation](https://twine.readthedocs.io/)
- Review [PyPI help](https://pypi.org/help/)
- Check package status at https://pypi.org/project/devtools-py/

## Security Notes

- Never commit API tokens to version control
- Use API tokens instead of passwords
- Regularly rotate your API tokens
- Consider using GitHub Actions for automated deployment