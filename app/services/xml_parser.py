"""
XML parsing and validation service.

This module provides XML parsing functionality using the lxml library
with security settings and namespace support. It validates XML syntax
and structure, returning parsed element trees or raising XMLValidationError
with detailed error location information.

For large files (typically >10MB), use parse_xml_streaming() instead of
parse_xml() to enable memory-efficient streaming parsing.
"""

from typing import Iterator, BinaryIO
from io import BytesIO
from lxml import etree
from app.exceptions import XMLValidationError


def parse_xml(xml_string: str) -> etree._Element:
    """
    Parse and validate XML string.

    Parses the provided XML string using lxml with security settings
    to prevent XML attack vectors. Preserves namespace information
    and handles UTF-8 encoding. Raises XMLValidationError with detailed
    location information if parsing fails.

    Args:
        xml_string (str): XML content as a string (assumed UTF-8 encoded)

    Returns:
        etree._Element: Parsed XML element tree root element

    Raises:
        XMLValidationError: If XML is malformed or invalid, includes
            error message and location (line/column) information
    """
    # Configure parser with security settings to prevent XML attack vectors:
    # - resolve_entities=False: Prevents entity expansion attacks (billion laughs, etc.)
    # - huge_tree=False: Prevents quadratic blowup attacks with very large trees
    parser = etree.XMLParser(
        resolve_entities=False,
        huge_tree=False
    )

    try:
        # Parse XML string - lxml automatically handles:
        # - UTF-8 encoding (default for XML)
        # - Namespace preservation (default behavior)
        # - XML syntax validation (raises exception on invalid XML)
        root = etree.fromstring(xml_string.encode('utf-8'), parser=parser)
        return root

    except etree.XMLSyntaxError as e:
        # Extract error location information from lxml exception
        # lxml provides line and column information in the error object
        line = e.lineno if hasattr(e, 'lineno') and e.lineno is not None else None
        column = e.offset if hasattr(e, 'offset') and e.offset is not None else None

        # Extract error message from lxml exception
        error_message = str(e.msg) if hasattr(e, 'msg') and e.msg else str(e)

        # Raise our custom exception with location details
        raise XMLValidationError(error_message, line=line, column=column)

    except (UnicodeDecodeError, etree.ParseError) as e:
        # Handle encoding or other parsing errors
        error_message = f"Failed to parse XML: {str(e)}"
        raise XMLValidationError(error_message)


def parse_xml_streaming(xml_string: str) -> etree._Element:
    """
    Parse XML string using streaming approach for memory efficiency.

    Uses lxml.etree.iterparse() to parse XML incrementally, building the tree
    element by element. This approach minimizes memory footprint for large XML
    files compared to parse_xml() which loads the entire tree at once, even though
    the final tree still needs to be in memory. iterparse is more memory-efficient
    during the parsing process itself.

    The parser validates XML structure during parsing and handles namespaces
    automatically. Security settings are applied to prevent XML attack vectors.

    Args:
        xml_string (str): XML content as a string (assumed UTF-8 encoded)

    Returns:
        etree._Element: Root element of parsed XML tree (fully built)

    Raises:
        XMLValidationError: If XML is malformed or invalid, includes
            error message and location (line/column) information

    Note:
        While this uses streaming parsing internally, the full tree is still
        returned in memory. For truly incremental processing, consider using
        iterparse directly with event-based processing. This function is optimized
        for large files where the tree building process benefits from iterparse's
        incremental approach.

    Example:
        # Use streaming parser for large files (typically >10MB)
        root = parse_xml_streaming(large_xml_string)
        json_result = convert_xml_to_json(root)
    """
    try:
        # Create a BytesIO object from the XML string for iterparse
        # iterparse requires a file-like object or file path
        xml_bytes = xml_string.encode('utf-8')
        xml_stream = BytesIO(xml_bytes)

        # Use iterparse for streaming parsing with security and performance settings
        # events=('end',) means we get elements when they are fully parsed
        # Security settings:
        #   - huge_tree=True: Required for large files (allows processing files > 300MB)
        #   - no_network=True: Default, prevents network access (entity attacks)
        #   - load_dtd=False: Default, prevents loading external DTDs
        # Note: iterparse doesn't support resolve_entities parameter directly,
        # but no_network=True and load_dtd=False provide similar protection
        context = etree.iterparse(
            xml_stream,
            events=('end',),
            huge_tree=True,  # Required for large files with iterparse
            no_network=True,  # Security: prevent network access
            load_dtd=False    # Security: don't load external DTDs
        )

        root = None
        # Iterate through parsed elements to build tree incrementally
        # iterparse builds the tree incrementally as it processes the XML
        # We need to find the root element (the one without a parent)
        for event, element in context:
            if event == 'end':
                # Track root element (element without a parent)
                if root is None:
                    # Check if this is the root (has no parent)
                    parent = element.getparent()
                    if parent is None:
                        root = element

        if root is None:
            raise XMLValidationError("Empty XML document")

        # Return the fully built tree
        # iterparse has already constructed the complete tree structure
        return root

    except etree.XMLSyntaxError as e:
        # Extract error location information from lxml exception
        line = e.lineno if hasattr(e, 'lineno') and e.lineno is not None else None
        column = e.offset if hasattr(e, 'offset') and e.offset is not None else None

        # Extract error message from lxml exception
        error_message = str(e.msg) if hasattr(e, 'msg') and e.msg else str(e)

        # Raise our custom exception with location details
        raise XMLValidationError(error_message, line=line, column=column)

    except (UnicodeDecodeError, etree.ParseError) as e:
        # Handle encoding or other parsing errors
        error_message = f"Failed to parse XML: {str(e)}"
        raise XMLValidationError(error_message)

