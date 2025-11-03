"""
Conversion route handlers.

This module contains route handlers for XML conversion endpoints,
including the health check endpoint.
"""

import logging
import time
import json
from flask import Blueprint, jsonify, request, Response
from app.services.json_converter import convert_xml_string_to_json
from app.services.csv_converter import convert_xml_string_to_csv, convert_xml_string_to_csv_by_xpath
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


@convert_bp.route('/convert/xml-to-csv', methods=['POST'])
def convert_xml_to_csv():
    """
    POST endpoint for converting XML to CSV.

    Accepts XML data in request body, validates Content-Type header,
    calls the conversion service, and returns CSV response.
    
    Query Parameters:
        - delimiter (optional): CSV delimiter character (default: ','). 
          Must be a single character. Common options: ',' (comma), ';' (semicolon), 
          '\\t' (tab), '|' (pipe)

    Returns:
        tuple: CSV response and HTTP status code (200 OK on success)
            or error response with appropriate HTTP status code

    Error Responses:
        - 413 Payload Too Large: Request size exceeds maximum limit (300MB)
        - 400 Bad Request: Invalid or missing Content-Type header
        - 400 Bad Request: Malformed XML (XMLValidationError)
        - 400 Bad Request: Invalid delimiter (must be single character)
        - 500 Internal Server Error: Unexpected server error
    
    Example:
        # Default comma delimiter
        POST /convert/xml-to-csv?delimiter=,
        
        # Semicolon delimiter (for European CSV format)
        POST /convert/xml-to-csv?delimiter=;
        
        # Tab delimiter
        POST /convert/xml-to-csv?delimiter=\\t
    """
    endpoint = '/convert/xml-to-csv'
    
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

    # Extract delimiter from query parameters (default: comma)
    delimiter = request.args.get('delimiter', ',')
    
    # Validate delimiter is a single character
    if len(delimiter) != 1:
        logger.warning(
            f"Invalid delimiter: endpoint={endpoint}, delimiter={delimiter}"
        )
        return format_error_response(
            code="INVALID_DELIMITER",
            message="Delimiter must be a single character",
            details=f"Received delimiter: {delimiter}. Common options: ',' (comma), ';' (semicolon), '\\t' (tab), '|' (pipe)",
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
        
        # Perform conversion with specified delimiter
        csv_result = convert_xml_string_to_csv(xml_string, delimiter=delimiter)
        
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
        
        # Create response with CSV content and proper Content-Type header
        response = Response(csv_result, mimetype='text/csv')
        response.headers['Content-Type'] = 'text/csv'
        
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
    except ValueError as e:
        # Handle delimiter validation errors (CSV endpoint only)
        if "Delimiter" in str(e):
            logger.warning(
                f"Delimiter validation error: endpoint={endpoint}, "
                f"error={str(e)}"
            )
            return format_error_response(
                code="INVALID_DELIMITER",
                message="Invalid delimiter specified",
                details=str(e),
                status_code=400
            )
        # Re-raise if it's a different ValueError
        raise
    except Exception as e:
        # Handle unexpected errors - log full details but return sanitized message
        logger.error(
            f"Unexpected server error: endpoint={endpoint}, "
            f"error={str(e)}",
            exc_info=True
        )
        return format_server_error(str(e))


@convert_bp.route('/convert/xml-to-csv-xpath', methods=['POST'])
def convert_xml_to_csv_xpath():
    """
    POST endpoint for converting XML to CSV using XPath to select specific elements.
    
    Uses XPath to extract only the specified array of items, excluding header/metadata.
    Returns one CSV row per element matched by the XPath expression.
    
    Query Parameters:
        - xpath (required): XPath expression to select elements (e.g., "//wd:Job_Requisition")
        - delimiter (optional): CSV delimiter character (default: ','). Must be a single character.
        - namespaces (optional): JSON-encoded namespace mapping for XPath (e.g., {"wd": "urn:com.workday/bsvc"})
        - path_separator (optional): Character(s) to separate nested path segments in column names (default: '/'). 
          Examples: '/' for "parent/child", '//' for "parent//child", '_' for "parent_child", '-' for "parent-child"
    
    Request Body:
        - Raw XML content (application/xml or text/xml)
    
    Returns:
        tuple: CSV response and HTTP status code (200 OK on success)
            or error response with appropriate HTTP status code
    
    Error Responses:
        - 400 Bad Request: Missing or invalid XPath expression
        - 400 Bad Request: Invalid delimiter (must be single character)
        - 400 Bad Request: Malformed XML (XMLValidationError)
        - 413 Payload Too Large: Request size exceeds maximum limit (300MB)
        - 400 Bad Request: Invalid or missing Content-Type header
        - 500 Internal Server Error: Unexpected server error
    
    Example:
        # Extract all Job_Requisition elements
        POST /convert/xml-to-csv-xpath?xpath=//wd:Job_Requisition&namespaces={"wd":"urn:com.workday/bsvc"}
        
        # Extract all item elements with default comma delimiter
        POST /convert/xml-to-csv-xpath?xpath=//item
        
        # Extract with semicolon delimiter
        POST /convert/xml-to-csv-xpath?xpath=//item&delimiter=;
    """
    endpoint = '/convert/xml-to-csv-xpath'
    
    # Log request received
    content_type = request.headers.get('Content-Type', 'missing')
    content_length = request.headers.get('Content-Length', 'unknown')
    logger.info(
        f"Request received: endpoint={endpoint}, "
        f"Content-Type={content_type}, Content-Length={content_length}"
    )
    
    # Extract XPath from query parameters (required)
    # Try lowercase first, then case-insensitive search
    xpath = request.args.get('xpath', '').strip()
    if not xpath:
        # Try case-insensitive search for common variations
        for key in request.args.keys():
            if key.lower() == 'xpath':
                xpath = request.args.get(key, '').strip()
                break
    
    if not xpath:
        logger.warning(
            f"Missing XPath parameter: endpoint={endpoint}"
        )
        return format_error_response(
            code="MISSING_XPATH",
            message="XPath parameter is required",
            details="Please provide an XPath expression via ?xpath= query parameter (e.g., ?xpath=//item). Send XML content in the request body.",
            status_code=400
        )
    
    # Extract delimiter from query parameters (optional, default: comma)
    delimiter = request.args.get('delimiter', ',')
    
    # Validate delimiter is a single character
    if len(delimiter) != 1:
        logger.warning(
            f"Invalid delimiter: endpoint={endpoint}, delimiter={delimiter}"
        )
        return format_error_response(
            code="INVALID_DELIMITER",
            message="Delimiter must be a single character",
            details=f"Received delimiter: {delimiter}. Common options: ',' (comma), ';' (semicolon), '\\t' (tab), '|' (pipe)",
            status_code=400
        )
    
    # Extract namespaces from query parameters (optional, JSON-encoded)
    namespaces = None
    namespaces_str = request.args.get('namespaces', '').strip()
    if namespaces_str:
        try:
            namespaces = json.loads(namespaces_str)
            if not isinstance(namespaces, dict):
                return format_error_response(
                    code="INVALID_NAMESPACES",
                    message="Namespaces must be a valid JSON object",
                    details="Expected format: {\"prefix\": \"uri\"} (e.g., {\"wd\": \"urn:com.workday/bsvc\"})",
                    status_code=400
                )
        except json.JSONDecodeError as e:
            return format_error_response(
                code="INVALID_NAMESPACES",
                message="Invalid JSON in namespaces parameter",
                details=str(e),
                status_code=400
            )
    
    # Extract path separator from query parameters (optional, default: slash)
    path_separator = request.args.get('path_separator', '/')
    # Validate path separator is 1-2 characters (allow for // double slash)
    if len(path_separator) == 0 or len(path_separator) > 2:
        logger.warning(
            f"Invalid path separator: endpoint={endpoint}, path_separator={path_separator}"
        )
        return format_error_response(
            code="INVALID_PATH_SEPARATOR",
            message="Path separator must be 1-2 characters",
            details=f"Received path_separator: {path_separator}. Common options: '/' (slash - default), '//' (double slash), '_' (underscore), '-' (dash), '.' (dot)",
            status_code=400
        )
    
    # Extract XML string from request body (raw XML content)
    try:
        xml_string = request.get_data(as_text=True)
        if not xml_string or not xml_string.strip():
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
    
    # Validate request size BEFORE any processing
    try:
        validate_request_size(request)
    except FileSizeExceededError as e:
        logger.warning(
            f"Request size exceeded limit: endpoint={endpoint}, "
            f"max_size={e.max_size_bytes}, actual_size={e.actual_size_bytes}"
        )
        return format_file_size_error(max_size_mb=300)
    
    # Validate Content-Type header (should be XML)
    content_type_lower = content_type.lower()
    if content_type_lower not in ['application/xml', 'text/xml']:
        logger.warning(
            f"Content-Type validation failed: endpoint={endpoint}, "
            f"received={content_type}"
        )
        return format_content_type_error(content_type)
    
    # Call conversion service and handle errors
    try:
        # Performance monitoring: record start time and file size
        start_time = time.time()
        file_size_bytes = len(xml_string.encode('utf-8'))
        
        # Track memory usage before processing (if available)
        memory_before = None
        try:
            import psutil
            process = psutil.Process()
            memory_before = process.memory_info().rss / (1024 * 1024)  # MB
        except ImportError:
            pass
        except Exception:
            pass
        
        # Perform conversion with XPath
        csv_result = convert_xml_string_to_csv_by_xpath(xml_string, xpath, delimiter=delimiter, namespaces=namespaces, path_separator=path_separator)
        
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
        
        # Create response with CSV content and proper Content-Type header
        response = Response(csv_result, mimetype='text/csv')
        response.headers['Content-Type'] = 'text/csv'
        
        # Log performance metrics using structured logging
        log_data = {
            'endpoint': endpoint,
            'xpath': xpath,
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
        
        # Count rows in output
        if csv_result:
            row_count = len([line for line in csv_result.split('\n') if line.strip()]) - 1  # -1 for header
            log_data['rows_extracted'] = row_count
        
        # Format log message
        log_parts = [f"{k}={v}" for k, v in log_data.items()]
        logger.info(f"Conversion successful: {', '.join(log_parts)}")
        
        return response, 200
    except XMLValidationError as e:
        # Handle XML validation errors (malformed XML or invalid XPath)
        logger.warning(
            f"XML validation/XPath error: endpoint={endpoint}, "
            f"error={str(e)}, xpath={xpath}, line={getattr(e, 'line', None)}, column={getattr(e, 'column', None)}"
        )
        # Check if it's an XPath error or XML parsing error
        if "XPath" in str(e) or "xpath" in str(e).lower():
            return format_error_response(
                code="XPATH_ERROR",
                message="XPath evaluation failed",
                details=str(e),
                status_code=400
            )
        return format_xml_validation_error(e)
    except ValueError as e:
        # Handle delimiter validation errors
        if "Delimiter" in str(e):
            logger.warning(
                f"Delimiter validation error: endpoint={endpoint}, "
                f"error={str(e)}"
            )
            return format_error_response(
                code="INVALID_DELIMITER",
                message="Invalid delimiter specified",
                details=str(e),
                status_code=400
            )
        elif "XPath" in str(e):
            logger.warning(
                f"XPath validation error: endpoint={endpoint}, "
                f"error={str(e)}"
            )
            return format_error_response(
                code="INVALID_XPATH",
                message="Invalid XPath expression",
                details=str(e),
                status_code=400
            )
        # Re-raise if it's a different ValueError
        raise
    except Exception as e:
        # Handle unexpected errors - log full details but return sanitized message
        logger.error(
            f"Unexpected server error: endpoint={endpoint}, "
            f"error={str(e)}, xpath={xpath}",
            exc_info=True
        )
        return format_server_error(str(e))

