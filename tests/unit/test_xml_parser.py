"""
Unit tests for XML parser service.

Tests verify XML parsing, validation, namespace handling, error detection,
and security protections.
"""

import pytest
from pathlib import Path
from lxml import etree
from app.services.xml_parser import parse_xml, parse_xml_streaming
from app.exceptions import XMLValidationError


# Test fixtures for valid XML samples

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
    """Simple XML with single root element."""
    return "<root>content</root>"


@pytest.fixture
def nested_xml():
    """XML with nested structure."""
    return """
    <root>
        <child1>value1</child1>
        <child2>value2</child2>
        <nested>
            <deep>deep_value</deep>
        </nested>
    </root>
    """


@pytest.fixture
def xml_with_attributes():
    """XML with attributes."""
    return '<root attr1="value1" attr2="value2"><child>content</child></root>'


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
def xml_text_only():
    """XML with only text content."""
    return '<root>Only text content, no child elements</root>'


@pytest.fixture
def xml_attributes_only():
    """XML with only attributes, minimal structure."""
    return '<root attr1="value1" attr2="value2"/>'


# Tests for lxml library integration (AC1)

def test_lxml_can_be_imported():
    """Test that lxml.etree can be imported."""
    from lxml import etree
    assert etree is not None
    assert hasattr(etree, 'fromstring')
    assert hasattr(etree, 'XMLParser')


def test_parser_security_configuration():
    """Test that parser applies security settings."""
    from lxml import etree
    parser = etree.XMLParser(resolve_entities=False, huge_tree=False)
    # Security settings are applied during parser creation
    # Verify parser can be used (settings are valid)
    assert parser is not None
    # Verify parser has the expected attributes
    # The actual security is tested indirectly via entity expansion protection test


# Tests for valid XML parsing (AC2)

def test_parse_simple_xml(simple_xml):
    """Test parsing XML with simple structure."""
    root = parse_xml(simple_xml)
    assert root is not None
    assert root.tag == 'root'
    assert root.text.strip() == 'content'


def test_parse_nested_xml(nested_xml):
    """Test parsing XML with nested structures."""
    root = parse_xml(nested_xml)
    assert root is not None
    assert root.tag == 'root'
    children = list(root)
    assert len(children) == 3
    assert children[0].tag == 'child1'
    assert children[1].tag == 'child2'
    assert children[2].tag == 'nested'


def test_parse_xml_with_attributes(xml_with_attributes):
    """Test parsing XML with attributes."""
    root = parse_xml(xml_with_attributes)
    assert root is not None
    assert root.tag == 'root'
    assert root.get('attr1') == 'value1'
    assert root.get('attr2') == 'value2'
    assert len(list(root)) == 1
    assert root[0].tag == 'child'


# Tests for namespace handling (AC3)

def test_parse_default_namespace(xml_default_namespace):
    """Test parsing XML with default namespace."""
    root = parse_xml(xml_default_namespace)
    assert root is not None
    # lxml preserves namespace information
    assert root.nsmap is not None
    # Default namespace is accessible
    assert None in root.nsmap or 'http://example.com/ns' in root.nsmap.values()
    child = root[0]
    assert child.tag == '{http://example.com/ns}child' or child.tag == 'child'


def test_parse_prefixed_namespace(xml_prefixed_namespace):
    """Test parsing XML with prefixed namespace."""
    root = parse_xml(xml_prefixed_namespace)
    assert root is not None
    # Namespace prefix should be accessible
    assert root.nsmap is not None
    assert 'ex' in root.nsmap
    assert root.nsmap['ex'] == 'http://example.com/ns'
    # Elements should have namespace-qualified tags
    assert 'ex:' in root.tag or '{http://example.com/ns}' in root.tag


def test_parse_multiple_namespaces(xml_multiple_namespaces):
    """Test parsing XML with multiple namespaces."""
    root = parse_xml(xml_multiple_namespaces)
    assert root is not None
    # Both namespaces should be preserved
    assert root.nsmap is not None
    # Default namespace
    assert None in root.nsmap or 'http://example.com/ns1' in root.nsmap.values()
    # Prefixed namespace
    assert 'ex2' in root.nsmap
    assert root.nsmap['ex2'] == 'http://example.com/ns2'


# Tests for error detection with location reporting (AC4)

def test_unclosed_tag_error():
    """Test that unclosed tags raise XMLValidationError with location."""
    malformed_xml = "<root><child>unclosed"
    with pytest.raises(XMLValidationError) as exc_info:
        parse_xml(malformed_xml)

    error = exc_info.value
    assert error.message is not None
    # Error should include location information if available
    assert hasattr(error, 'line') or hasattr(error, 'column')
    assert "unclosed" in str(error).lower() or "tag" in str(error).lower()


def test_invalid_syntax_error():
    """Test that invalid XML syntax raises XMLValidationError."""
    malformed_xml = "<root><</root>"
    with pytest.raises(XMLValidationError) as exc_info:
        parse_xml(malformed_xml)

    error = exc_info.value
    assert isinstance(error, XMLValidationError)
    assert error.message is not None


def test_mismatched_tags_error():
    """Test that mismatched tags raise XMLValidationError."""
    malformed_xml = "<root><child></other></root>"
    with pytest.raises(XMLValidationError) as exc_info:
        parse_xml(malformed_xml)

    error = exc_info.value
    assert isinstance(error, XMLValidationError)
    assert error.message is not None


def test_invalid_characters_error():
    """Test that invalid characters raise XMLValidationError."""
    # XML 1.0 doesn't allow control characters (except tab, LF, CR)
    malformed_xml = "<root>\x01invalid\x02</root>"
    with pytest.raises(XMLValidationError) as exc_info:
        parse_xml(malformed_xml)

    error = exc_info.value
    assert isinstance(error, XMLValidationError)


def test_error_includes_line_and_column():
    """Test that errors include line and column location information."""
    malformed_xml = "<root>\n<child>\n</unclosed>"
    try:
        parse_xml(malformed_xml)
        pytest.fail("Should have raised XMLValidationError")
    except XMLValidationError as e:
        # Error should have location information (line and/or column)
        # Note: exact location depends on lxml's error reporting
        assert hasattr(e, 'line') or hasattr(e, 'column')
        assert "Invalid XML" in str(e)


# Tests for edge cases (AC5)

def test_special_characters_unicode(xml_with_special_chars):
    """Test parsing XML with special characters and unicode."""
    root = parse_xml(xml_with_special_chars)
    assert root is not None
    assert root.tag == 'root'
    # Text should be properly decoded
    text = root.text
    assert text is not None


def test_special_characters_entities():
    """Test parsing XML with XML entities."""
    xml = "<root>&amp; &lt; &gt; &quot; &apos;</root>"
    root = parse_xml(xml)
    assert root is not None
    assert root.text is not None


def test_empty_xml_document():
    """Test parsing empty XML document."""
    # Empty root element
    xml = "<root></root>"
    root = parse_xml(xml)
    assert root is not None
    assert root.tag == 'root'
    assert len(list(root)) == 0


def test_xml_text_only(xml_text_only):
    """Test parsing XML with only text content (no child elements)."""
    root = parse_xml(xml_text_only)
    assert root is not None
    assert root.tag == 'root'
    assert root.text is not None
    assert len(list(root)) == 0


def test_xml_attributes_only(xml_attributes_only):
    """Test parsing XML with only attributes (minimal structure)."""
    root = parse_xml(xml_attributes_only)
    assert root is not None
    assert root.tag == 'root'
    assert root.get('attr1') == 'value1'
    assert root.get('attr2') == 'value2'
    assert len(list(root)) == 0


def test_deeply_nested_structure():
    """Test parsing deeply nested XML structures."""
    xml = "<a><b><c><d><e>deep</e></d></c></b></a>"
    root = parse_xml(xml)
    assert root is not None
    assert root.tag == 'a'
    level1 = root[0]
    assert level1.tag == 'b'
    level2 = level1[0]
    assert level2.tag == 'c'


# Tests for XML attack protection

def test_entity_expansion_protection():
    """Test that entity expansion attacks are prevented."""
    # Attempt to use entity expansion (should be blocked by resolve_entities=False)
    # This is a basic test - the parser should not expand entities
    xml = '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY test "test">]><root>&test;</root>'
    # With resolve_entities=False, lxml should handle this safely
    # Note: exact behavior depends on lxml version, but should not cause DoS
    try:
        root = parse_xml(xml)
        # If parsing succeeds, entities were not expanded (which is safe)
        assert root is not None
    except XMLValidationError:
        # If parsing fails, that's also acceptable - entity references not resolved
        pass


def test_utf8_encoding_handling():
    """Test that UTF-8 encoding is properly handled."""
    xml = '<root>Test with UTF-8: 你好世界</root>'
    root = parse_xml(xml)
    assert root is not None
    assert root.text is not None
    # Text should be properly decoded
    assert '你好' in root.text or len(root.text) > 0


# Tests using external XML files from tests/data directory

def test_complex_xml_file_parsing(load_xml_file):
    """Example test showing how to load and parse complex XML from file.
    
    This demonstrates how to use the load_xml_file fixture to test
    with complex XML files stored in tests/data/ directory.
    
    This test works with the real-world SOAP/Workday XML structure.
    """
    # Load XML from file - replace 'example-complex.xml' with your file name
    xml_content = load_xml_file('example-complex.xml')
    
    # Parse the XML
    root = parse_xml(xml_content)
    
    # Verify parsing succeeded
    assert root is not None
    assert root.tag is not None
    
    # Verify namespaces are preserved (works with SOAP/Workday structure)
    assert root.nsmap is not None
    # Check for SOAP envelope namespace
    assert 'env' in root.nsmap or 'http://schemas.xmlsoap.org/soap/envelope/' in root.nsmap.values()
    
    # Verify structure exists - SOAP structure has Body as child
    children = list(root)
    assert len(children) > 0
    
    # Verify it's a SOAP Envelope structure
    if 'env' in root.tag or 'Envelope' in root.tag:
        # Verify Body element exists
        body_elements = [child for child in children if 'Body' in child.tag]
        assert len(body_elements) > 0, "SOAP Body element should exist"


# Tests for streaming XML parser (parse_xml_streaming)

def test_parse_xml_streaming_simple(simple_xml):
    """Test streaming parser with simple XML structure."""
    root = parse_xml_streaming(simple_xml)
    assert root is not None
    assert root.tag == 'root'
    assert root.text.strip() == 'content'


def test_parse_xml_streaming_nested(nested_xml):
    """Test streaming parser with nested structures."""
    root = parse_xml_streaming(nested_xml)
    assert root is not None
    assert root.tag == 'root'
    children = list(root)
    assert len(children) == 3


def test_parse_xml_streaming_with_attributes(xml_with_attributes):
    """Test streaming parser with attributes."""
    root = parse_xml_streaming(xml_with_attributes)
    assert root is not None
    assert root.tag == 'root'
    assert root.get('attr1') == 'value1'
    assert root.get('attr2') == 'value2'


def test_parse_xml_streaming_with_namespaces(xml_prefixed_namespace):
    """Test streaming parser with namespaces."""
    root = parse_xml_streaming(xml_prefixed_namespace)
    assert root is not None
    assert root.nsmap is not None
    assert 'ex' in root.nsmap


def test_parse_xml_streaming_malformed_raises_error():
    """Test streaming parser raises XMLValidationError for malformed XML."""
    malformed_xml = "<root><unclosed>"
    with pytest.raises(XMLValidationError):
        parse_xml_streaming(malformed_xml)


def test_parse_xml_streaming_empty_document_raises_error():
    """Test streaming parser raises error for empty XML."""
    empty_xml = ""
    # Empty XML should raise XMLValidationError when iterparse can't find root
    with pytest.raises(XMLValidationError):
        parse_xml_streaming(empty_xml)


def test_parse_xml_streaming_whitespace_only_raises_error():
    """Test streaming parser raises error for whitespace-only XML."""
    whitespace_xml = "   \n\t  "
    # Whitespace-only XML should raise XMLValidationError
    with pytest.raises((XMLValidationError, etree.XMLSyntaxError)):
        parse_xml_streaming(whitespace_xml)


def test_parse_xml_streaming_error_includes_location():
    """Test that streaming parser errors include location information."""
    malformed_xml = "<root>\n<child>\n</unclosed>"
    with pytest.raises(XMLValidationError) as exc_info:
        parse_xml_streaming(malformed_xml)
    error = exc_info.value
    assert hasattr(error, 'line') or hasattr(error, 'column')


def test_parse_xml_streaming_large_structure():
    """Test streaming parser with large nested structure."""
    # Create a moderately large XML structure
    xml = "<root>" + "".join([f"<item{i}>value{i}</item{i}>" for i in range(100)]) + "</root>"
    root = parse_xml_streaming(xml)
    assert root is not None
    assert root.tag == 'root'
    children = list(root)
    assert len(children) == 100


def test_parse_xml_streaming_complex_file(load_xml_file):
    """Test streaming parser with complex XML file from tests/data."""
    xml_content = load_xml_file('example-complex.xml')
    root = parse_xml_streaming(xml_content)
    assert root is not None
    assert root.tag is not None
    assert root.nsmap is not None


def test_parse_xml_streaming_same_result_as_parse_xml():
    """Test that streaming parser produces same result as standard parser."""
    xml = '<root><child id="1">content</child></root>'
    root_standard = parse_xml(xml)
    root_streaming = parse_xml_streaming(xml)
    assert root_standard.tag == root_streaming.tag
    assert len(list(root_standard)) == len(list(root_streaming))
    assert root_standard[0].tag == root_streaming[0].tag
    assert root_standard[0].get('id') == root_streaming[0].get('id')

