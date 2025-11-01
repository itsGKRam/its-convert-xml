# API Reference

Complete API documentation for the XML-to-JSON conversion service.

## Base URL

All endpoints are relative to the base URL. For local development:
```
http://localhost:5000
```

## Endpoints

### GET /health

Health check endpoint for monitoring and orchestration platforms (Kubernetes, ECS, etc.).

**Request:**
- Method: `GET`
- URL: `/health`
- Headers: None required
- Body: None

**Success Response:**
- Status Code: `200 OK`
- Content-Type: `application/json`
- Body:
```json
{
  "status": "healthy"
}
```

**Example:**
```bash
curl http://localhost:5000/health
```

---

### POST /convert/xml-to-json

Convert XML data to JSON format.

#### Request

**HTTP Method:** `POST`

**URL Path:** `/convert/xml-to-json`

**Headers:**
- `Content-Type` (required): Must be either `application/xml` or `text/xml`
- `Content-Length` (optional): Request body size in bytes (checked if provided)

**Request Body:**
- Content: Valid XML string
- Size Limit: Maximum 300MB (314,572,800 bytes)
- Encoding: UTF-8

**Example Request:**
```bash
curl -X POST http://localhost:5000/convert/xml-to-json \
  -H "Content-Type: application/xml" \
  -d '<root><name>John</name><age>30</age></root>'
```

**Example Request (from file):**
```bash
curl -X POST http://localhost:5000/convert/xml-to-json \
  -H "Content-Type: application/xml" \
  --data-binary @input.xml
```

#### Success Response

**Status Code:** `200 OK`

**Headers:**
- `Content-Type: application/json`

**Response Body:** JSON representation of the input XML

**Example Response:**
```json
{
  "root": {
    "name": "John",
    "age": 30
  }
}
```

**Example with Attributes:**
```xml
<!-- Input XML -->
<user id="123" active="true">
  <name>Alice</name>
  <email>alice@example.com</email>
</user>
```

```json
// Output JSON
{
  "user": {
    "@attributes": {
      "id": "123",
      "active": "true"
    },
    "name": "Alice",
    "email": "alice@example.com"
  }
}
```

**Example with Nested Elements:**
```xml
<!-- Input XML -->
<catalog>
  <book>
    <title>Python Guide</title>
    <author>
      <name>John Doe</name>
      <email>john@example.com</email>
    </author>
    <price>29.99</price>
  </book>
</catalog>
```

```json
// Output JSON
{
  "catalog": {
    "book": {
      "title": "Python Guide",
      "author": {
        "name": "John Doe",
        "email": "john@example.com"
      },
      "price": 29.99
    }
  }
}
```

**Example with Namespaces:**
```xml
<!-- Input XML -->
<root xmlns:ns="http://example.com/namespace">
  <ns:item>Value</ns:item>
</root>
```

```json
// Output JSON
{
  "root": {
    "@xmlns:ns": "http://example.com/namespace",
    "ns:item": "Value"
  }
}
```

#### Error Responses

All error responses follow a consistent JSON structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Additional context (optional)"
  }
}
```

**Error Response Status Codes:**
- `400 Bad Request`: Client error (invalid Content-Type, malformed XML, empty body)
- `413 Payload Too Large`: Request size exceeds 300MB limit
- `500 Internal Server Error`: Server-side conversion error

For detailed error codes and troubleshooting, see [Error Reference](error-reference.md).

#### Performance Characteristics

- **Small files (< 1MB)**: Typically processes in < 1 second
- **Medium files (1-10MB)**: Typically processes in 1-5 seconds
- **Large files (10-300MB)**: Processes in under 30 seconds
- **Memory efficient**: Uses streaming XML parsing for large files

#### Size Limits

- **Maximum Request Size**: 300MB (314,572,800 bytes)
- **Validation**: Content-Length header is validated before processing
- **Early Rejection**: Requests exceeding the limit are rejected immediately to save server resources

#### Data Type Preservation

The conversion service preserves data types in JSON output:
- **Strings**: Preserved as strings
- **Numbers**: Converted to integers or floats (e.g., `30` → `30`, `29.99` → `29.99`)
- **Booleans**: Converted to boolean values (e.g., `"true"` → `true`, `"false"` → `false`)

#### XML Features Supported

- **Attributes**: Converted to `@attributes` object in JSON containing all attribute key-value pairs
- **Namespaces**: Preserved in JSON output with namespace prefixes and namespace declarations in `@attributes`
- **Nested Elements**: Deeply nested structures properly converted
- **Mixed Content**: Text and elements mixed together are handled appropriately (text stored in `#text` key)
- **Comments**: XML comments are preserved in conversion
- **Processing Instructions**: XML processing instructions are preserved

#### Python Client Example

```python
import requests

url = "http://localhost:5000/convert/xml-to-json"
headers = {"Content-Type": "application/xml"}
xml_data = """
<user>
    <name>Alice</name>
    <email>alice@example.com</email>
</user>
"""

response = requests.post(url, headers=headers, data=xml_data)
if response.status_code == 200:
    json_result = response.json()
    print(json_result)
else:
    error = response.json()
    print(f"Error: {error['error']['message']}")
```

---

## Additional Resources

- [Error Reference](error-reference.md) - Complete error codes and troubleshooting guide
- [OpenAPI Specification](openapi.yaml) - Machine-readable API specification
- [Example Files](examples/) - Sample XML inputs and expected JSON outputs

