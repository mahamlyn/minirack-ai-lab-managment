# MiniRack Management Portal - API Reference

## Base URL

```
http://192.168.1.161:8080/api/v1
```

## Health Checks

### Get Health Status

**Endpoint**: `GET /health/`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "cpu_percent": 25.3,
  "memory_percent": 45.2,
  "disk_percent": 60.1
}
```

### Get System Metrics

**Endpoint**: `GET /health/metrics`

**Response**:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "cpu_percent": 25.3,
  "memory_percent": 45.2,
  "disk_percent": 60.1,
  "network_io_bytes": 1073741824,
  "network_errors": 0
}
```

### Liveness Probe

**Endpoint**: `GET /health/live`

**Response**: `{"status": "alive"}`

### Readiness Probe

**Endpoint**: `GET /health/ready`

**Response**: `{"status": "ready"}`

---

## Dashboard

### Get Complete Dashboard

**Endpoint**: `GET /dashboard/`

**Response**:
```json
{
  "hosts": [
    {
      "name": "LaForge",
      "ip_address": "192.168.1.161",
      "status": "healthy",
      "role": "ai-utility",
      "uptime_seconds": 1209600,
      "cpu_percent": 25.3,
      "memory_percent": 45.2,
      "disk_percent": 60.1,
      "temperature_celsius": 42.5,
      "last_check": "2024-01-15T10:30:00Z"
    }
  ],
  "services": [
    {
      "name": "ollama",
      "host": "192.168.1.160",
      "status": "running",
      "process_id": 1234,
      "memory_mb": 2048.5,
      "cpu_percent": 15.0,
      "uptime_seconds": 86400,
      "last_check": "2024-01-15T10:30:00Z"
    }
  ],
  "models": [],
  "recent_metrics": [],
  "alerts": []
}
```

### Get All Hosts

**Endpoint**: `GET /dashboard/hosts`

**Response**: Array of host information

### Get All Services

**Endpoint**: `GET /dashboard/services`

**Response**: Array of service information

---

## Configuration

### Get Current Configuration

**Endpoint**: `GET /config/`

**Response**:
```json
{
  "ollama_model": "llama3.2",
  "ollama_host": "0.0.0.0:11434",
  "docker_admin_user": "docker-admin",
  "environment": "production"
}
```

### Get Deployment Info

**Endpoint**: `GET /config/deployment`

**Response**:
```json
{
  "environment": "production",
  "version": "1.0.0",
  "deployed_at": "2024-01-10T15:30:00Z",
  "hosts": {
    "ai_core": "192.168.1.160",
    "ai_web": "192.168.1.162",
    "ai_utility": "192.168.1.161"
  }
}
```

### Update Configuration

**Endpoint**: `POST /config/update`

**Request Body**:
```json
{
  "service": "ollama",
  "setting": "model",
  "value": "mistral",
  "reason": "Better performance for real-time applications"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Updated ollama.model"
}
```

### Validate Configuration

**Endpoint**: `POST /config/validate`

**Response**:
```json
{
  "valid": true,
  "issues": [],
  "config": {
    "ollama_model": "llama3.2",
    "ollama_host": "0.0.0.0:11434"
  }
}
```

### Get Ollama Configuration

**Endpoint**: `GET /config/ollama`

**Response**:
```json
{
  "model": "llama3.2",
  "host": "0.0.0.0:11434"
}
```

### Set Ollama Model

**Endpoint**: `POST /config/ollama/model`

**Request Body**:
```json
{
  "model": "mistral"
}
```

**Response**:
```json
{
  "success": true,
  "model": "mistral"
}
```

---

## AI Models

### Get Available Models

**Endpoint**: `GET /models/`

**Response**:
```json
[
  {
    "name": "llama3.2",
    "size": 4294967296,
    "digest": "sha256:...",
    "modified_at": "2024-01-15T10:30:00Z"
  },
  {
    "name": "mistral",
    "size": 3758096384,
    "digest": "sha256:...",
    "modified_at": "2024-01-15T10:30:00Z"
  }
]
```

### Get Model Info

**Endpoint**: `GET /models/{model_name}`

**Example**: `GET /models/llama3.2`

**Response**:
```json
{
  "name": "llama3.2",
  "size": 4294967296,
  "digest": "sha256:...",
  "modified_at": "2024-01-15T10:30:00Z",
  "details": {
    "parent_model": "llama3",
    "format": "gguf",
    "parameters": "8.0B"
  }
}
```

### Pull New Model

**Endpoint**: `POST /models/{model_name}/pull`

**Example**: `POST /models/neural-chat/pull`

**Response**:
```json
{
  "status": "pulling",
  "model": "neural-chat",
  "message": "Model pull initiated. Check progress on the dashboard."
}
```

### Remove Model

**Endpoint**: `POST /models/{model_name}/remove`

**Example**: `POST /models/llama2/remove`

**Response**:
```json
{
  "status": "removing",
  "model": "llama2",
  "message": "Model removal initiated."
}
```

---

## Logs

### Get System Logs

**Endpoint**: `GET /logs/system/{host}`

**Parameters**:
- `host` - Host name: `laforge`, `data`, or `riker`
- `lines` - Number of log lines (default: 50)

**Example**: `GET /logs/system/laforge?lines=50`

**Response**:
```json
{
  "host": "laforge",
  "ip": "192.168.1.161",
  "logs": [
    "2024-01-15 10:30:00 [INFO] System started",
    "2024-01-15 10:30:01 [INFO] Services initialized",
    "..."
  ],
  "line_count": 50
}
```

### Get Service Logs

**Endpoint**: `GET /logs/service/{service}`

**Parameters**:
- `service` - Service name: `ollama`, `openweb-ui`, `hermes`
- `lines` - Number of log lines (default: 50)

**Example**: `GET /logs/service/ollama?lines=50`

**Response**:
```json
{
  "service": "ollama",
  "host_ip": "192.168.1.160",
  "logs": [
    "2024-01-15 10:30:00 Ollama server listening on 0.0.0.0:11434",
    "2024-01-15 10:30:01 Loaded model llama3.2",
    "..."
  ],
  "line_count": 50
}
```

### Get All Logs

**Endpoint**: `GET /logs/`

**Parameters**:
- `service` - Filter by service (optional)
- `lines` - Number of log lines (default: 20)

**Example**: `GET /logs/?service=ollama&lines=20`

**Response**: Array of log entries from all services

---

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Failed to update configuration"
}
```

### 404 Not Found

```json
{
  "detail": "Unknown host: invalid-host"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error. Check logs for details."
}
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created |
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error - Server error |
| 503 | Service Unavailable - Service down |

---

## Authentication (Future)

Currently, the API has no authentication. For production:

1. Enable API keys via environment variable:
   ```
   API_AUTH_ENABLED=true
   API_KEYS=["your-secret-key"]
   ```

2. Include API key in requests:
   ```
   curl -H "X-API-Key: your-secret-key" \
     http://192.168.1.161:8080/api/v1/dashboard
   ```

---

## Rate Limiting

No rate limiting is currently implemented. For production, consider:

1. Configure via environment:
   ```
   RATE_LIMIT_ENABLED=true
   RATE_LIMIT_REQUESTS=100
   RATE_LIMIT_WINDOW=60
   ```

2. Use Nginx rate limiting as reverse proxy

---

## Examples

### Python

```python
import requests
import json

BASE_URL = "http://192.168.1.161:8080/api/v1"

# Get dashboard
response = requests.get(f"{BASE_URL}/dashboard/")
dashboard = response.json()

# Get specific host
hosts = dashboard["hosts"]
for host in hosts:
    print(f"{host['name']}: {host['status']}")

# Update config
config_update = {
    "service": "ollama",
    "setting": "model",
    "value": "mistral"
}
response = requests.post(f"{BASE_URL}/config/update", json=config_update)
print(response.json())
```

### cURL

```bash
# Get dashboard
curl http://192.168.1.161:8080/api/v1/dashboard/ | jq

# Get specific service logs
curl "http://192.168.1.161:8080/api/v1/logs/service/ollama?lines=20" | jq

# Update configuration
curl -X POST http://192.168.1.161:8080/api/v1/config/update \
  -H "Content-Type: application/json" \
  -d '{"service":"ollama","setting":"model","value":"mistral"}'
```

### JavaScript/Fetch

```javascript
const BASE_URL = "http://192.168.1.161:8080/api/v1";

// Get dashboard
fetch(`${BASE_URL}/dashboard/`)
  .then(r => r.json())
  .then(data => console.log(data));

// Update configuration
fetch(`${BASE_URL}/config/update`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    service: "ollama",
    setting: "model",
    value: "mistral"
  })
})
.then(r => r.json())
.then(data => console.log(data));
```

---

## Documentation

- **OpenAPI/Swagger**: http://192.168.1.161:8080/api/docs
- **ReDoc**: http://192.168.1.161:8080/api/redoc
- **OpenAPI JSON**: http://192.168.1.161:8080/api/openapi.json
