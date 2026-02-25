---
name: linux-commands
description: Essential Linux/Unix command reference covering file operations, text processing, process management, networking, disk usage, permissions, systemd services, SSH, package management, and shell scripting patterns for DevOps and development workflows.
---

# Linux Commands Reference

This skill should be used when working with Linux/Unix systems, writing shell scripts, or performing DevOps tasks. It covers essential commands, administration, and shell scripting.

## When to Use This Skill

Use this skill when you need to:

- Navigate and manage files on Linux systems
- Process text and logs from the command line
- Manage processes and services
- Configure networking and firewalls
- Write shell scripts
- Administer Linux servers

## File Operations

```bash
# Navigation
pwd                          # Print working directory
ls -la                       # List all files with details
ls -lhS                      # Sort by size, human-readable
tree -L 2                    # Directory tree, 2 levels deep

# File manipulation
cp -r src/ dest/             # Copy recursively
mv old.txt new.txt           # Rename/move
mkdir -p a/b/c               # Create nested directories
ln -s target link            # Create symbolic link

# Find files
find . -name "*.log" -mtime -7           # Files modified in last 7 days
find . -type f -size +100M               # Files larger than 100MB
find . -name "*.tmp" -delete             # Find and delete

# Disk usage
du -sh */                    # Directory sizes
df -h                        # Filesystem usage
ncdu /var                    # Interactive disk usage viewer
```

## Text Processing

```bash
# Search
grep -rn "pattern" .                     # Recursive search with line numbers
grep -rn --include="*.ts" "TODO" .       # Search only TypeScript files
grep -c "ERROR" app.log                  # Count matches
grep -A 3 -B 1 "Exception" app.log      # Show context around matches

# Transform
sed 's/old/new/g' file.txt              # Replace text
sed -i '' 's/http:/https:/g' *.html     # In-place replace (macOS)
awk '{print $1, $4}' access.log         # Extract columns
cut -d',' -f1,3 data.csv               # Extract CSV columns
sort -t',' -k3 -n data.csv             # Sort by 3rd column numerically
uniq -c | sort -rn                      # Count unique lines, sort by frequency

# Log analysis
tail -f app.log                         # Follow log in real-time
tail -f app.log | grep --line-buffered "ERROR"  # Filter real-time
wc -l app.log                           # Count lines
head -100 app.log                       # First 100 lines
```

## Process Management

```bash
# View processes
ps aux                       # All processes
ps aux | grep node           # Find specific processes
top -o %MEM                  # Sort by memory usage
htop                         # Interactive process viewer

# Process control
kill PID                     # Graceful stop (SIGTERM)
kill -9 PID                  # Force kill (SIGKILL)
pkill -f "node server.js"   # Kill by name pattern
nohup command &              # Run in background, survives logout

# Job control
command &                    # Run in background
jobs                         # List background jobs
fg %1                        # Bring job 1 to foreground
```

## Networking

```bash
# Connectivity
ping -c 4 google.com                    # Test connectivity
curl -s https://api.example.com | jq    # HTTP request + JSON parse
curl -X POST -H "Content-Type: application/json" -d '{"key":"value"}' URL
wget -q -O - URL                        # Download to stdout

# Ports and connections
ss -tlnp                                # Listening ports
lsof -i :3000                           # What's using port 3000
netstat -an | grep ESTABLISHED          # Active connections

# DNS
dig example.com                         # DNS lookup
nslookup example.com                    # Alternative DNS lookup
host example.com                        # Simple DNS lookup
```

## Permissions

```bash
# Change permissions
chmod 755 script.sh          # rwxr-xr-x
chmod +x script.sh           # Add execute permission
chmod -R 644 public/         # Recursive

# Change ownership
chown user:group file        # Change owner and group
chown -R www-data:www-data /var/www/    # Recursive

# Permission reference
# 7 = rwx (read + write + execute)
# 6 = rw- (read + write)
# 5 = r-x (read + execute)
# 4 = r-- (read only)
# 755 = owner:rwx, group:r-x, others:r-x
# 644 = owner:rw-, group:r--, others:r--
```

## Systemd Services

```bash
# Service management
systemctl start nginx        # Start service
systemctl stop nginx         # Stop service
systemctl restart nginx      # Restart
systemctl reload nginx       # Reload config without downtime
systemctl status nginx       # Check status
systemctl enable nginx       # Start on boot
journalctl -u nginx -f       # Follow service logs
```

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/myapp
ExecStart=/usr/bin/node /opt/myapp/dist/server.js
Restart=always
RestartSec=5
Environment=NODE_ENV=production
Environment=PORT=3000

[Install]
WantedBy=multi-user.target
```

## SSH

```bash
# Connect
ssh user@hostname
ssh -i ~/.ssh/key.pem user@hostname     # With key file
ssh -L 3000:localhost:3000 user@host    # Port forwarding (local)
ssh -R 8080:localhost:3000 user@host    # Port forwarding (remote)

# SSH config (~/.ssh/config)
Host myserver
  HostName 192.168.1.100
  User deploy
  IdentityFile ~/.ssh/deploy_key
  Port 22

# Key management
ssh-keygen -t ed25519 -C "email@example.com"  # Generate key
ssh-copy-id user@hostname                      # Copy key to server
```

## Shell Script Template

```bash
#!/usr/bin/env bash
set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Constants
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="/var/log/myapp/deploy.log"

# Functions
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }
die() { log "ERROR: $*"; exit 1; }

# Argument parsing
APP_ENV="${1:?Usage: $0 <environment>}"
[[ "$APP_ENV" =~ ^(dev|staging|prod)$ ]] || die "Invalid environment: $APP_ENV"

# Main
log "Starting deployment to $APP_ENV"
cd "$SCRIPT_DIR/.."

log "Building application..."
npm run build || die "Build failed"

log "Deployment complete"
```

## Additional Resources

- TLDR Pages: https://tldr.sh/
- ExplainShell: https://explainshell.com/
- Bash Reference: https://www.gnu.org/software/bash/manual/
- Linux Command Library: https://linuxcommandlibrary.com/
