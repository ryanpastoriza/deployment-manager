# Installation Guide

Complete installation instructions for the Woosoo Deployment Manager.

## Table of Contents

- [System Requirements](#system-requirements)
- [Pre-Installation Checklist](#pre-installation-checklist)
- [Installation Methods](#installation-methods)
  - [Method 1: Quick Setup (Recommended)](#method-1-quick-setup-recommended)
  - [Method 2: Manual Installation](#method-2-manual-installation)
  - [Method 3: Build from Source](#method-3-build-from-source)
- [Post-Installation Configuration](#post-installation-configuration)
- [Verification](#verification)
- [Troubleshooting Installation](#troubleshooting-installation)

## System Requirements

### Minimum Requirements
- **OS**: Windows 10/11 or Windows Server 2019+
- **CPU**: Dual-core 2.0 GHz
- **RAM**: 4 GB
- **Disk**: 500 MB free space
- **Python**: 3.11 or higher
- **Admin Rights**: Required for service installation

### Recommended Requirements
- **OS**: Windows 11 or Windows Server 2022
- **CPU**: Quad-core 2.5 GHz
- **RAM**: 8 GB
- **Disk**: 1 GB free space (including logs)
- **Python**: 3.12
- **Network**: Static IP configured

### Dependencies
- Python 3.11+
- pip (Python package installer)
- NSSM (included in bin/)
- mkcert (included in bin/)
- Administrative privileges

## Pre-Installation Checklist

Before installing, ensure you have:

- [ ] Administrator access to the Windows machine
- [ ] Python 3.11+ installed and added to PATH
- [ ] pip is working: `pip --version`
- [ ] Downloaded/cloned this repository
- [ ] Read the [Requirements](REQUIREMENTS.md) document
- [ ] Prepared your deployment configuration

**Test Python Installation:**
```powershell
python --version
# Should output: Python 3.11.x or higher

pip --version
# Should output: pip 23.x.x or higher
```

## Installation Methods

### Method 1: Quick Setup (Recommended)

The fastest way to get started:

1. **Navigate to the repository:**
   ```powershell
   cd C:\path\to\woosoo-deployment-manager
   ```

2. **Run the setup script:**
   ```powershell
   .\setup.bat
   ```

3. **Follow the prompts:**
   - Script checks Python version
   - Installs dependencies automatically
   - Creates configuration file from template
   - Opens config in Notepad for editing

4. **Edit configuration:**
   - Fill in your environment values
   - Save and close Notepad

5. **Verify installation:**
   ```powershell
   python deployment_manager\main.py --version
   ```

**That's it!** Skip to [Post-Installation Configuration](#post-installation-configuration).

### Method 2: Manual Installation

For users who prefer manual control:

#### Step 1: Clone/Download Repository

```powershell
# Using Git
git clone https://github.com/yourusername/woosoo-deployment-manager.git
cd woosoo-deployment-manager

# Or download ZIP and extract
```

#### Step 2: Install Python Dependencies

```powershell
pip install -r deployment_manager\requirements.txt
```

**Required packages:**
- colorama - Terminal colors
- python-dotenv - Environment file parsing
- click - CLI framework
- psutil - System monitoring
- cryptography - Certificate handling

#### Step 3: Create Configuration File

```powershell
# Copy the template
copy deployment.config.env.template deployment.config.env

# Or use an example
copy examples\deployment.config.env.local deployment.config.env
```

#### Step 4: Edit Configuration

Open `deployment.config.env` in your preferred editor:

```powershell
notepad deployment.config.env
# or
code deployment.config.env  # VS Code
```

Fill in all required values. See [CONFIGURATION.md](CONFIGURATION.md) for details.

#### Step 5: Verify Installation

```powershell
python deployment_manager\main.py config
```

You should see green checkmarks for all validations.

### Method 3: Build from Source

For building a standalone executable:

#### Step 1: Install Build Dependencies

```powershell
pip install -r deployment_manager\requirements.txt
pip install pyinstaller
```

#### Step 2: Run Build Script

```powershell
python deployment_manager\build_exe.py
```

#### Step 3: Locate Built Executable

The executable will be in:
```
dist\deployment-manager\deployment-manager.exe
```

#### Step 4: Copy Required Files

```powershell
# Create deployment folder
mkdir C:\woosoo-deployment

# Copy executable
copy dist\deployment-manager\deployment-manager.exe C:\woosoo-deployment\

# Copy bin folder
xcopy /E /I bin C:\woosoo-deployment\bin

# Copy config template
copy deployment.config.env.template C:\woosoo-deployment\deployment.config.env

# Edit config
cd C:\woosoo-deployment
notepad deployment.config.env
```

#### Step 5: Run from Anywhere

```powershell
C:\woosoo-deployment\deployment-manager.exe --help
```

**Optional:** Add `C:\woosoo-deployment` to your system PATH.

## Post-Installation Configuration

### 1. Configure Your Environment

Edit `deployment.config.env` with your specific values:

```ini
# Essential settings
DEPLOYMENT_ENV=production
SERVER_IP=192.168.1.100
USE_TLS=true

# Application paths (adjust to your project structure)
BACKEND_DIR=apps/woosoo-nexus
PWA_DIR=apps/tablet-ordering-pwa
RELAY_DIR=apps/relay-device-v2

# Tool paths (usually these defaults are fine)
NGINX_EXE=bin/nginx/nginx.exe
NGINX_CONFIG=configs/nginx.conf
```

See [CONFIGURATION.md](CONFIGURATION.md) for complete reference.

### 2. Generate TLS Certificates (if using HTTPS)

```powershell
# Using included mkcert
bin\mkcert\mkcert.exe -install
bin\mkcert\mkcert.exe -cert-file certs\localhost.pem -key-file certs\localhost-key.pem localhost 127.0.0.1 ::1

# Update config with cert paths
# TLS_CERT_PATH=certs/localhost.pem
# TLS_KEY_PATH=certs/localhost-key.pem
```

### 3. Validate Configuration

```powershell
python deployment_manager\main.py config
```

**Expected output:**
```
✓ Configuration file exists
✓ Python version (3.11.0) meets requirement
✓ Running as Administrator
✓ 4 CPU cores available
✓ 16.0 GB RAM available
✓ 500.0 GB disk space on C:
✓ All ports available
✓ Configuration is valid
```

### 4. Set Up Project Root (if needed)

If the tool isn't in your project root:

**Option A: Environment Variable**
```powershell
$env:WOOSOO_PROJECT_ROOT = "C:\path\to\your\project"
```

**Option B: CLI Option**
```powershell
python deployment_manager\main.py --project-root "C:\path\to\your\project" config
```

## Verification

### Test CLI Access

```powershell
# Check version
python deployment_manager\main.py --version

# Check help
python deployment_manager\main.py --help

# List available commands
python deployment_manager\main.py
```

### Run System Validation

```powershell
python deployment_manager\main.py validate
```

This checks:
- Python version
- Admin rights
- System resources (CPU, RAM, disk)
- Port availability
- Required files

### Test Configuration Loading

```powershell
python deployment_manager\main.py config
```

This validates:
- Config file exists and is readable
- All required fields present
- Values are valid format
- Paths exist

### Dry Run Service Installation

```powershell
python deployment_manager\main.py service install --dry-run
```

This shows what would be installed without actually installing.

## Troubleshooting Installation

### Python Not Found

**Error:**
```
'python' is not recognized as an internal or external command
```

**Solution:**
1. Ensure Python is installed
2. Add Python to PATH:
   - Windows Settings → System → About → Advanced system settings
   - Environment Variables → System variables → Path → Edit
   - Add: `C:\Python311` and `C:\Python311\Scripts`
3. Restart terminal

### Pip Install Fails

**Error:**
```
ERROR: Could not install packages due to an EnvironmentError
```

**Solution:**
```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install with --user flag
pip install --user -r deployment_manager\requirements.txt

# Or use virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r deployment_manager\requirements.txt
```

### Permission Denied

**Error:**
```
[Errno 13] Permission denied
```

**Solution:**
- Run PowerShell/CMD as Administrator
- Right-click → "Run as administrator"

### Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'colorama'
```

**Solution:**
```powershell
# Install missing package
pip install colorama

# Or reinstall all
pip install -r deployment_manager\requirements.txt
```

### Configuration File Not Found

**Error:**
```
Configuration file not found: deployment.config.env
```

**Solution:**
```powershell
# Copy from template
copy deployment.config.env.template deployment.config.env

# Or from example
copy examples\deployment.config.env.local deployment.config.env

# Edit it
notepad deployment.config.env
```

### Invalid Configuration

**Error:**
```
Configuration validation failed: APP_KEY is required
```

**Solution:**
1. Open `deployment.config.env`
2. Fill in missing values
3. For APP_KEY, generate with Laravel:
   ```bash
   php artisan key:generate --show
   ```
4. Save and re-validate

### NSSM Not Found

**Error:**
```
NSSM not found at: bin/nssm/win64/nssm.exe
```

**Solution:**
```powershell
# Check if bin folder exists
dir bin\nssm\win64\

# If missing, ensure you downloaded the complete repository
# Or manually download NSSM and place in bin/nssm/win64/
```

### Port Already in Use

**Error:**
```
Port 80 is already in use
```

**Solution:**
```powershell
# Check what's using the port
netstat -ano | findstr :80

# Kill the process (use PID from netstat)
taskkill /F /PID <pid>

# Or change port in deployment.config.env
# NGINX_HTTP_PORT=8080
```

### Build Executable Fails

**Error during PyInstaller build:**

**Solution:**
```powershell
# Clean previous builds
rmdir /S /Q build dist

# Update PyInstaller
pip install --upgrade pyinstaller

# Rebuild
python deployment_manager\build_exe.py

# If still fails, add --debug flag to build_exe.py
```

## Next Steps

After successful installation:

1. **Read the User Guide:** [COMPREHENSIVE.md](COMPREHENSIVE.md)
2. **Configure Your Environment:** [CONFIGURATION.md](CONFIGURATION.md)
3. **Install Services:** 
   ```powershell
   python deployment_manager\main.py service install
   ```
4. **Check Service Status:**
   ```powershell
   python deployment_manager\main.py service status
   ```
5. **Deploy Your Application:**
   ```powershell
   python deployment_manager\main.py deploy
   ```

## Getting Help

- **Documentation:** Check [COMPREHENSIVE.md](COMPREHENSIVE.md)
- **Configuration:** See [CONFIGURATION.md](CONFIGURATION.md)
- **Issues:** Visit [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Support:** Open an issue on GitHub

## Uninstallation

To completely remove the deployment manager:

```powershell
# Stop and remove services
python deployment_manager\main.py service stop --all
python deployment_manager\main.py service uninstall --all

# Delete the directory
cd ..
rmdir /S /Q woosoo-deployment-manager

# (Optional) Remove Python packages
pip uninstall -y colorama python-dotenv click psutil cryptography
```
