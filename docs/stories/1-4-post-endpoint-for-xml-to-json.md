# Story 1.4: POST Endpoint for XML-to-JSON

Status: done

## Story

As an API consumer,
I want to send XML data via POST request and receive JSON response,
So that I can integrate the conversion service into my applications.

## Acceptance Criteria

1. POST endpoint `/convert/xml-to-json` accepts XML in request body - [Source: docs/epics.md#Story-1.4]
2. Endpoint validates Content-Type header (application/xml, text/xml) - [Source: docs/epics.md#Story-1.4]
3. Endpoint calls parsing and conversion functions from previous stories - [Source: docs/epics.md#Story-1.4]
4. Returns HTTP 200 with JSON response body on success - [Source: docs/epics.md#Story-1.4]
5. Returns appropriate Content-Type header (application/json) - [Source: docs/epics.md#Story-1.4]
6. Integration tests verify end-to-end conversion flow - [Source: docs/epics.md#Story-1.4]

## Tasks / Subtasks

- [x] Task 1: Implement POST endpoint handler (AC: 1, 3, 4, 5)

  - [x] Create route handler function `convert_xml_to_json()` in `app/routes/convert.py` - [Source: docs/architecture.md#Project-Structure]
  - [x] Define route decorator `@convert_bp.route('/convert/xml-to-json', methods=['POST'])` - [Source: docs/architecture.md#Epic-to-Architecture-Mapping]
  - [x] Import `convert_xml_string_to_json` from `app.services.json_converter` - [Source: docs/stories/1-3-xml-to-json-conversion-engine.md#File-List]
  - [x] Extract XML string from Flask request body (request.data or request.get_data())
  - [x] Call `convert_xml_string_to_json()` service function - [Source: docs/stories/1-3-xml-to-json-conversion-engine.md#Dev-Agent-Record]
  - [x] Return Flask JSON response using `jsonify()` with HTTP 200 status
  - [x] Set Content-Type header to `application/json` in response

- [x] Task 2: Implement Content-Type validation (AC: 2)

  - [x] Import `request` from Flask
  - [x] Check request Content-Type header in route handler
  - [x] Accept `application/xml` or `text/xml` Content-Type values
  - [x] Return HTTP 400 error response if Content-Type invalid or missing
  - [x] Provide clear error message indicating required Content-Type values
  - [x] Follow architecture error response format (structured JSON error) - [Source: docs/architecture.md#Error-Response-Format]

- [x] Task 3: Implement error handling integration (AC: 4)

  - [x] Import `XMLValidationError` from `app.exceptions` - [Source: docs/stories/1-2-xml-parsing-and-validation-core.md#File-List]
  - [x] Wrap service call in try/except block to catch `XMLValidationError`
  - [x] Handle `XMLValidationError` exceptions from conversion service
  - [x] Convert `XMLValidationError` to HTTP 400 response with error details
  - [x] Handle unexpected exceptions and return HTTP 500 with generic error message
  - [x] Follow architecture error response format for all errors - [Source: docs/architecture.md#Error-Response-Format]

- [x] Task 4: Write integration tests (AC: 6)

  - [x] Create `tests/integration/test_xml_to_json_endpoint.py` test file - [Source: docs/architecture.md#Project-Structure]
  - [x] Test successful conversion: POST XML → receive JSON response
  - [x] Test Content-Type validation: invalid/missing Content-Type returns 400
  - [x] Test malformed XML: invalid XML returns 400 with error details
  - [x] Test response headers: Content-Type is application/json
  - [x] Test response status: successful request returns 200
  - [x] Test end-to-end flow: XML string → JSON dict → Flask response
  - [x] Use Flask test client for integration testing
  - [x] Follow test patterns from existing integration tests - [Source: docs/stories/1-1-project-setup-and-flask-application-foundation.md#File-List]

## Dev Notes

### Requirements Context Summary

This story implements the Flask POST endpoint that exposes the XML-to-JSON conversion engine built in Story 1.3. The endpoint accepts XML data in the request body, validates the Content-Type header, calls the existing conversion service, and returns JSON responses. This is the first API endpoint that connects the conversion engine to HTTP clients.

**Key Requirements:**
- POST endpoint at `/convert/xml-to-json` - [Source: docs/epics.md#Story-1.4]
- Content-Type header validation (application/xml, text/xml) - [Source: docs/epics.md#Story-1.4]
- Reuse conversion service from Story 1.3 - [Source: docs/stories/1-3-xml-to-json-conversion-engine.md#Dev-Agent-Record]
- Return HTTP 200 with JSON response on success - [Source: docs/epics.md#Story-1.4]
- Integration tests verify end-to-end flow - [Source: docs/epics.md#Story-1.4]

### Structure Alignment Summary

**Project Structure Alignment:**
- Follow exact directory structure from Architecture document - [Source: docs/architecture.md#Project-Structure]
- Route handler in `app/routes/convert.py` - [Source: docs/architecture.md#Project-Structure, docs/architecture.md#Epic-to-Architecture-Mapping]
- Integration tests in `tests/integration/` - [Source: docs/architecture.md#Project-Structure]
- Reuse existing services: `app/services/json_converter.py` - [Source: docs/stories/1-3-xml-to-json-conversion-engine.md#File-List]
- Reuse existing exceptions: `app/exceptions.py` - [Source: docs/stories/1-2-xml-parsing-and-validation-core.md#File-List]

**Component Boundaries:**
- Route handler: `app/routes/convert.py` - HTTP endpoint logic, Content-Type validation
- Service layer: `app/services/json_converter.py` - Business logic (already exists, REUSE)
- Exception handling: `app/exceptions.py` - Error classes (already exists, REUSE)
- Test structure mirrors source structure - [Source: docs/architecture.md#Structure-Patterns]

**Naming Conventions:**
- Files: snake_case (convert.py) - [Source: docs/architecture.md#Naming-Patterns]
- Functions/Variables: snake_case (convert_xml_to_json) - [Source: docs/architecture.md#Naming-Patterns]
- Routes: kebab-case in URLs (/convert/xml-to-json) - [Source: docs/architecture.md#Naming-Patterns]

### Learnings from Previous Story

**From Story 1.3 (Status: done)**

- **JSON Converter Service**: `app/services/json_converter.py` exists with `convert_xml_string_to_json(xml_string: str) -> Dict[str, Any]` function - REUSE this service, do not recreate conversion logic - [Source: docs/stories/1-3-xml-to-json-conversion-engine.md#File-List]
- **Exception Class**: `app/exceptions.py` contains `XMLValidationError` class with message, line, and column attributes - REUSE this exception for error handling - [Source: docs/stories/1-2-xml-parsing-and-validation-core.md#File-List]
- **Service Return Format**: Conversion service returns `Dict[str, Any]` (not Flask response) - route handler converts to Flask response - [Source: docs/stories/1-3-xml-to-json-conversion-engine.md#Completion-Notes-List]
- **Service Integration Pattern**: Services are called from route handlers, services return data structures (dicts), not Flask response objects - [Source: docs/architecture.md#Communication-Patterns]
- **Test Patterns**: Follow pytest framework with tests in `tests/integration/` - use Flask test client for endpoint testing - [Source: docs/architecture.md#Structure-Patterns]
- **Error Handling Pattern**: Services raise custom exceptions, route handlers catch and convert to JSON error responses - [Source: docs/architecture.md#Communication-Patterns]

**From Story 1.1 (Status: done)**

- **Flask App Structure**: Flask app factory pattern in `app/__init__.py` with blueprint registration - blueprint `convert_bp` already registered - [Source: docs/stories/1-1-project-setup-and-flask-application-foundation.md#File-List]
- **Route Blueprint**: `app/routes/convert.py` exists with `convert_bp` Blueprint - add new route to this file - [Source: docs/stories/1-1-project-setup-and-flask-application-foundation.md#File-List]
- **Health Check Pattern**: Route handler pattern exists (health_check function) - follow same pattern for new endpoint - [Source: docs/stories/1-1-project-setup-and-flask-application-foundation.md#File-List]

**Files to Reference:**
- `app/routes/convert.py` - Route handler file to add endpoint (EXISTS)
- `app/services/json_converter.py` - JSON conversion service to integrate (EXISTS)
- `app/exceptions.py` - XMLValidationError exception class (EXISTS)
- `tests/integration/test_health.py` - Integration test patterns to follow (EXISTS)

### Project Structure Notes

- **Directory Structure**: Match exactly as defined in Architecture document - [Source: docs/architecture.md#Project-Structure]
  - `app/routes/convert.py` - Add route handler (EXISTS, modify)
  - `tests/integration/test_xml_to_json_endpoint.py` - Integration tests for endpoint (NEW)
- **Reuse Existing Components**: 
  - `app/routes/convert.py` - Use existing convert_bp Blueprint (EXISTS) - [Source: docs/stories/1-1-project-setup-and-flask-application-foundation.md#File-List]
  - `app/services/json_converter.py` - Use `convert_xml_string_to_json()` function (EXISTS) - [Source: docs/stories/1-3-xml-to-json-conversion-engine.md#File-List]
  - `app/exceptions.py` - Use XMLValidationError class (EXISTS) - [Source: docs/stories/1-2-xml-parsing-and-validation-core.md#File-List]
- **No Conflicts Detected**: Structure aligns perfectly with Architecture specifications

### Testing Standards

- Use pytest framework - [Source: docs/architecture.md#Decision-Summary]
- Integration tests in `tests/integration/` for endpoint testing - [Source: docs/architecture.md#Project-Structure]
- Use Flask test client for integration testing - [Source: docs/architecture.md#Communication-Patterns]
- Test request/response cycles end-to-end - [Source: docs/epics.md#Story-1.4]
- Test error scenarios (invalid Content-Type, malformed XML) - [Source: docs/epics.md#Story-1.4]
- Follow test patterns from existing integration tests - [Source: docs/stories/1-1-project-setup-and-flask-application-foundation.md#File-List]

### References

- **Epic Breakdown**: [docs/epics.md#Story-1.4] - Story 1.4 acceptance criteria and user story
- **Architecture**: [docs/architecture.md#Project-Structure] - Project structure and naming conventions
- **Architecture**: [docs/architecture.md#Communication-Patterns] - Service layer communication patterns
- **Architecture**: [docs/architecture.md#Error-Response-Format] - Error response format specifications
- **PRD**: [docs/PRD.md] - Product requirements and constraints
- **Previous Story**: [docs/stories/1-3-xml-to-json-conversion-engine.md] - JSON conversion service learnings and patterns
- **Previous Story**: [docs/stories/1-1-project-setup-and-flask-application-foundation.md] - Flask app structure and blueprint patterns

## Dev Agent Record

### Context Reference

- `docs/stories/1-4-post-endpoint-for-xml-to-json.context.xml`

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

- Implemented POST endpoint `/convert/xml-to-json` in `app/routes/convert.py`
- Added Content-Type validation for `application/xml` and `text/xml`
- Integrated error handling for XMLValidationError and unexpected exceptions
- All error responses follow structured format: `{error: {code, message, details}}`
- Reused existing `convert_xml_string_to_json()` service from Story 1.3
- Reused existing `XMLValidationError` exception class from Story 1.2

### Completion Notes List

**Implementation Summary:**
- **POST Endpoint**: Implemented `/convert/xml-to-json` endpoint accepting XML in request body
- **Content-Type Validation**: Validates `application/xml` or `text/xml` headers, returns 400 with structured error for invalid/missing Content-Type
- **Service Integration**: Successfully integrated `convert_xml_string_to_json()` service from Story 1.3
- **Error Handling**: Comprehensive error handling for:
  - Invalid/missing Content-Type → HTTP 400 with `INVALID_CONTENT_TYPE` code
  - Empty request body → HTTP 400 with `EMPTY_REQUEST_BODY` code
  - Malformed XML (XMLValidationError) → HTTP 400 with `XML_PARSE_ERROR` code including line/column details
  - Unexpected errors → HTTP 500 with `SERVER_ERROR` code
- **Response Format**: All responses follow architecture error format `{error: {code, message, details}}`
- **Testing**: Created comprehensive integration test suite (13 tests) covering:
  - Successful conversions (simple, nested, with attributes)
  - Content-Type validation (valid and invalid cases)
  - Error handling (malformed XML, empty body, invalid Content-Type)
  - End-to-end flow verification
  - Response header validation
- **Test Results**: All 82 tests passing (13 new integration tests + 69 existing tests), no regressions

### Completion Notes
**Completed:** 2025-01-28
**Definition of Done:** All acceptance criteria met, code reviewed, tests passing

### File List

**Modified:**
- `app/routes/convert.py` - Added POST `/convert/xml-to-json` endpoint with Content-Type validation and error handling

**Created:**
- `tests/integration/test_xml_to_json_endpoint.py` - Integration tests for XML-to-JSON endpoint (13 test cases)

## Change Log

- 2025-10-30: Story drafted by SM agent - Initial story creation from epics and architecture
- 2025-10-30: Story context generated and marked ready-for-dev
- 2025-01-27: Story implementation completed - POST endpoint `/convert/xml-to-json` implemented with Content-Type validation, error handling, and comprehensive integration tests (13 tests). All 82 tests passing, no regressions. Status updated to review.

