"""
Unit tests for Flask app factory.

Tests verify that the app factory creates a properly configured Flask instance.
"""

import pytest
from app import create_app


def test_create_app_returns_flask_instance():
    """Test that create_app returns a Flask application instance."""
    app = create_app()
    assert app is not None
    assert hasattr(app, 'config')


def test_app_initializes_successfully():
    """Test that the Flask app initializes without errors."""
    app = create_app()
    assert app.name == 'app'
    assert app.config is not None


def test_app_registers_blueprints():
    """Test that blueprints are registered with the app."""
    app = create_app()
    # Check that convert blueprint is registered
    assert 'convert' in app.blueprints


def test_app_has_configuration():
    """Test that app loads configuration."""
    app = create_app()
    assert 'MAX_FILE_SIZE' in app.config
    assert 'LOG_LEVEL' in app.config

