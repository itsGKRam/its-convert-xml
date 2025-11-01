# Deployment Guide

This guide covers deployment procedures for the XML-to-JSON conversion service to various platforms.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Docker Deployment](#docker-deployment)
- [Gunicorn Deployment](#gunicorn-deployment)
- [Environment Configuration](#environment-configuration)
- [Deployment Platforms](#deployment-platforms)
- [Health Checks](#health-checks)
- [Monitoring and Logging](#monitoring-and-logging)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Python 3.11+
- Docker (for containerized deployment)
- Gunicorn (for production WSGI server)

## Docker Deployment

### Building the Docker Image

```bash
# Build the image
docker build -t its-convert-xml .

# Verify the build
docker images | grep its-convert-xml
```

### Running the Container

```bash
# Run with default settings
docker run -p 5000:5000 its-convert-xml

# Run with custom environment variables
docker run -p 5000:5000 \
  -e LOG_LEVEL=INFO \
  -e MAX_FILE_SIZE=314572800 \
  -e GUNICORN_WORKERS=4 \
  its-convert-xml

# Run with environment file
docker run -p 5000:5000 --env-file .env its-convert-xml
```

### Docker Compose (Local Development)

```bash
# Start the service
docker-compose up

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

The `docker-compose.yml` file includes:
- Service name: `xml-converter`
- Port mapping: `5000:5000`
- Health check configuration
- Environment variable support via `.env` file
- Volume mounts for local development (optional)

## Gunicorn Deployment

### Installing Gunicorn

```bash
pip install gunicorn
```

Or use requirements.txt:

```bash
pip install -r requirements.txt
```

### Running with Gunicorn

```bash
# Basic usage
gunicorn -c gunicorn_config.py app:app

# Custom bind address and port
gunicorn -c gunicorn_config.py --bind 0.0.0.0:8000 app:app

# With environment variables
GUNICORN_WORKERS=4 gunicorn -c gunicorn_config.py app:app
```

### Gunicorn Configuration

The `gunicorn_config.py` file includes optimized settings for handling large XML files:

- **Workers**: 2-4 per CPU core (default: `(CPU_COUNT * 2) + 1`)
- **Worker Class**: `sync` (default, configurable)
- **Timeout**: 120 seconds (for large file processing)
- **Graceful Timeout**: 30 seconds
- **Max Requests**: 1000 per worker (with jitter)

Configuration can be customized via environment variables (see [Environment Configuration](#environment-configuration)).

## Environment Configuration

### Environment Variables

All configuration is managed via environment variables following 12-factor app principles.

#### Flask Configuration

- `FLASK_ENV`: Application environment (`production`, `development`, `staging`)
- `FLASK_DEBUG`: Debug mode (`False` for production)

#### Application Configuration

- `MAX_FILE_SIZE`: Maximum file size in bytes (default: `314572800` = 300MB)
- `MAX_REQUEST_SIZE_BYTES`: Maximum request size in bytes (default: same as `MAX_FILE_SIZE`)
- `SECRET_KEY`: Flask secret key (required for production)

#### Logging Configuration

- `LOG_LEVEL`: Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)
  - Development: `DEBUG`
  - Production: `INFO`

#### Gunicorn Configuration

- `GUNICORN_BIND`: Bind address (default: `0.0.0.0:5000`)
- `GUNICORN_WORKERS`: Number of worker processes (default: `(CPU_COUNT * 2) + 1`)
- `GUNICORN_WORKER_CLASS`: Worker class (default: `sync`)
- `GUNICORN_TIMEOUT`: Worker timeout in seconds (default: `120`)
- `GUNICORN_GRACEFUL_TIMEOUT`: Graceful timeout in seconds (default: `30`)
- `GUNICORN_MAX_REQUESTS`: Max requests per worker (default: `1000`)
- `GUNICORN_LOG_LEVEL`: Gunicorn log level (default: `info`)

#### Port Configuration

- `PORT`: Application port (default: `5000`)

#### Deployment Stage

- `DEPLOYMENT_STAGE`: Deployment stage (`development`, `staging`, `production`)

### Environment File Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your configuration:
   ```bash
   nano .env
   ```

3. Ensure `.env` is in `.gitignore` (already configured)

### Deployment Stages

#### Development

```bash
FLASK_ENV=development
LOG_LEVEL=DEBUG
DEPLOYMENT_STAGE=development
```

#### Staging

```bash
FLASK_ENV=production
LOG_LEVEL=INFO
DEPLOYMENT_STAGE=staging
MAX_FILE_SIZE=314572800
```

#### Production

```bash
FLASK_ENV=production
LOG_LEVEL=INFO
DEPLOYMENT_STAGE=production
MAX_FILE_SIZE=314572800
SECRET_KEY=<strong-secret-key>
GUNICORN_WORKERS=4
```

## Deployment Platforms

The service is designed to be platform-agnostic using Docker containers. It's compatible with:

### AWS ECS (Elastic Container Service)

1. Build and push Docker image to ECR
2. Create ECS task definition with:
   - Image: Your ECR image
   - Port mappings: `5000:5000`
   - Environment variables from `.env.example`
   - Health check: `GET /health`

### Google Cloud Run

```bash
# Build and deploy
gcloud run deploy xml-converter \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 5000 \
  --set-env-vars LOG_LEVEL=INFO,DEPLOYMENT_STAGE=production
```

### Azure Container Instances

```bash
# Deploy container
az container create \
  --resource-group myResourceGroup \
  --name xml-converter \
  --image its-convert-xml:latest \
  --ports 5000 \
  --environment-variables LOG_LEVEL=INFO DEPLOYMENT_STAGE=production
```

### Railway

1. Connect your GitHub repository
2. Railway auto-detects Dockerfile
3. Configure environment variables in Railway dashboard
4. Deploy automatically on push

### Fly.io

```bash
# Install flyctl
# Initialize app
fly launch

# Deploy
fly deploy
```

### Heroku

```bash
# Create Procfile
echo "web: gunicorn -c gunicorn_config.py app:app" > Procfile

# Deploy
git push heroku main
```

## Health Checks

### Health Check Endpoint

The service provides a health check endpoint at `GET /health`:

```bash
# Test health check
curl http://localhost:5000/health

# Expected response
{"status": "healthy"}
```

**Response:**
- HTTP Status: `200 OK`
- Content-Type: `application/json`
- Body: `{"status": "healthy"}`

### Health Check Configuration

For containerized deployments, health checks are configured:

**Docker:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"
```

**Docker Compose:**
```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 5s
```

### Using Health Checks

- **Liveness Probe**: Check if container is running
- **Readiness Probe**: Check if service is ready to accept traffic
- **Orchestration Platforms**: Kubernetes, ECS, Cloud Run use health checks for automatic restart and load balancing

## Monitoring and Logging

### Logging Configuration

#### Production Logging (Structured JSON)

In production mode (`DEPLOYMENT_STAGE=production`), logs are output in structured JSON format:

```json
{
  "timestamp": "2025-10-30T14:30:45.123456Z",
  "level": "INFO",
  "logger": "app.routes.convert",
  "message": "Conversion successful",
  "endpoint": "/convert/xml-to-json",
  "file_size": 1048576
}
```

#### Development Logging (Human-Readable)

In development mode, logs use human-readable format:

```
2025-10-30 14:30:45 - app.routes.convert - INFO - Conversion successful
```

### Accessing Logs

#### Docker

```bash
# View container logs
docker logs xml-converter

# Follow logs
docker logs -f xml-converter
```

#### Docker Compose

```bash
# View logs
docker-compose logs

# Follow logs
docker-compose logs -f

# View specific service logs
docker-compose logs xml-converter
```

#### Gunicorn

Logs are output to stdout/stderr by default. For production:

- Use log aggregation services (CloudWatch, Datadog, etc.)
- Redirect logs to files if needed
- Use structured JSON format for parsing

### Monitoring Recommendations

1. **Application Metrics**:
   - Request rate
   - Response time
   - Error rate
   - File size distribution

2. **System Metrics**:
   - CPU usage
   - Memory usage
   - Disk I/O

3. **Health Check Monitoring**:
   - Monitor `/health` endpoint
   - Alert on health check failures

## Troubleshooting

### Container Won't Start

1. **Check logs**:
   ```bash
   docker logs xml-converter
   ```

2. **Verify environment variables**:
   ```bash
   docker run --env-file .env its-convert-xml env
   ```

3. **Test health endpoint**:
   ```bash
   curl http://localhost:5000/health
   ```

### Gunicorn Workers Dying

1. **Increase timeout**:
   ```bash
   GUNICORN_TIMEOUT=240 gunicorn -c gunicorn_config.py app:app
   ```

2. **Check memory limits**:
   - Large files (300MB) may require more memory
   - Increase container memory limits

3. **Reduce worker count** if memory constrained:
   ```bash
   GUNICORN_WORKERS=2 gunicorn -c gunicorn_config.py app:app
   ```

### Port Conflicts

1. **Change port**:
   ```bash
   # Docker
   docker run -p 8000:5000 -e PORT=5000 its-convert-xml
   
   # Gunicorn
   gunicorn -c gunicorn_config.py --bind 0.0.0.0:8000 app:app
   ```

### Health Check Failing

1. **Verify endpoint is accessible**:
   ```bash
   curl http://localhost:5000/health
   ```

2. **Check container health status**:
   ```bash
   docker inspect xml-converter | grep Health
   ```

3. **Increase health check timeout** if needed

### Performance Issues

1. **Optimize worker count**:
   - Default: `(CPU_COUNT * 2) + 1`
   - Adjust based on workload: `GUNICORN_WORKERS=4`

2. **Increase timeout for large files**:
   - Default: 120 seconds
   - For 300MB files: `GUNICORN_TIMEOUT=300`

3. **Monitor resource usage**:
   - CPU usage
   - Memory consumption
   - Request queue length

### Environment Variables Not Loading

1. **Verify `.env` file exists and is readable**
2. **Check Docker environment variable passing**:
   ```bash
   docker run --env-file .env its-convert-xml env | grep FLASK
   ```

3. **For platform deployments, verify environment variable configuration in platform dashboard**

## Additional Resources

- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Docker Documentation](https://docs.docker.com/)
- [12-Factor App](https://12factor.net/)
- [Flask Deployment Best Practices](https://flask.palletsprojects.com/en/latest/deploying/)

