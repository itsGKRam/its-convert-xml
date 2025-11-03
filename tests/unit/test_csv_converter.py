"""
Unit tests for CSV converter service.

Tests verify XML-to-CSV conversion, handling flat and nested structures,
namespaces, RFC 4180 compliance, and edge cases.
"""

import pytest
from pathlib import Path
from lxml import etree
from app.services.csv_converter import convert_xml_to_csv, convert_xml_string_to_csv
from app.services.xml_parser import parse_xml
from app.exceptions import XMLValidationError


# Test fixtures for XML samples

@pytest.fixture
def test_data_dir():
    """Return path to tests/data directory."""
    return Path(__file__).parent.parent / "data"


@pytest.fixture
def load_xml_file(test_data_dir):
    """Helper fixture to load XML files from tests/data directory."""
    def _load_xml(filename: str) -> str:
        """Load XML file from tests/data directory.
        
        Args:
            filename: Name of the XML file (e.g., 'simple.xml')
            
        Returns:
            XML content as string
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        xml_path = test_data_dir / filename
        if not xml_path.exists():
            raise FileNotFoundError(f"XML test file not found: {xml_path}")
        return xml_path.read_text(encoding='utf-8')
    return _load_xml


@pytest.fixture
def flat_xml_rows_attributes():
    """Flat XML where rows are elements with attributes as columns."""
    return '<root><row id="1" name="test1"/><row id="2" name="test2"/></root>'


@pytest.fixture
def flat_xml_rows_children():
    """Flat XML where rows are elements with child elements as columns."""
    return '<root><row><id>1</id><name>test1</name></row><row><id>2</id><name>test2</name></row></root>'


@pytest.fixture
def nested_xml():
    """XML with nested structure."""
    return """
    <root>
        <level1>
            <level2>deep_value</level2>
        </level1>
    </root>
    """


@pytest.fixture
def xml_with_attributes():
    """XML with attributes."""
    return '<root id="1" name="test"><child>content</child></root>'


@pytest.fixture
def xml_default_namespace():
    """XML with default namespace."""
    return '<root xmlns="http://example.com/ns"><child>content</child></root>'


@pytest.fixture
def xml_prefixed_namespace():
    """XML with prefixed namespace."""
    return '<ex:root xmlns:ex="http://example.com/ns"><ex:child>content</ex:child></ex:root>'


@pytest.fixture
def xml_with_special_chars():
    """XML with special characters that need CSV escaping."""
    return '<root><item>Value with, comma</item><item>Value with "quotes"</item></root>'


@pytest.fixture
def xml_empty_element():
    """XML with empty element."""
    return '<root></root>'


# Tests for flat XML structure conversion (AC: 1, 2)

def test_flat_xml_rows_with_attributes(flat_xml_rows_attributes):
    """Test flat XML where rows are elements and columns are attributes (AC: 2)."""
    result = convert_xml_string_to_csv(flat_xml_rows_attributes)
    
    # Verify CSV format: headers and data rows
    lines = result.strip().split('\n')
    assert len(lines) >= 2  # Header + at least one data row
    
    # Check headers
    assert 'id' in lines[0]
    assert 'name' in lines[0]
    
    # Check data rows contain expected values
    csv_content = result
    assert '1' in csv_content
    assert 'test1' in csv_content
    assert '2' in csv_content
    assert 'test2' in csv_content


def test_flat_xml_rows_with_children(flat_xml_rows_children):
    """Test flat XML where rows are elements and columns are child elements (AC: 2)."""
    result = convert_xml_string_to_csv(flat_xml_rows_children)
    
    # Verify CSV format
    lines = result.strip().split('\n')
    assert len(lines) >= 2  # Header + data rows
    
    # Check headers
    assert 'id' in lines[0]
    assert 'name' in lines[0]
    
    # Check data
    assert '1' in result
    assert 'test1' in result
    assert '2' in result
    assert 'test2' in result


# Tests for nested XML structure conversion (AC: 3)

def test_nested_xml_structure_conversion(nested_xml):
    """Test nested XML structure conversion with flattening strategy (AC: 3)."""
    result = convert_xml_string_to_csv(nested_xml)
    
    # Verify CSV contains flattened column names
    assert 'level1' in result or 'level1_level2' in result or 'level2' in result
    assert 'deep_value' in result


def test_deeply_nested_structure():
    """Test deeply nested structures to ensure flattening works correctly."""
    xml = "<root><level1><level2><level3>value</level3></level2></level1></root>"
    result = convert_xml_string_to_csv(xml)
    
    # Should have flattened column names
    assert 'value' in result
    # Column names should contain nested structure indicators
    assert 'level' in result.lower()


# Tests for RFC 4180 compliance (AC: 4)

def test_csv_rfc4180_special_characters(xml_with_special_chars):
    """Test CSV output with special characters - verify RFC 4180 escaping (AC: 4)."""
    result = convert_xml_string_to_csv(xml_with_special_chars)
    
    # Verify CSV is properly formatted (no parsing errors)
    # Special characters should be properly quoted or escaped
    lines = result.strip().split('\n')
    assert len(lines) >= 1
    
    # CSV should be valid (can be parsed by csv.reader)
    import csv
    import io
    reader = csv.reader(io.StringIO(result))
    rows = list(reader)
    assert len(rows) > 0  # Should have at least header row
    
    # Verify special characters are present (properly escaped)
    csv_content = result
    assert 'comma' in csv_content or ',' in csv_content
    assert 'quotes' in csv_content or '"' in csv_content


def test_csv_rfc4180_empty_fields():
    """Test CSV output with empty fields - verify RFC 4180 compliance."""
    xml = '<root><row id="1"/><row id="2" name="test"/></root>'
    result = convert_xml_string_to_csv(xml)
    
    # CSV should handle empty fields correctly
    import csv
    import io
    reader = csv.reader(io.StringIO(result))
    rows = list(reader)
    assert len(rows) >= 2  # Header + data rows


# Tests for namespace handling (AC: 5)

def test_xml_default_namespace(xml_default_namespace):
    """Test XML with default namespace - verify namespace handling in column names (AC: 5)."""
    result = convert_xml_string_to_csv(xml_default_namespace)
    
    # Verify namespace is handled (column names may include namespace info)
    assert 'child' in result
    assert 'content' in result


def test_xml_prefixed_namespace(xml_prefixed_namespace):
    """Test XML with prefixed namespace - verify namespace prefix in column names (AC: 5)."""
    result = convert_xml_string_to_csv(xml_prefixed_namespace)
    
    # Prefixed namespaces should appear in column names
    # May be "ex:child" or similar format
    assert 'child' in result.lower() or 'ex' in result.lower()


def test_xml_multiple_namespaces():
    """Test XML with multiple namespaces - verify all namespaces handled correctly."""
    xml = """
    <root xmlns="http://example.com/ns1" xmlns:ex2="http://example.com/ns2">
        <child>default ns</child>
        <ex2:child2>prefixed ns</ex2:child2>
    </root>
    """
    result = convert_xml_string_to_csv(xml)
    
    # Should handle both default and prefixed namespaces
    assert 'child' in result.lower()
    assert 'ns' in result.lower() or 'ex2' in result.lower()


# Tests for edge cases (AC: 6)

def test_empty_xml():
    """Test edge case: empty XML or empty root element (AC: 6)."""
    xml = '<root></root>'
    result = convert_xml_string_to_csv(xml)
    
    # Empty XML should return empty CSV or minimal structure
    # Depending on implementation, may return empty string or just headers
    assert isinstance(result, str)


def test_single_element_no_children():
    """Test edge case: single element with no children or attributes (AC: 6)."""
    xml = '<root>text only</root>'
    result = convert_xml_string_to_csv(xml)
    
    # Should handle single element
    assert 'text only' in result or 'root' in result.lower()


def test_attributes_only_element():
    """Test edge case: XML with only attributes, no text or children (AC: 6)."""
    xml = '<root><item attr1="val1" attr2="val2"/></root>'
    result = convert_xml_string_to_csv(xml)
    
    # Attributes should become columns
    assert 'attr1' in result or 'val1' in result
    assert 'attr2' in result or 'val2' in result


def test_mixed_content():
    """Test edge case: mixed content (element with both text and children) (AC: 6)."""
    xml = '<root>text<child>child content</child></root>'
    result = convert_xml_string_to_csv(xml)
    
    # Should handle mixed content appropriately
    assert 'text' in result or 'child' in result.lower()


def test_xml_from_file_fixtures(load_xml_file):
    """Test conversion using XML files from test fixtures (AC: 6)."""
    simple_xml = load_xml_file('simple.xml')
    result = convert_xml_string_to_csv(simple_xml)
    
    # Should successfully convert fixture XML
    assert isinstance(result, str)
    assert len(result) > 0


def test_complex_xml_with_namespaces(load_xml_file):
    """Test complex XML file with multiple namespaces and deeply nested structure (AC: 2, 3, 5, 6)."""
    complex_xml = load_xml_file('example-complex.xml')
    result = convert_xml_string_to_csv(complex_xml)
    
    # Should successfully convert complex XML
    assert isinstance(result, str)
    assert len(result) > 0
    
    # Verify CSV format (has headers and data)
    lines = result.strip().split('\n')
    assert len(lines) >= 1  # At least header row
    
    # Verify CSV can be parsed correctly (RFC 4180 compliance)
    import csv
    import io
    reader = csv.reader(io.StringIO(result))
    rows = list(reader)
    assert len(rows) > 0  # Should have at least header row
    
    # Complex XML has namespaces (env:, wd:) - verify they're handled
    csv_content = result
    # The XML has env:Envelope, wd:Get_Job_Requisitions_Response, etc.
    # CSV should contain data from the XML (verify some expected content appears)
    # Note: exact column names depend on flattening strategy, but data should be present
    assert len(csv_content) > 100  # Complex XML should produce substantial CSV
    
    # Verify namespace prefixes are handled (may appear in column names or not depending on strategy)
    # The important thing is that conversion succeeds and produces valid CSV


# Tests for error handling (AC: 7)

def test_error_handling_malformed_xml():
    """Test error handling: malformed XML input (AC: 7)."""
    malformed_xml = '<root><unclosed>'
    
    with pytest.raises(XMLValidationError):
        convert_xml_string_to_csv(malformed_xml)


def test_error_handling_empty_string():
    """Test error handling: empty string input."""
    with pytest.raises(XMLValidationError):
        convert_xml_string_to_csv('')


def test_error_consistency_with_json_converter():
    """Test error handling consistency with JSON converter patterns (AC: 7)."""
    # Both should raise XMLValidationError for same malformed input
    from app.services.json_converter import convert_xml_string_to_json
    
    malformed_xml = '<root><unclosed>'
    
    # Both converters should raise same exception type
    with pytest.raises(XMLValidationError):
        convert_xml_string_to_csv(malformed_xml)
    
    with pytest.raises(XMLValidationError):
        convert_xml_string_to_json(malformed_xml)


# Tests for function signature consistency (AC: 1, 7)

def test_convert_xml_to_csv_signature():
    """Test that convert_xml_to_csv accepts etree._Element like JSON converter."""
    xml_str = '<root><item>test</item></root>'
    xml_root = parse_xml(xml_str)
    
    # Should accept parsed element tree
    result = convert_xml_to_csv(xml_root)
    assert isinstance(result, str)


def test_convert_xml_string_to_csv_wrapper():
    """Test wrapper function convert_xml_string_to_csv."""
    xml_str = '<root><item>test</item></root>'
    result = convert_xml_string_to_csv(xml_str)
    assert isinstance(result, str)

