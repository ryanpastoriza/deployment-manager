# Woosoo Deployment Manager

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.11+-brightgreen.svg)

**A comprehensive Windows deployment management tool for managing services, validating system readiness, and orchestrating deployments.**

[Features](#-features) •
[Quick Start](#-quick-start) •
[Documentation](#-documentation) •
[Installation](#%EF%B8%8F-installation) •
[Usage](#-usage) •
[Contributing](#-contributing)

</div>

---

## 🎯 Features

- **✅ Service Management** - Install, start, stop, and monitor Windows services using NSSM
- **✅ Pre-Flight Validation** - Comprehensive system checks before deployment (14+ validators)
- **✅ Configuration Management** - Centralized config with validation
- **✅ Beautiful TUI** - Modern terminal interface with Rich/Textual libraries
- **✅ CLI Support** - Full command-line interface for automation
- **✅ Single Executable** - Build to standalone `.exe` with no external dependencies
- **✅ Configurable Paths** - Works with any project structure
- **✅ Cross-Project** - No monorepo assumptions, fully portable

## 🚀 Quick Start

### Prerequisites

- Windows 10/11 or Server 2019+
- Python 3.11+ (for running from source) OR the compiled `.exe`
- **Administrator privileges** (required for service management)
- Node.js 18+ (for your application)
- PHP 8.2+ (for your application)
- Composer 2.0+ (for your application)

### 5-Minute Setup

```powershell
# 1. Clone or download this repository
git clone https://github.com/yourorg/woosoo-deployment-manager.git
cd woosoo-deployment-manager

# 2. Create your configuration
copy deployment.config.env.template deployment.config.env
# Edit deployment.config.env with your settings

# 3. Install Python dependencies
pip install -r deployment_manager\requirements.txt

# 4. Run the manager (⚠️ AS ADMINISTRATOR!)
python deployment_manager\main.py dashboard
```

### Using the Pre-Built Executable

```powershell
# Download woosoo-deploy-manager.exe from releases
# Run AS ADMINISTRATOR
.\woosoo-deploy-manager.exe dashboard
```

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [COMPREHENSIVE.md](docs/COMPREHENSIVE.md) | Complete user guide with architecture, features, and roadmap |
| [REQUIREMENTS.md](docs/REQUIREMENTS.md) | Technical specifications and implementation plan |
| [INSTALLATION.md](docs/INSTALLATION.md) | Detailed installation guide |
| [CONFIGURATION.md](docs/CONFIGURATION.md) | Configuration reference |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues and solutions |

## ⚙️ Installation

### Option 1: Run from Source

```powershell
# Install Python 3.11+ from https://python.org
# IMPORTANT: Check "Add Python to PATH" during installation

# Clone repository
git clone https://github.com/yourorg/woosoo-deployment-manager.git
cd woosoo-deployment-manager

# Install dependencies
cd deployment_manager
pip install -r requirements.txt

# Configure
copy ..\deployment.config.env.template ..\deployment.config.env
notepad ..\deployment.config.env  # Edit with your values

# Run (AS ADMINISTRATOR!)
python main.py
```

### Option 2: Build Executable

```powershell
# Install build dependencies
pip install -r deployment_manager\requirements.txt

# Build
python deployment_manager\build_exe.py

# The executable will be at:
# deployment_manager\dist\woosoo-deploy-manager.exe

# Copy to convenient location
copy deployment_manager\dist\woosoo-deploy-manager.exe C:\Tools\
```

### Option 3: Download Pre-Built Release

1. Download the latest `woosoo-deploy-manager.exe` from [Releases](https://github.com/yourorg/woosoo-deployment-manager/releases)
2. Copy to your project directory
3. Create `deployment.config.env` from template
4. Run as Administrator

## 🖥️ Usage

### Dashboard

```powershell
# Show service status and configuration
python deployment_manager\main.py dashboard
```

### Pre-Flight Checks

```powershell
# Validate system readiness
python deployment_manager\main.py check
python deployment_manager\main.py check --verbose
```

**Checks Include:**
- Administrator privileges
- Disk space (5GB+ available)
- Required tools (Node.js, PHP, Composer, Flutter)
- Configuration file validity
- Port availability (8000, 80, 6001)
- Database connectivity
- PHP extensions

### Service Management

```powershell
# Install services
python deployment_manager\main.py install all

# Start services
python deployment_manager\main.py start all

# Stop services
python deployment_manager\main.py stop all

# Restart a single service
python deployment_manager\main.py stop reverb
python deployment_manager\main.py start reverb

# Uninstall services
python deployment_manager\main.py uninstall all --confirm
```

**Managed Services:**
- `woosoo-reverb` - Laravel Reverb WebSocket server
- `woosoo-queue-worker` - Laravel queue processor
- `woosoo-nginx` - Nginx web server

### Configuration

```powershell
# View current configuration
python deployment_manager\main.py config

# Edit configuration
notepad deployment.config.env
```

### Command-Line Options

```powershell
# Specify custom project root
python deployment_manager\main.py --project-root C:\MyProject dashboard

# Or set environment variable
$env:WOOSOO_PROJECT_ROOT = "C:\MyProject"
python deployment_manager\main.py dashboard
```

## 🛠️ Configuration

Create `deployment.config.env` from the template:

```env
# Essential settings
DEPLOYMENT_ENV=production
SERVER_IP=192.168.1.100
USE_TLS=true

# Network ports
NGINX_HTTPS_PORT=8000
NGINX_HTTP_PORT=80
REVERB_PORT=6001

# Database
DB_NAME=your_database
DB_USERNAME=your_username
DB_PASSWORD=your_password

# Laravel
APP_NAME=YourApp
APP_KEY=base64:...  # Generate with: php artisan key:generate --show

# Application paths (customize to your structure)
BACKEND_DIR=apps/your-backend
PWA_DIR=apps/your-pwa
NGINX_EXE=bin/nginx/nginx.exe
```

See [deployment.config.env.template](deployment.config.env.template) for all options.

## 📁 Project Structure

```
woosoo-deployment-manager/
├── deployment_manager/          # Python package
│   ├── main.py                  # CLI entry point
│   ├── config.py                # Configuration management
│   ├── validators.py            # System validation
│   ├── services.py              # Service management
│   ├── requirements.txt         # Dependencies
│   └── build_exe.py             # Executable builder
├── bin/                         # Binary tools
│   ├── nssm/                    # Service manager
│   └── mkcert/                  # Certificate generator
├── docs/                        # Documentation
├── examples/                    # Example configs
├── deployment.config.env.template  # Config template
├── README.md                    # This file
└── LICENSE                      # MIT License
```

## ⚠️ Important Notes

### Administrator Rights Required

**ALL service management operations require Administrator privileges!**

To run as Administrator:
1. Right-click PowerShell
2. Select "Run as Administrator"
3. Click "Yes" on UAC prompt

Verify admin status:
```powershell
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
# Should return: True
```

### Security

- **NEVER** commit `deployment.config.env` with real credentials
- Add `deployment.config.env` to `.gitignore`
- Use strong, unique passwords
- Rotate credentials periodically
- Enable TLS in production

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Access is denied" error | Run PowerShell as Administrator |
| "NSSM not found" | Verify `bin/nssm/win64/nssm.exe` exists |
| "Config file not found" | Copy `deployment.config.env.template` to `deployment.config.env` |
| Services show "Paused" | Resume with `python deployment_manager\main.py start all` |
| "Composer not found" | Install Composer and add to PATH |

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for more help.

## 🗺️ Roadmap

### Phase 1: Core (✅ Complete)
- [x] Service management
- [x] Pre-flight validation
- [x] Configuration management
- [x] TUI dashboard
- [x] Single executable build

### Phase 2: Deployment (Planned)
- [ ] Full deployment orchestration
- [ ] Backup & rollback system
- [ ] Certificate management
- [ ] Advanced log viewer
- [ ] Health monitoring

### Phase 3: Advanced (Future)
- [ ] Web-based interface
- [ ] Scheduled deployments
- [ ] Multi-environment support
- [ ] CI/CD integration

See [COMPREHENSIVE.md](docs/COMPREHENSIVE.md) for detailed roadmap.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [NS SSM](https://nssm.cc/) - The Non-Sucking Service Manager
- [mkcert](https://github.com/FiloSottile/mkcert) - Simple certificate generation
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal output
- [Click](https://click.palletsprojects.com/) - CLI framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourorg/woosoo-deployment-manager/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourorg/woosoo-deployment-manager/discussions)
- **Email**: support@yourcompany.com

---

<div align="center">

**Built with ❤️ by the Wooso Team**

</div>
