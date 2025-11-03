"""
Integration tests for XML to CSV conversion endpoint using XPath.

Tests verify XPath-based extraction of specific array items, excluding headers.
"""

import pytest
import csv
import json
import urllib.parse
from io import StringIO
from app import create_app


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_xml_to_csv_xpath_endpoint_success(client):
    """Test that successful POST /convert/xml-to-csv-xpath returns HTTP 200 OK with CSV response."""
    xml_data = '<root><header><info>test</info></header><items><item id="1"><name>Item1</name></item><item id="2"><name>Item2</name></item></items></root>'
    response = client.post(
        '/convert/xml-to-csv-xpath?xpath=//item',
        data=xml_data,
        content_type='application/xml'
    )
    assert response.status_code == 200
    assert response.data is not None


def test_xml_to_csv_xpath_endpoint_missing_xpath(client):
    """Test that missing XPath parameter returns 400 error."""
    xml_data = '<root><item>test</item></root>'
    response = client.post(
        '/convert/xml-to-csv-xpath',
        data=xml_data,
        content_type='application/xml'
    )
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert data['error']['code'] == 'MISSING_XPATH'


def test_xml_to_csv_xpath_endpoint_extracts_only_matched_elements(client):
    """Test that XPath extracts only matched elements, excluding headers."""
    xml_data = '<root><header><meta>ignore</meta></header><items><item id="1"><name>A</name></item><item id="2"><name>B</name></item></items></root>'
    response = client.post(
        '/convert/xml-to-csv-xpath?xpath=//item',
        data=xml_data,
        content_type='application/xml'
    )
    assert response.status_code == 200
    
    # Parse CSV and verify we only have item rows
    csv_text = response.data.decode('utf-8')
    reader = csv.DictReader(StringIO(csv_text))
    rows = list(reader)
    
    # Should have exactly 2 rows (one per item), no header data
    assert len(rows) == 2
    # Verify header is not in the data
    assert 'meta' not in rows[0].keys()  # Header element should not appear


def test_xml_to_csv_xpath_endpoint_with_namespaces(client):
    """Test XPath endpoint with namespace support."""
    xml_data = '''<root xmlns:wd="urn:com.workday/bsvc">
        <wd:Response_Data>
            <wd:Job_Requisition id="1"><wd:Title>Job1</wd:Title></wd:Job_Requisition>
            <wd:Job_Requisition id="2"><wd:Title>Job2</wd:Title></wd:Job_Requisition>
        </wd:Response_Data>
    </root>'''
    
    namespaces = json.dumps({"wd": "urn:com.workday/bsvc"})
    response = client.post(
        f'/convert/xml-to-csv-xpath?xpath=//wd:Job_Requisition&namespaces={urllib.parse.quote(namespaces)}',
        data=xml_data,
        content_type='application/xml'
    )
    assert response.status_code == 200
    
    # Verify we got 2 rows
    csv_text = response.data.decode('utf-8')
    reader = csv.DictReader(StringIO(csv_text))
    rows = list(reader)
    assert len(rows) == 2


def test_xml_to_csv_xpath_endpoint_custom_delimiter(client):
    """Test XPath endpoint with custom delimiter."""
    xml_data = '<root><item id="1"><name>Test</name><value>123</value></item></root>'
    response = client.post(
        '/convert/xml-to-csv-xpath?xpath=//item&delimiter=;',
        data=xml_data,
        content_type='application/xml'
    )
    assert response.status_code == 200
    csv_text = response.data.decode('utf-8')
    # Verify delimiter is used (should have semicolons separating columns)
    lines = csv_text.strip().split('\n')
    assert len(lines) >= 2  # Header + at least one data row
    # Check that semicolon appears in data rows (not just header)
    if len(lines) > 1:
        assert ';' in lines[1]  # Data row should have semicolons


def test_xml_to_csv_xpath_endpoint_invalid_xpath(client):
    """Test that invalid XPath returns 400 error."""
    xml_data = '<root><item>test</item></root>'
    response = client.post(
        '/convert/xml-to-csv-xpath?xpath=//[invalid',
        data=xml_data,
        content_type='application/xml'
    )
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert data['error']['code'] in ['XPATH_ERROR', 'INVALID_XPATH']


def test_xml_to_csv_xpath_endpoint_no_matches_returns_empty(client):
    """Test that XPath with no matches returns empty CSV."""
    xml_data = '<root><item>test</item></root>'
    response = client.post(
        '/convert/xml-to-csv-xpath?xpath=//nonexistent',
        data=xml_data,
        content_type='application/xml'
    )
    assert response.status_code == 200
    csv_text = response.data.decode('utf-8')
    # Should be empty or have only header
    assert len(csv_text.strip()) == 0 or csv_text.count('\n') == 0


def test_xml_to_csv_xpath_endpoint_complex_structure(client):
    """Test XPath endpoint with complex nested structure."""
    xml_data = '''<root>
        <metadata><version>1.0</version></metadata>
        <data>
            <record id="1"><name>Record1</name><value>100</value></record>
            <record id="2"><name>Record2</name><value>200</value></record>
            <record id="3"><name>Record3</name><value>300</value></record>
        </data>
    </root>'''
    
    response = client.post(
        '/convert/xml-to-csv-xpath?xpath=//record',
        data=xml_data,
        content_type='application/xml'
    )
    assert response.status_code == 200
    
    # Parse CSV
    csv_text = response.data.decode('utf-8')
    reader = csv.DictReader(StringIO(csv_text))
    rows = list(reader)
    
    # Should have exactly 3 rows (one per record), excluding metadata
    assert len(rows) == 3
    # Verify metadata is not in the CSV
    assert 'version' not in rows[0].keys()

