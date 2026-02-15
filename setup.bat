@echo off
REM Woosoo Deployment Manager - Windows Setup Script
REM Quick setup for Windows users

echo.
echo ================================================
echo   Woosoo Deployment Manager - Setup
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.11+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [OK] Python detected: 
python --version

echo.
echo Installing Python dependencies...
echo.

cd deployment_manager
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies!
    echo.
    pause
    exit /b 1
)

cd ..

echo.
echo ================================================
echo   Setup Complete!
echo ================================================
echo.
echo Next steps:
echo   1. Copy deployment.config.env.template to deployment.config.env
echo   2. Edit deployment.config.env with your settings
echo   3. Run: python deployment_manager\main.py check
echo   4. Run: python deployment_manager\main.py dashboard
echo.
echo IMPORTANT: Run PowerShell as Administrator for service management!
echo.

REM Check if config exists
if not exist deployment.config.env (
    echo [INFO] Config file not found. Creating from template...
    copy deployment.config.env.template deployment.config.env
    echo.
    echo [OK] deployment.config.env created. Please edit it with your settings.
    notepad deployment.config.env
)

echo.
pause
