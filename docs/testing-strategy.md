# Testing Strategy and Usage

This document provides a comprehensive guide to the testing infrastructure, test organization, running tests, and contributing new tests.

## Table of Contents

- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Test Fixtures](#test-fixtures)
- [CI/CD Integration](#cicd-integration)
- [Writing New Tests](#writing-new-tests)
- [Best Practices](#best-practices)

## Test Structure

The test suite is organized into three main categories:

### Unit Tests (`tests/unit/`)

Unit tests verify individual functions and services in isolation:

- **test_xml_parser.py**: Tests for XML parsing service
- **test_json_converter.py**: Tests for JSON conversion service
- **test_validators.py**: Tests for validation utilities
- **test_config.py**: Tests for configuration management
- **test_app.py**: Tests for Flask application setup

**Coverage Target**: > 80% for core conversion logic (`app/services/xml_parser.py`, `app/services/json_converter.py`)

### Integration Tests (`tests/integration/`)

Integration tests verify full request/response cycles using Flask test client:

- **test_xml_to_json_endpoint.py**: End-to-end conversion endpoint tests
- **test_error_handling.py**: Error handling and size validation tests
- **test_health.py**: Health check endpoint tests

**Purpose**: Verify API endpoints work correctly with real request/response flows

### Performance Tests (`tests/performance/`)

Performance tests validate response times and memory usage for large files:

- **test_large_files.py**: Performance tests for 1MB, 10MB, 100MB, and 300MB files

**Markers**: 
- `@pytest.mark.performance`: All performance tests
- `@pytest.mark.slow`: Tests taking several seconds
- `@pytest.mark.very_slow`: Tests taking several minutes

**Purpose**: Ensure files up to 300MB process within acceptable time limits (< 30 seconds)

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Performance tests only
pytest tests/performance/

# Exclude slow tests (for fast CI/CD runs)
pytest -m "not slow and not very_slow"
```

### Run Specific Test Files

```bash
# Run a specific test file
pytest tests/unit/test_xml_parser.py

# Run a specific test function
pytest tests/unit/test_xml_parser.py::test_parse_simple_xml
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests with Coverage

```bash
# Generate coverage report in terminal
pytest --cov=app --cov-report=term

# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Open HTML report (after generating)
open htmlcov/index.html

# Check coverage for core conversion logic only
pytest --cov=app.services.xml_parser --cov=app.services.json_converter --cov-report=term-missing
```

### Run Performance Tests Selectively

```bash
# Run only fast performance tests (1MB, 10MB)
pytest tests/performance/ -m "not slow"

# Run all performance tests including slow ones
pytest tests/performance/

# Skip very slow tests (300MB)
pytest tests/performance/ -m "not very_slow"
```

## Test Coverage

### Current Coverage

- **Core Conversion Logic**: > 80% (Target achieved)
  - `app/services/xml_parser.py`: 82%
  - `app/services/json_converter.py`: 93%
  - `app/utils/validators.py`: 92%
- **Overall Application**: 89%

### Coverage Commands

```bash
# Coverage for all app code
pytest --cov=app --cov-report=html

# Coverage for specific modules
pytest --cov=app.services --cov-report=term

# Coverage with fail threshold (warns if below 80%)
pytest --cov=app.services.xml_parser --cov=app.services.json_converter --cov-fail-under=80 tests/unit/
```

### Viewing Coverage Reports

1. Generate HTML report: `pytest --cov=app --cov-report=html`
2. Open `htmlcov/index.html` in your browser
3. Navigate through modules to see line-by-line coverage

## Test Fixtures

Test fixtures are stored in `tests/data/` directory and can be loaded using the helper function from `tests.fixtures`.

### Available Fixtures

See [tests/data/README.md](../tests/data/README.md) for complete list of available fixtures including:
- Simple structures: `simple.xml`, `nested.xml`
- Namespaces: `namespaced-default.xml`, `namespaced-prefixed.xml`
- Attributes: `with-attributes.xml`
- Special characters: `special-characters.xml`
- Malformed XML: `malformed-unclosed-tag.xml`, `malformed-mismatched-tags.xml`
- Data types: `data-types.xml`
- Complex examples: `example-complex.xml`

### Using Fixtures

**Option 1: Helper Function (Recommended)**

```python
from tests.fixtures import load_xml_fixture

def test_simple_xml():
    xml_content = load_xml_fixture('simple.xml')
    root = parse_xml(xml_content)
    assert root is not None
```

**Option 2: Pytest Fixture**

```python
import pytest
from tests.fixtures import load_xml_fixture

@pytest.fixture
def simple_xml():
    return load_xml_fixture('simple.xml')

def test_simple_xml_parsing(simple_xml):
    root = parse_xml(simple_xml)
    assert root is not None
```

### Fixture Reusability

All fixtures in `tests/data/` are designed to be reusable across:
- Unit tests
- Integration tests  
- Performance tests

## CI/CD Integration

### GitHub Actions Workflow

Tests run automatically on push and pull requests via `.github/workflows/tests.yml`.

**Workflow Steps:**
1. Install dependencies from `requirements.txt` and `requirements-dev.txt`
2. Run unit tests with coverage reporting
3. Run integration tests
4. Run fast performance tests (excluding slow/very_slow)
5. Check coverage threshold (warns if < 80% for core logic)
6. Upload coverage reports to artifacts
7. Upload test results (JUnit XML format)

**Test Reports:**
- Coverage reports: Available as HTML artifacts
- Test results: JUnit XML format for CI/CD integration
- Coverage metrics: Uploaded to codecov (if configured)

### Running Tests in CI/CD

Tests run automatically on:
- Push to `main`, `develop`, or `master` branches
- Pull requests to `main`, `develop`, or `master` branches

**Python Versions Tested**: 3.9, 3.10, 3.11

### Skipping Slow Tests in CI/CD

Performance tests marked with `@pytest.mark.slow` or `@pytest.mark.very_slow` are excluded from fast CI/CD runs to speed up the pipeline. They can be run manually or in scheduled workflows.

## Writing New Tests

### Unit Test Template

```python
import pytest
from app.services.xml_parser import parse_xml

def test_feature_name():
    """Test description explaining what is being tested."""
    # Arrange
    xml_data = '<root>test</root>'
    
    # Act
    result = parse_xml(xml_data)
    
    # Assert
    assert result is not None
    assert result.tag == 'root'
```

### Integration Test Template

```python
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_endpoint_feature(client):
    """Test endpoint feature."""
    response = client.post(
        '/convert/xml-to-json',
        data='<root>test</root>',
        content_type='application/xml'
    )
    assert response.status_code == 200
    assert response.get_json() is not None
```

### Performance Test Template

```python
import pytest
import time

@pytest.mark.performance
def test_performance_feature(client):
    """Test performance requirement."""
    xml_data = generate_large_xml(10)  # 10MB
    
    start_time = time.time()
    response = client.post(
        '/convert/xml-to-json',
        data=xml_data,
        content_type='application/xml'
    )
    processing_time = time.time() - start_time
    
    assert response.status_code == 200
    assert processing_time < 10.0  # Performance threshold
```

### Test Naming Conventions

- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`
- Use descriptive names: `test_parse_xml_with_namespaces` not `test_1`

### Test Organization

- **One assertion per test** (when possible)
- **Arrange-Act-Assert** pattern
- **Clear test descriptions** in docstrings
- **Use fixtures** for reusable test data

## Best Practices

### 1. Test Isolation

- Each test should be independent
- Tests should not depend on execution order
- Use fixtures for setup/teardown

### 2. Coverage Targets

- Maintain > 80% coverage for core conversion logic
- Cover edge cases: empty inputs, malformed data, boundaries
- Test both success and error paths

### 3. Performance Considerations

- Mark slow tests with `@pytest.mark.slow`
- Mark very slow tests with `@pytest.mark.very_slow`
- Fast CI/CD runs exclude slow tests

### 4. Test Data

- Use fixtures from `tests/data/` for consistency
- Create new fixtures for new test scenarios
- Document fixture purposes in `tests/data/README.md`

### 5. Error Testing

- Test error conditions explicitly
- Verify error messages and status codes
- Test boundary conditions (e.g., size limits)

### 6. Integration Tests

- Use Flask test client for endpoint testing
- Verify response formats, status codes, headers
- Test full request/response cycles

### 7. Continuous Improvement

- Review coverage reports regularly
- Add tests for bug fixes
- Update tests when requirements change
- Keep test documentation up to date

## Troubleshooting

### Tests Failing Locally

1. **Clear Python cache**: `find . -type d -name __pycache__ -exec rm -r {} +`
2. **Reinstall dependencies**: `pip install -r requirements-dev.txt`
3. **Check Python version**: Requires Python 3.9+

### Coverage Not Updating

1. **Clear coverage cache**: Remove `.coverage` file
2. **Regenerate reports**: `pytest --cov=app --cov-report=html`

### Slow Test Performance

1. **Run specific test categories**: `pytest tests/unit/` instead of all tests
2. **Exclude slow tests**: `pytest -m "not slow"`
3. **Run in parallel** (if pytest-xdist installed): `pytest -n auto`

### Fixture Not Found

1. **Check fixture path**: Ensure fixture exists in `tests/data/`
2. **Use helper function**: `from tests.fixtures import load_xml_fixture`
3. **Check file encoding**: Fixtures must be UTF-8 encoded

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Flask Testing Documentation](https://flask.palletsprojects.com/en/latest/testing/)
- [Test Fixtures Guide](../tests/data/README.md)

