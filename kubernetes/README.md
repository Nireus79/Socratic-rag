# Kubernetes Deployment

Complete Kubernetes manifests for deploying Socratic RAG in production.

## Files

- **deployment.yaml**: RAG API deployment with auto-scaling, health checks, and networking policies
- **qdrant-statefulset.yaml**: Qdrant vector database cluster with persistent storage
- **README.md**: This file

## Prerequisites

- Kubernetes cluster (1.20+)
- kubectl configured
- Docker image built and pushed: `socratic-rag:latest`
- Persistent volume provisioner (for Qdrant data)

## Quick Start

### 1. Create Namespace

```bash
kubectl create namespace socratic-rag
```

### 2. Build and Push Image

```bash
# Build Docker image
docker build -t socratic-rag:latest .

# Push to registry (replace with your registry)
docker tag socratic-rag:latest your-registry/socratic-rag:latest
docker push your-registry/socratic-rag:latest

# Update image in deployment.yaml if using different registry
kubectl patch deployment socratic-rag -n socratic-rag \
  -p '{"spec":{"template":{"spec":{"containers":[{"name":"rag-api","image":"your-registry/socratic-rag:latest"}]}}}}'
```

### 3. Deploy Qdrant

```bash
kubectl apply -f kubernetes/qdrant-statefulset.yaml -n socratic-rag

# Wait for Qdrant to be ready
kubectl wait --for=condition=ready pod -l app=qdrant -n socratic-rag --timeout=300s
```

### 4. Deploy RAG API

```bash
kubectl apply -f kubernetes/deployment.yaml -n socratic-rag

# Wait for deployment to be ready
kubectl rollout status deployment/socratic-rag -n socratic-rag
```

### 5. Verify Deployment

```bash
# Check pods
kubectl get pods -n socratic-rag

# Check services
kubectl get svc -n socratic-rag

# Check logs
kubectl logs -f deployment/socratic-rag -n socratic-rag
```

## Configuration

### Environment Variables

Edit ConfigMap in `deployment.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: socratic-rag-config
  namespace: socratic-rag
data:
  vector_store: "qdrant"        # chromadb, qdrant, faiss
  qdrant_host: "qdrant-service" # Qdrant service hostname
  embedding_cache: "true"       # Enable embedding cache
  log_level: "INFO"             # DEBUG, INFO, WARNING, ERROR
```

### Resource Limits

Adjust in `deployment.yaml`:

```yaml
resources:
  requests:
    memory: "512Mi"    # Minimum memory
    cpu: "250m"        # Minimum CPU
  limits:
    memory: "2Gi"      # Maximum memory
    cpu: "1000m"       # Maximum CPU
```

### Replicas

Change in `deployment.yaml`:

```yaml
spec:
  replicas: 3  # Number of pod replicas
```

Or use kubectl:

```bash
kubectl scale deployment socratic-rag --replicas=5 -n socratic-rag
```

### Qdrant Storage

Adjust in `qdrant-statefulset.yaml`:

```yaml
volumeClaimTemplates:
  - metadata:
      name: qdrant-data
    spec:
      resources:
        requests:
          storage: 50Gi  # Storage size for data
```

## Scaling

### Manual Scaling

```bash
# Scale to 5 replicas
kubectl scale deployment socratic-rag --replicas=5 -n socratic-rag

# Check status
kubectl get deployment socratic-rag -n socratic-rag
```

### Auto-scaling

HPA (Horizontal Pod Autoscaler) is configured in `deployment.yaml`:

```yaml
spec:
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

Auto-scales between 2-10 replicas based on CPU/memory usage.

## Monitoring

### Health Checks

Liveness and readiness probes are configured:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  periodSeconds: 10
```

### Logs

```bash
# Real-time logs
kubectl logs -f deployment/socratic-rag -n socratic-rag

# Specific pod
kubectl logs -f socratic-rag-0 -n socratic-rag

# Last 100 lines
kubectl logs --tail=100 deployment/socratic-rag -n socratic-rag
```

### Metrics

Prometheus annotations are configured for monitoring:

```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8000"
  prometheus.io/path: "/metrics"
```

## Networking

### Service Access

```bash
# Get service endpoint
kubectl get svc socratic-rag-service -n socratic-rag

# Port forward for local access
kubectl port-forward svc/socratic-rag-service 8000:80 -n socratic-rag

# Then access: http://localhost:8000
```

### Ingress Setup

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: socratic-rag-ingress
  namespace: socratic-rag
spec:
  ingressClassName: nginx
  rules:
  - host: rag.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: socratic-rag-service
            port:
              number: 80
  tls:
  - hosts:
    - rag.example.com
    secretName: rag-tls-cert
```

Apply with:

```bash
kubectl apply -f ingress.yaml -n socratic-rag
```

## Persistence

### Qdrant Data

Data is stored in PersistentVolumeClaims:

```bash
# View PVCs
kubectl get pvc -n socratic-rag

# Resize PVC (if storage class supports it)
kubectl patch pvc qdrant-data-qdrant-0 -p \
  '{"spec":{"resources":{"requests":{"storage":"100Gi"}}}}' \
  -n socratic-rag
```

### Backups

Backup Qdrant data:

```bash
# Create snapshot
kubectl exec -it qdrant-0 -n socratic-rag -- \
  curl -X POST http://localhost:6333/snapshots

# Copy snapshot from pod
kubectl cp socratic-rag/qdrant-0:/qdrant/snapshots/. \
  ./backups/ -n socratic-rag

# Restore from snapshot
kubectl cp ./backup-snapshot.tar \
  socratic-rag/qdrant-0:/qdrant/snapshots/ -n socratic-rag
```

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod socratic-rag-0 -n socratic-rag

# Check events
kubectl get events -n socratic-rag --sort-by='.lastTimestamp'

# Check logs
kubectl logs socratic-rag-0 -n socratic-rag
```

### Qdrant Connection Issues

```bash
# Test Qdrant connectivity
kubectl exec -it socratic-rag-0 -n socratic-rag -- \
  curl -s http://qdrant-service:6333/health | jq

# Check Qdrant logs
kubectl logs qdrant-0 -n socratic-rag
```

### Out of Memory

```bash
# Check memory usage
kubectl top pods -n socratic-rag

# Increase limits
kubectl set resources deployment socratic-rag \
  -n socratic-rag \
  --limits=memory=4Gi,cpu=2 \
  --requests=memory=1Gi,cpu=500m
```

### Slow Performance

```bash
# Check CPU usage
kubectl top nodes

# Check pod metrics
kubectl top pods -n socratic-rag

# Scale up if needed
kubectl scale deployment socratic-rag --replicas=5 -n socratic-rag
```

## Cleanup

```bash
# Delete deployment
kubectl delete deployment socratic-rag -n socratic-rag

# Delete Qdrant StatefulSet
kubectl delete statefulset qdrant -n socratic-rag

# Delete namespace (and all resources)
kubectl delete namespace socratic-rag

# Delete PVCs if desired (WARNING: deletes data)
kubectl delete pvc -l app=qdrant -n socratic-rag
```

## Production Considerations

### Security

1. **Network Policies**: Already configured to restrict traffic
2. **RBAC**: Add role-based access control as needed
3. **Secrets**: Store sensitive data in Kubernetes Secrets
4. **Pod Security**: Run as non-root (already configured)

### High Availability

1. **Multiple Replicas**: Set `replicas: 3` or higher
2. **Pod Anti-Affinity**: Spread pods across nodes (already configured)
3. **PDB**: Pod Disruption Budget prevents eviction (already configured)
4. **Qdrant Cluster**: Use StatefulSet with 3+ replicas

### Cost Optimization

1. **Resource Requests**: Set realistic values
2. **Node Affinity**: Run on cost-effective node types
3. **Horizontal Autoscaling**: Scale down when not needed
4. **Storage**: Use appropriate storage classes

## Advanced Setup

### Prometheus Monitoring

```bash
# Add Prometheus scrape config
prometheus_rules: |
  - job_name: 'socratic-rag'
    static_configs:
      - targets: ['socratic-rag-service:8000']
```

### Grafana Dashboards

Create dashboard for:
- Request rate
- Response latency
- Error rate
- Memory/CPU usage
- Qdrant storage size

### ELK Stack Integration

```bash
# Configure Fluentd/Filebeat to collect logs
# Send to Elasticsearch
# Visualize in Kibana
```

## References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [StatefulSet Guide](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/)
- [Horizontal Pod Autoscaler](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Qdrant Kubernetes Guide](https://qdrant.tech/documentation/guides/deployment/)

---

**Last Updated**: March 10, 2024
**Version**: 0.1.0
