"""
Unit tests for configuration management.

Tests verify that the Config class loads environment variables correctly
and applies sensible defaults when environment variables are missing.
"""

import os
import pytest
from app.config import Config


def test_config_loads_max_file_size_from_environment():
    """Test that MAX_FILE_SIZE loads from environment variable."""
    original_value = os.environ.get('MAX_FILE_SIZE')
    try:
        os.environ['MAX_FILE_SIZE'] = '500000000'
        # Reload module to pick up new env var
        import importlib
        import app.config
        importlib.reload(app.config)
        
        # Create new config instance
        config = app.config.Config()
        assert config.MAX_FILE_SIZE == 500000000
    finally:
        # Restore original value
        if original_value is not None:
            os.environ['MAX_FILE_SIZE'] = original_value
        else:
            os.environ.pop('MAX_FILE_SIZE', None)
        # Reload module to restore defaults
        import importlib
        import app.config
        importlib.reload(app.config)


def test_config_uses_default_max_file_size():
    """Test that MAX_FILE_SIZE uses default when environment variable is missing."""
    original_value = os.environ.get('MAX_FILE_SIZE')
    try:
        # Remove environment variable
        os.environ.pop('MAX_FILE_SIZE', None)
        # Reload module to pick up absence of env var
        import importlib
        import app.config
        importlib.reload(app.config)
        
        # Create new config instance
        config = app.config.Config()
        assert config.MAX_FILE_SIZE == 314572800  # Default: 300MB
    finally:
        # Restore original value
        if original_value is not None:
            os.environ['MAX_FILE_SIZE'] = original_value
        # Reload module to restore defaults
        import importlib
        import app.config
        importlib.reload(app.config)


def test_config_loads_log_level_from_environment():
    """Test that LOG_LEVEL loads from environment variable."""
    original_value = os.environ.get('LOG_LEVEL')
    try:
        os.environ['LOG_LEVEL'] = 'DEBUG'
        # Reload module to pick up new env var
        import importlib
        import app.config
        importlib.reload(app.config)
        
        # Create new config instance
        config = app.config.Config()
        assert config.LOG_LEVEL == 'DEBUG'
    finally:
        # Restore original value
        if original_value is not None:
            os.environ['LOG_LEVEL'] = original_value
        else:
            os.environ.pop('LOG_LEVEL', None)
        # Reload module to restore defaults
        import importlib
        import app.config
        importlib.reload(app.config)


def test_config_uses_default_log_level():
    """Test that LOG_LEVEL uses default when environment variable is missing."""
    original_value = os.environ.get('LOG_LEVEL')
    try:
        # Remove environment variable
        os.environ.pop('LOG_LEVEL', None)
        # Reload module to pick up absence of env var
        import importlib
        import app.config
        importlib.reload(app.config)
        
        # Create new config instance
        config = app.config.Config()
        assert config.LOG_LEVEL == 'INFO'  # Default
    finally:
        # Restore original value
        if original_value is not None:
            os.environ['LOG_LEVEL'] = original_value
        # Reload module to restore defaults
        import importlib
        import app.config
        importlib.reload(app.config)


def test_config_log_level_value_conversion_debug():
    """Test that LOG_LEVEL_VALUE converts DEBUG string to logging constant."""
    original_value = os.environ.get('LOG_LEVEL')
    try:
        os.environ['LOG_LEVEL'] = 'DEBUG'
        # Reload module
        import importlib
        import app.config
        from logging import DEBUG
        importlib.reload(app.config)
        
        config = app.config.Config()
        assert config.LOG_LEVEL_VALUE == DEBUG
    finally:
        if original_value is not None:
            os.environ['LOG_LEVEL'] = original_value
        else:
            os.environ.pop('LOG_LEVEL', None)
        import importlib
        import app.config
        importlib.reload(app.config)


def test_config_log_level_value_conversion_info():
    """Test that LOG_LEVEL_VALUE converts INFO string to logging constant."""
    original_value = os.environ.get('LOG_LEVEL')
    try:
        os.environ['LOG_LEVEL'] = 'INFO'
        # Reload module
        import importlib
        import app.config
        from logging import INFO
        importlib.reload(app.config)
        
        config = app.config.Config()
        assert config.LOG_LEVEL_VALUE == INFO
    finally:
        if original_value is not None:
            os.environ['LOG_LEVEL'] = original_value
        else:
            os.environ.pop('LOG_LEVEL', None)
        import importlib
        import app.config
        importlib.reload(app.config)


def test_config_loads_secret_key_from_environment():
    """Test that SECRET_KEY loads from environment variable."""
    original_value = os.environ.get('SECRET_KEY')
    try:
        os.environ['SECRET_KEY'] = 'test-secret-key-12345'
        # Reload module
        import importlib
        import app.config
        importlib.reload(app.config)
        
        config = app.config.Config()
        assert config.SECRET_KEY == 'test-secret-key-12345'
    finally:
        if original_value is not None:
            os.environ['SECRET_KEY'] = original_value
        else:
            os.environ.pop('SECRET_KEY', None)
        import importlib
        import app.config
        importlib.reload(app.config)


def test_config_uses_default_secret_key():
    """Test that SECRET_KEY uses default when environment variable is missing."""
    original_value = os.environ.get('SECRET_KEY')
    try:
        # Remove environment variable
        os.environ.pop('SECRET_KEY', None)
        # Reload module
        import importlib
        import app.config
        importlib.reload(app.config)
        
        config = app.config.Config()
        assert config.SECRET_KEY == 'dev-secret-key-change-in-production'
    finally:
        if original_value is not None:
            os.environ['SECRET_KEY'] = original_value
        import importlib
        import app.config
        importlib.reload(app.config)

