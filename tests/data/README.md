# Test Data Directory

This directory contains XML test fixtures used by the test suite.

## Available Fixtures

### Simple Structures
- **simple.xml**: Basic XML with single root and child elements
- **nested.xml**: Multi-level nested XML structure
- **empty-elements.xml**: XML with various empty element patterns

### Namespaces
- **namespaced-default.xml**: XML with default namespace
- **namespaced-prefixed.xml**: XML with prefixed namespace
- **namespaced-multiple.xml**: XML with multiple namespaces (default + prefixed)

### Attributes and Content
- **with-attributes.xml**: XML with attributes at multiple levels
- **mixed-content.xml**: XML with mixed content (text + elements)
- **multiple-same-name.xml**: XML with multiple elements having the same name

### Data Types
- **data-types.xml**: XML with various data types (strings, integers, floats, booleans)

### Special Characters
- **special-characters.xml**: XML with entities, unicode, and special characters

### Malformed XML (for error testing)
- **malformed-unclosed-tag.xml**: XML with unclosed tags
- **malformed-mismatched-tags.xml**: XML with mismatched opening/closing tags

### Complex Real-World Examples
- **example-complex.xml**: Large complex XML (SOAP/Workday structure)

## Usage in Tests

### Option 1: Using Helper Function

```python
from tests.fixtures import load_xml_fixture

def test_simple_xml():
    xml_content = load_xml_fixture('simple.xml')
    root = parse_xml(xml_content)
    assert root is not None
```

### Option 2: Using Pytest Fixture (Recommended)

```python
import pytest
from tests.fixtures import load_xml_fixture

@pytest.fixture
def simple_xml():
    """Load simple.xml fixture."""
    return load_xml_fixture('simple.xml')

def test_simple_xml_parsing(simple_xml):
    root = parse_xml(simple_xml)
    assert root is not None
```

### Option 3: Direct Path Access

```python
from pathlib import Path

def test_xml():
    data_dir = Path(__file__).parent / "data"
    xml_file = data_dir / "simple.xml"
    xml_content = xml_file.read_text(encoding='utf-8')
    root = parse_xml(xml_content)
    assert root is not None
```

## Fixture Purposes

- **Simple structures**: Test basic parsing and conversion
- **Nested structures**: Test deep hierarchy handling
- **Namespaces**: Test namespace preservation and handling
- **Attributes**: Test attribute conversion to JSON
- **Mixed content**: Test text + element handling
- **Data types**: Test type preservation (int, float, bool, string)
- **Special characters**: Test encoding, entities, unicode
- **Malformed XML**: Test error handling and validation
- **Complex examples**: Test real-world scenarios

## Reusability

All fixtures in this directory are designed to be reusable across:
- Unit tests (`tests/unit/`)
- Integration tests (`tests/integration/`)
- Performance tests (`tests/performance/`)

Use the `load_xml_fixture()` helper function from `tests.fixtures` for consistent access.

