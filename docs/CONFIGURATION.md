# Configuration Reference

Complete configuration guide for the Woosoo Deployment Manager.

## Table of Contents

- [Configuration File Location](#configuration-file-location)
- [Configuration Format](#configuration-format)
- [Configuration Sections](#configuration-sections)
  - [Environment Settings](#environment-settings)
  - [Network Configuration](#network-configuration)
  - [TLS/SSL Configuration](#tlsssl-configuration)
  - [WebSocket Configuration](#websocket-configuration)
  - [Database Configuration](#database-configuration)
  - [Application Settings](#application-settings)
  - [Path Configuration](#path-configuration)
- [Environment-Specific Configurations](#environment-specific-configurations)
- [Configuration Validation](#configuration-validation)
- [Security Best Practices](#security-best-practices)
- [Troubleshooting Configuration](#troubleshooting-configuration)

## Configuration File Location

The deployment manager looks for `deployment.config.env` in the **project root directory**.

**Default lookup order:**
1. Environment variable: `WOOSOO_PROJECT_ROOT`
2. CLI argument: `--project-root`
3. Current working directory

**Example:**
```powershell
# Using environment variable
$env:WOOSOO_PROJECT_ROOT = "C:\projects\woosoo"
python deployment_manager\main.py config

# Using CLI argument
python deployment_manager\main.py --project-root "C:\projects\woosoo" config

# Using current directory (default)
cd C:\projects\woosoo
python deployment_manager\main.py config
```

## Configuration Format

The configuration file uses the **dotenv** format:

```ini
# Comments start with hash
KEY=value                    # Simple value
KEY="value with spaces"      # Quoted value
KEY=multi\nline             # Escaped characters
```

**Rules:**
- One setting per line
- No spaces around `=` (unless quoted)
- Comments start with `#`
- Empty lines are ignored
- Values can be quoted for spaces/special chars

## Configuration Sections

### Environment Settings

#### `DEPLOYMENT_ENV`
- **Type:** String
- **Required:** Yes
- **Values:** `development`, `staging`, `production`
- **Description:** Determines environment-specific behavior

```ini
DEPLOYMENT_ENV=production
```

**Effects:**
- `development`: Verbose logging, debug mode enabled
- `staging`: Moderate logging, mimics production
- `production`: Minimal logging, strict security

---

### Network Configuration

#### `SERVER_IP`
- **Type:** IPv4 Address
- **Required:** Yes
- **Format:** `xxx.xxx.xxx.xxx`
- **Description:** Server's primary IP address

```ini
SERVER_IP=192.168.1.100
```

**Examples:**
- Development: `127.0.0.1` (localhost)
- Staging: `192.168.1.50` (internal IP)
- Production: `192.168.100.85` (static IP)

**Validation:**
- Must be valid IPv4 format
- No hostnames allowed
- Recommended: Use static IP for production

#### `NGINX_HTTPS_PORT`
- **Type:** Integer
- **Required:** Yes
- **Range:** `1024-65535` (recommended `8000-9999`)
- **Default:** `8000`
- **Description:** HTTPS port for Nginx

```ini
NGINX_HTTPS_PORT=8000
```

**Notes:**
- Ports below 1024 require admin rights
- Must not conflict with other services
- Standard HTTPS is 443, but 8000 avoids conflicts

#### `NGINX_HTTP_PORT`
- **Type:** Integer
- **Required:** Yes
- **Range:** `1024-65535`
- **Default:** `80`
- **Description:** HTTP port for Nginx (redirects to HTTPS if TLS enabled)

```ini
NGINX_HTTP_PORT=80
```

#### `REVERB_PORT`
- **Type:** Integer
- **Required:** Yes
- **Range:** `1024-65535`
- **Default:** `6001`
- **Description:** WebSocket server port (Laravel Reverb)

```ini
REVERB_PORT=6001
```

**Notes:**
- Must be accessible to clients (relay devices, PWA)
- Configure firewall to allow this port
- Reverb uses this for WebSocket connections

#### `MYSQL_PORT`
- **Type:** Integer
- **Required:** Yes
- **Range:** `1024-65535`
- **Default:** `3306`
- **Description:** MySQL database port

```ini
MYSQL_PORT=3306
```

---

### TLS/SSL Configuration

#### `USE_TLS`
- **Type:** Boolean
- **Required:** Yes
- **Values:** `true`, `false`
- **Description:** Enable HTTPS/WSS

```ini
USE_TLS=true
```

**Recommendations:**
- Development: `false` (HTTP is fine locally)
- Staging: `true` (test production setup)
- Production: `true` (MANDATORY for security)

#### `TLS_CERT_PATH`
- **Type:** File Path
- **Required:** If `USE_TLS=true`
- **Format:** Relative or absolute path to PEM certificate
- **Description:** SSL/TLS certificate file

```ini
TLS_CERT_PATH=certs/production.example.com.pem
```

**Certificate Types:**
- **Development:** Self-signed with mkcert
  ```powershell
  bin\mkcert\mkcert.exe -cert-file certs\localhost.pem -key-file certs\localhost-key.pem localhost 127.0.0.1
  ```
- **Staging:** Internal CA or self-signed
- **Production:** Trusted CA (Let's Encrypt, DigiCert, etc.)

#### `TLS_KEY_PATH`
- **Type:** File Path
- **Required:** If `USE_TLS=true`
- **Format:** Relative or absolute path to PEM private key
- **Description:** SSL/TLS private key file

```ini
TLS_KEY_PATH=certs/production.example.com-key.pem
```

**Security:**
- **Never commit private keys to version control**
- Set file permissions to read-only
- Rotate keys annually
- Keep separate keys per environment

---

### WebSocket Configuration

#### `REVERB_APP_ID`
- **Type:** String
- **Required:** Yes
- **Description:** Reverb application identifier

```ini
REVERB_APP_ID=prod_app_id_987
```

**Generation:**
- Use descriptive names: `{env}_app_id_{random}`
- Must be unique per environment
- No special characters

#### `REVERB_APP_KEY`
- **Type:** String
- **Required:** Yes
- **Length:** 20+ characters (recommended)
- **Description:** Reverb authentication key

```ini
REVERB_APP_KEY=prod_key_SECURE_RANDOM_STRING
```

**Generation:**
```powershell
# PowerShell random key generator
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

**Security:**
- Minimum 20 characters
- Mix of uppercase, lowercase, numbers
- Unique per environment
- Rotate quarterly

#### `REVERB_APP_SECRET`
- **Type:** String
- **Required:** Yes
- **Length:** 20+ characters (recommended)
- **Description:** Reverb signing secret

```ini
REVERB_APP_SECRET=prod_secret_SECURE_RANDOM_STRING
```

**Generation:** Same as `REVERB_APP_KEY`

**Security:**
- Never share or expose
- Different from APP_KEY
- Rotate quarterly

---

### Database Configuration

#### Main Database (Woosoo)

##### `DB_NAME`
- **Type:** String
- **Required:** Yes
- **Description:** Primary database name

```ini
DB_NAME=woosoo_production
```

**Naming Convention:**
- Development: `woosoo_dev`
- Staging: `woosoo_staging`
- Production: `woosoo_production`

##### `DB_USERNAME`
- **Type:** String
- **Required:** Yes
- **Description:** Database user

```ini
DB_USERNAME=woosoo_prod_user
```

**Security:**
- **Never use root in production**
- Create dedicated user per environment
- Grant only required permissions
- Different user per database

##### `DB_PASSWORD`
- **Type:** String
- **Required:** Yes (can be empty for local dev)
- **Length:** 16+ characters (production)
- **Description:** Database password

```ini
DB_PASSWORD=USE_VERY_STRONG_PASSWORD_HERE
```

**Requirements (Production):**
- Minimum 16 characters
- Mix of uppercase, lowercase, numbers, symbols
- No dictionary words
- Unique password (not reused)

#### POS Database (Krypton/Legacy)

##### `DB_POS_NAME`
- **Type:** String
- **Required:** Yes
- **Description:** POS system database name

```ini
DB_POS_NAME=krypton_production
```

##### `DB_POS_USERNAME`
- **Type:** String
- **Required:** Yes
- **Description:** POS database user

```ini
DB_POS_USERNAME=krypton_prod_user
```

##### `DB_POS_PASSWORD`
- **Type:** String
- **Required:** Yes
- **Description:** POS database password

```ini
DB_POS_PASSWORD=USE_VERY_STRONG_PASSWORD_HERE
```

**Note:** POS database is read-only for Woosoo. Ensure user has only SELECT permissions.

---

### Application Settings

#### `APP_NAME`
- **Type:** String
- **Required:** Yes
- **Description:** Laravel application name

```ini
APP_NAME=Woosoo
```

**Environment-Specific:**
- Development: `WoosooLocal`
- Staging: `WoosooStaging`
- Production: `Woosoo`

#### `APP_KEY`
- **Type:** String
- **Required:** Yes
- **Format:** `base64:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`
- **Description:** Laravel encryption key

```ini
APP_KEY=base64:GENERATE_UNIQUE_KEY_WITH_PHP_ARTISAN
```

**Generation:**
```bash
cd apps/woosoo-nexus
php artisan key:generate --show
```

**Security:**
- **CRITICAL**: Generate unique key per environment
- Never share between environments
- Rotate if compromised
- Changing this key will invalidate all encrypted data

#### `APP_DEBUG`
- **Type:** Boolean
- **Required:** Yes
- **Values:** `true`, `false`
- **Description:** Enable Laravel debug mode

```ini
APP_DEBUG=false
```

**Settings:**
- Development: `true`
- Staging: `false`
- Production: `false` (**MANDATORY**)

**Warning:** **NEVER** enable debug in production! It exposes:
- Full stack traces with file paths
- Environment variables
- Database queries
- Application secrets

#### `LOG_LEVEL`
- **Type:** String
- **Required:** Yes
- **Values:** `debug`, `info`, `warning`, `error`, `critical`
- **Description:** Minimum log level to record

```ini
LOG_LEVEL=error
```

**Recommendations:**
- Development: `debug` (everything)
- Staging: `info` (moderate)
- Production: `error` (minimal)

---

### Path Configuration

#### `BACKEND_DIR`
- **Type:** Directory Path
- **Required:** No
- **Default:** `apps/woosoo-nexus`
- **Description:** Path to Laravel backend (relative to project root)

```ini
BACKEND_DIR=apps/woosoo-nexus
```

**Formats:**
- Relative: `apps/woosoo-nexus`
- Absolute: `C:/projects/woosoo/apps/woosoo-nexus`
- Forward slashes recommended

#### `PWA_DIR`
- **Type:** Directory Path
- **Required:** No
- **Default:** `apps/tablet-ordering-pwa`
- **Description:** Path to Nuxt PWA (relative to project root)

```ini
PWA_DIR=apps/tablet-ordering-pwa
```

#### `RELAY_DIR`
- **Type:** Directory Path
- **Required:** No
- **Default:** `apps/relay-device-v2`
- **Description:** Path to Flutter relay device (relative to project root)

```ini
RELAY_DIR=apps/relay-device-v2
```

#### `NGINX_EXE`
- **Type:** File Path
- **Required:** No
- **Default:** `bin/nginx/nginx.exe`
- **Description:** Path to Nginx executable

```ini
NGINX_EXE=bin/nginx/nginx.exe
```

#### `NGINX_CONFIG`
- **Type:** File Path
- **Required:** No
- **Default:** `configs/nginx.conf`
- **Description:** Path to Nginx configuration file

```ini
NGINX_CONFIG=configs/nginx.conf
```

---

## Environment-Specific Configurations

### Development (Local)

```ini
DEPLOYMENT_ENV=development
SERVER_IP=127.0.0.1
USE_TLS=false
NGINX_HTTPS_PORT=8000
NGINX_HTTP_PORT=80
REVERB_PORT=6001

DB_NAME=woosoo_dev
DB_USERNAME=root
DB_PASSWORD=

APP_DEBUG=true
LOG_LEVEL=debug
```

**Characteristics:**
- Localhost only
- HTTP is acceptable
- Debug enabled
- Verbose logging
- Weak/no passwords ok

### Staging (Pre-Production)

```ini
DEPLOYMENT_ENV=staging
SERVER_IP=192.168.1.50
USE_TLS=true
NGINX_HTTPS_PORT=8000
NGINX_HTTP_PORT=80
REVERB_PORT=6001

TLS_CERT_PATH=certs/staging.example.com.pem
TLS_KEY_PATH=certs/staging.example.com-key.pem

DB_NAME=woosoo_staging
DB_USERNAME=woosoo_user
DB_PASSWORD=CHANGE_THIS_STAGING_PASSWORD

APP_DEBUG=false
LOG_LEVEL=info
```

**Characteristics:**
- Internal network
- HTTPS required
- Mirror production setup
- Moderate logging
- Strong passwords

### Production

```ini
DEPLOYMENT_ENV=production
SERVER_IP=192.168.100.85
USE_TLS=true
NGINX_HTTPS_PORT=8000
NGINX_HTTP_PORT=80
REVERB_PORT=6001

TLS_CERT_PATH=certs/production.example.com.pem
TLS_KEY_PATH=certs/production.example.com-key.pem

REVERB_APP_ID=prod_app_id_987
REVERB_APP_KEY=prod_key_SECURE_RANDOM_STRING
REVERB_APP_SECRET=prod_secret_SECURE_RANDOM_STRING

DB_NAME=woosoo_production
DB_USERNAME=woosoo_prod_user
DB_PASSWORD=USE_VERY_STRONG_PASSWORD_HERE

APP_NAME=Woosoo
APP_KEY=base64:GENERATE_UNIQUE_KEY_WITH_PHP_ARTISAN
APP_DEBUG=false
LOG_LEVEL=error
```

**Characteristics:**
- Static IP
- HTTPS mandatory
- Debug **disabled**
- Minimal logging
- Very strong passwords
- Unique keys

---

## Configuration Validation

### Automatic Validation

Run validation after any config changes:

```powershell
python deployment_manager\main.py config
```

**Checks:**
- File exists and is readable
- All required fields present
- Values are valid format
- IP addresses valid
- Ports in valid range
- Paths exist
- TLS files present (if enabled)

**Expected Output:**
```
✓ Configuration file exists
✓ DEPLOYMENT_ENV is valid
✓ SERVER_IP is valid IPv4
✓ All ports in valid range
✓ TLS certificate exists
✓ TLS key exists
✓ Configuration is valid
```

### Manual Validation

**Check specific values:**

```powershell
# View current configuration
python deployment_manager\main.py config --show

# Test specific setting
$env:SERVER_IP = "192.168.1.100"
python deployment_manager\main.py validate
```

### Common Validation Errors

#### Missing Required Field

**Error:**
```
Configuration validation failed: DEPLOYMENT_ENV is required
```

**Fix:** Add missing field to `deployment.config.env`

#### Invalid IP Format

**Error:**
```
Configuration validation failed: SERVER_IP must be valid IPv4
```

**Fix:** Use format `xxx.xxx.xxx.xxx`, e.g., `192.168.1.100`

#### Port Out of Range

**Error:**
```
Configuration validation failed: NGINX_HTTPS_PORT must be 1024-65535
```

**Fix:** Use port between 1024-65535

#### File Not Found

**Error:**
```
Configuration validation failed: TLS_CERT_PATH not found
```

**Fix:** Generate certificate or correct path

---

## Security Best Practices

### 1. Never Commit Secrets

```powershell
# .gitignore should contain:
*.config.env
.env
*.key
*.pem
```

### 2. Strong Passwords

**Requirements:**
- Minimum 16 characters
- Uppercase + lowercase
- Numbers + symbols
- No dictionary words
- Unique per environment

**Generator (PowerShell):**
```powershell
-join ((33..126) | Get-Random -Count 24 | ForEach-Object {[char]$_})
```

### 3. Principle of Least Privilege

**Database Users:**
```sql
-- Create dedicated user
CREATE USER 'woosoo_prod'@'localhost' IDENTIFIED BY 'strong_password';

-- Grant only required permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON woosoo_production.* TO 'woosoo_prod'@'localhost';

-- No DROP, CREATE, ALTER in production
FLUSH PRIVILEGES;
```

### 4. Regular Key Rotation

**Schedule:**
- Database passwords: Quarterly
- APP_KEY: Annually (or if compromised)
- Reverb keys: Quarterly
- TLS certificates: Before expiry

**Process:**
1. Generate new credentials
2. Update configuration
3. Restart services
4. Verify functionality
5. Document change

### 5. Environment Isolation

- **Never** copy production config to development
- **Never** use same keys across environments
- **Never** test with production data locally
- Keep configurations in separate files

### 6. Secure Storage

**Production Configs:**
- Store in password manager (1Password, Bitwarden)
- Encrypt config files at rest
- Limit access (need-to-know basis)
- Audit access logs

### 7. Backup Encryption

**Encrypting configs:**
```powershell
# Encrypt (PowerShell 7+)
$secret = ConvertTo-SecureString "deployment.config.env content" -AsPlainText
$secret | ConvertFrom-SecureString | Out-File secure-backup.txt

# Decrypt
$encrypted = Get-Content secure-backup.txt | ConvertTo-SecureString
[Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($encrypted))
```

---

## Troubleshooting Configuration

### Config File Not Found

**Error:** `Configuration file not found: deployment.config.env`

**Solution:**
```powershell
copy deployment.config.env.template deployment.config.env
notepad deployment.config.env
```

### Invalid Boolean Value

**Error:** `USE_TLS must be true or false`

**Solution:** Use lowercase `true` or `false` (not `True`, `FALSE`, `1`, `0`)

### Port Already in Use

**Check:**
```powershell
netstat -ano | findstr :8000
```

**Solution:**
```powershell
# Kill process using port
taskkill /F /PID <pid>

# Or change port in config
NGINX_HTTPS_PORT=8001
```

### TLS Certificate Not Found

**Error:** `TLS_CERT_PATH not found: certs/localhost.pem`

**Solution:**
```powershell
# Generate with mkcert
bin\mkcert\mkcert.exe -install
bin\mkcert\mkcert.exe -cert-file certs\localhost.pem -key-file certs\localhost-key.pem localhost 127.0.0.1
```

### Laravel APP_KEY Invalid

**Error:** `APP_KEY must start with base64:`

**Solution:**
```bash
cd apps/woosoo-nexus
php artisan key:generate --show
# Copy output to APP_KEY in config
```

### Database Connection Failed

**Check:**
```powershell
# Test MySQL connection
mysql -u woosoo_user -p woosoo_production
```

**Common Issues:**
- Wrong password
- User doesn't exist
- No permissions granted
- MySQL not running
- Wrong port

### Path Not Found

**Error:** `BACKEND_DIR not found: apps/woosoo-nexus`

**Solution:**
```powershell
# Verify path exists
Test-Path apps\woosoo-nexus

# Use absolute path if needed
BACKEND_DIR=C:/projects/woosoo/apps/woosoo-nexus
```

---

## Related Documentation

- [Installation Guide](INSTALLATION.md)
- [User Guide](COMPREHENSIVE.md)
- [Requirements](REQUIREMENTS.md)
- [Troubleshooting](TROUBLESHOOTING.md)

## Need Help?

- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- Open an issue on GitHub
- Email support: support@example.com
