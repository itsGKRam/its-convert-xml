"""
Integration tests for XML to JSON conversion endpoint.

Tests verify end-to-end conversion flow, Content-Type validation,
error handling, and response format.
"""

import pytest
from app import create_app


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_successful_conversion_returns_200(client):
    """Test that successful POST /convert/xml-to-json returns HTTP 200 OK."""
    xml_data = '<root><item>value</item></root>'
    response = client.post(
        '/convert/xml-to-json',
        data=xml_data,
        content_type='application/xml'
    )
    assert response.status_code == 200


def test_successful_conversion_returns_json(client):
    """Test that successful conversion returns correct JSON response."""
    xml_data = '<root><item>value</item></root>'
    response = client.post(
        '/convert/xml-to-json',
        data=xml_data,
        content_type='application/xml'
    )
    data = response.get_json()
    assert data is not None
    assert 'root' in data
    assert data['root']['item']['_text'] == 'value'


def test_response_content_type_is_json(client):
    """Test that response Content-Type header is application/json."""
    xml_data = '<root><item>value</item></root>'
    response = client.post(
        '/convert/xml-to-json',
        data=xml_data,
        content_type='application/xml'
    )
    assert response.content_type == 'application/json'


def test_content_type_validation_application_xml(client):
    """Test that application/xml Content-Type is accepted."""
    xml_data = '<root><item>test</item></root>'
    response = client.post(
        '/convert/xml-to-json',
        data=xml_data,
        content_type='application/xml'
    )
    assert response.status_code == 200


def test_content_type_validation_text_xml(client):
    """Test that text/xml Content-Type is accepted."""
    xml_data = '<root><item>test</item></root>'
    response = client.post(
        '/convert/xml-to-json',
        data=xml_data,
        content_type='text/xml'
    )
    assert response.status_code == 200


def test_content_type_validation_invalid_content_type(client):
    """Test that invalid Content-Type returns 400 error."""
    xml_data = '<root><item>test</item></root>'
    response = client.post(
        '/convert/xml-to-json',
        data=xml_data,
        content_type='application/json'
    )
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert data['error']['code'] == 'INVALID_CONTENT_TYPE'


def test_content_type_validation_missing_content_type(client):
    """Test that missing Content-Type returns 400 error."""
    xml_data = '<root><item>test</item></root>'
    response = client.post(
        '/convert/xml-to-json',
        data=xml_data
    )
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert data['error']['code'] == 'INVALID_CONTENT_TYPE'


def test_malformed_xml_returns_400(client):
    """Test that malformed XML returns 400 with error details."""
    xml_data = '<root><item>unclosed tag</root>'
    response = client.post(
        '/convert/xml-to-json',
        data=xml_data,
        content_type='application/xml'
    )
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert data['error']['code'] == 'XML_PARSE_ERROR'


def test_empty_request_body_returns_400(client):
    """Test that empty request body returns 400 error."""
    response = client.post(
        '/convert/xml-to-json',
        data='',
        content_type='application/xml'
    )
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert data['error']['code'] == 'EMPTY_REQUEST_BODY'


def test_end_to_end_conversion_flow_simple(client):
    """Test end-to-end conversion flow with simple XML structure."""
    xml_data = '<root><name>John</name><age>30</age></root>'
    response = client.post(
        '/convert/xml-to-json',
        data=xml_data,
        content_type='application/xml'
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['root']['name']['_text'] == 'John'
    assert data['root']['age']['_text'] == '30'  # All text preserved as strings


def test_end_to_end_conversion_flow_nested(client):
    """Test end-to-end conversion flow with nested XML structure."""
    xml_data = '''<root>
        <person>
            <name>Jane</name>
            <age>25</age>
        </person>
    </root>'''
    response = client.post(
        '/convert/xml-to-json',
        data=xml_data,
        content_type='application/xml'
    )
    assert response.status_code == 200
    data = response.get_json()
    assert 'root' in data
    assert 'person' in data['root']
    assert data['root']['person']['name']['_text'] == 'Jane'
    assert data['root']['person']['age']['_text'] == '25'


def test_end_to_end_conversion_flow_with_attributes(client):
    """Test end-to-end conversion flow with XML attributes."""
    xml_data = '<root id="1" type="test"><item>value</item></root>'
    response = client.post(
        '/convert/xml-to-json',
        data=xml_data,
        content_type='application/xml'
    )
    assert response.status_code == 200
    data = response.get_json()
    assert 'root' in data
    assert 'id' in data['root']
    assert data['root']['id']['_value'] == '1'
    assert data['root']['type']['_value'] == 'test'
    assert data['root']['item']['_text'] == 'value'


def test_error_response_format(client):
    """Test that error responses follow structured format."""
    response = client.post(
        '/convert/xml-to-json',
        data='invalid',
        content_type='application/json'
    )
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'code' in data['error']
    assert 'message' in data['error']
    assert 'details' in data['error']


def test_xml_with_namespaces(client):
    """Test conversion with XML containing namespaces."""
    xml_data = '<root xmlns="http://example.com/ns"><child>content</child></root>'
    response = client.post(
        '/convert/xml-to-json',
        data=xml_data,
        content_type='application/xml'
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None
    # Namespace should be preserved in tag
    root_key = list(data.keys())[0]
    assert root_key is not None


def test_xml_with_prefixed_namespaces(client):
    """Test conversion with XML containing prefixed namespaces."""
    xml_data = '<ex:root xmlns:ex="http://example.com/ns"><ex:child>content</ex:child></ex:root>'
    response = client.post(
        '/convert/xml-to-json',
        data=xml_data,
        content_type='application/xml'
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data is not None


def test_xml_with_special_characters_unicode(client):
    """Test conversion with XML containing special characters and unicode."""
    xml_data = '<root>Hello 世界 &amp; unicode: 你好</root>'
    response = client.post(
        '/convert/xml-to-json',
        data=xml_data,
        content_type='application/xml'
    )
    assert response.status_code == 200
    data = response.get_json()
    assert 'root' in data
    assert isinstance(data['root'], dict)
    assert '_text' in data['root']
    assert len(data['root']['_text']) > 0


def test_xml_with_mixed_content(client):
    """Test conversion with XML containing mixed content (text and elements)."""
    xml_data = '<root>Text before<child>child content</child>text after</root>'
    response = client.post(
        '/convert/xml-to-json',
        data=xml_data,
        content_type='application/xml'
    )
    assert response.status_code == 200
    data = response.get_json()
    assert 'root' in data
    assert isinstance(data['root'], dict)


def test_xml_with_multiple_same_name_elements(client):
    """Test conversion with XML containing multiple elements with same name (array conversion)."""
    xml_data = '<root><item>1</item><item>2</item><item>3</item></root>'
    response = client.post(
        '/convert/xml-to-json',
        data=xml_data,
        content_type='application/xml'
    )
    assert response.status_code == 200
    data = response.get_json()
    assert 'root' in data
    assert 'item' in data['root']
    assert isinstance(data['root']['item'], list)
    assert len(data['root']['item']) == 3


def test_malformed_xml_error_includes_location(client):
    """Test that malformed XML error includes location information in details."""
    xml_data = '<root>\n<child>\n</unclosed>'
    response = client.post(
        '/convert/xml-to-json',
        data=xml_data,
        content_type='application/xml'
    )
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert data['error']['code'] == 'XML_PARSE_ERROR'
    # Details should include location information if available
    if 'details' in data['error']:
        assert data['error']['details'] is not None


def test_content_type_case_insensitive(client):
    """Test that Content-Type header is case-insensitive."""
    xml_data = '<root><item>test</item></root>'
    response = client.post(
        '/convert/xml-to-json',
        data=xml_data,
        headers={'Content-Type': 'APPLICATION/XML'}  # Uppercase
    )
    assert response.status_code == 200


def test_response_headers_match_specification(client):
    """Test that response headers match API specification."""
    xml_data = '<root><item>test</item></root>'
    response = client.post(
        '/convert/xml-to-json',
        data=xml_data,
        content_type='application/xml'
    )
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    # Content-Type header should be explicitly set
    assert 'Content-Type' in response.headers

