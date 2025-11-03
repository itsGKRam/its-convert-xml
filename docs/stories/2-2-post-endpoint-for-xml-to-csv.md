# Story 2.2: POST Endpoint for XML-to-CSV

Status: review

## Story

As an API consumer,
I want to send XML data via POST request and receive CSV response,
So that I can integrate CSV conversion into my applications.

## Acceptance Criteria

1. POST endpoint `/convert/xml-to-csv` accepts XML in request body - [Source: docs/epics.md#Story-2.2]
2. Endpoint reuses XML parsing and validation from Epic 1 - [Source: docs/epics.md#Story-2.2]
3. Endpoint calls CSV conversion function from Story 2.1 - [Source: docs/epics.md#Story-2.2]
4. Returns HTTP 200 with CSV response body on success - [Source: docs/epics.md#Story-2.2]
5. Returns appropriate Content-Type header (`text/csv`) - [Source: docs/epics.md#Story-2.2]
6. Error handling consistent with `/convert/xml-to-json` endpoint - [Source: docs/epics.md#Story-2.2]
7. Integration tests verify end-to-end CSV conversion flow - [Source: docs/epics.md#Story-2.2]

## Tasks / Subtasks

- [x] Task 1: Add CSV endpoint to routes (AC: 1, 2, 3, 4, 5)
  - [x] Open `app/routes/convert.py` - [Source: docs/stories/1-4-post-endpoint-for-xml-to-json.md#File-List]
  - [x] Import csv_converter service from `app/services/csv_converter.py`
  - [x] Create new route handler `convert_xml_to_csv()` following JSON endpoint pattern - [Source: docs/stories/1-4-post-endpoint-for-xml-to-json.md#File-List]
  - [x] Register route `/convert/xml-to-csv` with POST method
  - [x] Reuse XML parsing and validation from Epic 1 (call xml_parser service)
  - [x] Call CSV conversion function from csv_converter service
  - [x] Return HTTP 200 with CSV response body
  - [x] Set Content-Type header to `text/csv` - [Source: docs/architecture.md#API-Contracts]
  - [x] Ensure error handling matches JSON endpoint pattern

- [x] Task 2: Integrate error handling consistency (AC: 6)
  - [x] Review error handling in JSON endpoint (`/convert/xml-to-json`) - [Source: docs/stories/1-4-post-endpoint-for-xml-to-json.md#File-List]
  - [x] Apply same error handling approach to CSV endpoint
  - [x] Verify HTTP 400 for client errors (malformed XML, invalid Content-Type)
  - [x] Verify HTTP 413 for requests exceeding 300MB size limit
  - [x] Verify HTTP 500 for server errors with generic message
  - [x] Ensure error responses use JSON format (consistent with Epic 1) - [Source: docs/architecture.md#Error-Response-Format]

- [x] Task 3: Write integration tests (AC: 7)
  - [x] Create or update `tests/integration/test_endpoints.py` - [Source: docs/testing-strategy.md#Test-Structure]
  - [x] Add test for successful CSV conversion: `test_xml_to_csv_endpoint_success()`
  - [x] Add test for malformed XML: `test_xml_to_csv_endpoint_malformed_xml()`
  - [x] Add test for invalid Content-Type: `test_xml_to_csv_endpoint_invalid_content_type()`
  - [x] Add test for size limit enforcement: `test_xml_to_csv_endpoint_size_limit()`
  - [x] Verify response Content-Type header is `text/csv`
  - [x] Verify response body is valid CSV format
  - [x] Use Flask test client following integration test patterns - [Source: docs/testing-strategy.md#Integration-Test-Template]

## Dev Notes

### Requirements Context Summary

This story creates the POST endpoint for XML-to-CSV conversion that exposes the CSV conversion service via HTTP API. The endpoint must reuse the XML parsing and validation infrastructure from Epic 1, call the CSV conversion service from Story 2.1, and maintain consistent error handling and response structure with the JSON endpoint.

**Key Requirements:**

- POST endpoint `/convert/xml-to-csv` - [Source: docs/epics.md#Story-2.2]
- Reuse XML parsing/validation from Epic 1 - [Source: docs/epics.md#Story-2.2]
- Call CSV conversion function - [Source: docs/epics.md#Story-2.2]
- Return CSV with `text/csv` Content-Type - [Source: docs/epics.md#Story-2.2]
- Consistent error handling - [Source: docs/epics.md#Story-2.2]
- Integration tests - [Source: docs/epics.md#Story-2.2]

### Structure Alignment Summary

**Project Structure Alignment:**

- Follow exact directory structure from Architecture document - [Source: docs/architecture.md#Project-Structure]
- `app/routes/convert.py` - Modify existing file to add CSV endpoint - [Source: docs/stories/1-4-post-endpoint-for-xml-to-json.md#File-List]
- `app/services/csv_converter.py` - Use service from Story 2.1 (EXISTS after 2.1)
- `tests/integration/test_endpoints.py` - Add integration tests (EXISTS, modify) - [Source: docs/testing-strategy.md#Test-Structure]

**Component Boundaries:**

- Route Handler: HTTP endpoint implementation
- CSV Service: Reuse conversion service from Story 2.1
- XML Parser: Reuse parsing service from Epic 1
- Error Handling: Consistent with JSON endpoint

**Naming Conventions:**

- Route function: `convert_xml_to_csv()` (snake_case) - [Source: docs/architecture.md#Naming-Patterns]
- Route path: `/convert/xml-to-csv` (kebab-case) - [Source: docs/architecture.md#Naming-Patterns]
- Test function: `test_xml_to_csv_endpoint_*` - [Source: docs/testing-strategy.md#Test-Naming-Conventions]

### Learnings from Previous Story

**From Story 2.1 (Status: drafted)**

- **CSV Service**: CSV converter service will be available at `app/services/csv_converter.py` - import and use `convert_xml_to_csv()` function - [Source: docs/stories/2-1-xml-to-csv-conversion-engine.md#File-List]

**From Story 1.4 (Status: done)**

- **Route Pattern**: JSON endpoint pattern established at `app/routes/convert.py` - follow same pattern for CSV endpoint - [Source: docs/stories/1-4-post-endpoint-for-xml-to-json.md#File-List]
- **Route Structure**: Routes registered via Flask Blueprint in `app/__init__.py` - add CSV route to same blueprint - [Source: docs/stories/1-4-post-endpoint-for-xml-to-json.md#File-List]
- **Error Handling**: Error handling pattern established - reuse same approach - [Source: docs/stories/1-5-error-handling-and-structured-error-responses.md#File-List]

**Files to Reference:**

- `app/routes/convert.py` - Route handler pattern (EXISTS, modify)
- `app/services/csv_converter.py` - CSV conversion service (WILL EXIST after Story 2.1)
- `app/services/xml_parser.py` - XML parsing service (EXISTS, reuse)
- `tests/integration/test_endpoints.py` - Integration test patterns (EXISTS, modify)

### Project Structure Notes

- **Directory Structure**: Match exactly as defined in Architecture document - [Source: docs/architecture.md#Project-Structure]
  - `app/routes/convert.py` - Add CSV endpoint (EXISTS, modify)
  - `tests/integration/test_endpoints.py` - Add CSV tests (EXISTS, modify)
- **Route Registration**: CSV endpoint in same Blueprint as JSON endpoint
- **No Conflicts Detected**: Structure aligns perfectly with Architecture specifications

### Testing Standards

- Integration tests in `tests/integration/test_endpoints.py` - [Source: docs/testing-strategy.md#Test-Structure]
- Use Flask test client for endpoint testing - [Source: docs/testing-strategy.md#Integration-Test-Template]
- Test success path, error paths, Content-Type headers, response format
- Follow Arrange-Act-Assert pattern - [Source: docs/testing-strategy.md#Best-Practices]

### References

- **Epic Breakdown**: [docs/epics.md#Story-2.2] - Story 2.2 acceptance criteria and user story
- **Architecture**: [docs/architecture.md#API-Contracts] - API contract specifications
- **Architecture**: [docs/architecture.md#Error-Response-Format] - Error response format
- **Testing Strategy**: [docs/testing-strategy.md] - Testing patterns
- **Previous Story**: [docs/stories/1-4-post-endpoint-for-xml-to-json.md] - JSON endpoint pattern reference
- **Previous Story**: [docs/stories/2-1-xml-to-csv-conversion-engine.md] - CSV converter service

## Dev Agent Record

### Context Reference

- `docs/stories/2-2-post-endpoint-for-xml-to-csv.context.xml`

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

**Implementation Plan**:
- Reviewed JSON endpoint pattern in `app/routes/convert.py` to ensure consistency
- Confirmed CSV converter service interface: `convert_xml_string_to_csv(xml_string: str) -> str`
- Followed exact same pattern: validate request size → validate Content-Type → read XML → call conversion service → handle errors → return response
- Used Flask `Response` object with `mimetype='text/csv'` for CSV responses (instead of `jsonify()` for JSON)
- Verified error formatters from `app/utils/validators.py` are reused for consistent error responses

### Completion Notes List

- **Implementation Summary**: Successfully implemented POST endpoint `/convert/xml-to-csv` following the same pattern as the JSON endpoint. The endpoint reuses XML parsing/validation from Epic 1, calls the CSV converter service from Story 2.1, and returns CSV responses with proper `text/csv` Content-Type header.

- **Key Implementation Details**:
  - Added `convert_xml_to_csv()` route handler in `app/routes/convert.py`
  - Imported `convert_xml_string_to_csv` from `app/services/csv_converter.py`
  - Reused exact error handling pattern from JSON endpoint (request size validation, Content-Type validation, XML parsing error handling)
  - Error responses return JSON format (consistent with Epic 1), while success responses return CSV with `text/csv` header
  - Implemented performance monitoring (same as JSON endpoint) with timing and optional memory tracking

- **Testing**: Created comprehensive integration test suite with 15 test cases covering:
  - Successful conversions with various XML structures (simple, nested, with attributes)
  - Error handling (malformed XML, invalid Content-Type, empty body, size limits)
  - Response format validation (Content-Type header, CSV format compliance, RFC 4180)
  - End-to-end conversion flows

- **Test Results**: All 169 tests pass (including 15 new CSV endpoint tests), no regressions introduced. Full test suite execution completed successfully.

### File List

- `app/routes/convert.py` - Added CSV endpoint route handler `convert_xml_to_csv()`
- `tests/integration/test_endpoints.py` - Created comprehensive integration test suite for CSV endpoint

## Change Log

- 2025-01-31: Story implementation completed - Added POST endpoint `/convert/xml-to-csv`, integrated CSV conversion service, implemented comprehensive integration tests (15 test cases), all tests passing (169 total, no regressions). Story marked ready for review.

