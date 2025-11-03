# its-convert-xml

A production-ready Flask microservice for converting XML data to multiple formats (JSON, CSV, String, and YAML).

## Project Overview

This microservice provides reliable API endpoints for converting XML data into JSON, CSV, plain text String, and YAML formats. It's designed to handle large XML files efficiently (up to 300MB) with high accuracy and clear error reporting.

## Features

- **XML to JSON Conversion**: Fast and accurate conversion of XML data to JSON format
- **Production Ready**: Built with Flask 3.0.x following best practices
- **Scalable**: Handles large files efficiently (up to 300MB)
- **Well Tested**: Comprehensive test coverage with pytest
- **12-Factor App**: Environment-based configuration
- **Clear Error Messages**: Structured error responses with detailed error codes
- **Performance Optimized**: Processes large files in under 30 seconds

## Technology Stack

- **Python 3.11**: Runtime environment
- **Flask 3.0.x**: Web framework
- **pytest**: Testing framework
- **Gunicorn**: Production WSGI server (for deployment)

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
│   │   └── __init__.py
│   └── utils/
│       ├── __init__.py
│       └── validators.py           # Request validation utilities
├── tests/
│   ├── unit/                       # Unit tests
│   ├── integration/                # Integration tests
│   └── performance/                # Performance tests
├── docs/                           # Project documentation
├── requirements.txt                # Production dependencies
├── requirements-dev.txt            # Development dependencies
├── pytest.ini                      # Pytest configuration
└── README.md                       # This file
```

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- pip (Python package installer)

### Virtual Environment Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
```

2. Activate the virtual environment:
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```

3. Verify activation (you should see `(venv)` in your terminal prompt)

### Installation

1. Install production dependencies:
```bash
pip install -r requirements.txt
```

2. Install development dependencies (optional, for testing and code quality):
```bash
pip install -r requirements-dev.txt
```

3. Create a `.env` file from the template:
```bash
cp .env.example .env
```

4. Edit `.env` file to configure your environment variables (optional, defaults are provided)

## Running the Application

### Development Mode

**Option 1: Auto-reload with Watchdog (Recommended for Development)**
```bash
# Make sure watchdog is installed
pip install -r requirements-dev.txt

# Run with automatic restart on file changes
python run_dev.py
```

**Option 2: Standard Flask Development Server**
```bash
export FLASK_APP=app
export FLASK_ENV=development
flask run
```

Or using Python directly:
```bash
python -m flask --app app run
```

The application will be available at `http://localhost:5000`

**Note:** The `run_dev.py` script uses watchdog to automatically restart the server when you modify Python files, configuration files, or requirements files. This is especially useful during active development.

### Quick Start Example

Once the application is running, convert XML to JSON:

```bash
# Simple XML conversion example
curl -X POST http://localhost:5000/convert/xml-to-json \
  -H "Content-Type: application/xml" \
  -d '<user><name>Alice</name><email>alice@example.com</email></user>'
```

**Expected Response:**
```json
{
  "user": {
    "name": "Alice",
    "email": "alice@example.com"
  }
}
```

### Testing the Health Endpoint

Check if the service is running:

```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy"
}
```

### Using Example Files

Example XML files and their expected JSON outputs are available in `docs/examples/`. See [Example Files](docs/examples/) for more examples and usage instructions.

## Development Setup

### Running Tests

Run all tests:
```bash
pytest
```

Run with coverage report:
```bash
pytest --cov=app --cov-report=html
```

Run specific test categories:
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Performance tests only
pytest tests/performance/
```

### Code Quality

Format code with black:
```bash
black app/ tests/
```

Check code style with flake8:
```bash
flake8 app/ tests/
```

## Configuration

The application uses environment variables for configuration. Key settings:

- `MAX_FILE_SIZE`: Maximum file size for uploads in bytes (default: 314572800 = 300MB)
- `LOG_LEVEL`: Logging level - INFO for production, DEBUG for development (default: INFO)
- `SECRET_KEY`: Flask secret key (default: dev-secret-key-change-in-production)

See `.env.example` for all available configuration options.

## API Overview

The service provides a RESTful API for converting XML data to JSON format:

- **Endpoint**: `POST /convert/xml-to-json`
- **Input**: XML data (up to 300MB) in request body
- **Output**: JSON representation of XML
- **Content-Type**: Accepts `application/xml` or `text/xml`
- **Performance**: Processes large files (300MB) in under 30 seconds
- **Error Handling**: Structured JSON error responses with error codes

### Supported Features

- **XML Attributes**: Converted to `@attributes` object in JSON containing all attribute key-value pairs
- **XML Namespaces**: Preserved in JSON output with namespace prefixes
- **Nested Structures**: Deeply nested XML elements properly converted
- **Data Type Preservation**: Strings, numbers, and booleans preserved in JSON

For detailed API documentation, see:
- [API Reference](docs/api-reference.md) - Complete endpoint documentation
- [Error Reference](docs/error-reference.md) - Error codes and troubleshooting
- [OpenAPI Specification](docs/openapi.yaml) - Machine-readable API spec
- [Example Files](docs/examples/) - Sample XML inputs and JSON outputs

## API Endpoints

### GET /health

Health check endpoint for monitoring and orchestration.

**Response:**
- Status Code: `200 OK`
- Content-Type: `application/json`
- Body: `{"status": "healthy"}`

**Example:**
```bash
curl http://localhost:5000/health
```

### POST /convert/xml-to-json

Convert XML data to JSON format.

**Request:**
- Method: `POST`
- URL: `/convert/xml-to-json`
- Headers:
  - `Content-Type: application/xml` or `Content-Type: text/xml` (required)
- Body: XML content (up to 300MB)

**Success Response:**
- Status Code: `200 OK`
- Content-Type: `application/json`
- Body: JSON representation of the XML

**Error Responses:**
- `400 Bad Request`: Invalid Content-Type header or malformed XML
- `413 Payload Too Large`: Request size exceeds 300MB limit
- `500 Internal Server Error`: Server-side conversion error

**Example Request:**
```bash
curl -X POST http://localhost:5000/convert/xml-to-json \
  -H "Content-Type: application/xml" \
  -d '<root><name>John</name><age>30</age></root>'
```

**Example Response (200 OK):**
```json
{
  "root": {
    "name": "John",
    "age": 30
  }
}
```

**Example Error Response (400 Bad Request):**
```json
{
  "error": {
    "code": "INVALID_CONTENT_TYPE",
    "message": "Content-Type must be application/xml or text/xml",
    "details": "Received Content-Type: application/json"
  }
}
```

For complete API documentation including all error codes, request/response formats, and detailed examples, see [API Reference](docs/api-reference.md).

For error handling details and troubleshooting, see [Error Reference](docs/error-reference.md).

## Contributing

1. Follow the project structure and naming conventions
2. Write tests for all new features
3. Ensure all tests pass before submitting changes
4. Follow PEP 8 style guidelines (enforced by flake8)

## License

[Add license information here]

## Support

[Add support information here]

