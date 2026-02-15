"""Windows service management using NSSM - Standalone Version."""

import subprocess
import platform
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass
from enum import Enum


class ServiceStatus(Enum):
    """Service status states."""

    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    NOT_INSTALLED = "not_installed"
    UNKNOWN = "unknown"


@dataclass
class ServiceInfo:
    """Information about a Windows service."""

    name: str
    display_name: str
    status: ServiceStatus
    executable: str = ""
    description: str = ""


class ServiceManager:
    """Manages Windows services using NSSM - Standalone Version with configurable paths."""

    # Default service templates (paths will be configured at init)
    SERVICES_TEMPLATE = {
        "reverb": {
            "name": "woosoo-reverb",
            "display": "Woosoo Reverb WebSocket Server",
            "description": "Laravel Reverb WebSocket server for real-time communication",
            "exe": "php",
            "args": "artisan reverb:start --host=0.0.0.0 --port=6001",
            "dir": None,  # Will be set from config
        },
        "queue": {
            "name": "woosoo-queue-worker",
            "display": "Woosoo Queue Worker",
            "description": "Laravel queue worker for background job processing",
            "exe": "php",
            "args": "artisan queue:work --tries=3 --timeout=90",
            "dir": None,  # Will be set from config
        },
        "nginx": {
            "name": "woosoo-nginx",
            "display": "Woosoo Nginx Server",
            "description": "Nginx web server for Woosoo applications",
            "exe": None,  # Will be set from config
            "args": None,  # Will be set from config
            "dir": "",
        },
    }

    def __init__(
        self,
        project_root: Path,
        nssm_path: Optional[str] = None,
        backend_dir: str = "apps/woosoo-nexus",
        nginx_exe: str = "bin/nginx/nginx.exe",
        nginx_config: str = "configs/nginx.conf",
    ):
        """Initialize service manager with configurable paths.

        Args:
            project_root: Project root directory
            nssm_path: Path to NSSM executable (auto-detected if None)
            backend_dir: Laravel backend directory (relative to project_root)
            nginx_exe: Nginx executable path (relative to project_root)
            nginx_config: Nginx config path (relative to project_root)
        """
        self.project_root = project_root

        # Auto-detect architecture if path not provided
        if nssm_path is None:
            arch = "win64" if platform.machine().endswith("64") else "win32"
            nssm_path = f"bin/nssm/{arch}/nssm.exe"

        self.nssm_path = project_root / nssm_path

        if not self.nssm_path.exists():
            raise FileNotFoundError(
                f"NSSM not found: {self.nssm_path}\n"
                f"Expected at: bin/nssm/win64/nssm.exe or bin/nssm/win32/nssm.exe"
            )

        # Configure service paths (deep copy template and update)
        import copy

        self.SERVICES = copy.deepcopy(self.SERVICES_TEMPLATE)

        # Set backend directory for Laravel services (use forward slashes, convert to backslash)
        backend_path = backend_dir.replace("/", "\\")
        self.SERVICES["reverb"]["dir"] = backend_path
        self.SERVICES["queue"]["dir"] = backend_path

        # Set nginx paths (use forward slashes, convert to backslash)
        nginx_exe_path = nginx_exe.replace("/", "\\")
        nginx_config_path = nginx_config.replace("/", "\\")
        self.SERVICES["nginx"]["exe"] = nginx_exe_path
        self.SERVICES["nginx"]["args"] = f"-c {nginx_config_path}"

    def get_service_status(self, service_name: str) -> ServiceStatus:
        """Get the status of a service."""
        try:
            # Use PowerShell Get-Service for better status detection
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    f'Get-Service -Name "{service_name}" | Select-Object -ExpandProperty Status',
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                return ServiceStatus.NOT_INSTALLED

            status = result.stdout.strip().lower()
            if "running" in status:
                return ServiceStatus.RUNNING
            elif "stopped" in status:
                return ServiceStatus.STOPPED
            elif "paused" in status:
                return ServiceStatus.PAUSED
            else:
                return ServiceStatus.UNKNOWN

        except Exception:
            return ServiceStatus.UNKNOWN

    def get_all_services_status(self) -> List[ServiceInfo]:
        """Get status of all Woosoo services."""
        services = []

        for key, config in self.SERVICES.items():
            status = self.get_service_status(config["name"])
            services.append(
                ServiceInfo(
                    name=config["name"],
                    display_name=config["display"],
                    status=status,
                    description=config["description"],
                )
            )

        return services

    def install_service(self, service_key: str) -> tuple[bool, str]:
        """Install a service using NSSM."""
        if service_key not in self.SERVICES:
            return False, f"Unknown service: {service_key}"

        config = self.SERVICES[service_key]
        service_name = config["name"]

        # Check if already installed
        status = self.get_service_status(service_name)
        if status != ServiceStatus.NOT_INSTALLED:
            return False, f"Service {service_name} is already installed"

        try:
            # Get full paths
            exe_path = config["exe"]
            if not Path(exe_path).is_absolute():
                if "php" in exe_path.lower():
                    # PHP should be in PATH
                    exe_path = (
                        subprocess.check_output(["where", "php"], text=True, shell=True)
                        .strip()
                        .split("\n")[0]
                    )
                else:
                    exe_path = str(self.project_root / exe_path)

            app_dir = (
                str(self.project_root / config["dir"])
                if config["dir"]
                else str(self.project_root)
            )

            # Install service
            install_cmd = [
                str(self.nssm_path),
                "install",
                service_name,
                exe_path,
            ] + config["args"].split()

            result = subprocess.run(install_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return False, f"Installation failed: {result.stderr}"

            # Set service parameters
            self._run_nssm(["set", service_name, "AppDirectory", app_dir])
            self._run_nssm(["set", service_name, "DisplayName", config["display"]])
            self._run_nssm(["set", service_name, "Description", config["description"]])
            self._run_nssm(["set", service_name, "Start", "SERVICE_AUTO_START"])

            # Set stdout/stderr redirection
            logs_dir = self.project_root / "logs" / service_key
            logs_dir.mkdir(parents=True, exist_ok=True)

            self._run_nssm(
                ["set", service_name, "AppStdout", str(logs_dir / "output.log")]
            )
            self._run_nssm(
                ["set", service_name, "AppStderr", str(logs_dir / "error.log")]
            )
            self._run_nssm(["set", service_name, "AppTimestampLog", "1"])

            return True, f"Service {service_name} installed successfully"

        except Exception as e:
            return False, f"Installation error: {str(e)}"

    def uninstall_service(
        self, service_key: str, stop_first: bool = True
    ) -> tuple[bool, str]:
        """Uninstall a service."""
        if service_key not in self.SERVICES:
            return False, f"Unknown service: {service_key}"

        config = self.SERVICES[service_key]
        service_name = config["name"]

        # Check if installed
        status = self.get_service_status(service_name)
        if status == ServiceStatus.NOT_INSTALLED:
            return True, f"Service {service_name} is not installed"

        try:
            # Stop if running
            if stop_first and status == ServiceStatus.RUNNING:
                self.stop_service(service_key)

            # Uninstall
            result = self._run_nssm(["remove", service_name, "confirm"])
            if result.returncode != 0:
                return False, f"Uninstallation failed: {result.stderr}"

            return True, f"Service {service_name} uninstalled successfully"

        except Exception as e:
            return False, f"Uninstallation error: {str(e)}"

    def start_service(self, service_key: str) -> tuple[bool, str]:
        """Start a service."""
        if service_key not in self.SERVICES:
            return False, f"Unknown service: {service_key}"

        config = self.SERVICES[service_key]
        service_name = config["name"]

        try:
            # Use net start for better compatibility and error messages
            result = subprocess.run(
                ["net", "start", service_name],
                capture_output=True,
                text=True,
                timeout=10,
                shell=True,
            )

            if result.returncode == 0:
                return True, f"Service {service_name} started"
            elif (
                "already" in result.stdout.lower() or "already" in result.stderr.lower()
            ):
                return True, f"Service {service_name} already running"
            else:
                error_msg = (
                    result.stderr.strip() if result.stderr else result.stdout.strip()
                )
                return False, f"Failed to start: {error_msg}"

        except Exception as e:
            return False, f"Start error: {str(e)}"

    def stop_service(self, service_key: str) -> tuple[bool, str]:
        """Stop a service."""
        if service_key not in self.SERVICES:
            return False, f"Unknown service: {service_key}"

        config = self.SERVICES[service_key]
        service_name = config["name"]

        try:
            # Use net stop for better compatibility and error messages
            result = subprocess.run(
                ["net", "stop", service_name],
                capture_output=True,
                text=True,
                timeout=10,
                shell=True,
            )

            if result.returncode == 0:
                return True, f"Service {service_name} stopped"
            elif (
                "not started" in result.stdout.lower()
                or "not started" in result.stderr.lower()
            ):
                return True, f"Service {service_name} already stopped"
            else:
                error_msg = (
                    result.stderr.strip() if result.stderr else result.stdout.strip()
                )
                return False, f"Failed to stop: {error_msg}"

        except Exception as e:
            return False, f"Stop error: {str(e)}"

    def restart_service(self, service_key: str) -> tuple[bool, str]:
        """Restart a service."""
        success, msg = self.stop_service(service_key)
        if not success:
            return False, f"Failed to stop: {msg}"

        import time

        time.sleep(2)  # Wait for service to fully stop

        return self.start_service(service_key)

    def resume_service(self, service_key: str) -> tuple[bool, str]:
        """Resume a paused service."""
        if service_key not in self.SERVICES:
            return False, f"Unknown service: {service_key}"

        config = self.SERVICES[service_key]
        service_name = config["name"]

        try:
            result = subprocess.run(
                ["powershell", "-Command", f'Resume-Service -Name "{service_name}"'],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                return True, f"Service {service_name} resumed"
            else:
                error_msg = (
                    result.stderr.strip() if result.stderr else result.stdout.strip()
                )
                # If it fails, try to start it instead
                return self.start_service(service_key)

        except Exception as e:
            # Fallback to start
            return self.start_service(service_key)

    def start_all(self) -> Dict[str, tuple[bool, str]]:
        """Start all services."""
        results = {}
        for key in self.SERVICES.keys():
            # Check if paused first, if so resume instead
            status = self.get_service_status(self.SERVICES[key]["name"])
            if status == ServiceStatus.PAUSED:
                results[key] = self.resume_service(key)
            else:
                results[key] = self.start_service(key)
        return results

    def stop_all(self) -> Dict[str, tuple[bool, str]]:
        """Stop all services."""
        results = {}
        for key in self.SERVICES.keys():
            results[key] = self.stop_service(key)
        return results

    def install_all(self) -> Dict[str, tuple[bool, str]]:
        """Install all services."""
        results = {}
        for key in self.SERVICES.keys():
            results[key] = self.install_service(key)
        return results

    def uninstall_all(self) -> Dict[str, tuple[bool, str]]:
        """Uninstall all services."""
        results = {}
        for key in self.SERVICES.keys():
            results[key] = self.uninstall_service(key)
        return results

    def _run_nssm(self, args: List[str]) -> subprocess.CompletedProcess:
        """Run NSSM command."""
        cmd = [str(self.nssm_path)] + args
        return subprocess.run(cmd, capture_output=True, text=True, timeout=10)
