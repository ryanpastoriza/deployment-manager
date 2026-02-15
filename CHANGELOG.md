# Changelog

All notable changes to Woosoo Deployment Manager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-02-15

### Added
- **Standalone Version**: Complete refactor for standalone repository
  - No monorepo dependencies
  - Configurable project root via `--project-root` CLI option
  - Environment variable support (`WOOSOO_PROJECT_ROOT`)
  - Self-contained binary tools (NSSM, mkcert)
  
- **Configuration Management**
  - New config template: `deployment.config.env.template`
  - Configurable application paths (BACKEND_DIR, PWA_DIR, etc.)
  - Enhanced validation with better error messages
  - Config path now included in dashboard summary
  
- **Service Management**
  - Configurable service directories
  - Support for custom nginx paths
  - Enhanced paused service detection
  - Better error messages with system error codes
  
- **Pre-Flight Validation**
  - 14+ comprehensive checks
  - Administrator privilege detection
  - Disk space validation (5GB minimum)
  - PHP extension validation
  - Port availability checks
  - Configuration file validation
  
- **CLI Enhancements**
  - `--project-root` option for all commands
  - Better help text and documentation
  - Improved error handling with tracebacks
  
- **Documentation**
  - Comprehensive README with quick start
  - COMPREHENSIVE.md with full feature guide
  - REQUIREMENTS.md with technical specifications
  - AUDIT.md with migration analysis
  - Configuration template with extensive comments

### Changed
- Python files reorganized for portability
- Services paths now dynamically configured from deployment.config.env
- Project root detection logic improved (env var → CLI arg → cwd)
- Error messages more actionable and user-friendly
- Dashboard shows project root location

### Fixed
- NSSM architecture detection (win32/win64)
- Composer detection on Windows PATH
- Paused service state handling
- Service status detection using PowerShell
- Administrator privilege checks

### Removed
- Hard dependency on parent.parent directory structure
- Hardcoded monorepo paths in service definitions

## [1.0.0] - 2026-02-14

### Added
- Initial release within monorepo
- Basic service management (reverb, queue, nginx)
- NSSM integration for Windows services
- Pre-flight validation system
- TUI dashboard with Rich library
- Configuration loading from deployment.config.env
- CLI commands: dashboard, check, start, stop, install, uninstall

---

## Upcoming (Roadmap)

### [2.1.0] - Planned
- Backup and rollback system
- Configuration sync engine
- Enhanced log viewer with real-time tailing
- Health monitoring dashboard

### [3.0.0] - Planned
- Full deployment orchestration
- Certificate management integration
- Web-based interface
- Multi-environment support
- Scheduled deployments
- CI/CD integration
