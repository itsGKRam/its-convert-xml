"""
XML-to-CSV conversion service.

This module provides functionality to convert XML data structures to CSV format,
handling flat and nested structures, preserving namespaces in column names,
and ensuring RFC 4180 compliance.
"""

import csv
import io
from typing import List, Dict, Any, Optional, Set
from lxml import etree

from app.services.xml_parser import parse_xml
from app.exceptions import XMLValidationError


def _extract_local_name_and_prefix(element: etree._Element) -> tuple[str, Optional[str]]:
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
        return local_name, prefix
    
    # Handle prefixed namespace: "prefix:localname" (shouldn't happen with lxml, but handle it)
    if ":" in tag:
        prefix, local_name = tag.split(":", 1)
        return local_name, prefix
    
    # No namespace
    return tag, None


def _get_namespace_prefix_for_column(element: etree._Element, namespace_uri: Optional[str]) -> Optional[str]:
    """
    Get prefix for a namespace URI for use in column names.
    
    Args:
        element: XML element
        namespace_uri: Namespace URI to find prefix for
        
    Returns:
        Prefix string or None if not found or default namespace
    """
    if not namespace_uri:
        return None
    
    nsmap = element.getroottree().getroot().nsmap if hasattr(element, 'getroottree') else getattr(element, 'nsmap', {})
    if nsmap:
        # Look for namespace URI in the map (reverse lookup)
        for prefix, uri in nsmap.items():
            if uri == namespace_uri:
                return prefix if prefix is not None else None
    return None


def _build_column_name(name: str, prefix: Optional[str], parent_path: str = "", path_separator: str = "/") -> str:
    """
    Build CSV column name from element/attribute name and namespace prefix.
    
    For nested structures, prepend parent path. For namespaces, include prefix.
    
    Args:
        name: Local name of element or attribute
        prefix: Namespace prefix (None for default or no namespace)
        parent_path: Path from root for nested structures (e.g., "parent_child" or "parent/child")
        path_separator: Character(s) to use when joining parent path to child name (default: "/", can be 1-2 chars like "//")
        
    Returns:
        Column name string
    """
    if prefix:
        col_name = f"{prefix}:{name}"
    else:
        col_name = name
    
    if parent_path:
        col_name = f"{parent_path}{path_separator}{col_name}"
    
    return col_name


def _collect_row_data_starting_from_children(element: etree._Element, parent_path: str = "", path_separator: str = "/") -> Dict[str, Any]:
    """
    Collect data from element's attributes and children into a dictionary row.
    
    This variant is used for XPath-matched elements where we want column headers
    to start from the matched element (parent). It includes:
    1. Attributes of the matched element (using @attribute_name format)
    2. Children of the matched element
    
    Args:
        element: XML element whose attributes and children to collect data from
        parent_path: Parent path for column headers (should be the matched element's name)
        path_separator: Character(s) to use when joining parent path to child name (default: "/")
        
    Returns:
        Dictionary with column names as keys and values
    """
    row = {}
    
    # Add attributes of the matched element (using @attribute_name format)
    local_name, prefix = _extract_local_name_and_prefix(element)
    for attr_name, attr_value in element.attrib.items():
        attr_local = attr_name
        attr_prefix = None
        
        if attr_name.startswith("{") and "}" in attr_name:
            namespace_uri, attr_local = attr_name[1:].split("}", 1)
            attr_prefix = _get_namespace_prefix_for_column(element, namespace_uri)
        
        # Build column name with @ prefix to indicate it's an attribute
        # Format: parent/@attribute_name (e.g., "item/@id" or "wd:Job_Requisition/@wd:ID")
        attr_base_name = _build_column_name(attr_local, attr_prefix, "", path_separator)
        col_name = f"{parent_path}{path_separator}@{attr_base_name}" if parent_path else f"@{attr_base_name}"
        row[col_name] = attr_value
    
    # Process children of the matched element
    children = list(element)
    
    for child in children:
        child_local, child_prefix = _extract_local_name_and_prefix(child)
        # Build path for nested columns starting from parent
        child_base_name = _build_column_name(child_local, child_prefix, "", path_separator)
        new_path = f"{parent_path}{path_separator}{child_base_name}" if parent_path else child_base_name
        
        # Recurse into child to collect its data
        child_data = _collect_row_data(child, new_path, path_separator)
        # Update row with child data (which already has proper column names with paths)
        row.update(child_data)
    
    return row


def _collect_row_data(element: etree._Element, path: str = "", path_separator: str = "/") -> Dict[str, Any]:
    """
    Collect data from a single element into a dictionary row.
    
    Args:
        element: XML element to collect data from
        path: Parent path for nested structures
        path_separator: Character(s) to use when joining parent path to child name (default: "/", can be 1-2 chars like "//")
        
    Returns:
        Dictionary with column names as keys and values
    """
    row = {}
    local_name, prefix = _extract_local_name_and_prefix(element)
    
    # Add attributes (using @attribute_name format)
    for attr_name, attr_value in element.attrib.items():
        attr_local = attr_name
        attr_prefix = None
        
        if attr_name.startswith("{") and "}" in attr_name:
            namespace_uri, attr_local = attr_name[1:].split("}", 1)
            attr_prefix = _get_namespace_prefix_for_column(element, namespace_uri)
        
        # Build column name with @ prefix to indicate it's an attribute
        # Format: path/@attribute_name (e.g., "item/@id" or "item/@wd:ID")
        attr_base_name = _build_column_name(attr_local, attr_prefix, "", path_separator)
        col_name = f"{path}{path_separator}@{attr_base_name}" if path else f"@{attr_base_name}"
        row[col_name] = attr_value
    
    # Add text content if element has no children
    children = list(element)
    text_content = (element.text or "").strip() if element.text else None
    
    if not children and text_content:
        col_name = _build_column_name(local_name, prefix, path, path_separator)
        row[col_name] = text_content
    
    # Process child elements (recurse for nested structures)
    for child in children:
        child_local, child_prefix = _extract_local_name_and_prefix(child)
        # Build path for nested columns
        child_base_name = _build_column_name(child_local, child_prefix, "", path_separator)
        new_path = f"{path}{path_separator}{child_base_name}" if path else child_base_name
        
        # Recurse into child to collect its data
        child_data = _collect_row_data(child, new_path, path_separator)
        # Update row with child data (which already has proper column names with paths)
        row.update(child_data)
    
    return row


def _flatten_element(element: etree._Element, parent_path: str = "", collected_data: List[Dict[str, Any]] = None, is_root: bool = False) -> List[Dict[str, Any]]:
    """
    Recursively flatten XML element into list of dictionaries (rows).
    
    Strategy:
    - Recursively traverse the tree
    - When encountering an element with multiple children of the same name: each child becomes a row (flat structure)
    - Otherwise: continue recursively to find flat structures deeper
    - Attributes become columns
    - Child elements (with text) become columns
    - Nested structures: column names use underscore separation
    
    Args:
        element: XML element to flatten
        parent_path: Path from root (for nested flattening)
        collected_data: List of row dictionaries (accumulated results)
        is_root: Whether this is the root element
        
    Returns:
        List of dictionaries, each representing a CSV row
    """
    if collected_data is None:
        collected_data = []
    
    children = list(element)
    
    # If no children, this is a leaf - handled by _collect_row_data
    if not children:
        # Leaf element - collect its data if it has content
        row = _collect_row_data(element, parent_path if not is_root else "", "_")
        if row:
            collected_data.append(row)
        return collected_data
    
    # Check if this element has multiple children with same name (flat structure)
    # Group children by element name (local name, ignoring namespace)
    children_by_name: Dict[str, List[etree._Element]] = {}
    for child in children:
        child_local, _ = _extract_local_name_and_prefix(child)
        if child_local not in children_by_name:
            children_by_name[child_local] = []
        children_by_name[child_local].append(child)
    
    # If we have multiple children with same name, treat as flat structure (rows)
    has_multiple_same = any(len(group) > 1 for group in children_by_name.values())
    
    if has_multiple_same:
        # Flat structure: each child element with same name becomes a row
        # First, collect parent's attributes if it has any
        parent_attrs = {}
        if element.attrib:
            local_name, prefix = _extract_local_name_and_prefix(element)
            for attr_name, attr_value in element.attrib.items():
                attr_local = attr_name
                attr_prefix = None
                if attr_name.startswith("{") and "}" in attr_name:
                    namespace_uri, attr_local = attr_name[1:].split("}", 1)
                    attr_prefix = _get_namespace_prefix_for_column(element, namespace_uri)
                attr_base_name = _build_column_name(attr_local, attr_prefix, "", "_")
                col_name = f"{parent_path}_@{attr_base_name}" if parent_path else f"@{attr_base_name}"
                parent_attrs[col_name] = attr_value
        
        for child_group_name, child_group in children_by_name.items():
            if len(child_group) > 1:
                # Multiple children with same name - each becomes a row
                # Use _collect_row_data to get all nested data flattened into columns
                # Don't recursively flatten - we want one row per child, with all nested data as columns
                for child in child_group:
                    child_row = _collect_row_data(child, parent_path, "_")
                    # Merge parent attributes with child data
                    if parent_attrs:
                        child_row = {**parent_attrs, **child_row}
                    if child_row:  # Only add non-empty rows
                        collected_data.append(child_row)
            else:
                # Single child in this group - but we have other groups with multiple
                # Still need to process this single child, but it becomes part of nested structure
                # Don't create a separate row for it since we're already in flat structure mode
                child = child_group[0]
                # Recursively check if this child has its own flat structure (deeper level)
                child_rows = _flatten_element(child, parent_path, [], is_root=False)
                if child_rows:
                    collected_data.extend(child_rows)
                else:
                    # No flat structure found in child - collect its data as nested columns
                    # But don't add as separate row since parent has flat structure
                    pass
        
        # If we found flat structure and collected rows, return them
        if collected_data:
            return collected_data
    
    # No flat structure at this level - recursively check children
    # This handles nested structures where flat structure is deeper
    for child in children:
        child_rows = _flatten_element(child, parent_path, [], is_root=False)
        if child_rows:
            # If child produced rows, merge element's attributes with each row
            if element.attrib:
                # Collect element's attributes
                local_name, prefix = _extract_local_name_and_prefix(element)
                element_attrs = {}
                for attr_name, attr_value in element.attrib.items():
                    attr_local = attr_name
                    attr_prefix = None
                    if attr_name.startswith("{") and "}" in attr_name:
                        namespace_uri, attr_local = attr_name[1:].split("}", 1)
                        attr_prefix = _get_namespace_prefix_for_column(element, namespace_uri)
                    attr_base_name = _build_column_name(attr_local, attr_prefix, "", "_")
                    col_name = f"{parent_path}_@{attr_base_name}" if parent_path else f"@{attr_base_name}"
                    element_attrs[col_name] = attr_value
                
                # Merge attributes into each child row
                for child_row in child_rows:
                    child_row.update(element_attrs)
            
            collected_data.extend(child_rows)
        else:
            # If child didn't produce rows, it's part of nested structure
            # Continue recursion but don't add intermediate rows
            pass
    
    # If we didn't find any flat structures in children, this might be a nested element
    # Only add as a row if we're at root and nothing was collected, or if this element has data
    if not collected_data or is_root:
        row = _collect_row_data(element, parent_path if not is_root else "", "_")
        # Only add if we have no rows yet (avoid duplicating nested data)
        if row and not collected_data:
            collected_data.append(row)
    
    return collected_data


def convert_xml_to_csv(xml_root: etree._Element, delimiter: str = ',') -> str:
    """
    Convert parsed XML element tree to CSV format string.
    
    Transforms XML elements into CSV rows and columns, handling:
    - Flat structures: rows as elements, columns as child elements or attributes
    - Nested structures: flattened using underscore-separated column names
    - Namespaces: included in column names as prefix:name
    - RFC 4180 compliance: proper escaping and quoting via Python csv module
    - Custom delimiters: supports comma (default), semicolon, tab, pipe, etc.
    
    Args:
        xml_root (etree._Element): Root element of parsed XML tree
        delimiter (str): CSV delimiter character (default: ','). Must be a single character.
        
    Returns:
        str: CSV-formatted string following RFC 4180 standard with specified delimiter
        
    Raises:
        ValueError: If delimiter is not a single character
        
    Example:
        XML: <root><row id="1"><name>Test</name></row></root>
        CSV (comma): id,name
                     1,Test
        CSV (semicolon): id;name
                         1;Test
    """
    # Validate delimiter is a single character
    if not delimiter or len(delimiter) != 1:
        raise ValueError(f"Delimiter must be a single character, got: {delimiter}")
    
    # Flatten XML into list of row dictionaries
    rows = _flatten_element(xml_root, is_root=True)
    
    if not rows:
        # Empty XML or no data rows
        return ""
    
    # Collect all unique column names from all rows in document order (first appearance)
    # Use OrderedDict to preserve insertion order (columns appear as 1, 2, 3, 4, 5... not 5, 4, 3, 2, 1)
    from collections import OrderedDict
    column_order = OrderedDict()
    for row in rows:
        for col_name in row.keys():
            if col_name not in column_order:
                column_order[col_name] = None
    
    # Convert to list preserving document order (order of first appearance)
    columns = list(column_order.keys())
    
    # Use StringIO to write CSV in memory
    output = io.StringIO()
    
    # Create CSV writer with RFC 4180 settings and custom delimiter
    writer = csv.writer(output, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
    
    # Write header row
    writer.writerow(columns)
    
    # Write data rows
    for row in rows:
        # Create row list with values in same order as columns
        # Missing values are empty strings
        row_values = [row.get(col, "") for col in columns]
        writer.writerow(row_values)
    
    # Return CSV string
    return output.getvalue()


def convert_xml_to_csv_by_xpath(xml_root: etree._Element, xpath: str, delimiter: str = ',', namespaces: Dict[str, str] = None, path_separator: str = '/') -> str:
    """
    Convert XML elements selected by XPath to CSV format string.
    
    Uses XPath to find all matching elements and converts each to a CSV row.
    This is useful when you want to extract only specific array items from XML,
    excluding header/metadata information.
    
    Args:
        xml_root (etree._Element): Root element of parsed XML tree
        xpath (str): XPath expression to select elements (e.g., "//wd:Job_Requisition")
        delimiter (str): CSV delimiter character (default: ','). Must be a single character.
        namespaces (Dict[str, str], optional): Namespace mapping for XPath (e.g., {"wd": "urn:com.workday/bsvc"})
        path_separator (str): Character to use when joining nested path segments in column names (default: '/')
        
    Returns:
        str: CSV-formatted string with one row per matched element
        
    Raises:
        ValueError: If delimiter is not a single character
        XMLValidationError: If XPath is invalid or no elements match
        
    Example:
        XML: <root><header>...</header><items><item id="1"><name>Test</name></item><item id="2"><name>Test2</name></item></items></root>
        XPath: "//item"
        CSV: id,name
             1,Test
             2,Test2
    """
    # Validate delimiter is a single character
    if not delimiter or len(delimiter) != 1:
        raise ValueError(f"Delimiter must be a single character, got: {delimiter}")
    
    # Validate XPath is provided
    if not xpath or not xpath.strip():
        raise ValueError("XPath expression is required")
    
    # Use provided namespaces or extract from root element
    if namespaces is None:
        # Try to extract namespaces from root element
        namespaces = {}
        if hasattr(xml_root, 'nsmap') and xml_root.nsmap:
            # lxml nsmap can have None key for default namespace, filter it out
            namespaces = {k if k else 'default': v for k, v in xml_root.nsmap.items() if k is not None}
    
    # Execute XPath query to find matching elements
    try:
        matched_elements = xml_root.xpath(xpath, namespaces=namespaces)
    except etree.XPathEvalError as e:
        raise XMLValidationError(f"Invalid XPath expression: {str(e)}")
    except Exception as e:
        raise XMLValidationError(f"XPath evaluation error: {str(e)}")
    
    # Check if any elements were found
    if not matched_elements:
        # Return empty CSV with just headers (if we can determine them) or empty string
        return ""
    
    # Convert each matched element to a row dictionary
    rows = []
    for element in matched_elements:
        # Handle different XPath result types
        if isinstance(element, etree._Element):
            # Check if element has children (parent element) or is a leaf (no children)
            children = list(element)
            
            if children:
                # Parent element: Start path with the matched element's name (parent of all headers)
                # This ensures column headers start from the matched XPath element, not root
                local_name, prefix = _extract_local_name_and_prefix(element)
                parent_path = _build_column_name(local_name, prefix, "", path_separator)
                # Collect data starting from this parent, but don't include the parent's own text/attrs in the row
                # Only process children - the parent name is already in the path
                row = _collect_row_data_starting_from_children(element, parent_path, path_separator)
            else:
                # Leaf element: Include the element's text content and attributes
                # This handles cases like: //element[@attr='value'] where element has no children
                local_name, prefix = _extract_local_name_and_prefix(element)
                parent_path = _build_column_name(local_name, prefix, "", path_separator)
                row = _collect_row_data(element, parent_path, path_separator)
            
            if row:  # Only add non-empty rows
                rows.append(row)
        elif isinstance(element, (str, bytes)):
            # XPath returned a string (e.g., attribute value or text)
            # Create a simple row with the matched value
            row = {"value": element if isinstance(element, str) else element.decode('utf-8')}
            rows.append(row)
        # Note: XPath can also return other types (numbers, booleans), but we'll handle those as strings
    
    if not rows:
        return ""
    
    # Collect all unique column names from all rows in document order (first appearance)
    # Use OrderedDict to preserve insertion order (columns appear as 1, 2, 3, 4, 5... not 5, 4, 3, 2, 1)
    from collections import OrderedDict
    column_order = OrderedDict()
    for row in rows:
        for col_name in row.keys():
            if col_name not in column_order:
                column_order[col_name] = None
    
    # Convert to list preserving document order (order of first appearance)
    columns = list(column_order.keys())
    
    # Use StringIO to write CSV in memory
    output = io.StringIO()
    
    # Create CSV writer with RFC 4180 settings and custom delimiter
    writer = csv.writer(output, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
    
    # Write header row
    writer.writerow(columns)
    
    # Write data rows
    for row in rows:
        # Create row list with values in same order as columns
        # Missing values are empty strings
        row_values = [row.get(col, "") for col in columns]
        writer.writerow(row_values)
    
    # Return CSV string
    return output.getvalue()


def convert_xml_string_to_csv(xml_string: str, delimiter: str = ',') -> str:
    """
    Convert XML string to CSV format string.
    
    Wrapper function that first parses XML string using parse_xml(),
    then converts the parsed XML tree to CSV using convert_xml_to_csv().
    Handles XMLValidationError exceptions from parsing.
    
    Args:
        xml_string (str): XML content as a string
        delimiter (str): CSV delimiter character (default: ','). Must be a single character.
        
    Returns:
        str: CSV-formatted string following RFC 4180 standard with specified delimiter
        
    Raises:
        XMLValidationError: If XML string is malformed or invalid (from parsing)
        ValueError: If delimiter is not a single character
        
    Example:
        xml_str = '<root><row id="1"><name>Test</name></row></root>'
        csv_str = convert_xml_string_to_csv(xml_str)
        # Returns: "id,name\\n1,Test\\n"
        csv_str = convert_xml_string_to_csv(xml_str, delimiter=';')
        # Returns: "id;name\\n1;Test\\n"
    """
    try:
        # Parse XML using xml_parser service
        xml_root = parse_xml(xml_string)
        
        # Convert to CSV with specified delimiter
        return convert_xml_to_csv(xml_root, delimiter=delimiter)
    except XMLValidationError:
        # Re-raise XMLValidationError with original details
        raise
    except ValueError:
        # Re-raise ValueError (delimiter validation error)
        raise
    except Exception as e:
        # Wrap unexpected errors
        raise XMLValidationError(f"Failed to convert XML to CSV: {str(e)}")


def convert_xml_string_to_csv_by_xpath(xml_string: str, xpath: str, delimiter: str = ',', namespaces: Dict[str, str] = None, path_separator: str = '/') -> str:
    """
    Convert XML string to CSV format using XPath to select specific elements.
    
    Wrapper function that first parses XML string using parse_xml(),
    then uses XPath to find matching elements and converts them to CSV.
    Handles XMLValidationError exceptions from parsing and XPath evaluation.
    
    Args:
        xml_string (str): XML content as a string
        xpath (str): XPath expression to select elements (e.g., "//wd:Job_Requisition")
        delimiter (str): CSV delimiter character (default: ','). Must be a single character.
        namespaces (Dict[str, str], optional): Namespace mapping for XPath
        path_separator (str): Character to use when joining nested path segments in column names (default: '/')
        
    Returns:
        str: CSV-formatted string with one row per XPath-matched element
        
    Raises:
        XMLValidationError: If XML string is malformed or XPath is invalid
        ValueError: If delimiter is not a single character
        
    Example:
        xml_str = '<root><items><item id="1"><name>Test</name></item></items></root>'
        csv_str = convert_xml_string_to_csv_by_xpath(xml_str, "//item")
        # Returns CSV with one row for the item element
    """
    try:
        # Parse XML using xml_parser service
        xml_root = parse_xml(xml_string)
        
        # Convert to CSV with XPath selection
        return convert_xml_to_csv_by_xpath(xml_root, xpath, delimiter=delimiter, namespaces=namespaces, path_separator=path_separator)
    except XMLValidationError:
        # Re-raise XMLValidationError with original details
        raise
    except ValueError:
        # Re-raise ValueError (delimiter validation error)
        raise
    except Exception as e:
        # Wrap unexpected errors
        raise XMLValidationError(f"Failed to convert XML to CSV using XPath: {str(e)}")

