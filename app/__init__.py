"""
Flask application factory module.

This module provides the create_app() function following the Flask app factory pattern,
enabling flexible application initialization with configuration management and blueprint registration.
"""

import logging
import sys
from flask import Flask


def create_app(config_name=None):
    """
    Create and configure Flask application instance.

    Args:
        config_name (str, optional): Configuration environment name.
            If None, uses default configuration.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__)

    # Load configuration
    from app.config import Config
    app.config.from_object(Config)

    # Configure logging
    # Production uses structured JSON logging, development uses human-readable format
    if Config.DEPLOYMENT_STAGE == 'production':
        import json
        from datetime import datetime, timezone
        
        class StructuredJSONFormatter(logging.Formatter):
            """JSON formatter for structured logging in production."""
            def format(self, record):
                log_entry = {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'level': record.levelname,
                    'logger': record.name,
                    'message': record.getMessage()
                }
                # Add context if available (from extra dict)
                if hasattr(record, 'context') and record.context:
                    log_entry['context'] = record.context
                if hasattr(record, 'endpoint') and record.endpoint:
                    log_entry['endpoint'] = record.endpoint
                if hasattr(record, 'file_size') and record.file_size:
                    log_entry['file_size'] = record.file_size
                return json.dumps(log_entry)
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredJSONFormatter())
        logging.basicConfig(
            level=Config.LOG_LEVEL_VALUE,
            handlers=[handler],
            format='%(message)s'  # JSON formatter handles the format
        )
    else:
        # Development: Human-readable format
        logging.basicConfig(
            level=Config.LOG_LEVEL_VALUE,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            stream=sys.stdout,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    app.logger.setLevel(Config.LOG_LEVEL_VALUE)

    # Register blueprints
    from app.routes.convert import convert_bp
    app.register_blueprint(convert_bp)

    return app

