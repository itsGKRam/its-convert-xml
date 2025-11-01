"""
Conversion route handlers.

This module contains route handlers for XML conversion endpoints,
including the health check endpoint.
"""

import logging
import time
from flask import Blueprint, jsonify, request
from app.services.json_converter import convert_xml_string_to_json
from app.exceptions import XMLValidationError
from app.utils.validators import (
    format_content_type_error,
    format_xml_validation_error,
    format_server_error,
    format_file_size_error,
    EMPTY_REQUEST_BODY,
    REQUEST_READ_ERROR,
    format_error_response,
    validate_request_size
)
from app.exceptions import FileSizeExceededError

logger = logging.getLogger(__name__)
convert_bp = Blueprint('convert', __name__)


@convert_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.

    Returns a simple JSON status response for monitoring and orchestration
    platforms (Kubernetes, ECS, etc.).

    Returns:
        tuple: JSON response and HTTP status code (200 OK)
    """
    return jsonify({"status": "healthy"}), 200


@convert_bp.route('/convert/xml-to-json', methods=['POST'])
def convert_xml_to_json():
    """
    POST endpoint for converting XML to JSON.

    Accepts XML data in request body, validates Content-Type header,
    calls the conversion service, and returns JSON response.

    Returns:
        tuple: JSON response and HTTP status code (200 OK on success)
            or error response with appropriate HTTP status code

    Error Responses:
        - 413 Payload Too Large: Request size exceeds maximum limit (300MB)
        - 400 Bad Request: Invalid or missing Content-Type header
        - 400 Bad Request: Malformed XML (XMLValidationError)
        - 500 Internal Server Error: Unexpected server error
    """
    endpoint = '/convert/xml-to-json'
    
    # Log request received
    content_type = request.headers.get('Content-Type', 'missing')
    content_length = request.headers.get('Content-Length', 'unknown')
    logger.info(
        f"Request received: endpoint={endpoint}, "
        f"Content-Type={content_type}, Content-Length={content_length}"
    )

    # Validate request size BEFORE any processing (early rejection to save resources)
    try:
        validate_request_size(request)
    except FileSizeExceededError as e:
        logger.warning(
            f"Request size exceeded limit: endpoint={endpoint}, "
            f"max_size={e.max_size_bytes}, actual_size={e.actual_size_bytes}"
        )
        # Return HTTP 413 (Payload Too Large) with structured error format
        return format_file_size_error(max_size_mb=300)

    # Validate Content-Type header
    content_type_lower = content_type.lower()
    if content_type_lower not in ['application/xml', 'text/xml']:
        logger.warning(
            f"Content-Type validation failed: endpoint={endpoint}, "
            f"received={content_type}"
        )
        return format_content_type_error(content_type)

    # Extract XML string from request body
    try:
        xml_string = request.get_data(as_text=True)
        if not xml_string:
            logger.warning(
                f"Empty request body: endpoint={endpoint}"
            )
            return format_error_response(
                code=EMPTY_REQUEST_BODY,
                message="Request body is empty",
                details="XML content is required in the request body",
                status_code=400
            )
    except Exception as e:
        logger.error(
            f"Failed to read request body: endpoint={endpoint}, "
            f"error={str(e)}",
            exc_info=True
        )
        return format_error_response(
            code=REQUEST_READ_ERROR,
            message="Failed to read request body",
            details=str(e),
            status_code=400
        )

    # Call conversion service and handle errors
    try:
        # Performance monitoring: record start time and file size
        start_time = time.time()
        file_size_bytes = len(xml_string.encode('utf-8'))
        
        # Track memory usage before processing (if available)
        memory_before = None
        try:
            # Try to get memory usage using psutil if available, otherwise skip
            # We don't want to make it a hard dependency, so we handle ImportError
            import psutil
            process = psutil.Process()
            memory_before = process.memory_info().rss / (1024 * 1024)  # MB
        except ImportError:
            # psutil not available, skip memory tracking
            pass
        except Exception:
            # Any other error, skip memory tracking
            pass
        
        # Perform conversion
        json_result = convert_xml_string_to_json(xml_string)
        
        # Calculate performance metrics
        processing_time = time.time() - start_time
        
        # Track memory usage after processing (if available)
        memory_after = None
        memory_delta = None
        try:
            import psutil
            process = psutil.Process()
            memory_after = process.memory_info().rss / (1024 * 1024)  # MB
            if memory_before is not None:
                memory_delta = memory_after - memory_before
        except ImportError:
            pass
        except Exception:
            pass
        
        # Create response
        response = jsonify(json_result)
        response.headers['Content-Type'] = 'application/json'
        
        # Log performance metrics using structured logging
        log_data = {
            'endpoint': endpoint,
            'file_size_bytes': file_size_bytes,
            'processing_time_seconds': round(processing_time, 3),
            'status': 'success'
        }
        
        # Add memory metrics if available
        if memory_before is not None:
            log_data['memory_before_mb'] = round(memory_before, 2)
        if memory_after is not None:
            log_data['memory_after_mb'] = round(memory_after, 2)
        if memory_delta is not None:
            log_data['memory_delta_mb'] = round(memory_delta, 2)
        
        # Format log message
        log_parts = [f"{k}={v}" for k, v in log_data.items()]
        logger.info(f"Conversion successful: {', '.join(log_parts)}")
        
        return response, 200
    except XMLValidationError as e:
        # Handle XML validation errors (malformed XML)
        logger.warning(
            f"XML validation error: endpoint={endpoint}, "
            f"error={str(e)}, line={e.line}, column={e.column}"
        )
        return format_xml_validation_error(e)
    except Exception as e:
        # Handle unexpected errors - log full details but return sanitized message
        logger.error(
            f"Unexpected server error: endpoint={endpoint}, "
            f"error={str(e)}",
            exc_info=True
        )
        return format_server_error(str(e))

