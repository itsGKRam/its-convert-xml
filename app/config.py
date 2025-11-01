"""
Configuration management module.

This module provides environment-based configuration following 12-factor app principles.
Configuration values are loaded from environment variables with sensible defaults.
"""

import os
from logging import INFO, DEBUG


class Config:
    """
    Application configuration class.

    Loads settings from environment variables with defaults.
    Follows 12-factor app principles for configuration management.
    """

    # Maximum file size for uploads (default: 300MB = 314572800 bytes)
    MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 314572800))
    
    # Maximum request size limit (default: 300MB = 314572800 bytes)
    # Can be overridden via MAX_REQUEST_SIZE_BYTES environment variable
    # Falls back to MAX_FILE_SIZE if not specified
    MAX_REQUEST_SIZE = int(os.environ.get('MAX_REQUEST_SIZE_BYTES', MAX_FILE_SIZE))

    # Log level configuration
    # Default: INFO for production, DEBUG for development
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Convert string log level to logging constant
    LOG_LEVEL_VALUE = DEBUG if LOG_LEVEL.upper() == 'DEBUG' else INFO

    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Deployment stage (development, staging, production)
    DEPLOYMENT_STAGE = os.environ.get('DEPLOYMENT_STAGE', 'development').lower()
    
    # Gunicorn configuration (used by gunicorn_config.py)
    GUNICORN_WORKERS = int(os.environ.get('GUNICORN_WORKERS', 4))
    GUNICORN_WORKER_CLASS = os.environ.get('GUNICORN_WORKER_CLASS', 'sync')
    GUNICORN_TIMEOUT = int(os.environ.get('GUNICORN_TIMEOUT', 120))
    GUNICORN_GRACEFUL_TIMEOUT = int(os.environ.get('GUNICORN_GRACEFUL_TIMEOUT', 30))
    GUNICORN_MAX_REQUESTS = int(os.environ.get('GUNICORN_MAX_REQUESTS', 1000))
    GUNICORN_LOG_LEVEL = os.environ.get('GUNICORN_LOG_LEVEL', 'info').lower()
    GUNICORN_BIND = os.environ.get('GUNICORN_BIND', '0.0.0.0:5000')

