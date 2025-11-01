"""
Unit tests for validation utilities.

Tests verify that request size validation functions correctly
for various scenarios including Content-Length header validation,
body size validation, boundary conditions, and error handling.
"""

import pytest
from unittest.mock import Mock, MagicMock
from flask import Request
from app import create_app
from app.utils.validators import validate_request_size, format_file_size_error
from app.exceptions import FileSizeExceededError
from app.config import Config


@pytest.fixture
def app():
    """Create Flask application instance for testing."""
    app = create_app()
    app.config['TESTING'] = True
    return app


class TestValidateRequestSize:
    """Test suite for validate_request_size() function."""

    def test_content_length_header_within_limit(self):
        """Test that request with Content-Length within limit passes validation."""
        # Create mock request with Content-Length header within limit
        request = Mock(spec=Request)
        request.headers = {'Content-Length': '1000000'}  # 1MB, well within 300MB limit
        request.content_length = None
        
        # Should not raise exception
        validate_request_size(request)

    def test_content_length_header_exceeds_limit(self):
        """Test that request with Content-Length exceeding limit raises FileSizeExceededError."""
        # Create mock request with Content-Length header exceeding limit
        request = Mock(spec=Request)
        max_size = Config.MAX_FILE_SIZE  # 300MB = 314572800 bytes
        exceeded_size = max_size + 1
        request.headers = {'Content-Length': str(exceeded_size)}
        request.content_length = None
        
        # Should raise FileSizeExceededError
        with pytest.raises(FileSizeExceededError) as exc_info:
            validate_request_size(request)
        
        assert exc_info.value.max_size_bytes == max_size
        assert exc_info.value.actual_size_bytes == exceeded_size

    def test_content_length_header_exactly_at_limit(self):
        """Test that request with Content-Length exactly at limit passes validation."""
        # Create mock request with Content-Length exactly at limit
        request = Mock(spec=Request)
        max_size = Config.MAX_FILE_SIZE  # 300MB = 314572800 bytes
        request.headers = {'Content-Length': str(max_size)}
        request.content_length = None
        
        # Should not raise exception (boundary condition: exactly at limit should pass)
        validate_request_size(request)

    def test_content_length_header_one_byte_over_limit(self):
        """Test that request with Content-Length one byte over limit fails."""
        # Create mock request with Content-Length one byte over limit
        request = Mock(spec=Request)
        max_size = Config.MAX_FILE_SIZE  # 300MB = 314572800 bytes
        exceeded_size = max_size + 1
        request.headers = {'Content-Length': str(exceeded_size)}
        request.content_length = None
        
        # Should raise FileSizeExceededError
        with pytest.raises(FileSizeExceededError) as exc_info:
            validate_request_size(request)
        
        assert exc_info.value.max_size_bytes == max_size
        assert exc_info.value.actual_size_bytes == exceeded_size

    def test_content_length_header_invalid_format(self):
        """Test that invalid Content-Length header format falls through to body check."""
        # Create mock request with invalid Content-Length header
        request = Mock(spec=Request)
        request.headers = {'Content-Length': 'invalid'}
        request.content_length = None
        request.get_data = Mock(return_value=b'x' * 1000)  # Small body, should pass
        
        # Should not raise exception (falls through to body check)
        validate_request_size(request)
        # Verify get_data was called (indicating fallback to body check)
        request.get_data.assert_called_once_with(cache=True)

    def test_request_content_length_attribute_within_limit(self):
        """Test that request.content_length attribute within limit passes validation."""
        # Create mock request with content_length attribute within limit
        request = Mock(spec=Request)
        request.headers = {}  # No Content-Length header
        request.content_length = 1000000  # 1MB, well within 300MB limit
        
        # Should not raise exception
        validate_request_size(request)

    def test_request_content_length_attribute_exceeds_limit(self):
        """Test that request.content_length attribute exceeding limit raises FileSizeExceededError."""
        # Create mock request with content_length attribute exceeding limit
        request = Mock(spec=Request)
        max_size = Config.MAX_FILE_SIZE  # 300MB = 314572800 bytes
        exceeded_size = max_size + 1
        request.headers = {}  # No Content-Length header
        request.content_length = exceeded_size
        
        # Should raise FileSizeExceededError
        with pytest.raises(FileSizeExceededError) as exc_info:
            validate_request_size(request)
        
        assert exc_info.value.max_size_bytes == max_size
        assert exc_info.value.actual_size_bytes == exceeded_size

    def test_body_size_within_limit(self):
        """Test that request body within limit passes validation."""
        # Create mock request without Content-Length header
        request = Mock(spec=Request)
        request.headers = {}  # No Content-Length header
        request.content_length = None
        request.get_data = Mock(return_value=b'x' * 1000000)  # 1MB body
        
        # Should not raise exception
        validate_request_size(request)
        request.get_data.assert_called_once_with(cache=True)

    def test_body_size_exceeds_limit(self):
        """Test that request body exceeding limit raises FileSizeExceededError."""
        # Create mock request without Content-Length header
        request = Mock(spec=Request)
        max_size = Config.MAX_FILE_SIZE  # 300MB = 314572800 bytes
        exceeded_size = max_size + 1
        request.headers = {}  # No Content-Length header
        request.content_length = None
        request.get_data = Mock(return_value=b'x' * exceeded_size)  # Body exceeding limit
        
        # Should raise FileSizeExceededError
        with pytest.raises(FileSizeExceededError) as exc_info:
            validate_request_size(request)
        
        assert exc_info.value.max_size_bytes == max_size
        assert exc_info.value.actual_size_bytes == exceeded_size

    def test_body_size_exactly_at_limit(self):
        """Test that request body exactly at limit passes validation."""
        # Create mock request without Content-Length header
        request = Mock(spec=Request)
        max_size = Config.MAX_FILE_SIZE  # 300MB = 314572800 bytes
        request.headers = {}  # No Content-Length header
        request.content_length = None
        request.get_data = Mock(return_value=b'x' * max_size)  # Body exactly at limit
        
        # Should not raise exception (boundary condition: exactly at limit should pass)
        validate_request_size(request)

    def test_body_size_one_byte_over_limit(self):
        """Test that request body one byte over limit fails."""
        # Create mock request without Content-Length header
        request = Mock(spec=Request)
        max_size = Config.MAX_FILE_SIZE  # 300MB = 314572800 bytes
        exceeded_size = max_size + 1
        request.headers = {}  # No Content-Length header
        request.content_length = None
        request.get_data = Mock(return_value=b'x' * exceeded_size)  # Body one byte over limit
        
        # Should raise FileSizeExceededError
        with pytest.raises(FileSizeExceededError) as exc_info:
            validate_request_size(request)
        
        assert exc_info.value.max_size_bytes == max_size
        assert exc_info.value.actual_size_bytes == exceeded_size

    def test_custom_max_size_parameter(self):
        """Test that custom max_size parameter is used when provided."""
        # Create mock request with Content-Length header
        request = Mock(spec=Request)
        custom_max_size = 1000000  # 1MB custom limit
        request.headers = {'Content-Length': str(custom_max_size + 1)}
        request.content_length = None
        
        # Should raise FileSizeExceededError with custom max_size
        with pytest.raises(FileSizeExceededError) as exc_info:
            validate_request_size(request, max_size=custom_max_size)
        
        assert exc_info.value.max_size_bytes == custom_max_size
        assert exc_info.value.actual_size_bytes == custom_max_size + 1

    def test_body_read_exception_handled_gracefully(self):
        """Test that exceptions during body read are handled gracefully."""
        # Create mock request that raises exception when reading body
        request = Mock(spec=Request)
        request.headers = {}  # No Content-Length header
        request.content_length = None
        request.get_data = Mock(side_effect=Exception("Stream read error"))
        
        # Should not raise exception (allows request through if size can't be determined)
        # This is a design decision: better to allow potentially oversized requests
        # than to block valid requests due to read errors
        validate_request_size(request)

    def test_priority_content_length_header_over_body(self):
        """Test that Content-Length header is checked before reading body."""
        # Create mock request with Content-Length header
        request = Mock(spec=Request)
        request.headers = {'Content-Length': '1000000'}  # Within limit
        request.content_length = None
        request.get_data = Mock(return_value=b'x' * (Config.MAX_FILE_SIZE + 1))  # Body exceeds limit
        
        # Should pass based on Content-Length header (body should not be read)
        validate_request_size(request)
        # Verify get_data was NOT called (Content-Length header checked first)
        request.get_data.assert_not_called()


class TestFormatFileSizeError:
    """Test suite for format_file_size_error() function."""

    def test_format_file_size_error_default(self, app):
        """Test that format_file_size_error() returns correct response format."""
        with app.app_context():
            response, status_code = format_file_size_error()
            
            assert status_code == 413
            assert response.json['error']['code'] == 'FILE_SIZE_EXCEEDED'
            assert '300MB' in response.json['error']['message']
            assert 'details' in response.json['error']

    def test_format_file_size_error_custom_size(self, app):
        """Test that format_file_size_error() accepts custom size parameter."""
        with app.app_context():
            response, status_code = format_file_size_error(max_size_mb=500)
            
            assert status_code == 413
            assert response.json['error']['code'] == 'FILE_SIZE_EXCEEDED'
            assert '500MB' in response.json['error']['message']
            assert '500MB' in response.json['error']['details']

    def test_format_file_size_error_structure(self, app):
        """Test that format_file_size_error() returns structured error format."""
        with app.app_context():
            response, status_code = format_file_size_error()
            
            assert 'error' in response.json
            assert 'code' in response.json['error']
            assert 'message' in response.json['error']
            assert 'details' in response.json['error']
            assert response.json['error']['code'] == 'FILE_SIZE_EXCEEDED'
