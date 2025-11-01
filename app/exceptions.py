"""
Custom exception classes for the application.

This module defines custom exception classes that will be used
for error handling across the application.
"""


class XMLValidationError(Exception):
    """
    Exception raised when XML parsing or validation fails.

    This exception includes detailed error information including
    the error message, line number, and column number for actionable
    error reporting.

    Attributes:
        message (str): Human-readable error message describing the validation failure
        line (int, optional): Line number where the error occurred (1-indexed)
        column (int, optional): Column number where the error occurred (1-indexed)
    """

    def __init__(self, message: str, line: int = None, column: int = None):
        """
        Initialize XMLValidationError.

        Args:
            message (str): Error message describing the validation failure
            line (int, optional): Line number where error occurred (1-indexed)
            column (int, optional): Column number where error occurred (1-indexed)
        """
        self.message = message
        self.line = line
        self.column = column

        # Format error message with location if available
        if line is not None and column is not None:
            error_msg = f"Invalid XML syntax at line {line}, column {column}: {message}"
        elif line is not None:
            error_msg = f"Invalid XML syntax at line {line}: {message}"
        else:
            error_msg = f"Invalid XML: {message}"

        super().__init__(error_msg)


class FileSizeExceededError(Exception):
    """
    Exception raised when request body size exceeds the maximum allowed limit.

    This exception is raised during request size validation to indicate
    that the Content-Length header or request body exceeds the configured
    maximum file size limit (default: 300MB).

    Attributes:
        message (str): Human-readable error message describing the size limit exceeded
        max_size_bytes (int): Maximum allowed size in bytes
        actual_size_bytes (int, optional): Actual size of the request in bytes
    """

    def __init__(self, message: str, max_size_bytes: int, actual_size_bytes: int = None):
        """
        Initialize FileSizeExceededError.

        Args:
            message (str): Error message describing the size limit exceeded
            max_size_bytes (int): Maximum allowed size in bytes
            actual_size_bytes (int, optional): Actual size of the request in bytes
        """
        self.message = message
        self.max_size_bytes = max_size_bytes
        self.actual_size_bytes = actual_size_bytes
        super().__init__(message)
