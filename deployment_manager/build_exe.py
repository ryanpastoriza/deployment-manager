"""
Build script for creating woosoo-deploy-manager.exe
"""

import PyInstaller.__main__
import shutil
from pathlib import Path

# Get paths
script_dir = Path(__file__).parent
project_root = script_dir.parent
icon_path = script_dir / "assets" / "icon.ico"

# Create assets directory if it doesn't exist
assets_dir = script_dir / "assets"
assets_dir.mkdir(exist_ok=True)

# Build configuration
build_args = [
    str(script_dir / "main.py"),
    "--onedir",  # Create directory with dependencies
    "--console",  # Keep console window for output
    "--name=deployment-manager",
    "--clean",
    "--noconfirm",
    # Hidden imports
    "--hidden-import=win32timezone",
    "--hidden-import=win32api",
    "--hidden-import=win32con",
    "--hidden-import=win32event",
    "--hidden-import=win32evtlog",
    "--hidden-import=win32service",
    "--hidden-import=win32serviceutil",
    "--hidden-import=servicemanager",
    # Add icon if exists
]

if icon_path.exists():
    build_args.append(f"--icon={icon_path}")

print("=" * 60)
print("Building Woosoo Deployment Manager Executable")
print("=" * 60)
print()
print("Configuration:")
print(f"  Script: {script_dir / 'main.py'}")
print(f"  Output: deployment-manager.exe")
print(f"  Type: Directory with dependencies")
print()

# Run PyInstaller
try:
    PyInstaller.__main__.run(build_args)

    print()
    print("=" * 60)
    print("Build Complete!")
    print("=" * 60)
    print()
    print(
        f"Executable location: {project_root / 'dist' / 'deployment-manager' / 'deployment-manager.exe'}"
    )
    print()
    print("Usage:")
    print("  deployment-manager.exe                    # Show help")
    print("  deployment-manager.exe validate           # Run pre-flight checks")
    print("  deployment-manager.exe service status     # Check services")
    print("  deployment-manager.exe --help             # Show full help")
    print()

except Exception as e:
    print()
    print("=" * 60)
    print("Build Failed!")
    print("=" * 60)
    print()
    print(f"Error: {e}")
    exit(1)
