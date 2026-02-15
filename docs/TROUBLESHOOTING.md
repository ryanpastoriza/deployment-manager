# Troubleshooting Guide

Solutions to common problems when using the Woosoo Deployment Manager.

## Table of Contents

- [Quick Diagnostic Commands](#quick-diagnostic-commands)
- [Installation Issues](#installation-issues)
- [Configuration Issues](#configuration-issues)
- [Service Management Issues](#service-management-issues)
- [Deployment Issues](#deployment-issues)
- [WebSocket Issues](#websocket-issues)
- [Certificate/TLS Issues](#certificatetls-issues)
- [Database Issues](#database-issues)
- [Performance Issues](#performance-issues)
- [Error Messages Reference](#error-messages-reference)
- [Getting Support](#getting-support)

## Quick Diagnostic Commands

Run these first to identify issues:

```powershell
# Check system requirements
python deployment_manager\main.py validate

# Verify configuration
python deployment_manager\main.py config

# Check service status
python deployment_manager\main.py service status --all

# View recent logs
Get-Content logs\deployment.log -Tail 50
```

---

## Installation Issues

### Python Not Found

**Symptom:**
```
'python' is not recognized as an internal or external command
```

**Diagnosis:**
```powershell
# Check if Python installed
python --version

# Check PATH
$env:Path -split ';' | Select-String python
```

**Solution:**
1. Install Python 3.11+: https://www.python.org/downloads/
2. During installation, check "✓ Add Python to PATH"
3. Or manually add to PATH:
   - Settings → System → About → Advanced settings
   - Environment Variables → Path → Edit → New
   - Add: `C:\Python311` and `C:\Python311\Scripts`
4. Restart terminal

### Module Not Found

**Symptom:**
```
ModuleNotFoundError: No module named 'colorama'
```

**Diagnosis:**
```powershell
pip list | Select-String colorama
```

**Solution:**
```powershell
# Install missing package
pip install colorama

# Or reinstall all dependencies
pip install -r deployment_manager\requirements.txt

# If pip fails, upgrade first
python -m pip install --upgrade pip
```

### Permission Denied During Installation

**Symptom:**
```
[Errno 13] Permission denied
```

**Solution:**
```powershell
# Run PowerShell as Administrator
# Right-click PowerShell → "Run as administrator"

# Or use --user flag
pip install --user -r deployment_manager\requirements.txt
```

### PyInstaller Build Fails

**Symptom:**
```
AttributeError during build
```

**Solution:**
```powershell
# Clean previous builds
Remove-Item -Recurse -Force build, dist

# Update PyInstaller
pip install --upgrade pyinstaller

# Rebuild
python deployment_manager\build_exe.py

# If still fails, check Python version
python --version  # Must be 3.11+
```

---

## Configuration Issues

### Config File Not Found

**Symptom:**
```
Configuration file not found: deployment.config.env
```

**Diagnosis:**
```powershell
# Check if file exists
Test-Path deployment.config.env
```

**Solution:**
```powershell
# Copy from template
Copy-Item deployment.config.env.template deployment.config.env

# Or use example
Copy-Item examples\deployment.config.env.local deployment.config.env

# Edit it
notepad deployment.config.env
```

### Invalid Configuration Values

**Symptom:**
```
Configuration validation failed: SERVER_IP must be valid IPv4
```

**Common Mistakes:**

| Field | Wrong | Right |
|-------|-------|-------|
| `SERVER_IP` | `localhost` | `127.0.0.1` |
| `SERVER_IP` | `192.168.1` | `192.168.1.100` |
| `USE_TLS` | `True` | `true` |
| `NGINX_HTTPS_PORT` | `443` | `8000` (>1024) |
| `APP_KEY` | Missing `base64:` | `base64:XXXXX` |

**Solution:**
```powershell
# Validate after changes
python deployment_manager\main.py config

# Check specific values
Get-Content deployment.config.env | Select-String SERVER_IP
```

### Environmental Variable Not Loading

**Symptom:**
Tool doesn't pick up `WOOSOO_PROJECT_ROOT`

**Diagnosis:**
```powershell
# Check variable
$env:WOOSOO_PROJECT_ROOT

# Check if set persistently
[Environment]::GetEnvironmentVariable("WOOSOO_PROJECT_ROOT", "User")
```

**Solution:**
```powershell
# Set for current session
$env:WOOSOO_PROJECT_ROOT = "C:\path\to\project"

# Set persistently (PowerShell)
[Environment]::SetEnvironmentVariable("WOOSOO_PROJECT_ROOT", "C:\path\to\project", "User")

# Or use CLI option
python deployment_manager\main.py --project-root "C:\path\to\project" config
```

### TLS Certificate Not Found

**Symptom:**
```
TLS_CERT_PATH not found: certs/localhost.pem
```

**Diagnosis:**
```powershell
# Check if cert exists
Test-Path certs\localhost.pem
```

**Solution:**
```powershell
# Create certs directory
New-Item -ItemType Directory -Force -Path certs

# Generate certificate with mkcert
bin\mkcert\mkcert.exe -install
bin\mkcert\mkcert.exe -cert-file certs\localhost.pem -key-file certs\localhost-key.pem localhost 127.0.0.1

# Verify
Get-ChildItem certs
```

---

## Service Management Issues

### Services Won't Install

**Symptom:**
```
Failed to install service: Access denied
```

**Diagnosis:**
```powershell
# Check if running as admin
([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
```

**Solution:**
1. Right-click PowerShell → "Run as administrator"
2. Navigate to project directory
3. Retry installation:
   ```powershell
   python deployment_manager\main.py service install
   ```

### Service Won't Start

**Symptom:**
```
Service failed to start: The service did not respond in a timely fashion
```

**Diagnosis:**
```powershell
# Check service status
python deployment_manager\main.py service status WoosooBackend

# View service logs
Get-Content logs\backend.log -Tail 50

# Check Windows Event Log
Get-EventLog -LogName Application -Source WoosooBackend -Newest 10
```

**Common Causes:**

#### 1. Port Already in Use
```powershell
# Check port
netstat -ano | findstr :8000

# Kill process
taskkill /F /PID <pid>

# Or change port in config
```

#### 2. Missing Dependencies
```powershell
# Check PHP version
php --version  # Must be 8.1+

# Check PHP extensions
php -m | findstr pdo_mysql

# Install missing extensions (in php.ini)
```

#### 3. Incorrect Paths
```powershell
# Verify backend directory exists
Test-Path apps\woosoo-nexus

# Check artisan file
Test-Path apps\woosoo-nexus\artisan
```

#### 4. Database Not Ready
```powershell
# Test MySQL connection
mysql -u woosoo_user -p -e "SHOW DATABASES;"

# Start MySQL if down
net start MySQL80
```

**Solution:**
```powershell
# Fix the issue, then restart
python deployment_manager\main.py service stop WoosooBackend
python deployment_manager\main.py service start WoosooBackend
```

### Service Stuck in "Starting" State

**Symptom:**
Service shows "Starting..." but never starts

**Diagnosis:**
```powershell
# Check process
Get-Process | Where-Object { $_.Name -like "*php*" }

# View logs
Get-Content logs\backend.log -Tail 100
```

**Solution:**
```powershell
# Force stop
python deployment_manager\main.py service stop --force WoosooBackend

# Wait 10 seconds
Start-Sleep -Seconds 10

# Start again
python deployment_manager\main.py service start WoosooBackend
```

### Can't Uninstall Service

**Symptom:**
```
Failed to uninstall service: Service marked for deletion
```

**Diagnosis:**
```powershell
# Check service status
sc query WoosooBackend
```

**Solution:**
```powershell
# Stop service first
python deployment_manager\main.py service stop WoosooBackend

# Wait for it to fully stop
Start-Sleep -Seconds 5

# Uninstall
python deployment_manager\main.py service uninstall WoosooBackend

# If still stuck, reboot and try again
```

---

## Deployment Issues

### Deployment Validation Fails

**Symptom:**
```
Pre-deployment validation failed
```

**Diagnosis:**
```powershell
# Run validation separately
python deployment_manager\main.py validate
```

**Common Failures:**

#### Not Running as Administrator
**Error:** `✗ Running as Administrator`

**Solution:** Right-click PowerShell → "Run as administrator"

#### Insufficient Resources
**Error:** `✗ 2.0 GB RAM available (minimum 4.0 GB)`

**Solution:** Close unnecessary applications, or upgrade hardware

#### Ports Not Available
**Error:** `✗ Port 8000 in use`

**Solution:**
```powershell
# Find what's using port
netstat -ano | findstr :8000

# Kill process or change port in config
```

### Deployment Gets Stuck

**Symptom:**
Deployment hangs at "Starting services..."

**Diagnosis:**
```powershell
# Open another terminal, check services
python deployment_manager\main.py service status --all

# Check for errors
Get-Content logs\deployment.log -Tail 20
```

**Solution:**
```powershell
# Cancel deployment (Ctrl+C)

# Check what's blocking
python deployment_manager\main.py validate

# Fix issues and redeploy
python deployment_manager\main.py deploy
```

### Rollback Fails

**Symptom:**
```
Rollback failed: Backup not found
```

**Diagnosis:**
```powershell
# Check backup directory
Get-ChildItem backups | Sort-Object LastWriteTime -Descending
```

**Solution:**
```powershell
# If backup missing, manually restore
# 1. Stop services
python deployment_manager\main.py service stop --all

# 2. Restore files from version control
git checkout HEAD~1

# 3. Restore database
mysql -u root -p woosoo_production < backups\db_backup.sql

# 4. Start services
python deployment_manager\main.py service start --all
```

---

## WebSocket Issues

### WebSocket Connection Fails

**Symptom:**
Relay devices or PWA can't connect to WebSocket server

**Diagnosis:**
```powershell
# Check Reverb service status
python deployment_manager\main.py service status WoosooReverb

# Test WebSocket locally
# Install wscat: npm install -g wscat
wscat -c ws://localhost:6001/app/local_app_key
```

**Common Causes:**

#### 1. Reverb Not Running
**Solution:**
```powershell
python deployment_manager\main.py service start WoosooReverb
```

#### 2. Firewall Blocking Port
**Solution:**
```powershell
# Add firewall rule
New-NetFirewallRule -DisplayName "Reverb WebSocket" -Direction Inbound -LocalPort 6001 -Protocol TCP -Action Allow
```

#### 3. Wrong Credentials
**Check config:**
```ini
REVERB_APP_ID=local_app_id
REVERB_APP_KEY=local_app_key_12345
REVERB_APP_SECRET=local_app_secret_67890
```

**Must match Laravel .env:**
```ini
REVERB_APP_ID=local_app_id
REVERB_APP_KEY=local_app_key_12345
REVERB_APP_SECRET=local_app_secret_67890
```

#### 4. TLS Mismatch
**Error:** `WebSocket connection failed: Invalid certificate`

**Solution:**
- Ensure `USE_TLS` matches in deployment and Laravel configs
- If using WSS, ensure valid certificate
- For development, accept self-signed cert in browser/app

### Messages Not Being Received

**Symptom:**
Events broadcast but devices don't receive them

**Diagnosis:**
```powershell
# Check Reverb logs
Get-Content logs\reverb.log -Tail 50

# Enable debug logging
# In apps\woosoo-nexus\.env:
# LOG_LEVEL=debug

# Restart Reverb
python deployment_manager\main.py service restart WoosooReverb
```

**Common Causes:**

#### 1. Wrong Channel Name
**Check broadcasting:**
```php
// Backend
broadcast(new OrderCreated($order))->toOthers();

// Relay device must subscribe to same channel
channel = pusher.subscribe('orders.' + deviceId);
```

#### 2. Device Not Subscribed
**Ensure device subscribes before events sent:**
```javascript
// Subscribe first
const channel = pusher.subscribe('orders.device_001');

// Then listen
channel.bind('order-created', function(data) {
    console.log('Order:', data);
});
```

#### 3. Private Channel Auth Issues
**Check authorization endpoint:**
```powershell
# Test auth endpoint
curl -X POST http://localhost:8000/broadcasting/auth -d "channel_name=private-orders"
```

---

## Certificate/TLS Issues

### Invalid Certificate Error

**Symptom:**
```
SSL certificate problem: self signed certificate
```

**For Development:**
```powershell
# Install mkcert root CA
bin\mkcert\mkcert.exe -install

# Regenerate certificates
bin\mkcert\mkcert.exe -cert-file certs\localhost.pem -key-file certs\localhost-key.pem localhost 127.0.0.1
```

**For Production:**
Use trusted CA certificate (Let's Encrypt, DigiCert, etc.)

### Certificate Expired

**Symptom:**
```
SSL certificate problem: certificate has expired
```

**Check Expiry:**
```powershell
# View certificate details
Get-Content certs\localhost.pem | openssl x509 -text -noout

# Check expiry date
openssl x509 -enddate -noout -in certs\localhost.pem
```

**Solution:**
```powershell
# Generate new certificate
bin\mkcert\mkcert.exe -cert-file certs\localhost.pem -key-file certs\localhost-key.pem localhost 127.0.0.1

# Update config paths if needed

# Restart Nginx
python deployment_manager\main.py service restart WoosooNginx
```

### TLS Handshake Fails

**Symptom:**
```
SSL handshake failed
```

**Diagnosis:**
```powershell
# Test SSL connection
openssl s_client -connect localhost:8000 -showcerts
```

**Common Causes:**

1. **Certificate/Key Mismatch**
   ```powershell
   # Verify certificate matches key
   openssl x509 -noout -modulus -in certs\localhost.pem | openssl md5
   openssl rsa -noout -modulus -in certs\localhost-key.pem | openssl md5
   # Hashes must match
   ```

2. **Wrong CA Certificate**
   - Ensure client trusts the CA
   - For mkcert, run `mkcert -install` on client

3. **Nginx Config Error**
   ```powershell
   # Test Nginx config
   bin\nginx\nginx.exe -t -c configs\nginx.conf

   # Check TLS settings in nginx.conf
   ```

---

## Database Issues

### Connection Refused

**Symptom:**
```
SQLSTATE[HY000] [2002] Connection refused
```

**Diagnosis:**
```powershell
# Check MySQL running
Get-Service MySQL* | Select-Object Status, Name

# Test connection
mysql -u woosoo_user -p -h 127.0.0.1 -P 3306
```

**Solution:**
```powershell
# Start MySQL
net start MySQL80

# Or with XAMPP/Laragon
# Use their control panel
```

### Access Denied

**Symptom:**
```
SQLSTATE[HY000] [1045] Access denied for user 'woosoo_user'@'localhost'
```

**Diagnosis:**
```powershell
# Test credentials
mysql -u woosoo_user -p
# Enter password from deployment.config.env
```

**Solution:**
```sql
-- Connect as root
mysql -u root -p

-- Check user exists
SELECT User, Host FROM mysql.user WHERE User='woosoo_user';

-- Create user if missing
CREATE USER 'woosoo_user'@'localhost' IDENTIFIED BY 'password';

-- Grant permissions
GRANT ALL PRIVILEGES ON woosoo_production.* TO 'woosoo_user'@'localhost';
FLUSH PRIVILEGES;
```

### Database Not Found

**Symptom:**
```
SQLSTATE[HY000] [1049] Unknown database 'woosoo_production'
```

**Diagnosis:**
```powershell
# List databases
mysql -u root -p -e "SHOW DATABASES;"
```

**Solution:**
```sql
-- Create database
CREATE DATABASE woosoo_production CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Or restore from backup
mysql -u root -p woosoo_production < backups\db_backup.sql
```

### Migration Fails

**Symptom:**
```
php artisan migrate failed
```

**Diagnosis:**
```bash
cd apps\woosoo-nexus

# Check migration status
php artisan migrate:status

# View error details
php artisan migrate --verbose
```

**Common Solutions:**
```bash
# Reset migrations (DANGER: Drops all tables)
php artisan migrate:fresh

# Rollback last batch
php artisan migrate:rollback

# Rollback specific migration
php artisan migrate:rollback --step=1

# Force migration
php artisan migrate --force
```

---

## Performance Issues

### High CPU Usage

**Symptom:**
Server CPU constantly at 80%+

**Diagnosis:**
```powershell
# Check process CPU usage
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10

# Monitor PHP workers
Get-Process php | Select-Object Id, CPU, WorkingSet
```

**Common Causes:**

1. **Too Many PHP Workers**
   ```ini
   # In deployment.config.env, reduce workers
   # If not configurable, edit service definition
   ```

2. **Infinite Loop in Code**
   - Check application logs
   - Review recent code changes
   - Use profiling tools (Xdebug)

3. **Database Query Issues**
   ```sql
   -- Check slow queries
   SHOW PROCESSLIST;
   ```

### High Memory Usage

**Symptom:**
System running out of RAM

**Diagnosis:**
```powershell
# Check memory usage
Get-Process | Sort-Object WS -Descending | Select-Object -First 10 Name, @{N='Memory(MB)';E={[int]($_.WS/1MB)}}
```

**Solution:**
```powershell
# Restart services to free memory
python deployment_manager\main.py service restart --all

# If persistent, increase RAM or optimize code
```

### Slow Response Times

**Symptom:**
API requests taking 5+ seconds

**Diagnosis:**
```powershell
# Test API endpoint
Measure-Command { Invoke-WebRequest http://localhost:8000/api/health }

# Check Laravel logs
Get-Content apps\woosoo-nexus\storage\logs\laravel.log -Tail 50
```

**Common Causes:**

1. **Database Not Indexed**
   ```sql
   -- Check query execution plan
   EXPLAIN SELECT * FROM orders WHERE status='pending';
   ```

2. **N+1 Query Problem**
   - Use eager loading in Laravel
   ```php
   // Bad
   $orders = Order::all();
   foreach ($orders as $order) {
       echo $order->customer->name;
   }

   // Good
   $orders = Order::with('customer')->get();
   ```

3. **Caching Disabled**
   ```bash
   # Enable Laravel caching
   php artisan config:cache
   php artisan route:cache
   php artisan view:cache
   ```

---

## Error Messages Reference

### Common Error Codes

| Error Code | Meaning | Common Cause |
|------------|---------|--------------|
| `E001` | Configuration invalid | Missing required field |
| `E002` | Service start failed | Port in use, missing executable |
| `E003` | Database connection failed | Wrong credentials, MySQL down |
| `E004` | Permission denied | Not running as admin |
| `E005` | File not found | Wrong path in config |
| `E006` | Port in use | Another service using port |
| `E007` | Certificate invalid | Expired or self-signed cert |
| `E008` | Validation failed | System requirements not met |

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | General error |
| `2` | Configuration error |
| `3` | Permission error |
| `4` | Service error |
| `5` | Validation error |

---

## Getting Support

### Before Asking for Help

1. **Run Diagnostics:**
   ```powershell
   python deployment_manager\main.py validate
   python deployment_manager\main.py config
   python deployment_manager\main.py service status --all
   ```

2. **Check Logs:**
   ```powershell
   Get-Content logs\deployment.log -Tail 100
   Get-Content logs\backend.log -Tail 100
   Get-Content logs\reverb.log -Tail 100
   ```

3. **Search Existing Issues:**
   - Check GitHub Issues
   - Search this documentation
   - Review [FAQ section in COMPREHENSIVE.md](COMPREHENSIVE.md#faq)

### Creating a Support Issue

**Include:**
1. **Environment:**
   - OS version: `systeminfo | findstr /B /C:"OS Name" /C:"OS Version"`
   - Python version: `python --version`
   - Tool version: `python deployment_manager\main.py --version`

2. **Configuration (sanitized):**
   - Remove passwords/secrets
   - Include relevant portions of `deployment.config.env`

3. **Error Output:**
   - Full error message
   - Stack trace if available
   - Command that triggered error

4. **Logs:**
   - Last 50 lines of relevant log file
   - Timestamp of error

5. **Steps to Reproduce:**
   - Exact commands run
   - Expected vs actual behavior

### Support Channels

- **GitHub Issues:** https://github.com/yourusername/woosoo-deployment-manager/issues
- **Documentation:** [COMPREHENSIVE.md](COMPREHENSIVE.md)
- **Email:** support@example.com
- **Discord:** (if applicable)

---

## Related Documentation

- [Installation Guide](INSTALLATION.md)
- [Configuration Reference](CONFIGURATION.md)
- [User Guide](COMPREHENSIVE.md)
- [Requirements](REQUIREMENTS.md)
