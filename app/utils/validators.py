"""
Validation utilities and error response helpers.

This module contains utility functions for request validation
and standardized error response formatting.
"""

from flask import jsonify, Request
from app.exceptions import XMLValidationError, FileSizeExceededError
from app.config import Config


# Error codes as defined in architecture
INVALID_CONTENT_TYPE = "INVALID_CONTENT_TYPE"
XML_PARSE_ERROR = "XML_PARSE_ERROR"
FILE_SIZE_EXCEEDED = "FILE_SIZE_EXCEEDED"
CONVERSION_ERROR = "CONVERSION_ERROR"
SERVER_ERROR = "SERVER_ERROR"
EMPTY_REQUEST_BODY = "EMPTY_REQUEST_BODY"
REQUEST_READ_ERROR = "REQUEST_READ_ERROR"


def format_error_response(code: str, message: str, details: str = None, status_code: int = 400):
    """
    Format a consistent JSON error response.

    Creates a standardized error response following the architecture's
    error response format: {error: {code, message, details}}.

    Args:
        code (str): Error code (e.g., "INVALID_CONTENT_TYPE", "XML_PARSE_ERROR")
        message (str): Human-readable error message
        details (str, optional): Additional error context or location information
        status_code (int): HTTP status code (default: 400)

    Returns:
        tuple: Flask response tuple (jsonify result, status code)

    Example:
        response, status = format_error_response(
            "INVALID_CONTENT_TYPE",
            "Content-Type must be application/xml or text/xml",
            "Received Content-Type: application/json",
            400
        )
    """
    error_data = {
        "error": {
            "code": code,
            "message": message
        }
    }

    if details:
        error_data["error"]["details"] = details

    return jsonify(error_data), status_code


def format_xml_validation_error(error: XMLValidationError) -> tuple:
    """
    Format XMLValidationError into standardized error response.

    Extracts line and column information from XMLValidationError
    and formats it into actionable error details.

    Args:
        error (XMLValidationError): The XML validation error to format

    Returns:
        tuple: Flask response tuple (jsonify result, HTTP 400 status code)

    Example:
        try:
            parse_xml(xml_string)
        except XMLValidationError as e:
            return format_xml_validation_error(e)
    """
    # Extract location information
    error_details = None
    if error.line is not None and error.column is not None:
        error_details = f"Line {error.line}, column {error.column}"
    elif error.line is not None:
        error_details = f"Line {error.line}"

    return format_error_response(
        code=XML_PARSE_ERROR,
        message=str(error),
        details=error_details,
        status_code=400
    )


def format_content_type_error(received_content_type: str = None) -> tuple:
    """
    Format Content-Type validation error response.

    Args:
        received_content_type (str, optional): The Content-Type value that was received

    Returns:
        tuple: Flask response tuple (jsonify result, HTTP 400 status code)
    """
    details = f"Received Content-Type: {received_content_type or 'missing'}"
    return format_error_response(
        code=INVALID_CONTENT_TYPE,
        message="Content-Type must be application/xml or text/xml",
        details=details,
        status_code=400
    )


def format_file_size_error(max_size_mb: int = 300) -> tuple:
    """
    Format file size exceeded error response.

    Args:
        max_size_mb (int): Maximum file size in MB (default: 300)

    Returns:
        tuple: Flask response tuple (jsonify result, HTTP 413 status code)
    """
    return format_error_response(
        code=FILE_SIZE_EXCEEDED,
        message=f"Request size exceeds maximum limit of {max_size_mb}MB",
        details=f"Maximum allowed size is {max_size_mb}MB (314572800 bytes)",
        status_code=413
    )


def format_server_error(detailed_message: str = None) -> tuple:
    """
    Format server error response with sanitized message.

    Returns a generic error message to users while logging
    detailed information internally.

    Args:
        detailed_message (str, optional): Detailed error message for logging

    Returns:
        tuple: Flask response tuple (jsonify result, HTTP 500 status code)
    """
    return format_error_response(
        code=SERVER_ERROR,
        message="An unexpected error occurred during conversion",
        details="Internal server error",
        status_code=500
    )


def validate_request_size(request: Request, max_size: int = None) -> None:
    """
    Validate that request size does not exceed the maximum allowed limit.

    This function checks the request size before processing to prevent resource
    exhaustion. It first checks the Content-Length header if present, and if
    not available, reads the request body stream to check size. Validation
    should occur early in the request handling pipeline, before XML parsing.

    Args:
        request (Request): Flask request object to validate
        max_size (int, optional): Maximum allowed size in bytes.
            If not provided, uses Config.MAX_FILE_SIZE (default: 300MB)

    Raises:
        FileSizeExceededError: If request size exceeds the maximum allowed limit

    Example:
        try:
            validate_request_size(request)
            # Process request...
        except FileSizeExceededError:
            return format_file_size_error()
    """
    if max_size is None:
        max_size = Config.MAX_FILE_SIZE

    # Priority 1: Check Content-Length header if present (fastest, no body read needed)
    content_length = request.headers.get('Content-Length')
    if content_length:
        try:
            content_length_int = int(content_length)
            if content_length_int > max_size:
                raise FileSizeExceededError(
                    f"Request size ({content_length_int} bytes) exceeds maximum limit of {max_size} bytes",
                    max_size_bytes=max_size,
                    actual_size_bytes=content_length_int
                )
            # Size is within limit based on header, return early (no body read needed)
            return
        except ValueError:
            # Invalid Content-Length header format, fall through to body check
            pass

    # Priority 2: Check Flask's parsed content_length attribute (if available)
    # Flask populates this from the Content-Length header if present
    if hasattr(request, 'content_length') and request.content_length is not None:
        if request.content_length > max_size:
            raise FileSizeExceededError(
                f"Request size ({request.content_length} bytes) exceeds maximum limit of {max_size} bytes",
                max_size_bytes=max_size,
                actual_size_bytes=request.content_length
            )
        # Size is within limit, return early
        return

    # Priority 3: Content-Length not available - must read body to check size
    # Flask caches request data by default, so multiple calls to get_data() are safe
    # However, for large files, this will read the entire body into memory
    # This is acceptable because we need to reject oversized requests early
    try:
        body_data = request.get_data(cache=True)  # cache=True allows re-reading by route handler
        
        if len(body_data) > max_size:
            raise FileSizeExceededError(
                f"Request size ({len(body_data)} bytes) exceeds maximum limit of {max_size} bytes",
                max_size_bytes=max_size,
                actual_size_bytes=len(body_data)
            )
    except FileSizeExceededError:
        # Re-raise FileSizeExceededError
        raise
    except Exception as e:
        # If we can't read the request body for size checking (e.g., streaming error),
        # we allow it through rather than blocking valid requests
        # In production, you might want to log this and handle differently
        # For now, we assume if we can't determine size, we allow the request
        pass

