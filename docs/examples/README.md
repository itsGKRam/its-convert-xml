# Example Files

This directory contains example XML files and their expected JSON outputs for testing the XML-to-JSON conversion service.

## Files

| XML File | JSON File | Description |
|----------|-----------|-------------|
| `simple.xml` | `simple.json` | Simple XML structure with basic elements |
| `nested.xml` | `nested.json` | Nested XML structure with multiple levels |
| `namespaced.xml` | `namespaced.json` | XML with namespace declarations |
| `with-attributes.xml` | `with-attributes.json` | XML with attributes and nested elements |

## Usage

### Using curl

Convert `simple.xml` to JSON:

```bash
curl -X POST http://localhost:5000/convert/xml-to-json \
  -H "Content-Type: application/xml" \
  --data-binary @docs/examples/simple.xml
```

Expected response should match `simple.json`.

### Using Python

```python
import requests

# Read XML file
with open('docs/examples/simple.xml', 'r') as f:
    xml_content = f.read()

# Convert to JSON
response = requests.post(
    'http://localhost:5000/convert/xml-to-json',
    headers={'Content-Type': 'application/xml'},
    data=xml_content
)

if response.status_code == 200:
    json_result = response.json()
    print(json_result)
else:
    print(f"Error: {response.json()}")
```

### Testing All Examples

Run all examples to verify conversion accuracy:

```bash
# Simple XML
curl -X POST http://localhost:5000/convert/xml-to-json \
  -H "Content-Type: application/xml" \
  --data-binary @docs/examples/simple.xml > /tmp/simple-output.json

# Nested XML
curl -X POST http://localhost:5000/convert/xml-to-json \
  -H "Content-Type: application/xml" \
  --data-binary @docs/examples/nested.xml > /tmp/nested-output.json

# Namespaced XML
curl -X POST http://localhost:5000/convert/xml-to-json \
  -H "Content-Type: application/xml" \
  --data-binary @docs/examples/namespaced.xml > /tmp/namespaced-output.json

# XML with attributes
curl -X POST http://localhost:5000/convert/xml-to-json \
  -H "Content-Type: application/xml" \
  --data-binary @docs/examples/with-attributes.xml > /tmp/with-attributes-output.json
```

Compare outputs with expected JSON files in this directory.

## Example Details

### Simple XML (`simple.xml`)

Demonstrates basic XML-to-JSON conversion with simple element structure.

**Key Features:**
- Basic elements
- Data type preservation (numbers, strings)
- Simple nested structure

### Nested XML (`nested.xml`)

Shows how deeply nested XML structures are converted to JSON.

**Key Features:**
- Multiple nesting levels
- Array handling (multiple `<book>` elements)
- Mixed content types

### Namespaced XML (`namespaced.xml`)

Demonstrates XML namespace handling in JSON conversion.

**Key Features:**
- Multiple namespace declarations
- Namespace prefixes preserved in JSON
- Namespace attributes included in output

### XML with Attributes (`with-attributes.xml`)

Shows how XML attributes are converted to JSON.

**Key Features:**
- Attributes converted to `@attribute` keys
- Boolean and numeric attribute values preserved
- Attributes on nested elements
- Empty elements with attributes

## Conversion Rules

The conversion service follows these rules:

1. **Attributes**: XML attributes are converted to an `@attributes` object in JSON containing all attribute key-value pairs
2. **Namespaces**: XML namespace declarations are preserved in the `@attributes` object with `xmlns:*` keys
3. **Multiple Elements**: Multiple elements with the same name become JSON arrays
4. **Data Types**: Strings, numbers, and booleans are preserved in JSON
5. **Nested Structures**: Deeply nested XML is properly converted to nested JSON
6. **Text Content**: Element text content is stored in the `#text` key when mixed with child elements or attributes

## Troubleshooting

If the conversion output doesn't match the expected JSON:

1. **Check XML validity**: Ensure your XML is well-formed
2. **Verify Content-Type**: Must be `application/xml` or `text/xml`
3. **Check encoding**: XML should be UTF-8 encoded
4. **Compare structure**: Verify XML structure matches expected output
5. **Review error messages**: Check error response for specific issues

See [Error Reference](../error-reference.md) for detailed error codes and troubleshooting.

## Additional Resources

- [API Reference](../api-reference.md) - Complete API documentation
- [Error Reference](../error-reference.md) - Error codes and troubleshooting
- [OpenAPI Specification](../openapi.yaml) - Machine-readable API spec

