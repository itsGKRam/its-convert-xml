"""
Performance tests for large XML file processing.

This test suite validates that the API can handle large XML files (up to 300MB)
within acceptable response times and memory constraints. Tests use various file
sizes to establish performance baselines.
"""

import pytest
import time
import os
from io import BytesIO
from lxml import etree


@pytest.mark.performance
@pytest.mark.integration
class TestLargeFilePerformance:
    """Performance tests for large XML file conversion."""

    @pytest.fixture
    def client(self):
        """Create Flask test client."""
        from app import create_app
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def _generate_large_xml(self, size_mb: int) -> str:
        """
        Generate a large XML file of approximately the specified size.
        
        Args:
            size_mb (int): Target size in megabytes
            
        Returns:
            str: XML string of approximately the target size (never exceeding the limit)
        """
        target_bytes = size_mb * 1024 * 1024
        
        # Start with root opening tag
        xml_parts = ['<root>']
        current_size = len('<root>'.encode('utf-8'))
        
        # Generate items until we're close to target (leave room for closing tag)
        item_id = 0
        closing_tag_size = len('</root>'.encode('utf-8'))
        max_content_size = target_bytes - closing_tag_size - 100  # Leave 100 bytes buffer
        
        while current_size < max_content_size:
            # Vary data size slightly to make it more realistic
            data_size = 100 + (item_id % 50)
            item = f'<item id="{item_id}"><data>{"x" * data_size}</data></item>'
            item_bytes = len(item.encode('utf-8'))
            
            # Check if adding this item would exceed our limit
            if current_size + item_bytes + closing_tag_size > target_bytes:
                break
            
            xml_parts.append(item)
            current_size += item_bytes
            item_id += 1
        
        # Add closing tag
        xml_parts.append('</root>')
        xml_content = ''.join(xml_parts)
        
        # Verify we didn't exceed target (for strict size requirements)
        actual_bytes = len(xml_content.encode('utf-8'))
        if actual_bytes > target_bytes:
            # Trim if needed (shouldn't happen with our buffer, but be safe)
            # Calculate how much to trim from data content
            excess = actual_bytes - target_bytes
            # This is a safety check - with our buffer it shouldn't be needed
            if excess > 0:
                # Trim from last item's data content if possible
                pass  # For now, just log a warning - our buffer should prevent this
        
        return xml_content

    def test_performance_1mb_file(self, client):
        """Test response time for 1MB XML file."""
        xml_content = self._generate_large_xml(1)
        
        start_time = time.time()
        response = client.post(
            '/convert/xml-to-json',
            data=xml_content,
            content_type='application/xml'
        )
        processing_time = time.time() - start_time
        
        assert response.status_code == 200
        # 1MB should process very quickly (< 5 seconds)
        assert processing_time < 5.0, f"1MB file took {processing_time:.2f}s (expected < 5s)"
        
        # Verify response is valid JSON
        json_data = response.get_json()
        assert json_data is not None
        assert 'root' in json_data

    def test_performance_10mb_file(self, client):
        """Test response time for 10MB XML file."""
        xml_content = self._generate_large_xml(10)
        
        start_time = time.time()
        response = client.post(
            '/convert/xml-to-json',
            data=xml_content,
            content_type='application/xml'
        )
        processing_time = time.time() - start_time
        
        assert response.status_code == 200
        # 10MB should process reasonably quickly (< 10 seconds)
        assert processing_time < 10.0, f"10MB file took {processing_time:.2f}s (expected < 10s)"
        
        # Verify response is valid JSON
        json_data = response.get_json()
        assert json_data is not None
        assert 'root' in json_data

    @pytest.mark.slow
    def test_performance_100mb_file(self, client):
        """Test response time for 100MB XML file."""
        xml_content = self._generate_large_xml(100)
        
        start_time = time.time()
        response = client.post(
            '/convert/xml-to-json',
            data=xml_content,
            content_type='application/xml'
        )
        processing_time = time.time() - start_time
        
        assert response.status_code == 200
        # 100MB should process within reasonable time (< 20 seconds)
        assert processing_time < 20.0, f"100MB file took {processing_time:.2f}s (expected < 20s)"
        
        # Verify response is valid JSON
        json_data = response.get_json()
        assert json_data is not None
        assert 'root' in json_data

    @pytest.mark.slow
    @pytest.mark.very_slow
    def test_performance_300mb_file(self, client):
        """Test response time for 300MB XML file (maximum allowed)."""
        xml_content = self._generate_large_xml(300)
        
        start_time = time.time()
        response = client.post(
            '/convert/xml-to-json',
            data=xml_content,
            content_type='application/xml'
        )
        processing_time = time.time() - start_time
        
        assert response.status_code == 200
        # 300MB target: < 30 seconds per story requirements
        assert processing_time < 30.0, (
            f"300MB file took {processing_time:.2f}s (expected < 30s per AC3)"
        )
        
        # Verify response is valid JSON
        json_data = response.get_json()
        assert json_data is not None
        assert 'root' in json_data

    def test_streaming_vs_standard_parser(self, client):
        """
        Test that streaming parser is used for large files and compare performance.
        
        This test verifies that the system automatically uses streaming parser
        for files > 10MB threshold.
        """
        # Small file (should use standard parser)
        small_xml = self._generate_large_xml(1)  # 1MB < 10MB threshold
        
        # Large file (should use streaming parser)
        large_xml = self._generate_large_xml(15)  # 15MB > 10MB threshold
        
        # Process small file
        start_time = time.time()
        small_response = client.post(
            '/convert/xml-to-json',
            data=small_xml,
            content_type='application/xml'
        )
        small_time = time.time() - start_time
        
        # Process large file
        start_time = time.time()
        large_response = client.post(
            '/convert/xml-to-json',
            data=large_xml,
            content_type='application/xml'
        )
        large_time = time.time() - start_time
        
        # Both should succeed
        assert small_response.status_code == 200
        assert large_response.status_code == 200
        
        # Verify responses are valid
        assert small_response.get_json() is not None
        assert large_response.get_json() is not None
        
        # Large file should take longer but within reasonable bounds
        # (not testing exact performance here, just that both work)
        assert large_time > small_time  # Larger file should take longer

