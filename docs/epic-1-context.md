# Epic Technical Specification: Project Foundation & XML-to-JSON Conversion

Date: 2025-10-30
Author: GK Ram
Epic ID: 1
Status: Draft

---

## Overview

This epic establishes the complete Flask application foundation and delivers the core XML-to-JSON conversion endpoint with full production-ready features. As outlined in the PRD, this microservice addresses the need for reliable XML-to-JSON transformation as a reusable, scalable service that handles large and complex XML files efficiently. The epic delivers all foundational infrastructure including project structure, XML parsing and validation, conversion engine, error handling, performance optimization, testing framework, documentation, and deployment configuration. Upon completion, the service will provide a fully functional POST endpoint at `/convert/xml-to-json` capable of handling files up to 300MB with robust error reporting and consistent JSON responses.

## Objectives and Scope

**In-Scope:**
- Flask application structure with proper project organization (app/, tests/, configuration files)
- Core XML parsing and validation using lxml library with namespace support
- XML-to-JSON conversion engine preserving all elements, attributes, and hierarchy
- POST endpoint `/convert/xml-to-json` with Content-Type validation
- Structured JSON error responses for all error scenarios (HTTP 400, 413, 500)
- Request size validation and enforcement (300MB limit)
- Performance optimization for large file handling (streaming, memory efficiency)
- Comprehensive testing infrastructure (unit, integration, performance tests)
- API documentation (README, OpenAPI/Swagger specification)
- Production deployment configuration (Docker, Gunicorn, environment variables)
- Health check endpoint for monitoring

**Out-of-Scope (per PRD):**
- CSV, String, or YAML conversion endpoints (deferred to Epic 2)
- Batch processing of multiple XML files
- File upload endpoints or persistent storage
- Authentication/authorization mechanisms
- Advanced rate limiting beyond size limits
- Asynchronous processing or job queues
- Bidirectional conversions (JSON to XML)
- Transformation customization (XSLT, XPath filters)
- Database integration or conversion history tracking

## System Architecture Alignment

This epic implements the foundational components of the Flask-based REST API microservice architecture as defined in the Decision Architecture document. The implementation follows the established technology stack decisions:

- **Runtime & Framework**: Python 3.11 with Flask 3.0.x for the web framework, using the app factory pattern for modular initialization
- **XML Processing**: lxml library for efficient parsing and validation, providing better performance for large files (300MB requirement) and robust namespace handling
- **Production Server**: Gunicorn WSGI server configuration for deployment
- **Testing**: pytest framework with structured test organization (unit/, integration/, performance/)

The epic creates the core service modules (`app/services/xml_parser.py`, `app/services/json_converter.py`) and route handlers (`app/routes/convert.py`) that establish patterns for consistency and extensibility. The error handling architecture (`app/exceptions.py`, Flask error handlers) ensures structured JSON responses across all endpoints, setting the foundation for Epic 2's additional conversion formats.

Key architectural constraints enforced:
- Stateless service architecture (no persistent storage)
- Memory-efficient streaming for large file processing
- Consistent error response format: `{"error": {"code": "...", "message": "...", "details": "..."}}`
- Environment-based configuration following 12-factor app principles

## Detailed Design

### Services and Modules

| Module | Responsibility | Inputs | Outputs | Owner |
|--------|---------------|--------|---------|-------|
| `app/__init__.py` | Flask app factory, blueprint registration | Configuration object | Flask app instance | Core |
| `app/config.py` | Configuration management from environment variables | Environment variables, defaults | Configuration object with settings (MAX_FILE_SIZE, LOG_LEVEL, etc.) | Core |
| `app/exceptions.py` | Custom exception classes for error handling | Error context | Exception instances (XMLValidationError, FileSizeExceededError, ConversionError) | Core |
| `app/routes/convert.py` | HTTP route handlers for conversion endpoints | Flask request objects | Flask response objects (JSON success or error) | Routes |
| `app/services/xml_parser.py` | XML parsing and validation logic | XML string, validation flags | Parsed XML tree object or raises XMLValidationError | Services |
| `app/services/json_converter.py` | XML-to-JSON conversion logic | Parsed XML tree object | JSON-serializable dict structure | Services |
| `app/utils/validators.py` | Request validation utilities (Content-Type, size) | Request object, configuration | Validation result or raises validation exceptions | Utils |

### Data Models and Contracts

**In-Memory Data Structures (Stateless Service):**

**XML Input:**
- Type: String (request body)
- Constraints: Valid XML syntax, max 300MB
- Encoding: UTF-8 assumed, validated during parsing

**Parsed XML Tree:**
- Type: lxml.etree._Element or lxml.etree._ElementTree
- Structure: Hierarchical tree preserving elements, attributes, namespaces, text content
- Validation: Syntax check, namespace resolution, structure integrity

**JSON Output:**
- Type: JSON-serializable dict/object
- Structure: Preserves XML hierarchy as nested objects
- Schema: Dynamic based on input XML (no fixed schema)
- Special handling:
  - XML elements → JSON objects with element name as key
  - XML attributes → JSON object properties (prefixed or in separate structure)
  - XML text content → JSON string values
  - XML namespaces → Incorporated into keys or namespace map

**Error Response Schema:**
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Additional context (optional)"
  }
}
```

**Request Validation Schema:**
- Content-Type: `application/xml` or `text/xml` (case-insensitive)
- Content-Length: ≤ 300MB (314572800 bytes)
- Method: POST only

### APIs and Interfaces

**POST /convert/xml-to-json**

**Request:**
- Method: POST
- Headers:
  - `Content-Type`: `application/xml` or `text/xml` (required)
  - `Content-Length`: Size in bytes (optional, validated if present)
- Body: XML content as string (up to 300MB)
- Path: `/convert/xml-to-json`

**Success Response:**
- Status: 200 OK
- Headers:
  - `Content-Type`: `application/json`
- Body: JSON representation of XML structure

**Error Responses:**

| Status | Error Code | Scenario | Message Example |
|--------|-----------|----------|-----------------|
| 400 | `INVALID_CONTENT_TYPE` | Missing or incorrect Content-Type header | "Content-Type must be application/xml or text/xml" |
| 400 | `XML_PARSE_ERROR` | Invalid XML syntax | "Invalid XML syntax at line 10, column 5: unclosed tag <item>" |
| 413 | `FILE_SIZE_EXCEEDED` | Request exceeds 300MB limit | "Request size exceeds maximum limit of 300MB" |
| 500 | `CONVERSION_ERROR` | Server-side conversion failure | "Internal server error during conversion" |
| 500 | `SERVER_ERROR` | Unexpected server error | "An unexpected error occurred" |

**Route Handler Interface:**
```python
def convert_xml_to_json() -> Response:
    """
    POST /convert/xml-to-json endpoint handler
    Returns Flask Response with JSON content or error
    """
```

**Service Layer Interfaces:**

```python
def parse_xml(xml_string: str) -> etree._Element:
    """
    Parse and validate XML string
    Raises XMLValidationError on invalid XML
    Returns parsed XML tree
    """

def convert_to_json(xml_element: etree._Element) -> dict:
    """
    Convert parsed XML element to JSON-serializable dict
    Preserves hierarchy, attributes, namespaces
    Returns dict structure
    """

def validate_request(request: Request) -> None:
    """
    Validate request headers and size
    Raises validation exceptions on failure
    Returns None on success
    """
```

**GET /health**

**Request:**
- Method: GET
- Path: `/health`

**Success Response:**
- Status: 200 OK
- Body: `{"status": "healthy"}`

### Workflows and Sequencing

**Request Processing Flow:**

1. **Request Reception** (Route Handler)
   - Flask receives POST request at `/convert/xml-to-json`
   - Route handler `convert_xml_to_json()` invoked

2. **Request Validation** (Validator Service)
   - Check Content-Type header (must be `application/xml` or `text/xml`)
   - Check Content-Length if present (must be ≤ 300MB)
   - Read request body with size limit enforcement
   - On validation failure: Return HTTP 400/413 with structured error

3. **XML Parsing** (XML Parser Service)
   - Parse XML string using lxml library
   - Validate XML syntax and structure
   - Handle XML namespaces
   - On parse error: Return HTTP 400 with error location (line/column)

4. **Conversion** (JSON Converter Service)
   - Transform XML tree to JSON-serializable dict structure
   - Preserve all elements, attributes, hierarchy
   - Handle namespace representation in JSON keys
   - On conversion error: Return HTTP 500 with generic error (details logged)

5. **Response Generation** (Route Handler)
   - Serialize dict to JSON string
   - Set Content-Type header to `application/json`
   - Return HTTP 200 with JSON response body

**Error Handling Flow:**

1. **Validation Errors** → HTTP 400
   - Catch `InvalidContentTypeError` or `FileSizeExceededError`
   - Return structured JSON error with appropriate code and message

2. **XML Parse Errors** → HTTP 400
   - Catch `XMLValidationError` from lxml parser
   - Extract error location (line/column) if available
   - Return structured JSON error with `XML_PARSE_ERROR` code and location details

3. **Conversion Errors** → HTTP 500
   - Catch `ConversionError` or unexpected exceptions
   - Log full error details internally
   - Return generic error message (no sensitive details exposed)

**Service Call Sequence:**
```
Route Handler → Validator → XML Parser → JSON Converter → Route Handler → Response
     ↓              ↓            ↓              ↓              ↓
  Request      Validate    Parse XML    Convert to    Serialize &
  Received     Headers/Size            JSON          Return Response
```

## Non-Functional Requirements

### Performance

**Target Performance Metrics (from NFR001):**
- Response time: < 30 seconds for 300MB XML files
- Throughput: Efficient handling of concurrent requests (multiple Gunicorn workers)
- Memory usage: Stay within acceptable limits during large file processing (streaming approach)

**Performance Requirements:**
- Use lxml `iterparse()` for large files (>10MB) to enable streaming XML parsing
- Memory-efficient conversion algorithms that avoid loading entire XML tree into memory when possible
- Content-Length validation before processing to reject oversized requests early
- Baseline performance testing with file sizes: 1MB, 10MB, 100MB, 300MB
- Document performance baselines in test suite

**Performance Optimization Strategies:**
- Streaming XML parsing for files larger than threshold (configurable)
- Efficient dict construction during JSON conversion (minimize intermediate data structures)
- Gunicorn worker process configuration for parallel request handling
- Response compression consideration (deferred to infrastructure layer if needed)

**Source References:**
- PRD NFR001: "API must process all XML conversions within acceptable response times (target: < 30 seconds for 300MB files)"
- Architecture Performance Considerations section: Streaming parsing, memory efficiency, worker configuration

### Security

**Security Requirements:**
- Request size limits (300MB) to prevent resource exhaustion attacks
- Content-Type validation to prevent content-sniffing vulnerabilities
- Protection against XML-based attacks:
  - XML bomb attacks (billion laughs, quadratic blowup) via parser configuration
  - Excessive nesting depth validation
  - Entity expansion limits
- Input sanitization: Validate XML structure before processing
- Error message sanitization: No sensitive server details in error responses

**Security Considerations:**
- XML parser configuration to limit entity expansion and prevent DoS attacks
- No authentication/authorization (per PRD out-of-scope for initial release)
- HTTPS enforcement at infrastructure/deployment layer (not application-level)
- Structured logging without sensitive data exposure

**Threat Mitigation:**
- XML parser: Use lxml with `resolve_entities=False` or `huge_tree=False` for very large structures
- Input validation: Reject requests exceeding size limits before parsing
- Error handling: Generic error messages for 500 errors, detailed errors logged internally only

**Source References:**
- Architecture Security Architecture section: XML parsing protection, input validation, error sanitization
- PRD: Request size limits, error message clarity

### Reliability/Availability

**Availability Requirements:**
- Health check endpoint (`GET /health`) for monitoring and orchestration platforms
- Graceful error handling: All exceptions caught and returned as structured JSON responses
- No single point of failure in application logic (stateless design enables horizontal scaling)

**Recovery and Degradation Behavior:**
- Validation failures: Early rejection with clear error messages (HTTP 400/413)
- XML parse errors: Detailed error location reported (HTTP 400)
- Conversion failures: Generic error with full details logged internally (HTTP 500)
- No partial results: Either full conversion succeeds or error is returned

**Reliability Patterns:**
- Stateless service design: No persistent state means service restarts don't lose data
- Request isolation: Each request processed independently, failures don't affect other requests
- Logging for debugging: Structured logging captures all errors for post-mortem analysis

**Deployment Considerations:**
- Gunicorn with multiple workers for redundancy
- Container health checks via `/health` endpoint
- Graceful shutdown handling for in-flight requests

**Source References:**
- Architecture Deployment Architecture: Health checks, containerization, worker configuration

### Observability

**Logging Requirements:**
- Structured logging format (JSON) for production environments
- Log levels: DEBUG (development), INFO (production)
- Log fields: timestamp (ISO 8601 UTC), level, endpoint, message, context (file_size, error_code, etc.)

**Required Log Signals:**
- Request received: endpoint, file size, Content-Type
- Validation failures: error type, error details
- XML parse errors: error location (line/column), error message
- Conversion success: file size, processing time (optional)
- Conversion errors: error type, error message (internal details)
- Health check requests: status

**Metrics to Track (via logs):**
- Request count per endpoint
- File size distribution
- Error rate by error code
- Response time percentiles (if timing instrumentation added)

**Tracing Considerations:**
- Log correlation IDs for request tracing (deferred to infrastructure layer if needed)
- Structured log format enables parsing by log aggregation systems (ELK, Splunk, etc.)

**Example Log Entry:**
```json
{
  "timestamp": "2025-10-30T14:30:45Z",
  "level": "INFO",
  "endpoint": "/convert/xml-to-json",
  "message": "Conversion completed",
  "file_size": 1048576,
  "status": "success"
}
```

**Source References:**
- Architecture Consistency Patterns: Logging format, ISO 8601 timestamps, structured JSON format

## Dependencies and Integrations

**Runtime Dependencies:**
- Python 3.11 (runtime environment)
- Flask 3.0.x (web framework) - Latest stable version
- lxml (latest) - XML parsing and validation library
- Gunicorn (latest) - Production WSGI server

**Development Dependencies:**
- pytest (latest) - Testing framework
- pytest-cov (latest, optional) - Test coverage reporting
- black (latest, optional) - Code formatting
- flake8 (latest, optional) - Linting

**Standard Library Modules (no external dependencies):**
- `json` - JSON serialization
- `logging` - Structured logging
- `os`, `sys` - System/environment access

**Integration Points:**
- **XML Input**: POST request body via HTTP (application/xml or text/xml Content-Type)
- **JSON Output**: HTTP response body (application/json Content-Type)
- **Error Responses**: JSON format via HTTP status codes (400, 413, 500)
- **Environment Configuration**: Environment variables for configuration (MAX_FILE_SIZE, LOG_LEVEL, etc.)
- **Health Check**: GET /health endpoint for orchestration platforms (Kubernetes, ECS, etc.)

**Deployment Dependencies:**
- Docker (for containerization)
- Gunicorn configuration file (`gunicorn_config.py`)
- Environment variable configuration (`.env` file for local development)

**Future Integration Points (not in Epic 1):**
- CSV, String, YAML conversion services (Epic 2)
- OpenAPI/Swagger documentation generation

## Acceptance Criteria (Authoritative)

**AC1.1: Flask Application Structure**
- Flask application initialized with proper project structure (app/, tests/, requirements.txt, README.md)
- Basic Flask app factory pattern implemented in `app/__init__.py`
- Project follows structure defined in Architecture document

**AC1.2: Configuration Management**
- Configuration management system in place (environment-based config in `app/config.py`)
- Environment variables supported with sensible defaults
- Configuration includes MAX_FILE_SIZE (300MB), LOG_LEVEL settings

**AC1.3: Health Check Endpoint**
- Application can start and serve a basic health check endpoint at `GET /health`
- Returns 200 OK with `{"status": "healthy"}` response

**AC1.4: XML Parsing Library Integration**
- XML parsing library (lxml) integrated and functional
- XML validation function checks syntax and structure
- XML parsing handles namespaces correctly

**AC1.5: XML Error Detection**
- Error detection returns specific error location (line/column) for malformed XML
- Error messages include actionable information about XML parsing failures

**AC1.6: XML-to-JSON Conversion Engine**
- Conversion function transforms XML to JSON preserving all elements, attributes, and hierarchy
- XML namespaces correctly represented in JSON output
- Conversion handles complex nested structures
- Conversion preserves data types appropriately (text, numbers, booleans)

**AC1.7: POST Endpoint Implementation**
- POST endpoint `/convert/xml-to-json` accepts XML in request body
- Endpoint validates Content-Type header (application/xml, text/xml)
- Endpoint calls parsing and conversion functions
- Returns HTTP 200 with JSON response body on success
- Returns appropriate Content-Type header (application/json)
- Integration tests verify end-to-end conversion flow

**AC1.8: Error Response Format**
- Structured error response format for all error types (JSON structure with error code, message, details)
- HTTP 400 for client errors (malformed XML, invalid Content-Type, etc.)
- HTTP 413 for requests exceeding 300MB size limit
- HTTP 500 for server errors with generic message (detailed logging internally)
- Error messages include actionable information (XML error location, missing headers, etc.)

**AC1.9: Request Size Validation**
- Request size validation checks Content-Length header or body size before processing
- 300MB maximum file size limit enforced
- Requests exceeding limit rejected early (before parsing) with HTTP 413
- Clear error message indicating size limit exceeded
- Configuration allows adjustment of size limit if needed

**AC1.10: Large File Performance**
- API handles large XML files (up to 300MB) efficiently
- Response time target: < 30 seconds for 300MB files (documented performance baseline)
- Memory usage stays within acceptable limits during processing
- Performance tests with various file sizes (1MB, 10MB, 100MB, 300MB)

**AC1.11: Testing Infrastructure**
- Unit test suite covering all core functions (parsing, conversion, error handling)
- Integration tests covering full request/response cycles
- Performance/load tests for large file handling
- Test coverage target: > 80% for core conversion logic
- Test fixtures for various XML structures and edge cases
- CI/CD integration ready (test command, test reports)

**AC1.12: Documentation**
- README.md with setup instructions, usage examples, and API overview
- API endpoint documented with request/response examples
- Error response formats documented with examples
- OpenAPI/Swagger specification file (optional but recommended)
- Example XML inputs and expected JSON outputs in documentation

**AC1.13: Deployment Configuration**
- Docker configuration (Dockerfile, docker-compose.yml if needed)
- Production-ready WSGI server configuration (Gunicorn/uWSGI)
- Environment configuration for different deployment stages
- Logging configuration for production (structured logging, log levels)
- Health check endpoint for monitoring
- Basic deployment documentation

## Traceability Mapping

| AC ID | Acceptance Criteria | Spec Section(s) | Component(s) | API(s) | Test Idea |
|-------|-------------------|----------------|---------------|--------|-----------|
| AC1.1 | Flask Application Structure | Detailed Design: Services and Modules | `app/__init__.py` | N/A | Test app factory creates Flask instance, test project structure exists |
| AC1.2 | Configuration Management | Detailed Design: Services and Modules | `app/config.py` | N/A | Test config loads from environment, test defaults applied |
| AC1.3 | Health Check Endpoint | APIs and Interfaces | `app/routes/convert.py` | `GET /health` | Test health endpoint returns 200 with healthy status |
| AC1.4 | XML Parsing Library Integration | Detailed Design: Services and Modules, Workflows | `app/services/xml_parser.py` | N/A | Test valid XML parsing, test namespace handling |
| AC1.5 | XML Error Detection | APIs and Interfaces, Workflows | `app/services/xml_parser.py`, error handlers | `POST /convert/xml-to-json` | Test malformed XML returns 400 with line/column location |
| AC1.6 | XML-to-JSON Conversion Engine | Detailed Design: Services and Modules, Data Models | `app/services/json_converter.py` | `POST /convert/xml-to-json` | Test conversion preserves hierarchy, attributes, namespaces, test various XML structures |
| AC1.7 | POST Endpoint Implementation | APIs and Interfaces, Workflows | `app/routes/convert.py` | `POST /convert/xml-to-json` | Integration test: valid XML → 200 JSON response, test Content-Type validation |
| AC1.8 | Error Response Format | APIs and Interfaces, Workflows | `app/exceptions.py`, error handlers | `POST /convert/xml-to-json` | Test all error scenarios return structured JSON with appropriate status codes |
| AC1.9 | Request Size Validation | APIs and Interfaces, Workflows, NFR Security | `app/utils/validators.py` | `POST /convert/xml-to-json` | Test 300MB limit enforcement, test early rejection before parsing |
| AC1.10 | Large File Performance | NFR Performance | `app/services/xml_parser.py`, `app/services/json_converter.py` | `POST /convert/xml-to-json` | Performance tests: 1MB, 10MB, 100MB, 300MB files, measure response time and memory |
| AC1.11 | Testing Infrastructure | Test Strategy | `tests/unit/`, `tests/integration/`, `tests/performance/` | All endpoints | Test coverage > 80%, test all test levels exist and run |
| AC1.12 | Documentation | N/A | `README.md`, OpenAPI spec | N/A | Verify documentation exists, examples work |
| AC1.13 | Deployment Configuration | Deployment Architecture | `Dockerfile`, `gunicorn_config.py` | `GET /health` | Test Docker build succeeds, test Gunicorn starts, test health endpoint accessible |

## Risks, Assumptions, Open Questions

**Risks:**
1. **Risk: Memory exhaustion with very large XML files (300MB)**
   - Mitigation: Use lxml streaming parsing (`iterparse()`), enforce size limits before processing, performance testing with large files
   - Impact: High - core requirement
   - Status: Active

2. **Risk: XML namespace complexity in JSON conversion**
   - Mitigation: Document namespace handling strategy, test with various namespace scenarios, establish clear JSON structure for namespaces
   - Impact: Medium - affects conversion accuracy
   - Status: Active

3. **Risk: Performance targets not met for 300MB files**
   - Mitigation: Establish baseline early, optimize parsing and conversion algorithms, consider caching strategies if needed
   - Impact: High - NFR requirement
   - Status: Active

**Assumptions:**
1. **Assumption: UTF-8 encoding for all XML input**
   - Rationale: Standard for XML, simplifies parsing
   - Validation: Document encoding assumption, test with various encodings if needed

2. **Assumption: XML files are well-formed (syntactically valid) before parsing**
   - Rationale: Validation is a core function, but we assume input attempts to be valid XML
   - Validation: Error handling covers malformed XML

3. **Assumption: Gunicorn worker configuration sufficient for concurrent requests**
   - Rationale: Standard deployment pattern, will be validated during testing
   - Validation: Load testing with concurrent requests

**Open Questions:**
1. **Question: How to represent XML attributes in JSON? (prefixed keys vs. nested structure)**
   - Resolution needed: Establish convention before implementation
   - Decision required: From architecture or development team

2. **Question: Should streaming parsing be used for all file sizes or only above a threshold?**
   - Resolution needed: Performance testing will determine threshold
   - Decision required: During Story 1.7 (Performance Optimization)

3. **Question: What is the expected concurrent request load?**
   - Resolution needed: Inform Gunicorn worker configuration
   - Decision required: Clarify with stakeholders or use default configuration initially

## Test Strategy Summary

**Test Levels:**

1. **Unit Tests** (`tests/unit/`):
   - `test_xml_parser.py`: XML parsing, validation, namespace handling, error detection
   - `test_json_converter.py`: Conversion logic, hierarchy preservation, attribute handling, namespace representation
   - `test_validators.py`: Content-Type validation, size validation
   - Coverage target: > 80% for core conversion logic

2. **Integration Tests** (`tests/integration/`):
   - `test_endpoints.py`: Full request/response cycles, Content-Type validation, success scenarios
   - `test_error_handling.py`: Error response formats, status codes, error messages for all error scenarios

3. **Performance Tests** (`tests/performance/`):
   - `test_large_files.py`: Response time and memory usage for 1MB, 10MB, 100MB, 300MB files
   - Baseline metrics: Response time < 30 seconds for 300MB, memory usage within limits

**Test Coverage:**
- All acceptance criteria covered by tests
- All error paths tested (validation, parsing, conversion errors)
- Edge cases: Empty XML, deeply nested structures, large attribute lists, special characters
- Namespace scenarios: Multiple namespaces, default namespaces, namespace prefixes

**Test Frameworks and Tools:**
- pytest for test execution
- pytest-cov for coverage reporting
- Flask test client for integration testing
- Memory profiling tools for performance tests (optional)

**Test Data:**
- Valid XML samples of various sizes and structures
- Malformed XML samples (syntax errors, unclosed tags, etc.)
- XML with namespaces
- XML with complex nested structures
- Edge cases: Empty elements, attributes only, text only

**CI/CD Integration:**
- Test command: `pytest`
- Coverage command: `pytest --cov=app tests/`
- Test reports: pytest HTML reports, coverage reports
- Pre-commit hooks: Run tests before commit (optional)

