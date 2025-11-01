# Decision Architecture

## Executive Summary

Flask-based REST API microservice providing XML-to-JSON, CSV, String, and YAML conversion endpoints. Stateless architecture with streaming support for large files (up to 300MB), using lxml for efficient XML parsing and Gunicorn for production deployment.

## Decision Summary

| Category          | Decision                           | Version | Affects Epics  | Rationale                                                   |
| ----------------- | ---------------------------------- | ------- | -------------- | ----------------------------------------------------------- |
| Runtime           | Python                             | 3.11    | All epics      | Stable, good performance, widely supported                  |
| Web Framework     | Flask                              | 3.0.x   | All epics      | Minimal, flexible, ideal for API microservices              |
| XML Parsing       | lxml                               | Latest  | Epic 1, Epic 2 | Better performance for large files, namespace support       |
| WSGI Server       | Gunicorn                           | Latest  | Epic 1         | Simple configuration, good performance, widely used         |
| Testing Framework | pytest                             | Latest  | Epic 1         | Industry standard, excellent fixtures, better than unittest |
| CSV Library       | csv (stdlib)                       | N/A     | Epic 2         | Standard library, no external dependency needed             |
| YAML Library      | PyYAML                             | Latest  | Epic 2         | Standard Python YAML library, well-maintained               |
| String Extraction | xml.etree.ElementTree              | N/A     | Epic 2         | Standard library, sufficient for text extraction            |
| Error Handling    | Custom exceptions + Flask handlers | N/A     | All epics      | Consistent JSON error responses across endpoints            |
| Logging           | Python logging (structured)        | N/A     | All epics      | Standard library, structured format for production          |
| Configuration     | Environment variables              | N/A     | All epics      | 12-factor app approach, container-friendly                  |
| API Documentation | OpenAPI/Swagger                    | Latest  | Epic 1         | Industry standard, auto-generated docs                      |
| Deployment        | Docker containerization            | Latest  | Epic 1         | Platform-agnostic, consistent environments                  |

## Project Structure

```
its-convert-xml/
├── app/
│   ├── __init__.py                 # Flask app factory
│   ├── config.py                   # Configuration management
│   ├── exceptions.py               # Custom exception classes
│   ├── routes/
│   │   ├── __init__.py
│   │   └── convert.py              # Conversion endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── xml_parser.py           # XML parsing and validation
│   │   ├── json_converter.py       # XML to JSON conversion
│   │   ├── csv_converter.py        # XML to CSV conversion
│   │   ├── string_converter.py     # XML to String conversion
│   │   └── yaml_converter.py       # XML to YAML conversion
│   └── utils/
│       ├── __init__.py
│       └── validators.py           # Request validation utilities
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_xml_parser.py
│   │   ├── test_json_converter.py
│   │   ├── test_csv_converter.py
│   │   ├── test_string_converter.py
│   │   └── test_yaml_converter.py
│   ├── integration/
│   │   ├── test_endpoints.py
│   │   └── test_error_handling.py
│   └── performance/
│       └── test_large_files.py
├── docs/
│   ├── PRD.md
│   ├── epics.md
│   └── architecture.md
├── .env.example                    # Environment variables template
├── .gitignore
├── Dockerfile
├── docker-compose.yml               # Optional local development
├── requirements.txt
├── requirements-dev.txt            # Development dependencies
├── pytest.ini                      # Pytest configuration
├── gunicorn_config.py              # Gunicorn settings
├── README.md
└── setup.py                        # Optional package setup
```

## Epic to Architecture Mapping

| Epic                                     | Components                                                                             | Location                                                                                                                                         |
| ---------------------------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Epic 1: Project Foundation & XML-to-JSON | Flask app factory, config, routes, XML parser, JSON converter, error handling, testing | `app/__init__.py`, `app/config.py`, `app/routes/convert.py`, `app/services/xml_parser.py`, `app/services/json_converter.py`, `app/exceptions.py` |
| Epic 2: Extended Conversion Formats      | CSV, String, YAML converters                                                           | `app/services/csv_converter.py`, `app/services/string_converter.py`, `app/services/yaml_converter.py`                                            |

## Technology Stack Details

### Core Technologies

- **Python 3.11**: Runtime environment
- **Flask 3.0.x**: Web framework
- **lxml**: XML parsing and validation library
- **Gunicorn**: Production WSGI server
- **pytest**: Testing framework
- **PyYAML**: YAML conversion library
- **csv** (stdlib): CSV conversion
- **xml.etree.ElementTree** (stdlib): Text extraction from XML

### Integration Points

- **XML Input**: POST request body (application/xml or text/xml)
- **Output Formats**: JSON (application/json), CSV (text/csv), String (text/plain), YAML (application/x-yaml)
- **Error Responses**: JSON format across all endpoints
- **Request Validation**: Content-Type header validation, Content-Length checking
- **Streaming**: Large file handling via streaming XML parsing (if supported by lxml iterparse)

## Implementation Patterns

These patterns ensure consistent implementation across all AI agents:

### Naming Patterns

**Python Modules and Files:**

- Use snake_case for all file names: `xml_parser.py`, `json_converter.py`
- Use descriptive names that indicate functionality
- Test files prefixed with `test_`: `test_xml_parser.py`

**Python Classes:**

- Use PascalCase: `XMLParser`, `JSONConverter`, `ConversionError`
- Exception classes end with `Error`: `XMLValidationError`, `FileSizeExceededError`

**Python Functions and Variables:**

- Use snake_case: `parse_xml()`, `convert_to_json()`, `validate_request()`

**API Routes:**

- Use kebab-case in URLs: `/convert/xml-to-json`, `/convert/xml-to-csv`
- Route function names use snake_case: `convert_xml_to_json()`

### Structure Patterns

**Module Organization:**

- Route handlers in `app/routes/`
- Business logic in `app/services/`
- Utilities in `app/utils/`
- Custom exceptions in `app/exceptions.py`

**Test Organization:**

- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- Performance tests in `tests/performance/`
- Mirror service structure: `tests/unit/test_json_converter.py` matches `app/services/json_converter.py`

**Import Organization:**

1. Standard library imports
2. Third-party imports
3. Local application imports

- Separate groups with blank line

### Format Patterns

**API Request Format:**

- POST requests with XML in body
- Content-Type: `application/xml` or `text/xml`
- Content-Length header checked before processing

**API Success Response Format:**

- HTTP 200 with converted data in body
- Content-Type matches output format:
  - JSON: `application/json`
  - CSV: `text/csv`
  - String: `text/plain`
  - YAML: `application/x-yaml`

**API Error Response Format:**

- Consistent JSON structure across all endpoints:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Additional context (optional)"
  }
}
```

- HTTP status codes: 400 (client error), 413 (payload too large), 500 (server error)

### Communication Patterns

**Service Layer Communication:**

- Services are called from route handlers
- Services return data structures (dicts, strings), not Flask response objects
- Route handlers convert service output to Flask responses

**Error Propagation:**

- Services raise custom exceptions
- Route handlers catch exceptions and convert to JSON error responses
- Use Flask `@app.errorhandler` decorator for global error handling

### Lifecycle Patterns

**Request Flow:**

1. Route handler receives request
2. Validate Content-Type header
3. Check Content-Length (if present)
4. Read request body (with size limit)
5. Call XML parser service
6. Call conversion service
7. Return response with appropriate Content-Type

**Error Handling Flow:**

1. Validation error → HTTP 400 with error details
2. XML parsing error → HTTP 400 with parsing error location
3. File size exceeded → HTTP 413 with size limit message
4. Conversion error → HTTP 500 with generic error (detailed error logged)

### Location Patterns

**Route Definitions:**

- All conversion routes in `app/routes/convert.py`
- Route registration in `app/__init__.py` via Blueprint

**Configuration:**

- Environment variables loaded in `app/config.py`
- Default values provided for development
- Production config via environment variables

**Static Files:**

- No static files (API-only service)
- Documentation in `docs/` directory

### Consistency Patterns

**Date/Time Format:**

- ISO 8601 format in logs: `2025-10-30T14:30:45Z`
- UTC timezone for all server-side operations

**Logging Format:**

- Structured logging with JSON format:

```json
{
  "timestamp": "2025-10-30T14:30:45Z",
  "level": "INFO",
  "endpoint": "/convert/xml-to-json",
  "message": "Conversion completed",
  "file_size": 1048576
}
```

**User-Facing Errors:**

- Clear, actionable messages
- Include specific error location for XML parsing errors (line/column)
- No sensitive information exposed

## Consistency Rules

### Naming Conventions

- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/Variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- API Routes: `/convert/xml-to-json` (kebab-case)

### Code Organization

- Route handlers: `app/routes/`
- Business logic: `app/services/`
- Utilities: `app/utils/`
- Tests mirror source structure in `tests/`

### Error Handling

- Custom exception classes in `app/exceptions.py`
- Flask error handlers return consistent JSON format
- All exceptions logged with full details
- User-facing errors are sanitized

### Logging Strategy

- Python logging module with structured JSON format
- Log levels: DEBUG (development), INFO (production)
- Include: timestamp, level, endpoint, message, context
- Output to stdout for containerized deployments

## Data Architecture

**No persistent data storage required** - This is a stateless microservice:

- Input: XML received via POST request body
- Processing: In-memory conversion
- Output: Converted format returned in response
- No database, no caching, no file storage

**In-Memory Data Flow:**

1. XML string → lxml parse → XML tree object
2. XML tree → Conversion service → Target format (JSON/CSV/String/YAML)
3. Target format → Flask response → Client

**Large File Handling:**

- Streaming XML parsing using lxml `iterparse()` for memory efficiency
- Content-Length validation before processing
- Memory-efficient conversion for large structures

## API Contracts

### POST /convert/xml-to-json

**Request:**

- Method: POST
- Headers: `Content-Type: application/xml` or `text/xml`
- Body: XML content (up to 300MB)

**Success Response:**

- Status: 200 OK
- Headers: `Content-Type: application/json`
- Body: JSON representation of XML

**Error Responses:**

- 400 Bad Request: Invalid XML or Content-Type
- 413 Payload Too Large: Request exceeds 300MB
- 500 Internal Server Error: Server-side conversion error

### POST /convert/xml-to-csv

**Request:** Same as xml-to-json
**Success Response:**

- Status: 200 OK
- Headers: `Content-Type: text/csv`
- Body: CSV representation of XML

**Error Responses:** Same as xml-to-json

### POST /convert/xml-to-string

**Request:** Same as xml-to-json
**Success Response:**

- Status: 200 OK
- Headers: `Content-Type: text/plain`
- Body: Plain text extracted from XML

**Error Responses:** Same as xml-to-json

### POST /convert/xml-to-yaml

**Request:** Same as xml-to-json
**Success Response:**

- Status: 200 OK
- Headers: `Content-Type: application/x-yaml`
- Body: YAML representation of XML

**Error Responses:** Same as xml-to-json

### Error Response Format (All Endpoints)

```json
{
  "error": {
    "code": "XML_PARSE_ERROR",
    "message": "Invalid XML syntax at line 10, column 5",
    "details": "unclosed tag: <item>"
  }
}
```

**Common Error Codes:**

- `INVALID_CONTENT_TYPE`: Missing or incorrect Content-Type header
- `XML_PARSE_ERROR`: XML syntax error with location
- `FILE_SIZE_EXCEEDED`: Request exceeds 300MB limit
- `CONVERSION_ERROR`: Server-side conversion failure
- `SERVER_ERROR`: Unexpected server error

## Security Architecture

**Current Release:**

- No authentication/authorization (per PRD out-of-scope)
- Request size limits (300MB) to prevent resource exhaustion
- Content-Type validation

**Security Considerations:**

- XML parsing: Protect against XML bomb attacks (billion laughs, quadratic blowup)
- Input validation: Reject excessively nested XML structures
- Rate limiting: Deferred to future release (per PRD)
- HTTPS: Enforced at infrastructure/deployment layer

## Performance Considerations

**Target Performance:**

- Response time: < 30 seconds for 300MB files (NFR001)
- Memory efficiency: Streaming parsing for large files
- Concurrent requests: Efficient handling via Gunicorn workers

**Optimization Strategies:**

- Use lxml `iterparse()` for large files instead of loading entire tree
- Streaming XML parsing to minimize memory footprint
- Gunicorn worker processes for parallel request handling
- Configurable worker count based on deployment environment

**Performance Testing:**

- Test with file sizes: 1MB, 10MB, 100MB, 300MB
- Monitor memory usage during processing
- Measure response times for each file size
- Baseline performance metrics documented in tests

## Deployment Architecture

**Containerization:**

- Docker container with Python 3.11 base image
- Gunicorn as WSGI server
- Multi-stage build for optimized image size

**Production Server:**

- Gunicorn with multiple workers (configurable via environment)
- Recommended: 2-4 workers per CPU core
- Timeout settings appropriate for large file processing

**Deployment Targets:**

- Platform-agnostic (Docker-based)
- Compatible with: AWS ECS, Google Cloud Run, Azure Container Instances, Railway, Fly.io, Heroku

**Environment Configuration:**

- Environment variables for all configuration
- `.env` file for local development
- Container environment variables for production

**Health Checks:**

- Health check endpoint: `GET /health`
- Returns 200 OK when service is ready
- Used by orchestration platforms for container health

## Development Environment

### Prerequisites

- Python 3.11
- pip (Python package manager)
- Virtual environment tool (venv or virtualenv)
- Git

### Setup Commands

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run development server
flask run

# Run with Gunicorn (production-like)
gunicorn -c gunicorn_config.py app:app
```

### Local Development

```bash
# Set environment variables (copy from .env.example)
cp .env.example .env

# Run in development mode
export FLASK_ENV=development
flask run
```

### Docker Development

```bash
# Build image
docker build -t its-convert-xml .

# Run container
docker run -p 5000:5000 its-convert-xml

# Or use docker-compose
docker-compose up
```

## Architecture Decision Records (ADRs)

### ADR-001: Python 3.11 Selection

**Decision:** Use Python 3.11 as runtime environment

**Rationale:** Stable release with good performance improvements over 3.10, widely supported by hosting platforms, good balance of features and stability.

**Alternatives Considered:**

- Python 3.12: Newer but less battle-tested at project start
- Python 3.10: Stable but missing performance improvements

### ADR-002: Flask Over FastAPI

**Decision:** Use Flask instead of FastAPI

**Rationale:** Minimal framework perfect for simple API microservice, lighter weight, sufficient for conversion endpoints without async requirements. FastAPI adds complexity not needed for this use case.

**Alternatives Considered:**

- FastAPI: Better for async, but not needed for this synchronous conversion service
- Django: Overkill for simple API microservice

### ADR-003: lxml Over xml.etree

**Decision:** Use lxml for XML parsing instead of standard library xml.etree

**Rationale:** Better performance for large files (300MB requirement), better namespace handling, XPath support if needed, more robust error reporting with line/column numbers.

**Alternatives Considered:**

- xml.etree.ElementTree: Standard library but slower for large files
- xml.dom: Slower and more memory-intensive

### ADR-004: Gunicorn Over uWSGI

**Decision:** Use Gunicorn as production WSGI server

**Rationale:** Simpler configuration, excellent documentation, sufficient performance for this use case, easier to debug, widely used in Python community.

**Alternatives Considered:**

- uWSGI: More complex configuration, overkill for this service
- Waitress: Windows-friendly but less common on Linux deployments

### ADR-005: Stateless Architecture

**Decision:** Stateless service with no persistent storage

**Rationale:** Simplifies deployment, scales horizontally easily, no database maintenance, matches use case (transformation service, not data storage).

**Alternatives Considered:**

- Database for caching: Adds complexity without clear benefit for transformation service
- File storage: Out of scope per PRD

### ADR-006: Structured JSON Error Responses

**Decision:** Consistent JSON error format across all endpoints

**Rationale:** Developer-friendly API, predictable error handling for clients, easier to document, supports OpenAPI specification.

**Alternatives Considered:**

- Plain text errors: Less structured, harder for clients to parse
- Varying error formats: Inconsistent developer experience

---

_Generated by BMAD Decision Architecture Workflow v1.3.2_
_Date: 2025-10-30_
_For: GK Ram_
