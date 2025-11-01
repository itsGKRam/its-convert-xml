"""
XML-to-JSON conversion service.

This module provides functionality to convert XML data structures to JSON format,
preserving elements, attributes, namespaces, hierarchy, and data types.
"""

import json
from typing import Dict, Any, List, Union, Optional, Tuple
from lxml import etree

from app.services.xml_parser import parse_xml, parse_xml_streaming
from app.exceptions import XMLValidationError


def _extract_local_name_and_prefix(element: etree._Element) -> Tuple[str, Optional[str]]:
    """
    Extract local name and prefix from XML element.
    
    Args:
        element: XML element from lxml
        
    Returns:
        Tuple of (local_name, prefix)
    """
    tag = element.tag
    
    # Try to get prefix from element (lxml provides this for prefixed namespaces)
    prefix = element.prefix if hasattr(element, 'prefix') else None
    
    # Handle lxml's namespace format: "{namespace}localname"
    if tag.startswith("{") and "}" in tag:
        local_name = tag.split("}", 1)[1]
        # If we have a prefix from element.prefix, use it
        # Otherwise, it's a default namespace (prefix is None)
        return local_name, prefix
    
    # Handle prefixed namespace: "prefix:localname" (shouldn't happen with lxml, but handle it)
    if ":" in tag:
        prefix, local_name = tag.split(":", 1)
        return local_name, prefix
    
    # No namespace
    return tag, None


def _get_prefix_from_namespace(element: etree._Element, namespace_uri: str) -> Optional[str]:
    """
    Get prefix for a namespace URI by looking up in element's namespace map.
    
    Args:
        element: XML element
        namespace_uri: Namespace URI to find prefix for
        
    Returns:
        Prefix string or None if not found
    """
    nsmap = element.getroottree().getroot().nsmap if hasattr(element, 'getroottree') else getattr(element, 'nsmap', {})
    if nsmap:
        # Look for namespace URI in the map (reverse lookup)
        for prefix, uri in nsmap.items():
            if uri == namespace_uri:
                return prefix if prefix is not None else None
    return None


def convert_xml_to_json(xml_root: etree._Element) -> Dict[str, Any]:
    """
    Convert parsed XML element tree to JSON-serializable dictionary.

    Transforms XML elements, attributes, text content, and namespaces into
    a nested JSON structure. Handles multiple elements with the same name
    by converting them to arrays, preserves data types, and maintains
    namespace information in the format:
    - Element keys use local names only (no namespace prefix)
    - _prefix field contains the namespace prefix
    - Attributes use attrname as key with _prefix and _value inside
    - Text content uses _text field
    - Namespace declarations use _xmlns:prefix format

    Args:
        xml_root (etree._Element): Root element of parsed XML tree

    Returns:
        Dict[str, Any]: JSON-serializable dictionary representing XML structure.
            Root element local name becomes the top-level key.
    """
    element_dict = _element_to_dict(xml_root)
    # Get root local name (without namespace prefix)
    root_local_name, _ = _extract_local_name_and_prefix(xml_root)
    return {root_local_name: element_dict}


def _element_to_dict(element: etree._Element) -> Dict[str, Any]:
    """
    Recursively convert XML element to dictionary.

    Args:
        element (etree._Element): XML element to convert

    Returns:
        Dict[str, Any]: Dictionary representation with format:
            - Local name as keys (no namespace prefix)
            - _prefix field for namespace prefix
            - Attributes: attrname as key with _prefix and _value inside
            - _text for text content
            - _xmlns:prefix for namespace declarations
    """
    # Extract local name and prefix from element
    local_name, prefix = _extract_local_name_and_prefix(element)
    
    # Build result dictionary
    result: Dict[str, Any] = {}
    
    # Add _prefix field if prefix exists
    if prefix:
        result["_prefix"] = prefix
    
    # Get text content (direct text, not from children)
    text_content = (element.text or "").strip()

    # Get all child elements
    children = list(element)

    # Handle namespace declarations first (before regular attributes)
    # lxml doesn't include xmlns in element.attrib, but we can detect them
    # by comparing element's nsmap with parent's nsmap
    element_nsmap = getattr(element, 'nsmap', {}) or {}
    
    # Get parent's nsmap for comparison
    parent_nsmap = {}
    parent = element.getparent()
    if parent is not None:
        parent_nsmap = getattr(parent, 'nsmap', {}) or {}
    elif element == element.getroottree().getroot() if hasattr(element, 'getroottree') else element:
        # This is the root element - all namespaces in its nsmap are declared on it
        parent_nsmap = {}
    
    xmlns_attrs = set()  # Keep for consistency, though we won't use it for xmlns
    
    # Find namespaces declared on this element (in element_nsmap but not in parent_nsmap)
    for ns_prefix, ns_uri in element_nsmap.items():
        # Check if this namespace is declared on this element (not inherited)
        if ns_prefix not in parent_nsmap or parent_nsmap.get(ns_prefix) != ns_uri:
            if ns_prefix is None:
                # Default namespace
                result["_xmlns"] = ns_uri
        else:
                result[f"_xmlns:{ns_prefix}"] = ns_uri
    
    # Handle attributes - store as attrname with prefix and value inside
    # (xmlns attributes are not in element.attrib, they're handled above via nsmap)
    for attr_name, attr_value in element.attrib.items():
            
        # Extract prefix from attribute name if it has one
        # lxml stores namespaced attributes as "{namespace}attrname"
        attr_prefix = None
        attr_local_name = attr_name
        
        # Check if attribute has namespace in format "{namespace}attrname"
        if attr_name.startswith("{") and "}" in attr_name:
            # Namespace-qualified attribute: "{namespace}attrname"
            namespace_uri, attr_local_name = attr_name[1:].split("}", 1)
            # Find prefix for this namespace URI from element's namespace map
            element_nsmap_for_attr = getattr(element, 'nsmap', {}) or {}
            # Reverse lookup: find prefix for this URI
            for ns_prefix, ns_uri in element_nsmap_for_attr.items():
                if ns_uri == namespace_uri:
                    attr_prefix = ns_prefix if ns_prefix is not None else None
                    break
        elif ":" in attr_name:
            # Prefixed attribute (shouldn't happen with lxml, but handle it): "prefix:attrname"
            attr_prefix, attr_local_name = attr_name.split(":", 1)
        
        # Store attribute as object with prefix and value
        attr_obj: Dict[str, Any] = {"_value": attr_value}

        # Only use the attribute's own prefix (don't inherit from element)
        # In XML, unprefixed attributes are in "no namespace", not in element's namespace
        if attr_prefix:
            attr_obj["_prefix"] = attr_prefix
        
        # Use local name as the key (attrname as main key)
        result[attr_local_name] = attr_obj
    
    # Process children - use local names as keys
    for child in children:
        child_dict = _element_to_dict(child)
        child_local_name, _ = _extract_local_name_and_prefix(child)

        # If tag already exists, convert to array (multiple elements with same local name)
        if child_local_name in result:
            # Convert existing value to array if not already
            if not isinstance(result[child_local_name], list):
                result[child_local_name] = [result[child_local_name]]
            result[child_local_name].append(child_dict)
        else:
            result[child_local_name] = child_dict

    # Handle text content - always use _text field
    # Keep all text as strings to match the requested format
    if text_content:
        result["_text"] = text_content

    return result


def _preserve_data_types(value: str) -> Union[str, int, float, bool]:
    """
    Attempt to preserve data types when converting text content.

    Tries to convert string values to appropriate Python types (int, float, bool)
    while preserving as string if conversion doesn't make sense.

    Args:
        value (str): Text value from XML (already stripped)

    Returns:
        Union[str, int, float, bool]: Converted value with preserved type
    """
    if not value:
        return value

    # Try boolean detection (common XML/JSON patterns)
    value_lower = value.lower()
    if value_lower in ("true", "false"):
        return value_lower == "true"

    # Try integer (only if no decimal point)
    # But preserve leading zeros as strings (e.g., "007", "01")
    try:
        if "." not in value and "e" not in value_lower and "E" not in value:
            # Check for leading zeros (preserve as string)
            stripped = value.lstrip("-+")
            if stripped.startswith("0") and len(stripped) > 1 and stripped != "0":
                # Has leading zeros and not just "0", preserve as string
                return value
            
            int_val = int(value)
            # Verify it's not just a number that happened to parse as int
            # but should be a string
            if value.lstrip("-+").lstrip("0") == str(int_val).lstrip("-").lstrip("0") or value == "0":
                return int_val
    except ValueError:
        pass

    # Try float
    try:
        float_val = float(value)
        # Check if it's actually a float (not just an int)
        if "." in value or "e" in value_lower or "E" in value:
            return float_val
        # If it's an integer-looking float, return as int
        if float_val.is_integer():
            return int(float_val)
    except ValueError:
        pass

    # Return as string if no conversion works
    return value


def convert_xml_string_to_json(xml_string: str, use_streaming: bool = None) -> Dict[str, Any]:
    """
    Convert XML string to JSON-serializable dictionary.

    Wrapper function that first parses XML string using parse_xml() or
    parse_xml_streaming() based on file size, then converts the parsed XML
    tree to JSON using convert_xml_to_json(). Handles XMLValidationError
    exceptions from parsing.

    Args:
        xml_string (str): XML content as a string
        use_streaming (bool, optional): Force use of streaming parser.
            If None (default), automatically chooses based on file size:
            - Files > 10MB: uses streaming parser
            - Files <= 10MB: uses standard parser

    Returns:
        Dict[str, Any]: JSON-serializable dictionary representing XML structure

    Raises:
        XMLValidationError: If XML string is malformed or invalid (from parsing)

    Example:
        xml_str = '<root><child>value</child></root>'
        result = convert_xml_string_to_json(xml_str)
        # Returns: {"root": {"child": "value"}}
    """
    try:
        # Determine whether to use streaming parser
        # Default threshold: 10MB (10485760 bytes) for switching to streaming
        STREAMING_THRESHOLD = 10 * 1024 * 1024  # 10MB in bytes
        
        if use_streaming is None:
            # Auto-detect: use streaming for large files
            use_streaming = len(xml_string.encode('utf-8')) > STREAMING_THRESHOLD
        elif use_streaming:
            # Explicitly requested streaming
            use_streaming = True
        
        # Parse XML using appropriate method
        if use_streaming:
            xml_root = parse_xml_streaming(xml_string)
        else:
            xml_root = parse_xml(xml_string)
        
        # Convert to JSON (same process regardless of parsing method)
        return convert_xml_to_json(xml_root)
    except XMLValidationError:
        # Re-raise XMLValidationError with original details
        raise
    except Exception as e:
        # Wrap unexpected errors
        raise XMLValidationError(f"Failed to convert XML to JSON: {str(e)}")

