"""
Integration tests for health check endpoint.

Tests verify that the health check endpoint returns the correct response.
"""

import pytest
from app import create_app


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint_returns_200(client):
    """Test that GET /health returns HTTP 200 OK status."""
    response = client.get('/health')
    assert response.status_code == 200


def test_health_endpoint_content_type(client):
    """Test that health endpoint returns JSON content type."""
    response = client.get('/health')
    assert response.content_type == 'application/json'


def test_health_endpoint_response_body(client):
    """Test that health endpoint returns correct JSON response body."""
    response = client.get('/health')
    data = response.get_json()
    assert data == {"status": "healthy"}

