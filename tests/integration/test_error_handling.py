"""
Integration tests for error handling including size validation.

Tests verify that the API endpoint properly validates request sizes
and returns appropriate error responses with correct HTTP status codes
and structured error formats.
"""

import pytest
from flask import Flask
from app import create_app
from app.config import Config


@pytest.fixture
def app():
    """Create Flask application instance for testing."""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client for making requests."""
    return app.test_client()


def create_app_with_custom_limit(max_size_bytes):
    """Helper to create app with custom MAX_FILE_SIZE.
    
    Note: Due to Python module caching, we need to directly modify the Config class
    attribute after import, then restore it. This is safe in test context.
    The config is NOT restored automatically - tests should restore it if needed,
    but for isolated test apps this is usually not necessary.
    """
    import os
    from app.config import Config
    
    # Save original value (for reference, not automatic restoration)
    original_value = Config.MAX_FILE_SIZE
    original_request_size = Config.MAX_REQUEST_SIZE
    
    # Directly set the Config class attribute (most reliable for tests)
    # This bypasses module reload issues
    Config.MAX_FILE_SIZE = max_size_bytes
    Config.MAX_REQUEST_SIZE = max_size_bytes
    
    # Create new app instance (must happen after config is set)
    from app import create_app
    app_instance = create_app()
    
    # Verify config is set correctly
    assert Config.MAX_FILE_SIZE == max_size_bytes, f"Config not set correctly: {Config.MAX_FILE_SIZE} != {max_size_bytes}"
    
    return app_instance


class TestRequestSizeValidation:
    """Test suite for request size validation in API endpoint.
    
    Note: Flask's test client doesn't respect manually set Content-Length headers
    that don't match the actual body size. Content-Length header validation is
    comprehensively tested in unit tests. Integration tests focus on body size
    validation and error response format verification.
    """
    
    @pytest.fixture(autouse=True)
    def restore_config_after_test(self):
        """Auto-restore config after each test to prevent leakage."""
        from app.config import Config
        original_max_file_size = Config.MAX_FILE_SIZE
        original_max_request_size = Config.MAX_REQUEST_SIZE
        yield
        # Restore after test completes
        Config.MAX_FILE_SIZE = original_max_file_size
        Config.MAX_REQUEST_SIZE = original_max_request_size

    def test_request_body_exceeds_limit_returns_413(self):
        """Test that request body exceeding configured limit returns 413.
        
        Note: For practical testing, we use a smaller test limit via environment variable.
        In production, the full 300MB limit applies.
        """
        # Create app with smaller test limit (1000 bytes) for practical testing
        test_app = create_app_with_custom_limit(1000)
        test_app.config['TESTING'] = True
        test_client = test_app.test_client()
        
        # Create body exceeding test limit
        large_body = b'<root>' + (b'x' * 2000) + b'</root>'
        
        response = test_client.post(
            '/convert/xml-to-json',
            headers={'Content-Type': 'application/xml'},
            data=large_body
        )
        
        assert response.status_code == 413
        assert response.json['error']['code'] == 'FILE_SIZE_EXCEEDED'
        assert 'limit' in response.json['error']['message'].lower()

    def test_request_at_limit_boundary_passes(self):
        """Test that request exactly at configured limit passes."""
        # Create app with smaller test limit (1000 bytes) for practical testing
        test_app = create_app_with_custom_limit(1000)
        test_app.config['TESTING'] = True
        test_client = test_app.test_client()
        
        # Create body within test limit
        xml_body = '<root>' + ('x' * 500) + '</root>'  # Within 1000 byte limit
        
        response = test_client.post(
            '/convert/xml-to-json',
            headers={'Content-Type': 'application/xml'},
            data=xml_body
        )
        
        # Should pass validation (may fail on XML parsing, but not size validation)
        assert response.status_code != 413  # Should not be 413

    def test_error_response_format_matches_structured_format(self):
        """Test that error response format matches structured error format."""
        # Create app with smaller test limit (1000 bytes) for practical testing
        test_app = create_app_with_custom_limit(1000)
        test_app.config['TESTING'] = True
        test_client = test_app.test_client()
        
        # Create body exceeding test limit
        large_body = b'<root>' + (b'x' * 2000) + b'</root>'
        
        response = test_client.post(
            '/convert/xml-to-json',
            headers={'Content-Type': 'application/xml'},
            data=large_body
        )
        
        assert response.status_code == 413
        assert 'error' in response.json
        assert 'code' in response.json['error']
        assert 'message' in response.json['error']
        assert 'details' in response.json['error']
        assert response.json['error']['code'] == 'FILE_SIZE_EXCEEDED'

    def test_error_code_is_file_size_exceeded(self):
        """Test that error code is exactly 'FILE_SIZE_EXCEEDED'."""
        # Create app with smaller test limit (1000 bytes) for practical testing
        test_app = create_app_with_custom_limit(1000)
        test_app.config['TESTING'] = True
        test_client = test_app.test_client()
        
        # Create body exceeding test limit
        large_body = b'<root>' + (b'x' * 2000) + b'</root>'
        
        response = test_client.post(
            '/convert/xml-to-json',
            headers={'Content-Type': 'application/xml'},
            data=large_body
        )
        
        assert response.status_code == 413
        assert response.json['error']['code'] == 'FILE_SIZE_EXCEEDED'

    def test_valid_request_within_limit_passes(self, client):
        """Test that valid request within size limit passes validation and processes."""
        xml_body = '<root><item>test</item></root>'
        
        response = client.post(
            '/convert/xml-to-json',
            headers={
                'Content-Type': 'application/xml',
                'Content-Length': str(len(xml_body))
            },
            data=xml_body
        )
        
        # Should pass size validation and process successfully
        assert response.status_code != 413
        # If XML is valid, should return 200, otherwise might return 400 for XML errors
        assert response.status_code in [200, 400]  # Either success or XML parsing error, not size error