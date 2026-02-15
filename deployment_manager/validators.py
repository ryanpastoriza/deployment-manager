"""Pre-flight validation checks for deployment readiness."""

import subprocess
import socket
import psutil
import os
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class ValidationLevel(Enum):
    """Validation check severity levels."""

    CRITICAL = "critical"  # Blocking
    HIGH = "high"  # Warning
    MEDIUM = "medium"  # Recommendation
    LOW = "low"  # Info


@dataclass
class ValidationResult:
    """Result of a validation check."""

    name: str
    level: ValidationLevel
    passed: bool
    message: str
    recommendation: str = ""


class SystemValidator:
    """Validates system readiness for deployment."""

    def __init__(self, project_root: Path):
        """Initialize validator."""
        self.project_root = project_root
        self.results: List[ValidationResult] = []

    def run_all_checks(self) -> List[ValidationResult]:
        """Run all validation checks."""
        self.results = []

        # Level 0: Critical
        self.check_admin_privileges()
        self.check_disk_space()
        self.check_node_js()
        self.check_php()
        self.check_composer()
        self.check_config_file()

        # Level 1: High
        self.check_php_extensions()
        self.check_mysql()
        self.check_file_permissions()

        # Level 2: Medium
        self.check_flutter()
        self.check_existing_services()

        # Level 3: Low
        self.check_system_info()

        return self.results

    def _add_result(
        self,
        name: str,
        level: ValidationLevel,
        passed: bool,
        message: str,
        recommendation: str = "",
    ):
        """Add validation result."""
        result = ValidationResult(
            name=name,
            level=level,
            passed=passed,
            message=message,
            recommendation=recommendation,
        )
        self.results.append(result)

    def check_admin_privileges(self):
        """Check for administrator privileges."""
        try:
            import ctypes

            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            self._add_result(
                "Administrator Privileges",
                ValidationLevel.CRITICAL,
                is_admin,
                (
                    "Running with admin rights"
                    if is_admin
                    else "Not running as administrator"
                ),
                "Right-click and select 'Run as Administrator'",
            )
        except Exception as e:
            self._add_result(
                "Administrator Privileges",
                ValidationLevel.CRITICAL,
                False,
                f"Cannot check admin status: {e}",
                "Ensure Windows security policies allow privilege checks",
            )

    def check_disk_space(self, minimum_gb: int = 5):
        """Check available disk space."""
        try:
            disk = psutil.disk_usage(str(self.project_root))
            free_gb = disk.free / (1024**3)
            passed = free_gb >= minimum_gb

            self._add_result(
                "Disk Space",
                ValidationLevel.CRITICAL,
                passed,
                f"{free_gb:.2f} GB free (minimum: {minimum_gb} GB)",
                "Free up disk space before deployment" if not passed else "",
            )
        except Exception as e:
            self._add_result(
                "Disk Space",
                ValidationLevel.CRITICAL,
                False,
                f"Cannot check disk space: {e}",
            )

    def check_node_js(self):
        """Check Node.js installation."""
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=True,
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                major = int(version.replace("v", "").split(".")[0])
                passed = major >= 18

                self._add_result(
                    "Node.js",
                    ValidationLevel.CRITICAL,
                    passed,
                    f"Version {version} detected",
                    (
                        "Install Node.js 18+ from https://nodejs.org/"
                        if not passed
                        else ""
                    ),
                )
            else:
                raise Exception("Node.js command failed")
        except Exception as e:
            self._add_result(
                "Node.js",
                ValidationLevel.CRITICAL,
                False,
                "Not installed or not in PATH",
                "Install Node.js 18+ from https://nodejs.org/",
            )

    def check_php(self):
        """Check PHP installation."""
        try:
            result = subprocess.run(
                ["php", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=True,
            )
            if result.returncode == 0:
                import re

                match = re.search(r"PHP (\d+\.\d+\.\d+)", result.stdout)
                if match:
                    version = match.group(1)
                    major, minor = map(int, version.split(".")[:2])
                    passed = (major == 8 and minor >= 2) or major > 8

                    self._add_result(
                        "PHP",
                        ValidationLevel.CRITICAL,
                        passed,
                        f"Version {version} detected",
                        (
                            "Install PHP 8.2+ from https://windows.php.net/"
                            if not passed
                            else ""
                        ),
                    )
                else:
                    raise Exception("Cannot parse PHP version")
            else:
                raise Exception("PHP command failed")
        except Exception as e:
            self._add_result(
                "PHP",
                ValidationLevel.CRITICAL,
                False,
                "Not installed or not in PATH",
                "Install PHP 8.2+ from https://windows.php.net/",
            )

    def check_composer(self):
        """Check Composer installation."""
        try:
            # On Windows, use shell=True to properly access PATH
            result = subprocess.run(
                ["composer", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=True,
            )
            if result.returncode == 0:
                import re

                match = re.search(r"Composer version (\d+\.\d+\.\d+)", result.stdout)
                if match:
                    version = match.group(1)
                    major = int(version.split(".")[0])
                    passed = major >= 2

                    self._add_result(
                        "Composer",
                        ValidationLevel.CRITICAL,
                        passed,
                        f"Version {version} detected",
                        (
                            "Install Composer 2+ from https://getcomposer.org/"
                            if not passed
                            else ""
                        ),
                    )
                else:
                    self._add_result(
                        "Composer",
                        ValidationLevel.CRITICAL,
                        True,
                        "Installed (version unknown)",
                    )
            else:
                raise Exception("Composer command failed")
        except Exception as e:
            self._add_result(
                "Composer",
                ValidationLevel.CRITICAL,
                False,
                "Not installed or not in PATH",
                "Install Composer from https://getcomposer.org/",
            )

    def check_config_file(self):
        """Check configuration file exists."""
        config_path = self.project_root / "deployment.config.env"
        exists = config_path.exists()

        self._add_result(
            "Configuration File",
            ValidationLevel.CRITICAL,
            exists,
            (
                "deployment.config.env found"
                if exists
                else "deployment.config.env missing"
            ),
            "Create deployment.config.env from template" if not exists else "",
        )

    def check_php_extensions(self):
        """Check required PHP extensions."""
        required = ["mbstring", "pdo_mysql", "openssl", "json", "curl", "bcmath"]
        missing = []

        try:
            result = subprocess.run(
                ["php", "-m"], capture_output=True, text=True, timeout=5, shell=True
            )
            if result.returncode == 0:
                installed = result.stdout.lower()
                for ext in required:
                    if ext.lower() not in installed:
                        missing.append(ext)

                passed = len(missing) == 0
                message = (
                    "All required extensions present"
                    if passed
                    else f"Missing: {', '.join(missing)}"
                )

                self._add_result(
                    "PHP Extensions",
                    ValidationLevel.HIGH,
                    passed,
                    message,
                    "Enable missing extensions in php.ini" if not passed else "",
                )
            else:
                raise Exception("Cannot list PHP extensions")
        except Exception as e:
            self._add_result(
                "PHP Extensions",
                ValidationLevel.HIGH,
                False,
                f"Cannot check extensions: {e}",
                "Verify PHP is properly installed",
            )

    def check_mysql(self):
        """Check MySQL/MariaDB is running."""
        try:
            # Check if MySQL process is running
            mysql_running = False
            for proc in psutil.process_iter(["name"]):
                if "mysql" in proc.info["name"].lower():
                    mysql_running = True
                    break

            self._add_result(
                "MySQL/MariaDB",
                ValidationLevel.HIGH,
                mysql_running,
                "Running" if mysql_running else "Not running or not accessible",
                "Start MySQL service" if not mysql_running else "",
            )
        except Exception as e:
            self._add_result(
                "MySQL/MariaDB",
                ValidationLevel.HIGH,
                False,
                f"Cannot check MySQL: {e}",
                "Ensure MySQL/MariaDB is installed and running",
            )

    def check_file_permissions(self):
        """Check write permissions to project directory."""
        try:
            test_file = self.project_root / f".write_test_{os.getpid()}"
            test_file.write_text("test")
            test_file.unlink()

            self._add_result(
                "Write Permissions",
                ValidationLevel.HIGH,
                True,
                "Can write to project directory",
            )
        except Exception as e:
            self._add_result(
                "Write Permissions",
                ValidationLevel.HIGH,
                False,
                "Cannot write to project directory",
                "Check folder permissions or run as administrator",
            )

    def check_flutter(self):
        """Check Flutter SDK (optional)."""
        try:
            result = subprocess.run(
                ["flutter", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                shell=True,
            )
            if result.returncode == 0:
                import re

                match = re.search(r"Flutter (\d+\.\d+\.\d+)", result.stdout)
                if match:
                    version = match.group(1)
                    self._add_result(
                        "Flutter SDK",
                        ValidationLevel.MEDIUM,
                        True,
                        f"Version {version} detected",
                    )
                else:
                    self._add_result(
                        "Flutter SDK",
                        ValidationLevel.MEDIUM,
                        True,
                        "Installed (version unknown)",
                    )
            else:
                raise Exception("Flutter command failed")
        except Exception:
            self._add_result(
                "Flutter SDK",
                ValidationLevel.MEDIUM,
                False,
                "Not installed (relay device build will be skipped)",
                "Install Flutter SDK from https://flutter.dev/ if needed",
            )

    def check_existing_services(self):
        """Check for existing Woosoo services."""
        services_to_check = ["woosoo-reverb", "woosoo-nginx", "woosoo-queue-worker"]
        found = []

        try:
            result = subprocess.run(
                ["sc", "query"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                output = result.stdout.lower()
                for svc in services_to_check:
                    if svc.lower() in output:
                        found.append(svc)

                if found:
                    self._add_result(
                        "Existing Services",
                        ValidationLevel.MEDIUM,
                        True,
                        f"Found: {', '.join(found)}",
                        "These will be replaced during deployment",
                    )
                else:
                    self._add_result(
                        "Existing Services",
                        ValidationLevel.MEDIUM,
                        True,
                        "No existing Woosoo services (fresh installation)",
                    )
        except Exception as e:
            self._add_result(
                "Existing Services",
                ValidationLevel.MEDIUM,
                True,
                f"Cannot check services: {e}",
            )

    def check_system_info(self):
        """Get system information."""
        try:
            # RAM
            ram = psutil.virtual_memory()
            total_gb = ram.total / (1024**3)

            self._add_result(
                "System RAM",
                ValidationLevel.LOW,
                total_gb >= 4,
                f"{total_gb:.2f} GB total",
                "Minimum 4GB recommended" if total_gb < 4 else "",
            )

            # CPU
            cpu_count = psutil.cpu_count()
            self._add_result(
                "CPU Cores", ValidationLevel.LOW, True, f"{cpu_count} cores detected"
            )
        except Exception as e:
            pass

    def check_ports(self, ports: List[int]) -> Dict[int, bool]:
        """Check if ports are available."""
        results = {}
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(("127.0.0.1", port))
                results[port] = result != 0  # True if available
                sock.close()
            except:
                results[port] = True  # Assume available if check fails
        return results

    def get_summary(self) -> Dict[str, int]:
        """Get validation summary."""
        summary = {
            "total": len(self.results),
            "passed": sum(1 for r in self.results if r.passed),
            "failed": sum(1 for r in self.results if not r.passed),
            "critical_failed": sum(
                1
                for r in self.results
                if not r.passed and r.level == ValidationLevel.CRITICAL
            ),
        }
        summary["can_proceed"] = summary["critical_failed"] == 0
        return summary
