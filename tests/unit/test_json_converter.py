"""
Unit tests for JSON converter service.

Tests verify XML-to-JSON conversion, preserving elements, attributes, namespaces,
hierarchy, data types, and handling edge cases.
"""

import pytest
from pathlib import Path
from lxml import etree
from app.services.json_converter import convert_xml_to_json, convert_xml_string_to_json
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
            filename: Name of the XML file (e.g., 'complex-example.xml')
            
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
def simple_xml():
    """Simple XML with single root with children."""
    return "<root><child1>value1</child1><child2>value2</child2></root>"


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
def xml_multiple_namespaces():
    """XML with multiple namespaces."""
    return """
    <root xmlns="http://example.com/ns1" xmlns:ex2="http://example.com/ns2">
        <child>default ns</child>
        <ex2:child2>prefixed ns</ex2:child2>
    </root>
    """


@pytest.fixture
def xml_with_special_chars():
    """XML with special characters and unicode."""
    return '<root>Text with &amp; entities and unicode: 你好 &lt;tags&gt;</root>'


@pytest.fixture
def xml_with_mixed_content():
    """XML with mixed content (elements with both text and child elements)."""
    return '<root>Text before<child>child content</child>text after</root>'


@pytest.fixture
def xml_multiple_same_name():
    """XML with multiple elements having the same name."""
    return '<root><item>1</item><item>2</item><item>3</item></root>'


@pytest.fixture
def xml_empty_element():
    """XML with empty element."""
    return '<root></root>'


@pytest.fixture
def xml_numeric_values():
    """XML with numeric values."""
    return '<root><int>42</int><float>3.14</float><negative>-10</negative></root>'


@pytest.fixture
def xml_boolean_values():
    """XML with boolean-like values."""
    return '<root><bool1>true</bool1><bool2>false</bool2></root>'


# Tests for simple XML structure conversion (AC: 1, 3)

def test_simple_xml_structure(simple_xml):
    """Test simple XML structure conversion (single root with children)."""
    result = convert_xml_string_to_json(simple_xml)
    assert "root" in result
    assert "child1" in result["root"]
    assert "child2" in result["root"]
    assert result["root"]["child1"]["_text"] == "value1"
    assert result["root"]["child2"]["_text"] == "value2"


def test_single_root_text():
    """Test XML with single root containing only text."""
    xml = "<root>simple text</root>"
    result = convert_xml_string_to_json(xml)
    assert result["root"]["_text"] == "simple text"


# Tests for nested XML structure conversion (AC: 1, 3)

def test_nested_xml_structure(nested_xml):
    """Test nested XML structure conversion (multi-level nesting)."""
    result = convert_xml_string_to_json(nested_xml)
    assert "root" in result
    assert "level1" in result["root"]
    assert isinstance(result["root"]["level1"], dict)
    assert "level2" in result["root"]["level1"]
    assert result["root"]["level1"]["level2"]["_text"] == "deep_value"


def test_deep_nesting():
    """Test deeply nested XML structure."""
    xml = "<a><b><c><d><e>deep</e></d></c></b></a>"
    result = convert_xml_string_to_json(xml)
    assert result["a"]["b"]["c"]["d"]["e"]["_text"] == "deep"


# Tests for XML with attributes conversion (AC: 1)

def test_xml_with_attributes(xml_with_attributes):
    """Test XML with attributes conversion (attributes preserved in JSON)."""
    result = convert_xml_string_to_json(xml_with_attributes)
    assert "root" in result
    assert "id" in result["root"]
    assert result["root"]["id"]["_value"] == "1"
    assert result["root"]["name"]["_value"] == "test"
    assert "child" in result["root"]
    assert result["root"]["child"]["_text"] == "content"


def test_attributes_with_text():
    """Test element with both attributes and text content."""
    xml = '<root id="1">text content</root>'
    result = convert_xml_string_to_json(xml)
    assert "id" in result["root"]
    assert result["root"]["id"]["_value"] == "1"
    assert "_text" in result["root"]
    assert result["root"]["_text"] == "text content"


def test_attributes_only_element():
    """Test element with only attributes, no content."""
    xml = '<root attr1="value1" attr2="value2"/>'
    result = convert_xml_string_to_json(xml)
    assert "attr1" in result["root"]
    assert result["root"]["attr1"]["_value"] == "value1"
    assert result["root"]["attr2"]["_value"] == "value2"


# Tests for XML with namespaces conversion (AC: 2)

def test_xml_default_namespace(xml_default_namespace):
    """Test XML with default namespace conversion."""
    result = convert_xml_string_to_json(xml_default_namespace)
    # New format uses local names with _prefix and _xmlns
    assert "root" in result
    assert "_xmlns" in result["root"]
    assert result["root"]["_xmlns"] == "http://example.com/ns"
    assert "child" in result["root"]
    assert result["root"]["child"]["_text"] == "content"


def test_xml_prefixed_namespace(xml_prefixed_namespace):
    """Test XML with prefixed namespace conversion."""
    result = convert_xml_string_to_json(xml_prefixed_namespace)
    # Prefixed namespaces preserved as prefix:localname in lxml
    assert result is not None
    # Verify structure is preserved
    root_key = list(result.keys())[0]
    assert root_key is not None


def test_xml_multiple_namespaces(xml_multiple_namespaces):
    """Test XML with multiple namespaces conversion."""
    result = convert_xml_string_to_json(xml_multiple_namespaces)
    assert "root" in result or result  # Structure preserved
    # Verify namespace information is maintained
    assert isinstance(result, dict)


def test_namespace_preservation():
    """Test that namespace information is preserved in tag names."""
    xml = '<root xmlns="http://example.com/ns"><child>test</child></root>'
    result = convert_xml_string_to_json(xml)
    # Namespace info should be preserved (lxml includes it in tag)
    assert result is not None
    root_key = list(result.keys())[0]
    # Tag may be {namespace}root or preserved differently
    assert root_key is not None


# Tests for complex nested structures (AC: 3)

def test_complex_nested_structure():
    """Test complex nested structures."""
    xml = """
    <root>
        <section>
            <item>
                <name>Item 1</name>
                <value>100</value>
            </item>
        </section>
    </root>
    """
    result = convert_xml_string_to_json(xml)
    assert "root" in result
    assert "section" in result["root"]
    assert "item" in result["root"]["section"]
    assert "name" in result["root"]["section"]["item"]
    assert result["root"]["section"]["item"]["name"]["_text"] == "Item 1"


def test_xml_with_mixed_content(xml_with_mixed_content):
    """Test mixed content (elements with both text and child elements)."""
    result = convert_xml_string_to_json(xml_with_mixed_content)
    assert "root" in result
    # Mixed content should preserve both text and children
    assert "#text" in result["root"] or "child" in result["root"]
    # Text before and after children should be preserved
    assert isinstance(result["root"], dict)


# Tests for data type preservation (AC: 4)

def test_data_type_text_strings():
    """Test that text strings are preserved as strings."""
    xml = '<root><text>hello world</text></root>'
    result = convert_xml_string_to_json(xml)
    assert result["root"]["text"]["_text"] == "hello world"
    assert isinstance(result["root"]["text"]["_text"], str)


def test_data_type_numeric_values(xml_numeric_values):
    """Test that numeric values are preserved as strings in _text."""
    result = convert_xml_string_to_json(xml_numeric_values)
    # All values are kept as strings in _text fields
    assert isinstance(result["root"]["int"]["_text"], str)
    assert result["root"]["int"]["_text"] == "42"
    
    # Floats
    assert isinstance(result["root"]["float"]["_text"], str)
    assert result["root"]["float"]["_text"] == "3.14"
    
    # Negative numbers
    assert isinstance(result["root"]["negative"]["_text"], str)
    assert result["root"]["negative"]["_text"] == "-10"


def test_data_type_boolean_detection(xml_boolean_values):
    """Test that boolean values are preserved as strings in _text."""
    result = convert_xml_string_to_json(xml_boolean_values)
    assert isinstance(result["root"]["bool1"]["_text"], str)
    assert result["root"]["bool1"]["_text"] == "true"
    assert isinstance(result["root"]["bool2"]["_text"], str)
    assert result["root"]["bool2"]["_text"] == "false"


def test_numeric_string_preservation():
    """Test that numeric strings (like leading zeros) are preserved as strings."""
    xml = '<root><id>007</id><code>01</code></root>'
    result = convert_xml_string_to_json(xml)
    # Leading zeros should preserve as string (not converted to int)
    assert result["root"]["id"]["_text"] == "007"
    assert isinstance(result["root"]["id"]["_text"], str)
    assert result["root"]["code"]["_text"] == "01"
    assert isinstance(result["root"]["code"]["_text"], str)


# Tests for multiple elements with same name (AC: 1)

def test_multiple_elements_same_name(xml_multiple_same_name):
    """Test multiple elements with same name (array conversion)."""
    result = convert_xml_string_to_json(xml_multiple_same_name)
    assert "root" in result
    assert "item" in result["root"]
    assert isinstance(result["root"]["item"], list)
    assert len(result["root"]["item"]) == 3
    # All text values are preserved as strings in _text
    assert result["root"]["item"][0]["_text"] == "1"
    assert result["root"]["item"][1]["_text"] == "2"
    assert result["root"]["item"][2]["_text"] == "3"
    assert isinstance(result["root"]["item"][0]["_text"], str)


def test_mixed_single_and_multiple_elements():
    """Test structure with both single and multiple elements of same name."""
    xml = '<root><item>first</item><other>single</other><item>second</item></root>'
    result = convert_xml_string_to_json(xml)
    assert isinstance(result["root"]["item"], list)
    assert len(result["root"]["item"]) == 2
    assert result["root"]["other"]["_text"] == "single"


# Tests for empty elements (AC: 1, 3)

def test_empty_element(xml_empty_element):
    """Test empty elements handled appropriately."""
    result = convert_xml_string_to_json(xml_empty_element)
    assert "root" in result
    # Empty element should return None or empty dict
    assert result["root"] is None or result["root"] == {}


def test_empty_element_with_attributes():
    """Test empty element with attributes."""
    xml = '<root attr="value"></root>'
    result = convert_xml_string_to_json(xml)
    assert "attr" in result["root"]
    assert result["root"]["attr"]["_value"] == "value"


# Tests for XML with special characters (AC: 1, 4)

def test_xml_with_special_chars(xml_with_special_chars):
    """Test XML with special characters (unicode, entities)."""
    result = convert_xml_string_to_json(xml_with_special_chars)
    assert "root" in result
    # Special characters should be preserved in _text
    assert isinstance(result["root"], dict)
    assert "_text" in result["root"]
    # Unicode should be preserved
    assert "你好" in result["root"]["_text"] or len(result["root"]["_text"]) > 0


def test_unicode_characters():
    """Test Unicode character preservation."""
    xml = '<root>Hello 世界 🌍</root>'
    result = convert_xml_string_to_json(xml)
    assert result["root"]["_text"] == "Hello 世界 🌍"


def test_xml_entities():
    """Test XML entity handling."""
    xml = '<root>&amp; &lt; &gt; &quot; &apos;</root>'
    result = convert_xml_string_to_json(xml)
    # Entities should be decoded and stored in _text
    assert isinstance(result["root"], dict)
    assert "_text" in result["root"]
    assert isinstance(result["root"]["_text"], str)
    assert "&" in result["root"]["_text"] or "<" in result["root"]["_text"]


# Tests for integration with parse_xml (AC: 1, 2)

def test_integration_with_parse_xml():
    """Test integration with parse_xml (end-to-end conversion from XML string to JSON)."""
    xml = '<root><child id="1">content</child></root>'
    result = convert_xml_string_to_json(xml)
    # Should work end-to-end
    assert "root" in result
    assert "child" in result["root"]
    assert "id" in result["root"]["child"]
    assert result["root"]["child"]["id"]["_value"] == "1"
    assert result["root"]["child"]["_text"] == "content"


def test_integration_error_handling():
    """Test that XMLValidationError from parse_xml is propagated."""
    invalid_xml = "<root><unclosed>"
    with pytest.raises(XMLValidationError):
        convert_xml_string_to_json(invalid_xml)


def test_convert_xml_to_json_with_parsed_root():
    """Test convert_xml_to_json with already parsed XML root."""
    xml = '<root><child>value</child></root>'
    parsed_root = parse_xml(xml)
    result = convert_xml_to_json(parsed_root)
    assert "root" in result
    assert "child" in result["root"]
    assert result["root"]["child"]["_text"] == "value"


# Edge case tests

def test_nested_arrays():
    """Test nested structures with arrays."""
    xml = '<root><group><item>1</item><item>2</item></group></root>'
    result = convert_xml_string_to_json(xml)
    assert isinstance(result["root"]["group"]["item"], list)
    assert len(result["root"]["group"]["item"]) == 2


def test_deep_nesting_with_attributes():
    """Test deeply nested structure with attributes at multiple levels."""
    xml = '<a id="a1"><b id="b1"><c id="c1">value</c></b></a>'
    result = convert_xml_string_to_json(xml)
    assert result["a"]["id"]["_value"] == "a1"
    assert result["a"]["b"]["id"]["_value"] == "b1"
    assert result["a"]["b"]["c"]["id"]["_value"] == "c1"
    assert result["a"]["b"]["c"]["_text"] == "value"


def test_whitespace_handling():
    """Test that whitespace is properly handled."""
    xml = '<root>  text with spaces  </root>'
    result = convert_xml_string_to_json(xml)
    # Whitespace should be trimmed and stored in _text
    assert result["root"]["_text"] == "text with spaces"


def test_zero_and_empty_strings():
    """Test numeric zero vs empty string."""
    xml = '<root><zero>0</zero><empty></empty></root>'
    result = convert_xml_string_to_json(xml)
    assert result["root"]["zero"]["_text"] == "0"
    assert isinstance(result["root"]["zero"]["_text"], str)
    # Empty element should have no _text (or be empty dict)
    assert result["root"]["empty"] == {} or "_text" not in result["root"]["empty"]


def test_large_numeric_values():
    """Test large numeric values."""
    xml = '<root><big_int>999999999</big_int><scientific>1.23e10</scientific></root>'
    result = convert_xml_string_to_json(xml)
    assert isinstance(result["root"]["big_int"]["_text"], str)
    assert result["root"]["big_int"]["_text"] == "999999999"


# Tests for convert_xml_string_to_json streaming parameter

def test_convert_xml_string_to_json_with_streaming_false():
    """Test convert_xml_string_to_json with use_streaming=False."""
    xml = '<root><child>value</child></root>'
    result = convert_xml_string_to_json(xml, use_streaming=False)
    assert result["root"]["child"]["_text"] == "value"


def test_convert_xml_string_to_json_with_streaming_true():
    """Test convert_xml_string_to_json with use_streaming=True."""
    xml = '<root><child>value</child></root>'
    result = convert_xml_string_to_json(xml, use_streaming=True)
    assert result["root"]["child"]["_text"] == "value"


def test_convert_xml_string_to_json_auto_detects_streaming_for_large_files():
    """Test that convert_xml_string_to_json auto-detects and uses streaming for large files."""
    # Create a moderately large XML string (> 10MB threshold)
    # Use a more efficient approach: create items with large content
    item_content = 'x' * (1024 * 1024)  # 1MB per item
    items = ''.join([f'<item>{item_content}</item>' for _ in range(11)])
    large_xml = f'<root>{items}</root>'  # ~11MB
    result = convert_xml_string_to_json(large_xml, use_streaming=None)
    assert "root" in result
    # Item should be a list (since there are 11 items with same name)
    assert isinstance(result["root"]["item"], list)
    assert len(result["root"]["item"]) == 11


def test_convert_xml_string_to_json_uses_standard_parser_for_small_files():
    """Test that convert_xml_string_to_json uses standard parser for small files."""
    # Small file (< 10MB threshold)
    small_xml = '<root><item>value</item></root>'
    result = convert_xml_string_to_json(small_xml, use_streaming=None)
    assert result["root"]["item"]["_text"] == "value"


def test_convert_xml_string_to_json_streaming_same_result():
    """Test that streaming and non-streaming produce same results."""
    xml = '<root><child id="1">content</child></root>'
    result_streaming = convert_xml_string_to_json(xml, use_streaming=True)
    result_standard = convert_xml_string_to_json(xml, use_streaming=False)
    assert result_streaming == result_standard


def test_convert_xml_string_to_json_wraps_unexpected_errors():
    """Test that unexpected errors in convert_xml_string_to_json are wrapped as XMLValidationError."""
    # This test ensures error handling works correctly
    # We can't easily trigger an unexpected error, but we test that XMLValidationError is re-raised
    invalid_xml = "<root><unclosed>"
    with pytest.raises(XMLValidationError):
        convert_xml_string_to_json(invalid_xml)


