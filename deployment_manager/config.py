"""Configuration management for Woosoo Deployment Manager."""

import os
import platform
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass, field
import re


@dataclass
class DeploymentConfig:
    """Deployment configuration loaded from deployment.config.env."""
    
    # Environment
    deployment_env: str = "production"
    server_ip: str = "192.168.100.85"
    use_tls: bool = True
    
    # Ports
    nginx_https_port: int =8000
    nginx_http_port: int = 80
    reverb_port: int = 6001
    mysql_port: int = 3306
    
    # TLS
    tls_cert_path: str = "certs/192.168.100.85+3.pem"
    tls_key_path: str = "certs/192.168.100.85+3-key.pem"
    
    # Reverb
    reverb_app_id: str = ""
    reverb_app_key: str = ""
    reverb_app_secret: str = ""
    
    # Database
    db_name: str = "woosoo_api"
    db_username: str = "root"
    db_password: str = ""
    db_pos_name: str = "krypton_woosoo"
    db_pos_username: str = "root"
    db_pos_password: str = ""
    
    # Laravel
    app_name: str = "Woosoo"
    app_key: str = ""
    app_debug: bool = False
    log_level: str = "error"
    
    # Application Paths (configurable - NEW in standalone version)
    backend_dir: str = "apps/woosoo-nexus"
    pwa_dir: str = "apps/tablet-ordering-pwa"
    relay_dir: str = "apps/relay-device-v2"
    nginx_exe: str = "bin/nginx/nginx.exe"
    nginx_config: str = "configs/nginx.conf"
    
    # Raw config for reference
    raw_config: Dict[str, str] = field(default_factory=dict)


@dataclass
class ManagerConfig:
    """Deployment Manager settings."""
    
    version: str = "2.0.0"
    project_root: Path = None
    auto_backup: bool = True
    auto_rollback_on_failure: bool = True
    log_level: str = "INFO"
    
    # Paths
    backup_dir: Path = None
    logs_dir: Path = None
    
    # Tools
    node_path: str = "node"
    php_path: str = "php"
    composer_path: str = "composer"
    flutter_path: str = "flutter"
    mkcert_path: str = "bin\\mkcert\\mkcert.exe"
    nssm_path: str = None  # Will be auto-detected based on architecture
    
    def __post_init__(self):
        """Initialize default paths."""
        if self.project_root is None:
            # NEW: Check environment variable first, then current directory
            env_root = os.getenv('WOOSOO_PROJECT_ROOT')
            if env_root:
                self.project_root = Path(env_root)
            else:
                # Default to current working directory (not parent.parent)
                self.project_root = Path.cwd()
        
        if self.backup_dir is None:
            self.backup_dir = self.project_root / "backups"
        
        if self.logs_dir is None:
            self.logs_dir = self.project_root / "logs"
        
        # Auto-detect NSSM path based on architecture
        if self.nssm_path is None:
            arch = "win64" if platform.machine().endswith('64') else "win32"
            self.nssm_path = f"bin\\nssm\\{arch}\\nssm.exe"


class ConfigManager:
    """Manages loading and syncing configuration."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize config manager.
        
        Args:
            project_root: Project root directory. If None, uses current directory or WOOSOO_PROJECT_ROOT env var.
        """
        if project_root is None:
            # NEW: Check environment variable first
            env_root = os.getenv('WOOSOO_PROJECT_ROOT')
            if env_root:
                project_root = Path(env_root)
            else:
                # Default to current working directory
                project_root = Path.cwd()
        
        self.project_root = project_root
        self.config_path = self.project_root / "deployment.config.env"
        self.deployment_config: Optional[DeploymentConfig] = None
        self.manager_config = ManagerConfig(project_root=self.project_root)
    
    def load_config(self) -> DeploymentConfig:
        """Load configuration from deployment.config.env."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Expected at: {self.project_root}/deployment.config.env\n"
                f"Copy deployment.config.env.template and fill in your values."
            )
        
        raw_config = {}
        with open(self.config_path, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse key=value
                if '=' in line:
                    # Remove inline comments
                    line = re.sub(r'\s+#.*$', '', line)
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    raw_config[key] = value
        
        # Map to DeploymentConfig
        config = DeploymentConfig(
            deployment_env=raw_config.get('DEPLOYMENT_ENV', 'production'),
            server_ip=raw_config.get('SERVER_IP', '192.168.100.85'),
            use_tls=(raw_config.get('USE_TLS', 'true').lower() == 'true'),
            nginx_https_port=int(raw_config.get('NGINX_HTTPS_PORT', 8000)),
            nginx_http_port=int(raw_config.get('NGINX_HTTP_PORT', 80)),
            reverb_port=int(raw_config.get('REVERB_PORT', 6001)),
            mysql_port=int(raw_config.get('MYSQL_PORT', 3306)),
            tls_cert_path=raw_config.get('TLS_CERT_PATH', 'certs/cert.pem'),
            tls_key_path=raw_config.get('TLS_KEY_PATH', 'certs/key.pem'),
            reverb_app_id=raw_config.get('REVERB_APP_ID', ''),
            reverb_app_key=raw_config.get('REVERB_APP_KEY', ''),
            reverb_app_secret=raw_config.get('REVERB_APP_SECRET', ''),
            db_name=raw_config.get('DB_NAME', 'woosoo_api'),
            db_username=raw_config.get('DB_USERNAME', 'root'),
            db_password=raw_config.get('DB_PASSWORD', ''),
            db_pos_name=raw_config.get('DB_POS_NAME', 'krypton_woosoo'),
            db_pos_username=raw_config.get('DB_POS_USERNAME', 'root'),
            db_pos_password=raw_config.get('DB_POS_PASSWORD', ''),
            app_name=raw_config.get('APP_NAME', 'Woosoo'),
            app_key=raw_config.get('APP_KEY', ''),
            app_debug=(raw_config.get('APP_DEBUG', 'false').lower() == 'true'),
            log_level=raw_config.get('LOG_LEVEL', 'error'),
            # NEW: Application paths
            backend_dir=raw_config.get('BACKEND_DIR', 'apps/woosoo-nexus'),
            pwa_dir=raw_config.get('PWA_DIR', 'apps/tablet-ordering-pwa'),
            relay_dir=raw_config.get('RELAY_DIR', 'apps/relay-device-v2'),
            nginx_exe=raw_config.get('NGINX_EXE', 'bin/nginx/nginx.exe'),
            nginx_config=raw_config.get('NGINX_CONFIG', 'configs/nginx.conf'),
            raw_config=raw_config
        )
        
        self.deployment_config = config
        return config
    
    def validate_config(self) -> tuple[bool, list[str]]:
        """Validate configuration completeness."""
        if not self.deployment_config:
            self.load_config()
        
        errors = []
        
        # Required fields
        if not self.deployment_config.server_ip:
            errors.append("SERVER_IP is required")
        
        if not self.deployment_config.app_key:
            errors.append("APP_KEY is required (generate with: php artisan key:generate)")
        
        # Port validation
        for port_name, port_value in [
            ('NGINX_HTTPS_PORT', self.deployment_config.nginx_https_port),
            ('NGINX_HTTP_PORT', self.deployment_config.nginx_http_port),
            ('REVERB_PORT', self.deployment_config.reverb_port),
        ]:
            if not (1024 <= port_value <= 65535):
                errors.append(f"{port_name} must be between 1024-65535")
        
        # IP validation
        import re
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(ip_pattern, self.deployment_config.server_ip):
            errors.append(f"Invalid IP address: {self.deployment_config.server_ip}")
        
        return (len(errors) == 0, errors)
    
    def get_config_summary(self) -> Dict[str, str]:
        """Get human-readable configuration summary."""
        if not self.deployment_config:
            self.load_config()
        
        return {
            "Environment": self.deployment_config.deployment_env,
            "Server IP": self.deployment_config.server_ip,
            "HTTPS Port": str(self.deployment_config.nginx_https_port),
            "HTTP Port": str(self.deployment_config.nginx_http_port),
            "WebSocket Port": str(self.deployment_config.reverb_port),
            "TLS Enabled": "Yes" if self.deployment_config.use_tls else "No",
            "Database": self.deployment_config.db_name,
            "Project Root": str(self.project_root),
        }
