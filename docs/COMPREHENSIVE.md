# Woosoo Deployment Manager - Comprehensive Documentation

**Version:** 2.0.0  
**Date:** February 15, 2026  
**Status:** Production Ready (with enhancements planned)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Architecture](#architecture)
4. [Folder Structure](#folder-structure)
5. [Current Features](#current-features)
6. [Installation Guide](#installation-guide)
7. [Usage Guide](#usage-guide)
8. [Enhancements & Improvements](#enhancements--improvements)
9. [Roadmap](#roadmap)
10. [Troubleshooting](#troubleshooting)
11. [Best Practices](#best-practices)

---

## 🎯 Overview

The Woosoo Deployment Manager is a comprehensive Python-based tool designed to simplify deployment, service management, and configuration for the Woosoo monorepo. It provides both interactive (TUI) and command-line interfaces for managing Windows services, validating system readiness, and orchestrating deployments.

### Key Goals
- **Simplify Deployment** - One command to deploy entire stack
- **Service Management** - Install, start, stop, monitor Windows services
- **Pre-Flight Validation** - Comprehensive system checks before deployment
- **Configuration Management** - Centralized config sync across all apps
- **Single Executable** - Portable .exe with no runtime dependencies

---

## 💻 System Requirements

### Runtime Requirements (for .exe)

| Component | Requirement | Purpose |
|-----------|-------------|---------|
| **Operating System** | Windows 10/11 or Server 2019+ | Base OS |
| **Architecture** | x64 (64-bit) | Modern hardware |
| **Administrator Rights** | Required | Service management, file operations |
| **Disk Space** | 5 GB free minimum | Deployment artifacts, logs, backups |
| **RAM** | 4 GB minimum, 8 GB recommended | Build processes, services |
| **CPU** | 2 cores minimum, 4+ recommended | Concurrent operations |

### Development Tools (must be installed on target machine)

| Tool | Version | Required For | Installation |
|------|---------|--------------|--------------|
| **Node.js** | 18.0+ | PWA build, config sync | https://nodejs.org/ |
| **PHP** | 8.2+ | Laravel backend | https://windows.php.net/ |
| **Composer** | 2.0+ | PHP dependencies | https://getcomposer.org/ |
| **MySQL/MariaDB** | 8.0+/10.5+ | Database | Laragon or standalone |
| **Flutter** | 3.0+ (optional) | Relay device APK | https://flutter.dev/ |
| **Git** | Latest (optional) | Version control | https://git-scm.com/ |

### PHP Extensions Required

```ini
extension=mbstring
extension=pdo_mysql
extension=openssl
extension=json
extension=curl
extension=bcmath
extension=fileinfo
extension=tokenizer
```

### Development Requirements (for Python development)

| Component | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.11+ | Runtime environment |
| **pip** | Latest | Package management |
| **PyInstaller** | 6.3+ | Executable builder |

---

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│           Woosoo Deployment Manager                     │
│                                                           │
│  ┌─────────────────┐        ┌─────────────────┐        │
│  │   CLI Interface │        │  TUI Dashboard  │        │
│  └────────┬────────┘        └────────┬────────┘        │
│           │                          │                  │
│           └──────────┬───────────────┘                  │
│                      │                                   │
│           ┌──────────▼──────────┐                       │
│           │   Core Orchestrator │                       │
│           └──────────┬──────────┘                       │
│                      │                                   │
│      ┌───────────────┼───────────────┐                 │
│      │               │               │                  │
│ ┌────▼────┐    ┌────▼────┐    ┌────▼────┐             │
│ │Validator│    │ Config  │    │ Service │             │
│ │ Engine  │    │ Manager │    │ Manager │             │
│ └─────────┘    └─────────┘    └────┬────┘             │
│                                     │                   │
└─────────────────────────────────────┼───────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
              ┌─────▼─────┐    ┌─────▼─────┐    ┌─────▼─────┐
              │   NSSM    │    │  Windows  │    │   System  │
              │  (win64)  │    │ Services  │    │    API    │
              └───────────┘    └───────────┘    └───────────┘
```

### Component Responsibilities

1. **CLI Interface** (`main.py`)
   - Command parsing and routing
   - User input handling
   - Output formatting

2. **TUI Dashboard** (`main.py`)
   - Real-time service monitoring
   - Configuration display
   - Interactive navigation

3. **Core Orchestrator** (`main.py`)
   - Coordinates all operations
   - Error handling and logging
   - State management

4. **Validator Engine** (`validators.py`)
   - Pre-flight system checks
   - Dependency verification
   - Port availability testing

5. **Config Manager** (`config.py`)
   - Load `deployment.config.env`
   - Validate configuration
   - Sync to app-specific configs

6. **Service Manager** (`services.py`)
   - NSSM wrapper for service control
   - Service status monitoring
   - Log redirection management

---

## 📁 Folder Structure

### Current Structure

```
project-woosoo/
├── deployment_manager/              # Python deployment manager
│   ├── __init__.py                  # Package initialization
│   ├── main.py                      # CLI/TUI entry point (1,000+ lines)
│   ├── config.py                    # Configuration management (300+ lines)
│   ├── validators.py                # Pre-flight validation (500+ lines)
│   ├── services.py                  # Service management (400+ lines)
│   ├── requirements.txt             # Python dependencies
│   ├── build_exe.py                 # PyInstaller build script
│   ├── README.md                    # Quick reference
│   └── assets/                      # Icons, resources (optional)
│       └── icon.ico                 # Application icon
│
├── deployment.config.env            # Master configuration (SINGLE SOURCE OF TRUTH)
│
├── bin/                             # Binary tools
│   ├── nssm/                        # Non-Sucking Service Manager
│   │   ├── win64/                   # 64-bit NSSM
│   │   │   └── nssm.exe
│   │   └── win32/                   # 32-bit NSSM
│   │       └── nssm.exe
│   ├── mkcert/                      # Certificate generation
│   │   └── mkcert.exe
│   ├── nginx/                       # Nginx web server
│   └── php/                         # PHP binaries (if embedded)
│
├── logs/                            # Service and deployment logs
│   ├── reverb/                      # Reverb WebSocket logs
│   │   ├── output.log
│   │   └── error.log
│   ├── queue/                       # Queue worker logs
│   │   ├── output.log
│   │   └── error.log
│   ├── nginx/                       # Nginx logs
│   │   ├── access.log
│   │   └── error.log
│   └── deployment/                  # Deployment operation logs
│       └── deploy-2026-02-15.log
│
├── backups/                         # Automatic backups
│   └── 2026-02-15_14-30-00/         # Timestamped backup
│       ├── deployment.config.env
│       ├── apps/                    # App configs
│       └── metadata.json            # Backup context
│
├── configs/                         # Server configurations
│   ├── nginx.conf                   # Nginx configuration
│   ├── php-fpm.conf                 # PHP-FPM settings
│   └── deployment_manager.yaml      # Manager settings (future)
│
├── certs/                           # TLS certificates
│   ├── 192.168.100.85+3.pem        # Certificate
│   └── 192.168.100.85+3-key.pem    # Private key
│
├── apps/                            # Application directories
│   ├── woosoo-nexus/                # Laravel backend
│   ├── tablet-ordering-pwa/         # Nuxt PWA
│   └── relay-device-v2/             # Flutter app
│
├── scripts/                         # Legacy PowerShell scripts
│   ├── deploy-complete.ps1
│   ├── install-services.ps1
│   └── [other scripts]
│
└── vault/                           # Archived documentation
    └── [historical files]
```

### Proposed Enhanced Structure

```
project-woosoo/
├── deployment_manager/              # Refactored for modularity
│   ├── __init__.py
│   ├── main.py                      # Entry point (simplified)
│   │
│   ├── core/                        # Core functionality
│   │   ├── __init__.py
│   │   ├── orchestrator.py          # Main deployment orchestrator
│   │   ├── logger.py                # Centralized logging
│   │   └── exceptions.py            # Custom exceptions
│   │
│   ├── cli/                         # Command-line interface
│   │   ├── __init__.py
│   │   ├── commands.py              # Click commands
│   │   └── formatters.py            # Output formatting
│   │
│   ├── tui/                         # Terminal UI (Textual)
│   │   ├── __init__.py
│   │   ├── dashboard.py             # Main dashboard widget
│   │   ├── service_view.py          # Service status widget
│   │   └── config_editor.py         # Config editor widget
│   │
│   ├── managers/                    # Business logic
│   │   ├── __init__.py
│   │   ├── config_manager.py        # Configuration management
│   │   ├── service_manager.py       # Service operations
│   │   ├── certificate_manager.py   # Certificate operations
│   │   ├── deployment_manager.py    # Deployment orchestration
│   │   └── backup_manager.py        # Backup/rollback
│   │
│   ├── validators/                  # Validation modules
│   │   ├── __init__.py
│   │   ├── base.py                  # Base validator class
│   │   ├── system_validator.py      # System checks
│   │   ├── tool_validator.py        # Tool version checks
│   │   ├── config_validator.py      # Config validation
│   │   └── network_validator.py     # Network/port checks
│   │
│   ├── builders/                    # Build orchestration
│   │   ├── __init__.py
│   │   ├── backend_builder.py       # Laravel build
│   │   ├── pwa_builder.py           # Nuxt build
│   │   └── relay_builder.py         # Flutter build
│   │
│   ├── models/                      # Data models
│   │   ├── __init__.py
│   │   ├── config.py                # Config dataclasses
│   │   ├── service.py               # Service models
│   │   └── validation.py            # Validation results
│   │
│   ├── utils/                       # Utilities
│   │   ├── __init__.py
│   │   ├── file_utils.py            # File operations
│   │   ├── network_utils.py         # Network utilities
│   │   ├── process_utils.py         # Process management
│   │   └── parser_utils.py          # Parsing helpers
│   │
│   ├── templates/                   # Config templates
│   │   ├── nginx.conf.j2            # Nginx template
│   │   ├── .env.j2                  # Laravel .env template
│   │   └── service.xml.j2           # NSSM service template
│   │
│   ├── tests/                       # Unit tests
│   │   ├── __init__.py
│   │   ├── test_config.py
│   │   ├── test_services.py
│   │   └── test_validators.py
│   │
│   ├── requirements.txt             # Python dependencies
│   ├── requirements-dev.txt         # Development dependencies
│   ├── build_exe.py                 # Build script
│   ├── setup.py                     # Package setup
│   └── README.md
│
├── deployment.config.env            # Master config
├── .deployment_manager.yaml         # Manager preferences
│
└── [rest of project structure...]
```

---

## ✨ Current Features

### 1. Pre-Flight Validation

- ✅ **System Checks**
  - Administrator privileges
  - Disk space availability (5GB+ check)
  - System RAM and CPU cores
  - Windows version detection

- ✅ **Tool Detection**
  - Node.js version validation (18+)
  - PHP version validation (8.2+)
  - Composer version validation (2.0+)
  - Flutter SDK detection (optional)
  - MySQL/MariaDB availability

- ✅ **PHP Extensions**
  - Validates 7 required extensions
  - Reports missing extensions with recommendations

- ✅ **Configuration**
  - Validates `deployment.config.env` exists
  - Checks required configuration keys
  - IP address format validation
  - Port range validation (1024-65535)

- ✅ **Network**
  - Port availability checks (8000, 80, 6001)
  - IP reachability (ping test)
  - Service conflict detection

- ✅ **Permissions**
  - Write permissions to project directory
  - Service management capability

### 2. Service Management

- ✅ **Service Control**
  - Install services via NSSM
  - Start/stop/restart services
  - Resume paused services
  - Uninstall services
  - Bulk operations (all services)

- ✅ **Managed Services**
  - `woosoo-reverb` - Laravel Reverb WebSocket server
  - `woosoo-queue-worker` - Laravel queue processor
  - `woosoo-nginx` - Nginx web server

- ✅ **Service Configuration**
  - Auto-configures working directories
  - Sets up log redirection
  - Configures auto-start behavior
  - Handles service dependencies

- ✅ **Status Monitoring**
  - Real-time service status
  - Detects: Running, Stopped, Paused, Not Installed

### 3. Configuration Management

- ✅ **Master Configuration**
  - Single source of truth (`deployment.config.env`)
  - Environment-specific settings
  - Network configuration (IP, ports)
  - Database credentials
  - TLS/SSL settings

- ✅ **Validation**
  - Schema validation
  - Type checking
  - Required field verification
  - Range validation (ports, IPs)

- ✅ **Display**
  - Pretty-printed configuration summary
  - Validation status with errors
  - Color-coded output

### 4. User Interface

- ✅ **TUI Dashboard**
  - Service status overview
  - Configuration summary
  - Color-coded status indicators
  - Clean, modern design using Rich library

- ✅ **CLI Commands**
  - `check` - Run pre-flight validation
  - `dashboard` - Show interactive dashboard
  - `start/stop/restart` - Service control
  - `install/uninstall` - Service lifecycle
  - `config` - Configuration display
  - `version` - Version information

- ✅ **Output Formatting**
  - Tables with borders
  - Color-coded icons (✓, ✗, ●, ○, ⏸)
  - Progress indicators
  - Structured error messages

### 5. Platform Integration

- ✅ **Windows Services**
  - Native Windows service integration
  - NSSM wrapper for robust service management
  - Auto-restart on failure support
  - Log redirection to files

- ✅ **Architecture Detection**
  - Auto-detects x64 vs x86
  - Uses appropriate NSSM binary
  - Platform-specific path handling

---

## 📦 Installation Guide

### Quick Setup (3 Steps)

#### Step 1: Install Python
```powershell
# Download Python 3.11+ from https://python.org
# IMPORTANT: Check "Add Python to PATH" during installation
```

#### Step 2: Run Setup Script
```powershell
cd C:\laragon\www\project-woosoo
.\setup_deployment_manager.bat
```

#### Step 3: Verify Installation
```powershell
python deployment_manager\main.py check --verbose
```

### Manual Installation

```powershell
# Install dependencies
cd deployment_manager
pip install -r requirements.txt

# Test
python main.py --help
```

### Building Executable

```powershell
# Install PyInstaller
pip install pyinstaller

# Build
python deployment_manager\build_exe.py

# Result: deployment_manager\dist\woosoo-deploy-manager.exe
```

---

## 📖 Usage Guide

### Basic Commands

```powershell
# Show dashboard
python deployment_manager\main.py
python deployment_manager\main.py dashboard

# Run system validation
python deployment_manager\main.py check
python deployment_manager\main.py check --verbose

# Service management
python deployment_manager\main.py install all
python deployment_manager\main.py start all
python deployment_manager\main.py stop all
python deployment_manager\main.py uninstall all --confirm

# Individual services
python deployment_manager\main.py start reverb
python deployment_manager\main.py stop nginx
python deployment_manager\main.py restart queue

# Configuration
python deployment_manager\main.py config

# Version info
python deployment_manager\main.py version
python deployment_manager\main.py --help
```

### Using the Executable

```powershell
# Copy to convenient location
copy deployment_manager\dist\woosoo-deploy-manager.exe C:\Tools\

# Run from anywhere
woosoo-deploy-manager.exe
woosoo-deploy-manager.exe check
woosoo-deploy-manager.exe start all
```

### Administrator Privileges

**CRITICAL:** Service management requires Administrator rights!

```powershell
# Verify admin status
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
# Should return: True

# If False, close and reopen PowerShell as Administrator:
# 1. Right-click PowerShell icon
# 2. Select "Run as Administrator"
# 3. Click "Yes" on UAC prompt
```

---

## 🚀 Enhancements & Improvements

### Priority 1: Critical Enhancements

#### 1.1 Deployment Orchestration
```python
# Add full deployment workflow
python deployment_manager\main.py deploy --full
python deployment_manager\main.py deploy --backend-only
python deployment_manager\main.py deploy --pwa-only
```

**Features:**
- Pre-deployment backup
- Config sync
- Build orchestration (Laravel, Nuxt, Flutter)
- Service restart
- Health checks
- Automatic rollback on failure

#### 1.2 Backup & Rollback System
```python
# Backup management
python deployment_manager\main.py backup create
python deployment_manager\main.py backup list
python deployment_manager\main.py backup restore 2026-02-15_14-30-00
python deployment_manager\main.py backup cleanup --older-than 30d
```

**Features:**
- Automatic pre-deployment backups
- Config file snapshots
- Database dumps (optional)
- Timestamped archives
- One-click rollback
- Backup retention policies

#### 1.3 Certificate Management
```python
# Certificate operations
python deployment_manager\main.py cert generate
python deployment_manager\main.py cert info
python deployment_manager\main.py cert verify
python deployment_manager\main.py cert trust
```

**Features:**
- mkcert integration
- Auto-generate self-signed certs
- Certificate expiry warnings
- Trust store management
- Certificate renewal

#### 1.4 Log Viewer
```python
# Log management
python deployment_manager\main.py logs reverb --tail
python deployment_manager\main.py logs reverb --lines 100
python deployment_manager\main.py logs all --errors-only
python deployment_manager\main.py logs search "error"
```

**Features:**
- Real-time log tailing
- Multi-service log aggregation
- Log level filtering
- Search and filter
- Export logs
- Color-coded output

### Priority 2: Quality of Life

#### 2.1 Interactive Configuration Editor
```python
python deployment_manager\main.py config edit
```

**Features:**
- TUI-based config editor
- Field validation in real-time
- Help text for each setting
- Preview changes before saving
- Automatic backup before changes

#### 2.2 Health Monitoring
```python
python deployment_manager\main.py health
python deployment_manager\main.py health --watch
```

**Features:**
- Service health status
- CPU/Memory usage per service
- WebSocket connection test
- Database connectivity test
- API endpoint checks
- Response time metrics
- Auto-refresh display

#### 2.3 Deployment Reports
```python
python deployment_manager\main.py deploy --report report.json
python deployment_manager\main.py deploy --report report.html
```

**Features:**
- JSON/HTML/PDF reports
- Deployment timeline
- Success/failure metrics
- Error logs
- System snapshot
- Email/Slack notifications

### Priority 3: Advanced Features

#### 3.1 Web-Based Interface
```python
python deployment_manager\main.py serve --port 8080
# Opens web UI at http://localhost:8080
```

**Features:**
- Browser-based dashboard
- Remote management
- Real-time updates via WebSockets
- Mobile-responsive design
- Multi-user support
- Authentication & authorization

#### 3.2 Scheduled Deployments
```python
python deployment_manager\main.py schedule deploy --at "02:00 AM"
python deployment_manager\main.py schedule list
python deployment_manager\main.py schedule cancel <id>
```

**Features:**
- Cron-like scheduling
- Maintenance window support
- Pre-deployment notifications
- Automatic health checks
- Rollback if failures

#### 3.3 Multi-Environment Support
```python
python deployment_manager\main.py --env production deploy
python deployment_manager\main.py --env staging deploy
python deployment_manager\main.py config switch staging
```

**Features:**
- Environment profiles (dev, staging, prod)
- Environment-specific configs
- Quick environment switching
- Config inheritance
- Environment validation

#### 3.4 Dependency Management
```python
python deployment_manager\main.py deps check
python deployment_manager\main.py deps update
python deployment_manager\main.py deps audit
```

**Features:**
- Check for tool updates (Node.js, PHP, etc.)
- Security vulnerability scanning
- Dependency version tracking
- Update recommendations
- Automated updates (with confirmation)

---

## 🗓️ Roadmap

### Phase 1: Core Stability (Weeks 1-2)
- [x] Service management
- [x] Pre-flight validation
- [x] Configuration management
- [x] Basic TUI dashboard
- [x] Single executable build
- [ ] Fix paused service detection
- [ ] Improve error messages
- [ ] Add comprehensive logging

### Phase 2: Deployment Features (Weeks 3-4)
- [ ] Full deployment orchestration
- [ ] Backup & rollback system
- [ ] Certificate management
- [ ] Log viewer with tailing
- [ ] Health monitoring
- [ ] Deployment reports

### Phase 3: Advanced UX (Weeks 5-6)
- [ ] Interactive config editor
- [ ] Enhanced TUI with navigation
- [ ] Progress bars for long operations
- [ ] Real-time service monitoring
- [ ] Search and filter capabilities

### Phase 4: Enterprise Features (Weeks 7-8)
- [ ] Web-based interface
- [ ] Scheduled deployments
- [ ] Multi-environment support
- [ ] Dependency management
- [ ] CI/CD integration
- [ ] Webhook notifications

### Phase 5: Polish & Optimization (Week 9)
- [ ] Performance optimization
- [ ] Comprehensive testing
- [ ] Documentation updates
- [ ] Video tutorials
- [ ] Code signing for .exe
- [ ] Release packaging

---

## 🛠️ Technical Improvements

### Code Refactoring

#### Current Issues
- Large monolithic files (main.py 1000+ lines)
- Mixed concerns (UI + business logic)
- Limited error handling
- No unit tests
- Hard-coded paths

#### Proposed Solution
```python
# Modular structure with separation of concerns
deployment_manager/
├── core/          # Core business logic
├── cli/           # CLI interface
├── tui/           # TUI widgets
├── managers/      # Domain managers
├── validators/    # Validation modules
├── builders/      # Build orchestrators
└── tests/         # Unit tests
```

### Enhanced Error Handling

```python
# Custom exception hierarchy
class DeploymentManagerError(Exception):
    """Base exception"""
    pass

class ValidationError(DeploymentManagerError):
    """Validation failed"""
    pass

class ServiceError(DeploymentManagerError):
    """Service operation failed"""
    pass

class ConfigurationError(DeploymentManagerError):
    """Configuration invalid"""
    pass
```

### Logging Infrastructure

```python
# Centralized logging
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('deployment_manager')
handler = RotatingFileHandler(
    'logs/deployment_manager.log',
    maxBytes=10485760,  # 10MB
    backupCount=5
)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
```

### Configuration Management

```yaml
# .deployment_manager.yaml
manager:
  version: "2.0.0"
  log_level: INFO
  auto_backup: true
  backup_retention_days: 30
  
validation:
  skip_optional_tools: false
  strict_mode: false
  
services:
  auto_restart_on_failure: true
  startup_timeout_seconds: 30
  health_check_interval_seconds: 60
  
deployment:
  parallel_builds: true
  max_workers: 4
  deployment_timeout_minutes: 30
  
notifications:
  enabled: false
  slack_webhook_url: ""
  email_recipients: []
```

### Testing Framework

```python
# pytest structure
tests/
├── conftest.py              # Fixtures
├── test_config.py           # Config tests
├── test_services.py         # Service tests
├── test_validators.py       # Validator tests
├── integration/             # Integration tests
│   ├── test_deployment.py
│   └── test_workflow.py
└── fixtures/                # Test data
    ├── sample_config.env
    └── mock_services.json
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "Access is denied" (Error 5)
**Cause:** Not running as Administrator  
**Solution:**
```powershell
# Close PowerShell and reopen as Administrator
# Right-click PowerShell → "Run as Administrator"
```

#### 2. "NSSM not found"
**Cause:** Incorrect NSSM path  
**Solution:**
```powershell
# Verify NSSM exists
dir bin\nssm\win64\nssm.exe
dir bin\nssm\win32\nssm.exe
```

#### 3. Services showing "Paused"
**Cause:** Service in paused state  
**Solution:**
```powershell
# Resume services
Resume-Service -Name "woosoo-reverb","woosoo-queue-worker","woosoo-nginx"

# Or stop and restart
python deployment_manager\main.py stop all
python deployment_manager\main.py start all
```

#### 4. "Composer not found"
**Cause:** Composer not in PATH  
**Solution:**
```powershell
# Find Composer
where.exe composer

# If found, the issue is with subprocess shell=True
# Already fixed in validators.py

# If not found, install from https://getcomposer.org/
```

#### 5. Services fail to start
**Causes:**
- Ports already in use
- PHP/Node.js not in PATH
- Missing configuration
- Database not running

**Solution:**
```powershell
# Check pre-flight
python deployment_manager\main.py check --verbose

# Check ports
netstat -ano | findstr ":8000"
netstat -ano | findstr ":6001"

# Check service logs
type logs\reverb\error.log
type logs\queue\error.log
```

### Debugging Tools

```powershell
# Enable verbose logging
$env:DEPLOYMENT_MANAGER_DEBUG = "1"
python deployment_manager\main.py [command]

# Check Python environment
python --version
pip list

# Check service details
Get-Service -Name "woosoo*" | Format-List *

# Check NSSM service config
.\bin\nssm\win64\nssm.exe get woosoo-reverb Application
.\bin\nssm\win64\nssm.exe get woosoo-reverb AppDirectory
```

---

## 📝 Best Practices

### Development

1. **Always run pre-flight checks before deployment**
   ```powershell
   python deployment_manager\main.py check --verbose
   ```

2. **Use version control**
   ```bash
   git commit -m "Update deployment config"
   git tag -a v1.0.0 -m "Production release"
   ```

3. **Test in staging first**
   ```powershell
   # Future: Multi-environment support
   python deployment_manager\main.py --env staging deploy
   ```

4. **Review logs after deployment**
   ```powershell
   type logs\reverb\error.log
   type logs\deployment\deploy-2026-02-15.log
   ```

### Operations

1. **Always backup before major changes**
   ```powershell
   # Future: Backup command
   python deployment_manager\main.py backup create
   ```

2. **Monitor service health**
   ```powershell
   python deployment_manager\main.py dashboard
   Get-Service -Name "woosoo*"
   ```

3. **Keep logs for troubleshooting**
   - Retain logs for at least 30 days
   - Archive logs before cleanup
   - Monitor log file sizes

4. **Regular updates**
   - Update Node.js, PHP, Composer monthly
   - Check for security updates weekly
   - Update deployment manager quarterly

### Security

1. **Never commit secrets**
   - Use `.gitignore` for `.env` files
   - Use environment variables for sensitive data
   - Rotate credentials regularly

2. **Use HTTPS in production**
   - Generate proper TLS certificates
   - Configure nginx for SSL
   - Enforce HTTPS redirects

3. **Limit service permissions**
   - Run services with minimal privileges
   - Use dedicated service accounts
   - Restrict file system access

4. **Regular audits**
   - Review service logs
   - Check for unauthorized access
   - Monitor system resources

---

## 🎓 Training & Documentation

### For Developers

1. **Read this document thoroughly**
2. **Run through installation guide**
3. **Practice with test commands**
4. **Review code structure**
5. **Contribute improvements**

### For Operations

1. **Understand service architecture**
2. **Learn pre-flight validation**
3. **Practice deployment workflow**
4. **Master troubleshooting**
5. **Document incidents**

### Resources

- [DEPLOYMENT_MANAGER_SETUP.md](DEPLOYMENT_MANAGER_SETUP.md) - Quick setup guide
- [DEPLOYMENT_MANAGER_PLAN.md](DEPLOYMENT_MANAGER_PLAN.md) - Design document
- [deployment_manager/README.md](deployment_manager/README.md) - Technical docs
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - General deployment guide

---

## 📞 Support & Contributing

### Getting Help

1. **Check this documentation first**
2. **Review troubleshooting section**
3. **Check service logs**
4. **Contact development team**

### Contributing

1. **Fork the repository**
2. **Create feature branch**
3. **Write tests**
4. **Submit pull request**
5. **Update documentation**

### Reporting Issues

```markdown
**Environment:**
- OS: Windows 11
- Python: 3.11.5
- Node.js: 18.17.0
- PHP: 8.3.1

**Steps to reproduce:**
1. Run command X
2. Observe error Y

**Expected behavior:**
Should do Z

**Actual behavior:**
Does W instead

**Logs:**
[Attach relevant logs]
```

---

## 📊 Metrics & KPIs

### Performance Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Pre-flight check time | < 5s | ~3s |
| Service start time (all) | < 30s | ~15s |
| Full deployment time | < 10m | TBD |
| Executable size | < 25MB | ~18MB |
| Memory usage | < 100MB | ~60MB |

### Reliability Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Deployment success rate | > 95% | TBD |
| Service uptime | > 99.5% | TBD |
| Rollback success rate | > 99% | TBD |
| Mean time to recover | < 5m | TBD |

---

## 🔮 Future Vision

### Long-Term Goals

1. **Zero-Downtime Deployments**
   - Blue-green deployment
   - Rolling updates
   - Health checks before cutover

2. **Cloud Integration**
   - AWS/Azure deployment
   - Container orchestration
   - Serverless functions

3. **AI-Powered Operations**
   - Predictive failure detection
   - Automated optimization
   - Intelligent log analysis

4. **Full GitOps**
   - Git-based configuration
   - Automated deployments on commit
   - Version-controlled infrastructure

---

## 📄 License & Credits

**License:** Proprietary - Woosoo Team  
**Author:** Woosoo Development Team  
**Contributors:** [List contributors]  
**Version:** 2.0.0  
**Last Updated:** February 15, 2026  

---

**"Everything is moving according to the master schedule."**  
— Dazai Osamu, Strategist Mode
