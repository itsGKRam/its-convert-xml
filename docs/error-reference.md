# Error Reference

Complete error codes and troubleshooting guide for the XML-to-JSON conversion service.

## Error Response Format

All error responses follow a consistent JSON structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Additional context or location information (optional)"
  }
}
```

## HTTP Status Code Mapping

| HTTP Status Code | Description | Use Case |
|-----------------|-------------|----------|
| `400 Bad Request` | Client error | Invalid Content-Type, malformed XML, empty request body |
| `413 Payload Too Large` | Request too large | Request size exceeds 300MB limit |
| `500 Internal Server Error` | Server error | Unexpected server-side conversion error |

## Error Codes

### INVALID_CONTENT_TYPE

**HTTP Status:** `400 Bad Request`

**Description:** The request is missing the required `Content-Type` header or the header value is not supported.

**Required Content-Type Values:**
- `application/xml`
- `text/xml`

**Error Response Example:**
```json
{
  "error": {
    "code": "INVALID_CONTENT_TYPE",
    "message": "Content-Type must be application/xml or text/xml",
    "details": "Received Content-Type: application/json"
  }
}
```

**Common Causes:**
- Missing `Content-Type` header
- Incorrect `Content-Type` value (e.g., `application/json`, `text/plain`)
- Typos in header name or value

**How to Fix:**
1. Ensure the request includes a `Content-Type` header
2. Set the header value to either `application/xml` or `text/xml`
3. Example:
   ```bash
   curl -X POST http://localhost:5000/convert/xml-to-json \
     -H "Content-Type: application/xml" \
     -d '<root>content</root>'
   ```

---

### XML_PARSE_ERROR

**HTTP Status:** `400 Bad Request`

**Description:** The XML content in the request body is malformed or contains syntax errors.

**Error Response Example:**
```json
{
  "error": {
    "code": "XML_PARSE_ERROR",
    "message": "XML syntax error: mismatched tag",
    "details": "Line 5, column 12"
  }
}
```

**Common Causes:**
- Unclosed XML tags
- Mismatched opening and closing tags
- Invalid XML characters
- Malformed XML structure
- Encoding issues

**How to Fix:**
1. Validate your XML content using an XML validator
2. Check that all opening tags have corresponding closing tags
3. Ensure proper XML structure (single root element)
4. Verify XML encoding is UTF-8
5. Check the `details` field for line and column information to locate the error

**Example Fix:**
```xml
<!-- Invalid XML (missing closing tag) -->
<root>
  <item>Value</item>
  <item>Another value
</root>

<!-- Valid XML -->
<root>
  <item>Value</item>
  <item>Another value</item>
</root>
```

---

### FILE_SIZE_EXCEEDED

**HTTP Status:** `413 Payload Too Large`

**Description:** The request body size exceeds the maximum allowed limit of 300MB.

**Error Response Example:**
```json
{
  "error": {
    "code": "FILE_SIZE_EXCEEDED",
    "message": "Request size exceeds maximum limit of 300MB",
    "details": "Maximum allowed size is 300MB (314572800 bytes)"
  }
}
```

**Size Limits:**
- Maximum file size: **300MB** (314,572,800 bytes)
- Validation occurs early to save server resources

**Common Causes:**
- XML file larger than 300MB
- Incorrect file selection
- Need to split large files into smaller chunks

**How to Fix:**
1. Check the file size before sending the request
2. Split large XML files into smaller chunks if possible
3. Use streaming or chunked processing for very large files
4. Consider compressing the XML if appropriate
5. Contact support if you require processing files larger than 300MB

**Example:**
```bash
# Check file size before sending
ls -lh large-file.xml

# If file is too large, consider splitting or compressing
```

---

### EMPTY_REQUEST_BODY

**HTTP Status:** `400 Bad Request`

**Description:** The request body is empty or contains no XML content.

**Error Response Example:**
```json
{
  "error": {
    "code": "EMPTY_REQUEST_BODY",
    "message": "Request body is empty",
    "details": "XML content is required in the request body"
  }
}
```

**Common Causes:**
- Request sent without body content
- Empty XML file
- File upload failed silently
- Content not properly included in request

**How to Fix:**
1. Ensure the request includes XML content in the body
2. Verify file is not empty
3. Check that the file path is correct when reading from file
4. Ensure proper encoding when sending XML data

**Example Fix:**
```bash
# Correct - includes XML in request body
curl -X POST http://localhost:5000/convert/xml-to-json \
  -H "Content-Type: application/xml" \
  -d '<root><data>content</data></root>'

# Correct - reads XML from file
curl -X POST http://localhost:5000/convert/xml-to-json \
  -H "Content-Type: application/xml" \
  --data-binary @input.xml
```

---

### REQUEST_READ_ERROR

**HTTP Status:** `400 Bad Request`

**Description:** The server failed to read the request body due to an error during request processing.

**Error Response Example:**
```json
{
  "error": {
    "code": "REQUEST_READ_ERROR",
    "message": "Failed to read request body",
    "details": "Connection error: stream closed"
  }
}
```

**Common Causes:**
- Network connection interrupted during request
- Request stream closed prematurely
- Timeout during request transmission
- Server-side I/O error

**How to Fix:**
1. Retry the request
2. Check network connectivity
3. Verify request is complete before sending
4. Check for timeout settings that might interrupt large file uploads
5. If the issue persists, contact support

---

### CONVERSION_ERROR

**HTTP Status:** `500 Internal Server Error`

**Description:** An error occurred during the XML-to-JSON conversion process. This is a server-side error.

**Error Response Example:**
```json
{
  "error": {
    "code": "CONVERSION_ERROR",
    "message": "An unexpected error occurred during conversion",
    "details": "Internal server error"
  }
}
```

**Common Causes:**
- Server-side processing error
- Memory exhaustion during conversion
- Corrupted XML data that passes initial parsing
- Internal service failure

**How to Fix:**
1. Verify the XML content is valid
2. Retry the request (may be a transient error)
3. If the error persists, try with a smaller file to isolate the issue
4. Check server logs for detailed error information
5. Contact support if the issue continues

---

### SERVER_ERROR

**HTTP Status:** `500 Internal Server Error`

**Description:** An unexpected server error occurred. Detailed error information is logged server-side but not exposed to clients for security reasons.

**Error Response Example:**
```json
{
  "error": {
    "code": "SERVER_ERROR",
    "message": "An unexpected error occurred during conversion",
    "details": "Internal server error"
  }
}
```

**Common Causes:**
- Unexpected exception in server code
- System resource exhaustion
- Database or external service failures
- Configuration errors

**How to Fix:**
1. Retry the request (may be a transient error)
2. Verify service is running and healthy (check `/health` endpoint)
3. Wait a few moments and retry
4. If the error persists, contact support with:
   - Request timestamp
   - Request size and content type
   - Error code received

---

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue: "Content-Type must be application/xml or text/xml"

**Problem:** The `Content-Type` header is missing or incorrect.

**Solution:**
```bash
# Ensure Content-Type header is set correctly
curl -X POST http://localhost:5000/convert/xml-to-json \
  -H "Content-Type: application/xml" \
  -d '<root>content</root>'
```

#### Issue: "Request size exceeds maximum limit"

**Problem:** The XML file is larger than 300MB.

**Solutions:**
1. Split the XML file into smaller chunks
2. Compress the XML file (if supported by your use case)
3. Contact support to discuss options for processing larger files

#### Issue: "XML syntax error"

**Problem:** The XML content is malformed.

**Solutions:**
1. Validate XML using an XML validator tool
2. Check the error `details` field for line and column information
3. Common XML issues:
   - Unclosed tags: `<tag>content` → `<tag>content</tag>`
   - Mismatched tags: `<tag1>content</tag2>` → `<tag1>content</tag1>`
   - Invalid characters: Remove or escape invalid XML characters
   - Encoding issues: Ensure UTF-8 encoding

#### Issue: "Empty request body"

**Problem:** No XML content was sent in the request.

**Solution:**
```bash
# Ensure XML content is included
curl -X POST http://localhost:5000/convert/xml-to-json \
  -H "Content-Type: application/xml" \
  -d '<root><data>content</data></root>'
```

#### Issue: Intermittent 500 errors

**Problem:** Server errors that occur occasionally.

**Solutions:**
1. Retry the request (may be transient)
2. Check if the issue is specific to certain XML files
3. Verify service health: `curl http://localhost:5000/health`
4. Check server logs for detailed error information
5. Contact support if the issue persists

### Best Practices

1. **Always set Content-Type header** to avoid `INVALID_CONTENT_TYPE` errors
2. **Validate XML before sending** to catch syntax errors early
3. **Check file size** before sending large files to avoid `FILE_SIZE_EXCEEDED` errors
4. **Handle errors gracefully** in your client code by checking status codes
5. **Retry transient errors** (5xx status codes) with exponential backoff
6. **Log error responses** for debugging and troubleshooting

### Client Error Handling Example

```python
import requests
from requests.exceptions import RequestException

def convert_xml_to_json(xml_content, base_url="http://localhost:5000"):
    """Convert XML to JSON with proper error handling."""
    url = f"{base_url}/convert/xml-to-json"
    headers = {"Content-Type": "application/xml"}
    
    try:
        response = requests.post(url, headers=headers, data=xml_content, timeout=60)
        
        if response.status_code == 200:
            return response.json(), None
        
        # Handle error responses
        error_data = response.json()
        error_code = error_data.get("error", {}).get("code")
        error_message = error_data.get("error", {}).get("message")
        error_details = error_data.get("error", {}).get("details")
        
        return None, {
            "code": error_code,
            "message": error_message,
            "details": error_details,
            "status_code": response.status_code
        }
        
    except RequestException as e:
        return None, {
            "code": "NETWORK_ERROR",
            "message": f"Network error: {str(e)}",
            "details": None
        }
```

## Additional Resources

- [API Reference](api-reference.md) - Complete API endpoint documentation
- [OpenAPI Specification](openapi.yaml) - Machine-readable API specification
- [Example Files](examples/) - Sample XML inputs and expected JSON outputs

