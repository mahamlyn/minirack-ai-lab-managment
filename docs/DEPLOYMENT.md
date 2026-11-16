# MiniRack Management Portal - Deployment Guide

## Overview

The MiniRack Management Portal is a modern web-based dashboard that monitors and manages your distributed AI Lab environment. This guide covers all deployment methods.

## Supported Environments

✅ **Supported**:
- Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+)
- Docker & Docker Compose
- Kubernetes (via Helm charts - optional)
- Bare metal (systemd)
- LaForge (ai-utility) host

❌ **Not Supported**:
- Windows (use WSL2 or Docker Desktop)
- Python < 3.9

## Prerequisites

### All Deployments
- Python 3.9+ (included in Docker)
- Network access to all three hosts:
  - LaForge (ai-utility): 192.168.1.161
  - Data (ai-core): 192.168.1.160
  - Riker (ai-web): 192.168.1.162
- Port 8080 available on LaForge

### For Ansible Deployment
- Ansible 2.10+
- SSH access to LaForge with sudo privileges
- `community.docker` collection installed:
  ```bash
  ansible-galaxy collection install community.docker
  ```

### For Docker Deployment
- Docker 20.10+
- Docker Compose 2.0+

### For Bare Metal Deployment
- systemd support
- Python venv support

## Deployment Methods

### Method 1: Docker Compose (Recommended for LaForge)

Fastest and most reliable deployment method for the LaForge host.

#### Step 1: Prepare Repository

On the LaForge host:
```bash
# SSH into LaForge
ssh localadmin@192.168.1.161

# Clone the management repository
git clone https://github.com/yourusername/minirack-ai-lab-managment.git
cd minirack-ai-lab-managment

# Copy and configure environment
cp .env.example .env
# Edit .env as needed (keep defaults or customize)
```

#### Step 2: Build and Deploy

```bash
# Option A: Using the quick start script
chmod +x start.sh
./start.sh

# Option B: Manual deployment
docker-compose build
docker-compose up -d
```

#### Step 3: Verify Deployment

```bash
# Check if container is running
docker ps | grep minirack-management

# Check health
curl http://localhost:8080/health

# View logs
docker-compose logs -f
```

#### Step 4: Access the Portal

- **Dashboard**: http://192.168.1.161:8080
- **API Docs**: http://192.168.1.161:8080/api/docs

---

### Method 2: Ansible Deployment (Full Automation)

Automates everything including host preparation.

#### Step 1: Update Ansible Inventory

Edit `../minirack-ai-lab/inventory/servers.ini`:
```ini
[ai-utility]
192.168.1.161 # LAFORGE
```

#### Step 2: Run Deployment Playbook

From the minirack-ai-lab directory:

```bash
# Option A: Automated management deployment
ansible-playbook tasks/deploy-management.yaml -i inventory/servers.ini \
  -u localadmin -k -K

# Option B: Include in main deployment
ansible-playbook main.yml -i inventory/servers.ini \
  -u localadmin -k -K
```

The playbook will:
1. Clone the management repository
2. Build the Docker image
3. Create configuration directories
4. Deploy the container
5. Verify service health
6. Display access information

#### Step 3: Monitor Deployment

```bash
# SSH into LaForge and check logs
ssh localadmin@192.168.1.161
docker logs -f minirack-management
```

---

### Method 3: Bare Metal with systemd

For direct system integration without containers.

#### Step 1: Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev \
    build-essential git curl

# Create application directory
sudo mkdir -p /opt/minirack-management
sudo chown localadmin:localadmin /opt/minirack-management
cd /opt/minirack-management
```

#### Step 2: Clone and Setup

```bash
# Clone repository
git clone https://github.com/yourusername/minirack-ai-lab-managment.git .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -e .
```

#### Step 3: Configure Service

Create `/etc/systemd/system/minirack-management.service`:

```ini
[Unit]
Description=MiniRack AI Lab Management Portal
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=localadmin
WorkingDirectory=/opt/minirack-management
Environment="PATH=/opt/minirack-management/venv/bin"
Environment="DEBUG=false"
Environment="PORT=8080"
Environment="LOG_LEVEL=INFO"
ExecStart=/opt/minirack-management/venv/bin/python -m uvicorn \
    minirack_ai_lab_management.main:app \
    --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Step 4: Enable and Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable minirack-management
sudo systemctl start minirack-management

# Check status
sudo systemctl status minirack-management

# View logs
sudo journalctl -u minirack-management -f
```

---

### Method 4: Kubernetes (Optional)

For enterprise deployments.

#### Step 1: Create Namespace

```bash
kubectl create namespace minirack
kubectl label namespace minirack name=minirack
```

#### Step 2: Create ConfigMap

```bash
kubectl create configmap minirack-config \
  --from-literal=LAFORGE_HOST=192.168.1.161 \
  --from-literal=DATA_HOST=192.168.1.160 \
  --from-literal=RIKER_HOST=192.168.1.162 \
  -n minirack
```

#### Step 3: Deploy

```bash
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: minirack-management
  namespace: minirack
spec:
  replicas: 1
  selector:
    matchLabels:
      app: minirack-management
  template:
    metadata:
      labels:
        app: minirack-management
    spec:
      containers:
      - name: management
        image: minirack-management:latest
        ports:
        - containerPort: 8080
        envFrom:
        - configMapRef:
            name: minirack-config
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /api/v1/health/ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: minirack-management
  namespace: minirack
spec:
  selector:
    app: minirack-management
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 8080
  type: LoadBalancer
EOF
```

---

## Post-Deployment Configuration

### 1. Access the Portal

Navigate to: **http://192.168.1.161:8080**

### 2. Verify All Hosts

Dashboard should show:
- ✅ LaForge (ai-utility) - HEALTHY
- ✅ Data (ai-core) - HEALTHY
- ✅ Riker (ai-web) - HEALTHY

### 3. Configure Environment (Optional)

Edit `/etc/minirack-ai-lab/config.yaml`:
```yaml
ollama_model: llama3.2
ollama_host: 0.0.0.0:11434
```

### 4. Set Custom API Keys (Production Only)

Generate a secure key:
```bash
openssl rand -hex 32
```

Set in environment:
```bash
# Docker Compose
export API_KEY_SECRET="your-generated-key"
docker-compose up -d

# Bare metal
sudo systemctl set-environment API_KEY_SECRET="your-generated-key"
sudo systemctl restart minirack-management
```

---

## Security Hardening

### 1. Network Security

```bash
# Firewall - Allow only necessary access
sudo ufw allow from 192.168.1.0/24 to any port 8080

# Or for specific hosts only
sudo ufw allow from 192.168.1.160 to any port 8080
sudo ufw allow from 192.168.1.162 to any port 8080
```

### 2. HTTPS/TLS Setup

Using Nginx reverse proxy:

```bash
# Install Nginx
sudo apt-get install -y nginx certbot python3-certbot-nginx

# Create configuration
sudo tee /etc/nginx/sites-available/minirack <<EOF
server {
    listen 443 ssl http2;
    server_name minirack.local;
    
    ssl_certificate /etc/letsencrypt/live/minirack.local/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/minirack.local/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}

server {
    listen 80;
    server_name minirack.local;
    return 301 https://\$server_name\$request_uri;
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/minirack /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3. Regular Backups

```bash
# Backup configuration
cp -r /etc/minirack-ai-lab /backup/minirack-ai-lab-$(date +%Y%m%d)

# Or with Docker
docker-compose exec management-portal \
  tar czf /backup/portal-$(date +%Y%m%d).tar.gz /app
```

---

## Troubleshooting

### Portal Not Starting

**Symptom**: Container exits or fails to start

**Solution**:
```bash
# Check logs
docker logs minirack-management

# Verify configuration
cat .env

# Check port conflicts
sudo netstat -tuln | grep 8080

# Try rebuilding
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Services Not Showing

**Symptom**: Dashboard shows "offline" for all hosts

**Solution**:
```bash
# Verify host connectivity
ping 192.168.1.160  # Data
ping 192.168.1.162  # Riker

# Check Prometheus exporters
curl http://192.168.1.160:9100/metrics
curl http://192.168.1.162:9100/metrics

# Verify API connectivity
curl http://192.168.1.161:8080/api/v1/dashboard

# Check logs
docker logs minirack-management
```

### High Memory Usage

**Symptom**: Container using > 500MB RAM

**Solution**:
1. Increase health check interval in `.env`:
   ```
   HEALTH_CHECK_INTERVAL=60
   ```

2. Reduce metrics retention:
   ```
   METRICS_RETENTION_HOURS=12
   ```

3. Restart service:
   ```bash
   docker-compose restart
   ```

### API Rate Limiting

If experiencing 429 errors:
```bash
# Increase timeout in .env
API_REQUEST_TIMEOUT=10
```

---

## Maintenance

### Regular Tasks

**Weekly**:
- Check dashboard for alerts
- Review performance trends
- Verify all services are running

**Monthly**:
- Update container images: `docker-compose pull && docker-compose up -d`
- Review and rotate logs
- Check disk space

**Quarterly**:
- Security updates: `docker pull minirack-management:latest`
- Backup configuration: `cp -r /etc/minirack-ai-lab backup/`
- Test failover scenarios

### Logs Location

```bash
# Docker Compose
docker-compose logs -f

# Docker direct
docker logs minirack-management -f

# Bare metal
sudo journalctl -u minirack-management -f

# Application logs
docker exec minirack-management tail -f /var/log/application.log
```

### Backup Strategy

```bash
#!/bin/bash
# Daily backup script
BACKUP_DIR="/backups/minirack"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup configuration
tar czf $BACKUP_DIR/config_$DATE.tar.gz /etc/minirack-ai-lab

# Backup database (if using)
# docker-compose exec -T db mysqldump -u user -p database > $BACKUP_DIR/db_$DATE.sql

# Keep only last 30 days
find $BACKUP_DIR -mtime +30 -delete
```

---

## Uninstallation

### Docker Compose

```bash
# Stop and remove containers
docker-compose down

# Remove images
docker rmi minirack-management:latest

# Clean up volumes (if needed)
docker volume prune
```

### Bare Metal

```bash
# Stop service
sudo systemctl stop minirack-management
sudo systemctl disable minirack-management

# Remove service file
sudo rm /etc/systemd/system/minirack-management.service

# Remove application
sudo rm -rf /opt/minirack-management

# Clean up
sudo systemctl daemon-reload
```

### Ansible

```bash
# Create cleanup playbook or manually remove containers/services
docker-compose down
sudo rm -rf /opt/minirack-management
```

---

## Support

For deployment issues:
1. Check this guide thoroughly
2. Review troubleshooting section
3. Check application logs
4. Create an issue with log output

## Related Documentation

- [README.md](README.md) — Overview and features
- [Configuration Guide](docs/CONFIGURATION.md) — Detailed settings
- [API Reference](docs/API.md) — REST API endpoints
- [Security Guide](docs/SECURITY.md) — Security best practices
