# Contributing to Woosoo Deployment Manager

Thank you for your interest in contributing! This guide will help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project team. All complaints will be reviewed and investigated promptly and fairly.

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Python 3.11+** installed
- **Git** for version control
- **Windows 10/11** for development (tool is Windows-specific)
- **Administrator access** for testing service functionality
- **Code editor** (VS Code recommended)

### Types of Contributions

We welcome:
- **Bug reports** - Found an issue? Let us know!
- **Feature requests** - Ideas for improvements
- **Code contributions** - Bug fixes, new features, optimizations
- **Documentation** - Improvements to guides, examples, comments
- **Testing** - Help test on different Windows versions/configurations

## Development Setup

### 1. Fork and Clone

```powershell
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/woosoo-deployment-manager.git
cd woosoo-deployment-manager
```

### 2. Set Up Development Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r deployment_manager\requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy
```

### 3. Create Configuration

```powershell
# Copy template
copy deployment.config.env.template deployment.config.env

# Or use local example
copy examples\deployment.config.env.local deployment.config.env

# Edit for your environment
notepad deployment.config.env
```

### 4. Verify Setup

```powershell
# Run validation
python deployment_manager\main.py validate

# Check config
python deployment_manager\main.py config

# Run tests (when added)
pytest
```

## Project Structure

```
woosoo-deployment-manager/
├── deployment_manager/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # CLI entry point (Click commands)
│   ├── config.py             # Configuration management
│   ├── services.py           # Windows service management (NSSM)
│   ├── validators.py         # Pre-flight validation
│   ├── requirements.txt      # Python dependencies
│   └── build_exe.py          # PyInstaller build script
├── bin/
│   ├── nssm/                 # NSSM service wrapper
│   │   ├── win64/nssm.exe
│   │   └── win32/nssm.exe
│   └── mkcert/               # Certificate generation
│       └── mkcert.exe
├── docs/
│   ├── COMPREHENSIVE.md      # User guide
│   ├── REQUIREMENTS.md       # Technical requirements
│   ├── AUDIT.md              # Pre-migration audit
│   ├── INSTALLATION.md       # Installation guide
│   ├── CONFIGURATION.md      # Config reference
│   ├── TROUBLESHOOTING.md    # Problem solutions
│   └── CONTRIBUTING.md       # This file
├── examples/
│   ├── deployment.config.env.local     # Local example
│   ├── deployment.config.env.staging   # Staging example
│   ├── deployment.config.env.production # Production example
│   └── README.md                        # Examples guide
├── .github/
│   └── workflows/
│       └── build.yml         # CI/CD workflow
├── deployment.config.env.template     # Config template
├── .gitignore                # Git ignore rules
├── README.md                 # Main readme
├── LICENSE                   # MIT License
├── CHANGELOG.md              # Version history
└── setup.bat                 # Quick setup script
```

### Key Modules

#### `main.py` - CLI Interface
- Uses Click framework for commands
- Command groups: `cli`, `service`, `deploy`
- Context passing for project_root
- Entry point: `if __name__ == '__main__': cli()`

#### `config.py` - Configuration
- `DeploymentConfig` dataclass with all settings
- `ConfigManager` loads and validates .env file
- Environment variable support (`WOOSOO_PROJECT_ROOT`)
- Path resolution (relative to project root)

#### `services.py` - Service Management
- `ServiceManager` wraps NSSM functionality
- `SERVICES_TEMPLATE` defines service configurations
- Dynamic path configuration at initialization
- Service operations: install, start, stop, restart, uninstall, status

#### `validators.py` - Validation
- `SystemValidator` checks system requirements
- Pre-flight validation before deployment
- Checks: Python version, admin rights, resources, ports

## Development Workflow

### 1. Create a Branch

```powershell
# Always branch from main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name

# Or bug fix branch
git checkout -b fix/issue-number-description
```

**Branch naming:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation only
- `refactor/` - Code refactoring
- `test/` - Test additions/changes

### 2. Make Changes

**Development cycle:**
1. Write/modify code
2. Test locally
3. Update documentation
4. Add/update tests
5. Commit changes

**Testing your changes:**
```powershell
# Run validation
python deployment_manager\main.py validate

# Test configuration
python deployment_manager\main.py config

# Test service operations (as admin)
python deployment_manager\main.py service status --all

# Build executable (optional)
python deployment_manager\build_exe.py
```

### 3. Commit Changes

```powershell
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: Add support for custom service names"

# Or for bug fix
git commit -m "fix: Resolve port conflict detection issue"
```

**Commit message format:**
```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `style:` - Code style (formatting, no logic change)
- `refactor:` - Code refactoring
- `test:` - Adding/updating tests
- `chore:` - Maintenance (dependencies, build)

**Examples:**
```
feat: Add rollback command for failed deployments

Implements automatic rollback when deployment fails validation.
Includes backup of previous state before deployment starts.

Closes #42
```

### 4. Push and Create Pull Request

```powershell
# Push to your fork
git push origin feature/your-feature-name
```

Then on GitHub:
1. Navigate to your fork
2. Click "Compare & pull request"
3. Fill in PR template
4. Submit for review

## Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications.

**Key points:**
- **Indentation:** 4 spaces (no tabs)
- **Line Length:** 100 characters (slightly more than PEP 8's 79)
- **Imports:** Grouped by standard library, third-party, local
- **Naming:**
  - `snake_case` for functions, variables, methods
  - `PascalCase` for classes
  - `UPPER_CASE` for constants

**Example:**
```python
"""Module docstring describing purpose."""

import os
from pathlib import Path
from typing import Optional

from click import command, option
from colorama import Fore

from .config import ConfigManager

# Constants
DEFAULT_PORT = 8000
MAX_RETRIES = 3


class ServiceManager:
    """Manages Windows services using NSSM."""

    def __init__(self, config_path: Path, backend_dir: Optional[Path] = None):
        """Initialize service manager.

        Args:
            config_path: Path to configuration file
            backend_dir: Optional backend directory override
        """
        self.config_path = config_path
        self.backend_dir = backend_dir or Path("apps/woosoo-nexus")

    def install_service(self, service_name: str, *, force: bool = False) -> bool:
        """Install Windows service.

        Args:
            service_name: Name of service to install
            force: Whether to reinstall if exists

        Returns:
            True if successful, False otherwise

        Raises:
            PermissionError: If not running as administrator
        """
        if not self._check_admin():
            raise PermissionError("Administrator rights required")

        # Implementation...
        return True


def validate_port(port: int) -> bool:
    """Validate port number is in valid range.

    Args:
        port: Port number to validate

    Returns:
        True if valid, False otherwise
    """
    return 1024 <= port <= 65535
```

### Code Formatting

**Use Black for automated formatting:**
```powershell
# Format all code
black deployment_manager/

# Check formatting without changes
black --check deployment_manager/
```

**Black configuration** (in `pyproject.toml` if added):
```toml
[tool.black]
line-length = 100
target-version = ['py311']
```

### Linting

**Use Flake8 for linting:**
```powershell
# Lint all code
flake8 deployment_manager/

# Configuration in setup.cfg or .flake8
```

**Flake8 configuration:**
```ini
[flake8]
max-line-length = 100
exclude = .git,__pycache__,build,dist,venv
ignore = E203,W503  # Black compatibility
```

### Type Hints

**Use type hints for all functions:**
```python
from typing import Optional, List, Dict

def process_config(
    config_path: Path,
    options: Optional[Dict[str, str]] = None
) -> List[str]:
    """Process configuration file."""
    # Implementation...
    return []
```

**Check types with mypy:**
```powershell
mypy deployment_manager/
```

### Documentation

**Docstrings for all public functions/classes:**
```python
def install_service(self, name: str, force: bool = False) -> bool:
    """Install a Windows service using NSSM.

    This function creates a new Windows service with the specified
    configuration. If the service already exists, it will fail unless
    the force parameter is set to True.

    Args:
        name: The display name for the service
        force: If True, reinstall existing service. Default is False.

    Returns:
        True if installation succeeded, False otherwise.

    Raises:
        PermissionError: If not running with administrator privileges
        FileNotFoundError: If NSSM executable not found
        ValueError: If service configuration is invalid

    Example:
        >>> manager = ServiceManager(config_path)
        >>> manager.install_service("WoosooBackend")
        True
    """
```

## Testing

### Running Tests

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=deployment_manager --cov-report=html

# Run specific test
pytest tests/test_config.py

# Run with verbose output
pytest -v
```

### Writing Tests

**Test file structure:**
```
tests/
├── __init__.py
├── test_config.py
├── test_services.py
├── test_validators.py
└── fixtures/
    └── sample.config.env
```

**Example test:**
```python
"""Tests for configuration management."""

import pytest
from pathlib import Path
from deployment_manager.config import ConfigManager, DeploymentConfig


@pytest.fixture
def sample_config(tmp_path):
    """Create a sample configuration file."""
    config_file = tmp_path / "deployment.config.env"
    config_file.write_text("""
DEPLOYMENT_ENV=development
SERVER_IP=127.0.0.1
USE_TLS=false
NGINX_HTTPS_PORT=8000
    """)
    return config_file


def test_config_loading(sample_config):
    """Test loading configuration from file."""
    manager = ConfigManager(sample_config)
    config = manager.load()

    assert config.deployment_env == "development"
    assert config.server_ip == "127.0.0.1"
    assert config.use_tls is False
    assert config.nginx_https_port == 8000


def test_invalid_ip_raises_error():
    """Test that invalid IP address raises ValueError."""
    with pytest.raises(ValueError, match="Invalid IP address"):
        DeploymentConfig(server_ip="invalid.ip")


def test_port_validation():
    """Test port number validation."""
    # Valid port
    config = DeploymentConfig(nginx_https_port=8000)
    assert config.nginx_https_port == 8000

    # Invalid port (too low)
    with pytest.raises(ValueError):
        DeploymentConfig(nginx_https_port=80)

    # Invalid port (too high)
    with pytest.raises(ValueError):
        DeploymentConfig(nginx_https_port=70000)
```

### Manual Testing Checklist

Before submitting PR, manually test:

- [ ] Configuration validation with valid config
- [ ] Configuration validation with invalid config
- [ ] System validation on target Windows version
- [ ] Service installation (as admin)
- [ ] Service start/stop/restart
- [ ] Service status checking
- [ ] Service uninstallation
- [ ] Build executable with PyInstaller
- [ ] Run executable from different directory

## Documentation

### Documentation Requirements

**All PRs must include:**
- **Code comments** for complex logic
- **Docstrings** for public functions/classes
- **README updates** if adding features
- **CHANGELOG updates** with changes
- **Example updates** if changing config format

### Writing Documentation

**Documentation style:**
- Clear, concise language
- Examples for all features
- Common pitfalls and solutions
- Cross-references to related docs

**Updating CHANGELOG.md:**
```markdown
## [Unreleased]

### Added
- Support for custom service names
- Rollback command for failed deployments

### Changed
- Improved error messages for port conflicts

### Fixed
- Service status detection on Windows 11
```

## Submitting Changes

### Pull Request Process

1. **Ensure your PR:**
   - Addresses a specific issue or feature
   - Includes tests for new functionality
   - Updates documentation
   - Passes all CI checks
   - Follows coding standards

2. **PR Title Format:**
   ```
   <type>: <short description>
   ```
   Example: `feat: Add rollback command`

3. **PR Description Template:**
   ```markdown
   ## Description
   Brief description of changes

   ## Motivation and Context
   Why is this change needed? What problem does it solve?

   ## Type of Change
   - [ ] Bug fix (non-breaking change fixing an issue)
   - [ ] New feature (non-breaking change adding functionality)
   - [ ] Breaking change (fix or feature causing existing functionality to not work as expected)
   - [ ] Documentation update

   ## Testing
   How has this been tested?
   - [ ] Unit tests
   - [ ] Integration tests
   - [ ] Manual testing

   ## Checklist
   - [ ] Code follows project style guidelines
   - [ ] Self-review completed
   - [ ] Code comments added for complex areas
   - [ ] Documentation updated
   - [ ] No new warnings generated
   - [ ] Tests added/updated
   - [ ] All tests passing
   - [ ] CHANGELOG.md updated

   ## Related Issues
   Closes #42
   Related to #38
   ```

4. **Review Process:**
   - Maintainer will review within 1-3 business days
   - Address feedback through discussion or new commits
   - Once approved, maintainer will merge

5. **After Merge:**
   - Delete your branch
   - Update your fork
   ```powershell
   git checkout main
   git pull upstream main
   git push origin main
   ```

### Commit Guidelines

**Good commits:**
- Atomic (one logical change per commit)
- Descriptive message explaining *why*
- References issue numbers

**Bad commits:**
- Too large (many unrelated changes)
- Vague messages ("fixed stuff", "updates")
- No context

## Release Process

### Versioning

We use **Semantic Versioning** (SemVer): `MAJOR.MINOR.PATCH`

- **MAJOR:** Breaking changes
- **MINOR:** New features (backward compatible)
- **PATCH:** Bug fixes (backward compatible)

### Release Checklist

For maintainers releasing new versions:

1. **Update Version:**
   - `deployment_manager/__init__.py`: `__version__ = "2.1.0"`
   - `CHANGELOG.md`: Move `[Unreleased]` to `[2.1.0] - 2026-01-XX`

2. **Build and Test:**
   ```powershell
   # Run all tests
   pytest

   # Build executable
   python deployment_manager\build_exe.py

   # Test executable
   dist\deployment-manager\deployment-manager.exe --version
   ```

3. **Create Git Tag:**
   ```powershell
   git add .
   git commit -m "chore: Release v2.1.0"
   git tag -a v2.1.0 -m "Release v2.1.0"
   git push origin main --tags
   ```

4. **Create GitHub Release:**
   - Go to GitHub → Releases → New Release
   - Choose tag `v2.1.0`
   - Title: `v2.1.0`
   - Description: Copy from CHANGELOG.md
   - Attach: `deployment-manager.exe` (built executable)

5. **Announce:**
   - Update README.md download links
   - Post in discussions/community channels

## Questions?

- **General Questions:** Open a GitHub Discussion
- **Bug Reports:** Create an Issue
- **Security Issues:** Email security@example.com (do not open public issue)
- **Chat:** Join our Discord (if applicable)

## Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort! 🙏
