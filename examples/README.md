# Configuration Examples

This directory contains example configuration files for different environments.

## Files

- `deployment.config.env.local` - Local development configuration
- `deployment.config.env.staging` - Staging environment configuration
- `deployment.config.env.production` - Production environment configuration (sanitized)

## Usage

1. Choose the example that matches your environment
2. Copy it to the project root as `deployment.config.env`:

```powershell
# For local development
copy examples\deployment.config.env.local deployment.config.env

# For staging
copy examples\deployment.config.env.staging deployment.config.env

# For production
copy examples\deployment.config.env.production deployment.config.env
```

3. Edit the file with your actual values
4. **NEVER** commit the configured file to version control

## Configuration Guidelines

### Local Development
- `APP_DEBUG=true` - Enable debugging
- `LOG_LEVEL=debug` - Verbose logging
- `USE_TLS=false` - HTTP is ok for local  
- Simple passwords are acceptable

### Staging
- `APP_DEBUG=false` - Disable debugging
- `LOG_LEVEL=info` - Moderate logging
- `USE_TLS=true` - Always use HTTPS
- Use strong passwords
- Mirror production setup as closely as possible

### Production
- `APP_DEBUG=false` - **CRITICAL**: Never enable debug in production
- `LOG_LEVEL=error` - Minimal logging
- `USE_TLS=true` - **MANDATORY**: Always use HTTPS
- **VERY STRONG** passwords required
- Regular backups configured
- Security hardening applied
- Monitoring and alerting enabled

## Security Best Practices

1. **Never Commit Secrets**
   - Add `deployment.config.env` to `.gitignore`
   - Only commit `.template` and `.example` files
   - Use environment-specific configs, not branches

2. **Strong Credentials**
   - Minimum 16 characters for passwords
   - Mix of uppercase, lowercase, numbers, symbols
   - Generate APP_KEY with: `php artisan key:generate --show`
   - Use unique passwords for each service

3. **Principle of Least Privilege**
   - Database users should have minimal required permissions
   - Don't use root/admin accounts in production
   - Separate users for different databases

4. **Regular Rotation**
   - Rotate passwords quarterly
   - Rotate keys annually
   - Update certificates before expiry

5. **Secure Storage**
   - Store production configs in secure password manager
   - Encrypt backups containing credentials
   - Limit access to configuration files

## Validation

Always validate your configuration after changes:

```powershell
python deployment_manager\main.py config
```

Look for the green "✓ Configuration is valid" message.

## Environment-Specific Tips

### Local Development
- Use `127.0.0.1` or `localhost` as SERVER_IP
- Ports 80/443 may require admin rights, use 8000+
- mkcert for local HTTPS: `mkcert localhost 127.0.0.1 ::1`

### Staging
- Use internal IP or hostname
- Test with production-like data
- Enable detailed logging for debugging
- Test backup/restore procedures

### Production
- Use static IP or load balancer
- Configure firewall rules
- Set up monitoring and alerting
- Have rollback plan ready
- Document all configuration decisions

## Troubleshooting

**"Configuration file not found"**
```powershell
copy deployment.config.env.template deployment.config.env
```

**"Configuration has errors: APP_KEY is required"**
```bash
php artisan key:generate --show
# Copy the output to APP_KEY in config
```

**"Invalid IP address"**
- Must be valid IPv4 format: `192.168.1.100`
- No hostnames, only IP addresses

**"Port must be between 1024-65535"**  
- Ports below 1024 require admin rights
- Choose ports 8000+ for easier setup

## Need Help?

- Read [CONFIGURATION.md](../docs/CONFIGURATION.md) for detailed reference
- Check [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md) for common issues
- Open an issue on GitHub for support
