# IP Address & Network Configuration Guide

## Overview

The MiniRack Management Portal is **fully network-agnostic** and supports deployment on any network with any IP addressing scheme. This guide explains how to configure the application for your specific network environment.

## Key Concept: No Hardcoded IPs

✅ **All network addresses are configurable via environment variables**
- No hardcoded IP addresses in the application code
- Support for any subnet (192.168.x.x, 10.x.x.x, 172.16.x.x, etc.)
- Support for DNS hostnames instead of IP addresses
- Support for different port mappings
- Support for different SSH credentials per host

## Configuration Methods

### Method 1: Environment Variables (Recommended)

Set environment variables before starting the application:

```bash
export LAFORGE_HOST=192.168.1.161
export DATA_HOST=192.168.1.160
export RIKER_HOST=192.168.1.162
export OLLAMA_API_HOST=http://192.168.1.160:11434
export OPENWEB_UI_URL=http://192.168.1.162:8000

python -m uvicorn minirack_ai_lab_management.main:app
```

### Method 2: .env File

Create a `.env` file in the project root:

```bash
cp .env.example .env
# Edit .env with your network details
docker-compose up -d
```

### Method 3: Docker Compose Override

Modify `docker-compose.yml` environment section:

```yaml
services:
  management-portal:
    environment:
      LAFORGE_HOST: "10.0.0.161"
      DATA_HOST: "10.0.0.160"
      RIKER_HOST: "10.0.0.162"
      OLLAMA_API_HOST: "http://10.0.0.160:11434"
      OPENWEB_UI_URL: "http://10.0.0.162:8000"
```

### Method 4: Docker Compose .env File

Create `.env` file at project root:

```env
LAFORGE_HOST=192.168.1.161
DATA_HOST=192.168.1.160
RIKER_HOST=192.168.1.162
OLLAMA_API_HOST=http://192.168.1.160:11434
OPENWEB_UI_URL=http://192.168.1.162:8000
```

Then run:
```bash
docker-compose up -d
```

Docker Compose will automatically load the `.env` file.

### Method 5: Kubernetes ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: minirack-config
data:
  LAFORGE_HOST: "192.168.1.161"
  DATA_HOST: "192.168.1.160"
  RIKER_HOST: "192.168.1.162"
  OLLAMA_API_HOST: "http://192.168.1.160:11434"
  OPENWEB_UI_URL: "http://192.168.1.162:8000"
---
apiVersion: v1
kind: Pod
metadata:
  name: minirack-management
spec:
  containers:
  - name: management-portal
    image: minirack-ai-lab-management:latest
    envFrom:
    - configMapRef:
        name: minirack-config
```

## Configurable Variables

### Core Host Configuration

| Variable | Default | Purpose | Example |
|----------|---------|---------|---------|
| `LAFORGE_HOST` | `192.168.1.161` | Management/utility host IP | `10.0.0.161` or `laforge.local` |
| `DATA_HOST` | `192.168.1.160` | AI-core (Ollama) host IP | `10.0.0.160` or `data.local` |
| `RIKER_HOST` | `192.168.1.162` | AI-web (Open WebUI) host IP | `10.0.0.162` or `riker.local` |

### API Endpoints

| Variable | Default | Purpose | Format |
|----------|---------|---------|--------|
| `OLLAMA_API_HOST` | `http://192.168.1.160:11434` | Ollama API endpoint | `http://host:port` |
| `OPENWEB_UI_URL` | `http://192.168.1.162:8000` | Open WebUI endpoint | `http://host:port` |

### SSH Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `LAFORGE_SSH_USER` | `localadmin` | SSH username for LaForge |
| `LAFORGE_SSH_PORT` | `22` | SSH port for LaForge |

### Application Server

| Variable | Default | Purpose |
|----------|---------|---------|
| `HOST` | `0.0.0.0` | Bind address (all interfaces) |
| `PORT` | `8080` | Application port |

## Common Network Scenarios

### Scenario 1: Default MiniRack Lab (192.168.1.x)

```env
# No configuration needed, use defaults
LAFORGE_HOST=192.168.1.161
DATA_HOST=192.168.1.160
RIKER_HOST=192.168.1.162
OLLAMA_API_HOST=http://192.168.1.160:11434
OPENWEB_UI_URL=http://192.168.1.162:8000
```

### Scenario 2: Private Network (10.0.0.x)

```env
LAFORGE_HOST=10.0.0.161
DATA_HOST=10.0.0.160
RIKER_HOST=10.0.0.162
OLLAMA_API_HOST=http://10.0.0.160:11434
OPENWEB_UI_URL=http://10.0.0.162:8000
```

### Scenario 3: Using DNS Hostnames

```env
LAFORGE_HOST=laforge.example.com
DATA_HOST=data.example.com
RIKER_HOST=riker.example.com
OLLAMA_API_HOST=http://data.example.com:11434
OPENWEB_UI_URL=http://riker.example.com:8000
```

This approach allows you to change IPs without redeploying the application - just update DNS records.

### Scenario 4: Corporate Network (172.16.x.x)

```env
LAFORGE_HOST=172.16.100.161
DATA_HOST=172.16.100.160
RIKER_HOST=172.16.100.162
OLLAMA_API_HOST=http://172.16.100.160:11434
OPENWEB_UI_URL=http://172.16.100.162:8000
```

### Scenario 5: Mixed Hostnames and IPs

```env
LAFORGE_HOST=laforge.local
DATA_HOST=192.168.1.160          # Can mix IPs and hostnames
RIKER_HOST=riker.local
OLLAMA_API_HOST=http://192.168.1.160:11434
OPENWEB_UI_URL=http://riker.local:8000
```

### Scenario 6: Non-Standard Ports

```env
# If services run on different ports
OLLAMA_API_HOST=http://192.168.1.160:11434
OPENWEB_UI_URL=http://192.168.1.162:8080    # Custom port instead of 8000
```

### Scenario 7: Behind NAT / Port Forwarding

```env
# External addresses for remote access
LAFORGE_HOST=192.168.1.161          # Internal IP
# Access from outside:
# http://your-public-ip:8080 (port forwarded to 192.168.1.161:8080)

# For services behind NAT:
OLLAMA_API_HOST=http://192.168.1.160:11434
# Access from outside via proxy or VPN
```

### Scenario 8: Kubernetes ClusterIP Services

```env
# When running in Kubernetes using service discovery
LAFORGE_HOST=minirack-management  # Service name, resolved by K8s DNS
DATA_HOST=minirack-data           # K8s DNS resolves to ClusterIP
RIKER_HOST=minirack-web
OLLAMA_API_HOST=http://minirack-data:11434
OPENWEB_UI_URL=http://minirack-web:8000
```

## Validation & Troubleshooting

### Verify Configuration at Startup

The application logs the configuration on startup:

```bash
docker-compose up -d
docker-compose logs

# Look for:
# INFO: Configuration loaded
# - LAFORGE_HOST: 192.168.1.161
# - DATA_HOST: 192.168.1.160
# - RIKER_HOST: 192.168.1.162
```

### Test Connectivity

After deployment, test connectivity to each host:

```bash
# Test LaForge
curl http://192.168.1.161:8080/health

# Test Data host (from your machine)
curl http://192.168.1.160:11434/api/tags

# Test Riker
curl http://192.168.1.162:8000
```

### Check Configuration via API

```bash
# Get current deployment configuration
curl http://192.168.1.161:8080/api/v1/config/deployment

# Response will show:
{
  "environment": "production",
  "version": "1.0.0",
  "deployed_at": "2024-01-15T10:30:00Z",
  "hosts": {
    "ai_core": "192.168.1.160",
    "ai_web": "192.168.1.162",
    "ai_utility": "192.168.1.161"
  }
}
```

### Common Issues

**Issue: Connection Refused**
```
Error: Unable to connect to DATA_HOST
```
Solution: Verify IP address is correct and host is reachable
```bash
ping 192.168.1.160
ssh -v localadmin@192.168.1.160
```

**Issue: Hostname Resolution Failed**
```
Error: Name resolution failed
```
Solution: Verify hostname is resolvable
```bash
nslookup data.local
# or
dig data.example.com
```

**Issue: API Endpoint Unreachable**
```
Error: Unable to reach OLLAMA_API_HOST
```
Solution: Verify API host and port are correct
```bash
curl -v http://192.168.1.160:11434/api/tags
```

## Changing IP Addresses After Deployment

You can change IP addresses without code changes:

### For Docker Compose

```bash
# 1. Stop the application
docker-compose down

# 2. Update .env file
nano .env
# Edit LAFORGE_HOST, DATA_HOST, RIKER_HOST, etc.

# 3. Restart
docker-compose up -d
```

### For Kubernetes

```bash
# 1. Update ConfigMap
kubectl edit configmap minirack-config
# Update the IP addresses

# 2. Restart pods to reload config
kubectl rollout restart deployment minirack-management
```

### For Bare Metal / systemd

```bash
# 1. Update .env or /etc/minirack-ai-lab/minirack.env
sudo nano /etc/minirack-ai-lab/minirack.env

# 2. Restart service
sudo systemctl restart minirack-management
```

## Network Diagram Examples

### Standard Setup (Default)
```
┌─────────────────────────────────────────────┐
│          192.168.1.0/24 Network             │
├─────────────────────────────────────────────┤
│                                             │
│  Data (ai-core)      Riker (ai-web)   │
│  192.168.1.160       192.168.1.162    │
│  Ollama (11434)      OpenWebUI (8000) │
│           │                 │          │
│           └─────────┬───────┘          │
│                     │                  │
│              LaForge (ai-utility)      │
│              192.168.1.161             │
│              Portal (8080)             │
│                                        │
└─────────────────────────────────────────────┘
```

### Alternative Setup (Different Subnet)
```
┌─────────────────────────────────────────────┐
│          10.0.0.0/24 Network                │
├─────────────────────────────────────────────┤
│                                             │
│  Data (ai-core)      Riker (ai-web)   │
│  10.0.0.160          10.0.0.162       │
│  Ollama (11434)      OpenWebUI (8000) │
│           │                 │          │
│           └─────────┬───────┘          │
│                     │                  │
│              LaForge (ai-utility)      │
│              10.0.0.161                │
│              Portal (8080)             │
│                                        │
└─────────────────────────────────────────────┘
```

## Best Practices

1. **Use DNS Hostnames** when possible for flexibility
   ```env
   LAFORGE_HOST=laforge.local
   DATA_HOST=data.local
   RIKER_HOST=riker.local
   ```

2. **Document Your Network** in a configuration file
   ```bash
   # Create a network-config.md file
   # or comment in docker-compose.yml
   ```

3. **Use Environment Files** for each environment
   ```
   .env.local          # Local development
   .env.staging        # Staging deployment
   .env.production     # Production deployment
   ```

4. **Validate Connectivity** after deployment
   ```bash
   ./scripts/validate-network.sh
   ```

5. **Keep Defaults** when possible for portability
   - Stick to standard ports (8080, 11434, 8000)
   - Use consistent IP schemes within your organization

6. **Monitor Connectivity** with health checks
   ```bash
   curl http://192.168.1.161:8080/health
   curl http://192.168.1.161:8080/api/v1/health/
   ```

## Related Documentation

- [Deployment Guide](./DEPLOYMENT.md) - Deployment methods
- [Architecture Guide](./ARCHITECTURE.md) - System architecture
- [Quick Reference](./QUICK_REFERENCE.md) - Quick commands
- [.env.example](../.env.example) - Configuration template
