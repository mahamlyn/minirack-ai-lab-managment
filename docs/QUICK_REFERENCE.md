# MiniRack Management Portal - Quick Reference

## 🚀 60-Second Deployment

```bash
# Local (testing)
docker-compose up -d
# Portal at http://localhost:8080

# LaForge (production)
ssh localadmin@192.168.1.161
cd minirack-ai-lab-managment
docker-compose up -d
# Portal at http://192.168.1.161:8080
```

## 📍 Portal URLs

| Resource | URL |
|----------|-----|
| Dashboard | http://192.168.1.161:8080 |
| API Docs | http://192.168.1.161:8080/api/docs |
| ReDoc | http://192.168.1.161:8080/api/redoc |
| OpenAPI JSON | http://192.168.1.161:8080/api/openapi.json |
| Health Check | http://192.168.1.161:8080/health |

## 🔗 Host IPs

| Host | IP | Role | Service |
|------|----|----|---------|
| Data | 192.168.1.160 | ai-core | Ollama (11434) |
| Riker | 192.168.1.162 | ai-web | OpenWebUI (8000) |
| LaForge | 192.168.1.161 | ai-utility | Portal (8080) |

## 📋 Dashboard Pages

| Page | Purpose |
|------|---------|
| Dashboard | Summary + host metrics + services |
| Hosts | Detailed per-host information |
| Services | Service status and health |
| Models | Available Ollama models |
| Logs | System and service logs |
| Config | Configuration management |

## 🔧 Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Check status
docker-compose ps

# Restart
docker-compose restart

# View specific logs
docker-compose logs -f management-portal
```

## 🛠️ Common Tasks

### View Dashboard
1. Open http://192.168.1.161:8080
2. Check host status (green = healthy)
3. Review service status
4. Check performance metrics

### Change Ollama Model
1. Go to Configuration page
2. Select new model from dropdown
3. Click "Save Configuration"
4. Wait for deployment

### View System Logs
1. Go to Logs page
2. Select host or service
3. Scroll through logs
4. Use Ctrl+F to search

### Monitor Performance
1. Dashboard shows real-time metrics
2. Check CPU/Memory/Disk usage
3. View service status
4. Review alerts if any

## 📡 API Quick Examples

### Get Dashboard
```bash
curl http://192.168.1.161:8080/api/v1/dashboard/ | jq
```

### Get Host Status
```bash
curl http://192.168.1.161:8080/api/v1/dashboard/hosts | jq
```

### Change Ollama Model
```bash
curl -X POST http://192.168.1.161:8080/api/v1/config/update \
  -H "Content-Type: application/json" \
  -d '{
    "service": "ollama",
    "setting": "model",
    "value": "mistral"
  }'
```

### Get Ollama Models
```bash
curl http://192.168.1.161:8080/api/v1/models/ | jq
```

### Get Logs
```bash
curl "http://192.168.1.161:8080/api/v1/logs/system/laforge?lines=20" | jq
```

## 🐛 Troubleshooting

### Portal Not Starting
```bash
# Check logs
docker-compose logs -f management-portal

# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Hosts Show Offline
```bash
# Verify connectivity
ping 192.168.1.160  # Data
ping 192.168.1.162  # Riker

# Check exporters
curl http://192.168.1.160:9100/metrics
curl http://192.168.1.162:9100/metrics
```

### High Memory Usage
```bash
# Edit docker-compose.yml
# Reduce HEALTH_CHECK_INTERVAL
# Reduce METRICS_RETENTION_HOURS

docker-compose restart
```

### API Rate Limiting
```bash
# Edit .env or docker-compose.yml
API_REQUEST_TIMEOUT=10
docker-compose restart
```

## 📚 Documentation

| Doc | Purpose |
|-----|---------|
| README.md | Features and overview |
| DEPLOYMENT.md | Installation guide |
| API.md | REST API reference |
| ARCHITECTURE.md | System design |
| COMPLETION_SUMMARY.md | Project summary |

## 🔐 Security

### Change Default Secret
```bash
# Generate new secret
openssl rand -hex 32

# Set in .env or compose
API_KEY_SECRET=<generated-secret>

# Restart
docker-compose restart
```

### Enable HTTPS
```bash
# Use Nginx reverse proxy or Let's Encrypt
# See DEPLOYMENT.md for setup
```

## 📊 Configuration Options

**Environment Variables**:
- `DEBUG=false` — Debug mode
- `LOG_LEVEL=INFO` — Logging level
- `PORT=8080` — Server port
- `HEALTH_CHECK_INTERVAL=30` — Check interval (seconds)
- `METRICS_RETENTION_HOURS=24` — Data retention

## 🎯 Performance Tuning

### For Better Performance
```bash
# In .env or docker-compose.yml
HEALTH_CHECK_INTERVAL=60    # Less frequent checks
METRICS_RETENTION_HOURS=12  # Keep fewer metrics
```

### For Better Real-Time
```bash
HEALTH_CHECK_INTERVAL=10    # More frequent checks
METRICS_RETENTION_HOURS=24  # Keep more data
```

## 🔄 Maintenance

### Weekly
- Monitor dashboard for alerts
- Check performance trends

### Monthly
- Update images: `docker-compose pull && docker-compose up -d`
- Review logs

### Quarterly
- Security audit
- Backup configuration

## 🚨 Critical Commands

```bash
# Emergency stop
docker-compose down

# Check health
curl http://192.168.1.161:8080/health

# View all logs
docker-compose logs

# Update and restart
docker-compose pull
docker-compose up -d

# Full rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🎓 Learning Path

1. **Read**: README.md (5 min)
2. **Deploy**: Follow DEPLOYMENT.md (5 min)
3. **Explore**: Visit dashboard (5 min)
4. **Learn API**: Check API.md (10 min)
5. **Deep Dive**: Read ARCHITECTURE.md (15 min)

## 📞 Getting Help

1. Check DEPLOYMENT.md troubleshooting section
2. Review application logs: `docker-compose logs`
3. Visit API docs: http://192.168.1.161:8080/api/docs
4. Create GitHub issue with logs

## ✅ Checklist for New Users

- [ ] Read README.md
- [ ] Deploy to local Docker
- [ ] Access dashboard at http://localhost:8080
- [ ] Verify all 3 hosts show (or mock data)
- [ ] Try API endpoints
- [ ] Read DEPLOYMENT.md
- [ ] Deploy to LaForge
- [ ] Access at http://192.168.1.161:8080
- [ ] Verify real hosts and services
- [ ] Configure environment
- [ ] Save to bookmarks
- [ ] Share with team

## 🎉 You're Ready!

The portal is configured and ready to use. Start by visiting:

**http://192.168.1.161:8080**

Enjoy monitoring your MiniRack AI Lab! 🚀
