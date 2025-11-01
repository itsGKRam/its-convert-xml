"""
Gunicorn configuration for production deployment.

This configuration is optimized for handling large XML files (up to 300MB)
while maintaining good performance and resource utilization.
"""

import multiprocessing
import os

# Server socket
bind = os.environ.get('GUNICORN_BIND', '0.0.0.0:5000')
backlog = 2048

# Worker processes
# Calculate workers: 2-4 per CPU core as per architecture
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = os.environ.get('GUNICORN_WORKER_CLASS', 'sync')
worker_connections = 1000
timeout = int(os.environ.get('GUNICORN_TIMEOUT', 120))  # 120 seconds for large file processing
keepalive = 5

# Graceful timeout for worker lifecycle
graceful_timeout = int(os.environ.get('GUNICORN_GRACEFUL_TIMEOUT', 30))
max_requests = int(os.environ.get('GUNICORN_MAX_REQUESTS', 1000))
max_requests_jitter = 50

# Logging
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info').lower()
accesslog = '-'  # Log to stdout for containerized deployments
errorlog = '-'   # Log to stdout for containerized deployments
access_log_format = (
    '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" '
    '%(D)s %(p)s'
)

# Process naming
proc_name = 'xml-converter'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed in future)
# keyfile = None
# certfile = None

