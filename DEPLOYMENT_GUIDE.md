# Deployment Guide

Complete guide for deploying Socratic RAG in different environments.

## Pre-Deployment Checklist

- [ ] Code tested locally (110+ tests passing)
- [ ] Type hints verified (MyPy strict)
- [ ] Performance benchmarked (meets SLA)
- [ ] Security reviewed (no secrets in code)
- [ ] Documentation complete
- [ ] Version bumped in pyproject.toml
- [ ] CHANGELOG.md updated
- [ ] All dependencies specified

---

## Local Development Deployment

### Setup

```bash
# Clone repository
git clone https://github.com/Nireus79/Socratic-rag.git
cd Socratic-rag

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v --cov=socratic_rag
```

### Running Locally

```python
from socratic_rag import RAGClient

client = RAGClient()
client.add_document("Python is great", "python.txt")
results = client.search("Python")
print(results)
```

---

## Docker Deployment

### Single Container

```bash
# Build image
docker build -t socratic-rag:latest .

# Run container
docker run -p 8000:8000 socratic-rag:latest

# Or with environment variables
docker run -p 8000:8000 \
  -e VECTOR_STORE=chromadb \
  -e EMBEDDING_CACHE=true \
  socratic-rag:latest

# View logs
docker logs <container_id>

# Stop container
docker stop <container_id>
```

### Docker Compose

```bash
# Start services
docker-compose up -d

# View status
docker-compose ps

# View logs
docker-compose logs -f rag-api

# Stop services
docker-compose down

# Full cleanup (including volumes)
docker-compose down -v
```

### With Qdrant

```bash
# Start with Qdrant enabled
docker-compose --profile with-qdrant up -d

# Configure client to use Qdrant
# Set VECTOR_STORE=qdrant environment variable
```

---

## Production Deployment

### Requirements

- **Python**: 3.8+ (3.11+ recommended)
- **Memory**: Minimum 2GB, recommended 8GB+
- **Disk**: Space for vector store (10-20% of data size)
- **Network**: Stable connection to vector store
- **Security**: HTTPS, authentication, encryption

### Environment Variables

```bash
# Vector Store
VECTOR_STORE=chromadb           # chromadb, qdrant, faiss
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Embeddings
EMBEDDING_CACHE=true
EMBEDDING_CACHE_TTL=3600

# Performance
CHUNK_SIZE=512
CHUNK_OVERLAP=50
TOP_K=5

# Logging
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1

# Security
SECRET_KEY=your-secret-key
DEBUG=false
```

### Systemd Service

```ini
# /etc/systemd/system/socratic-rag.service
[Unit]
Description=Socratic RAG API Service
After=network.target

[Service]
Type=notify
User=rag-user
WorkingDirectory=/opt/socratic-rag
Environment="PATH=/opt/socratic-rag/venv/bin"
Environment="VECTOR_STORE=qdrant"
Environment="QDRANT_HOST=localhost"

ExecStart=/opt/socratic-rag/venv/bin/python -m uvicorn \
  examples.06_rest_api:app \
  --host 0.0.0.0 \
  --port 8000

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Usage**:
```bash
# Enable and start service
sudo systemctl enable socratic-rag
sudo systemctl start socratic-rag

# Check status
sudo systemctl status socratic-rag

# View logs
sudo journalctl -u socratic-rag -f
```

### NGINX Reverse Proxy

```nginx
# /etc/nginx/sites-available/socratic-rag
upstream socratic_rag {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name rag.example.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name rag.example.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/rag.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/rag.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Gzip compression
    gzip on;
    gzip_types text/plain application/json;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    location / {
        limit_req zone=api_limit burst=20 nodelay;

        proxy_pass http://socratic_rag;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://socratic_rag/health;
        access_log off;
    }
}
```

---

## Kubernetes Deployment

### Prerequisites

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Install helm (optional)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### Dockerfile (Multi-stage)

See `Dockerfile` in repository (already optimized).

### Kubernetes Manifests

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: socratic-rag
  labels:
    app: socratic-rag
spec:
  replicas: 3
  selector:
    matchLabels:
      app: socratic-rag
  template:
    metadata:
      labels:
        app: socratic-rag
    spec:
      containers:
      - name: rag-api
        image: socratic-rag:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
        env:
        - name: VECTOR_STORE
          value: "qdrant"
        - name: QDRANT_HOST
          value: "qdrant-service"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: socratic-rag-service
spec:
  selector:
    app: socratic-rag
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer

---
# qdrant-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: qdrant
spec:
  serviceName: qdrant-service
  replicas: 3
  selector:
    matchLabels:
      app: qdrant
  template:
    metadata:
      labels:
        app: qdrant
    spec:
      containers:
      - name: qdrant
        image: qdrant/qdrant:latest
        ports:
        - containerPort: 6333
        volumeMounts:
        - name: qdrant-storage
          mountPath: /qdrant/storage
  volumeClaimTemplates:
  - metadata:
      name: qdrant-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 10Gi

---
# service.yaml for Qdrant
apiVersion: v1
kind: Service
metadata:
  name: qdrant-service
spec:
  clusterIP: None
  selector:
    app: qdrant
  ports:
  - port: 6333
    targetPort: 6333
```

**Deploy**:
```bash
# Create namespace
kubectl create namespace socratic-rag

# Apply manifests
kubectl apply -f deployment.yaml -n socratic-rag
kubectl apply -f service.yaml -n socratic-rag
kubectl apply -f qdrant-statefulset.yaml -n socratic-rag

# Check status
kubectl get pods -n socratic-rag
kubectl get services -n socratic-rag

# View logs
kubectl logs -f deployment/socratic-rag -n socratic-rag

# Scale replicas
kubectl scale deployment socratic-rag --replicas=5 -n socratic-rag

# Auto-scaling
kubectl autoscale deployment socratic-rag --min=2 --max=10 -n socratic-rag
```

---

## AWS Deployment

### EC2 Deployment

```bash
#!/bin/bash
# User data script for EC2 instance

#!/bin/bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Clone repository
cd /opt
sudo git clone https://github.com/Nireus79/Socratic-rag.git
cd Socratic-rag

# Setup virtual environment
sudo python3.11 -m venv venv
source venv/bin/activate

# Install package
pip install -e ".[all]"

# Create systemd service
sudo tee /etc/systemd/system/socratic-rag.service > /dev/null <<EOF
[Unit]
Description=Socratic RAG
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/Socratic-rag
Environment="PATH=/opt/Socratic-rag/venv/bin"
ExecStart=/opt/Socratic-rag/venv/bin/python -m uvicorn \
  examples.06_rest_api:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable socratic-rag
sudo systemctl start socratic-rag
```

### ECS Deployment

```json
{
  "family": "socratic-rag",
  "containerDefinitions": [
    {
      "name": "rag-api",
      "image": "account.dkr.ecr.region.amazonaws.com/socratic-rag:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "VECTOR_STORE",
          "value": "qdrant"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/socratic-rag",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ],
  "requiresCompatibilities": ["FARGATE"],
  "networkMode": "awsvpc",
  "cpu": "512",
  "memory": "1024"
}
```

---

## GCP Deployment

### Cloud Run

```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT_ID/socratic-rag

# Deploy to Cloud Run
gcloud run deploy socratic-rag \
  --image gcr.io/PROJECT_ID/socratic-rag \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --set-env-vars VECTOR_STORE=qdrant
```

### Compute Engine

```bash
# Create instance
gcloud compute instances create socratic-rag \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --machine-type=n1-standard-2 \
  --zone=us-central1-a \
  --metadata-from-file startup-script=startup.sh

# SSH into instance
gcloud compute ssh socratic-rag --zone=us-central1-a
```

---

## Monitoring & Logging

### Health Checks

```python
from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0"
    }

@app.get("/ready")
async def readiness():
    try:
        # Check vector store connection
        client.search("test")
        return {"ready": True}
    except Exception as e:
        return {"ready": False, "error": str(e)}
```

### Logging Configuration

```python
import logging
from logging.handlers import RotatingFileHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# File handler
file_handler = RotatingFileHandler(
    'logs/socratic-rag.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

logger = logging.getLogger()
logger.addHandler(file_handler)
```

### Metrics Collection

```python
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
searches = Counter('socratic_rag_searches_total', 'Total searches')
search_latency = Histogram('socratic_rag_search_latency_seconds', 'Search latency')

@app.get("/search")
async def search(query: str):
    with search_latency.time():
        results = client.search(query)
    searches.inc()
    return results

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

---

## Backup & Disaster Recovery

### Backup Strategy

```bash
# Daily backup of vector store
0 2 * * * docker exec socratic-rag-chromadb \
  tar czf /backup/chroma_$(date +\%Y\%m\%d).tar.gz \
  /chroma/chroma

# Upload to S3
0 3 * * * aws s3 cp /backup/ s3://backups/socratic-rag/ --recursive
```

### Recovery Procedure

```bash
# 1. Restore backup
aws s3 cp s3://backups/socratic-rag/chroma_20240310.tar.gz .
tar xzf chroma_20240310.tar.gz

# 2. Restart services
docker-compose restart rag-api

# 3. Verify health
curl http://localhost:8000/health
```

---

## Security Checklist

- [ ] Secrets stored in environment variables
- [ ] HTTPS/TLS enabled
- [ ] Authentication enabled
- [ ] Rate limiting configured
- [ ] Input validation in place
- [ ] Dependencies scanned for vulnerabilities
- [ ] Logs sanitized (no secrets)
- [ ] Regular backups tested
- [ ] Disaster recovery plan documented
- [ ] Security audit completed

---

## Performance Tuning

### Under Load

1. **Increase replicas**: `kubectl scale deployment socratic-rag --replicas=5`
2. **Enable caching**: Set `EMBEDDING_CACHE=true`
3. **Use FAISS**: Faster searches for large datasets
4. **Load balancing**: Distribute across multiple instances
5. **Connection pooling**: Reuse connections to vector store

### Memory Optimization

1. **Reduce chunk size**: `CHUNK_SIZE=256` (default: 512)
2. **Disable cache**: `EMBEDDING_CACHE=false`
3. **External vector store**: Use Qdrant instead of ChromaDB
4. **Instance sizing**: Right-size based on workload

---

## Troubleshooting Deployment

### Service won't start

```bash
# Check logs
docker logs socratic-rag

# Verify port is available
lsof -i :8000

# Check environment variables
env | grep SOCRATIC
```

### High memory usage

```bash
# Monitor memory
docker stats

# Reduce chunk size
export CHUNK_SIZE=256

# Disable cache
export EMBEDDING_CACHE=false
```

### Slow searches

```bash
# Check vector store performance
curl http://qdrant:6333/health

# Use FAISS for faster search
export VECTOR_STORE=faiss

# Monitor query latency
curl http://localhost:8000/metrics
```

---

## Support & Resources

- **Documentation**: [README.md](README.md), [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/Nireus79/Socratic-rag/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Nireus79/Socratic-rag/discussions)

---

**Last Updated**: March 10, 2024
**Version**: 0.1.0
