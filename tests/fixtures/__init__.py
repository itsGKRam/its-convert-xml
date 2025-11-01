"""
Test fixtures module for reusable XML test data.

This module provides pytest fixtures and helper functions for loading
XML test fixtures from the tests/data directory. Fixtures can be used
across unit, integration, and performance tests.
"""

from pathlib import Path

# Path to test data directory
TEST_DATA_DIR = Path(__file__).parent.parent / "data"


def load_xml_fixture(filename: str) -> str:
    """
    Load an XML fixture file from tests/data directory.
    
    Args:
        filename: Name of the XML file (e.g., 'simple.xml', 'nested.xml')
        
    Returns:
        XML content as string
        
    Raises:
        FileNotFoundError: If fixture file doesn't exist
        
    Example:
        xml_content = load_xml_fixture('simple.xml')
    """
    fixture_path = TEST_DATA_DIR / filename
    if not fixture_path.exists():
        raise FileNotFoundError(f"Fixture file not found: {fixture_path}")
    return fixture_path.read_text(encoding='utf-8')


