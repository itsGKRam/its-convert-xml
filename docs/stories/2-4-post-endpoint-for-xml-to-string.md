# Story 2.4: POST Endpoint for XML-to-String

Status: drafted

## Story

As an API consumer,
I want to send XML data via POST request and receive plain text string response,
So that I can extract text content from XML documents.

## Acceptance Criteria

1. POST endpoint `/convert/xml-to-string` accepts XML in request body - [Source: docs/epics.md#Story-2.4]
2. Endpoint reuses XML parsing and validation from Epic 1 - [Source: docs/epics.md#Story-2.4]
3. Endpoint calls string conversion function from Story 2.3 - [Source: docs/epics.md#Story-2.4]
4. Returns HTTP 200 with plain text response body on success - [Source: docs/epics.md#Story-2.4]
5. Returns appropriate Content-Type header (`text/plain`) - [Source: docs/epics.md#Story-2.4]
6. Error handling consistent with other conversion endpoints - [Source: docs/epics.md#Story-2.4]
7. Integration tests verify end-to-end string conversion flow - [Source: docs/epics.md#Story-2.4]

## Tasks / Subtasks

- [ ] Task 1: Add String endpoint to routes (AC: 1, 2, 3, 4, 5)
  - [ ] Open `app/routes/convert.py` - [Source: docs/stories/2-2-post-endpoint-for-xml-to-csv.md#File-List]
  - [ ] Import string_converter service from `app/services/string_converter.py`
  - [ ] Create new route handler `convert_xml_to_string()` following JSON/CSV endpoint patterns
  - [ ] Register route `/convert/xml-to-string` with POST method
  - [ ] Reuse XML parsing and validation from Epic 1 (call xml_parser service)
  - [ ] Call String conversion function from string_converter service
  - [ ] Return HTTP 200 with plain text response body
  - [ ] Set Content-Type header to `text/plain` - [Source: docs/architecture.md#API-Contracts]
  - [ ] Ensure error handling matches other endpoint patterns

- [ ] Task 2: Integrate error handling consistency (AC: 6)
  - [ ] Review error handling in JSON/CSV endpoints - [Source: docs/stories/2-2-post-endpoint-for-xml-to-csv.md#File-List]
  - [ ] Apply same error handling approach to String endpoint
  - [ ] Verify HTTP 400 for client errors (malformed XML, invalid Content-Type)
  - [ ] Verify HTTP 413 for requests exceeding 300MB size limit
  - [ ] Verify HTTP 500 for server errors with generic message
  - [ ] Ensure error responses use JSON format (consistent with Epic 1) - [Source: docs/architecture.md#Error-Response-Format]

- [ ] Task 3: Write integration tests (AC: 7)
  - [ ] Create or update `tests/integration/test_endpoints.py` - [Source: docs/testing-strategy.md#Test-Structure]
  - [ ] Add test for successful String conversion: `test_xml_to_string_endpoint_success()`
  - [ ] Add test for malformed XML: `test_xml_to_string_endpoint_malformed_xml()`
  - [ ] Add test for invalid Content-Type: `test_xml_to_string_endpoint_invalid_content_type()`
  - [ ] Add test for size limit enforcement: `test_xml_to_string_endpoint_size_limit()`
  - [ ] Verify response Content-Type header is `text/plain`
  - [ ] Verify response body is plain text (not JSON)
  - [ ] Use Flask test client following integration test patterns - [Source: docs/testing-strategy.md#Integration-Test-Template]

## Dev Notes

### Requirements Context Summary

This story creates the POST endpoint for XML-to-String conversion that exposes the String conversion service via HTTP API. The endpoint must reuse the XML parsing and validation infrastructure from Epic 1, call the String conversion service from Story 2.3, and maintain consistent error handling and response structure with other conversion endpoints.

**Key Requirements:**

- POST endpoint `/convert/xml-to-string` - [Source: docs/epics.md#Story-2.4]
- Reuse XML parsing/validation from Epic 1 - [Source: docs/epics.md#Story-2.4]
- Call String conversion function - [Source: docs/epics.md#Story-2.4]
- Return plain text with `text/plain` Content-Type - [Source: docs/epics.md#Story-2.4]
- Consistent error handling - [Source: docs/epics.md#Story-2.4]
- Integration tests - [Source: docs/epics.md#Story-2.4]

### Structure Alignment Summary

**Project Structure Alignment:**

- Follow exact directory structure from Architecture document - [Source: docs/architecture.md#Project-Structure]
- `app/routes/convert.py` - Modify existing file to add String endpoint - [Source: docs/stories/2-2-post-endpoint-for-xml-to-csv.md#File-List]
- `app/services/string_converter.py` - Use service from Story 2.3 (EXISTS after 2.3)
- `tests/integration/test_endpoints.py` - Add integration tests (EXISTS, modify) - [Source: docs/testing-strategy.md#Test-Structure]

**Component Boundaries:**

- Route Handler: HTTP endpoint implementation
- String Service: Reuse conversion service from Story 2.3
- XML Parser: Reuse parsing service from Epic 1
- Error Handling: Consistent with other endpoints

**Naming Conventions:**

- Route function: `convert_xml_to_string()` (snake_case) - [Source: docs/architecture.md#Naming-Patterns]
- Route path: `/convert/xml-to-string` (kebab-case) - [Source: docs/architecture.md#Naming-Patterns]
- Test function: `test_xml_to_string_endpoint_*` - [Source: docs/testing-strategy.md#Test-Naming-Conventions]

### Learnings from Previous Story

**From Story 2.3 (Status: drafted)**

- **String Service**: String converter service will be available at `app/services/string_converter.py` - import and use `convert_xml_to_string()` function - [Source: docs/stories/2-3-xml-to-string-plain-text-conversion-engine.md#File-List]

**From Story 2.2 (Status: drafted)**

- **Route Pattern**: CSV endpoint pattern established at `app/routes/convert.py` - follow same pattern for String endpoint - [Source: docs/stories/2-2-post-endpoint-for-xml-to-csv.md#File-List]
- **Route Structure**: Routes registered via Flask Blueprint - add String route to same blueprint
- **Error Handling**: Error handling pattern established - reuse same approach

**Files to Reference:**

- `app/routes/convert.py` - Route handler pattern (EXISTS, modify)
- `app/services/string_converter.py` - String conversion service (WILL EXIST after Story 2.3)
- `app/services/xml_parser.py` - XML parsing service (EXISTS, reuse)
- `tests/integration/test_endpoints.py` - Integration test patterns (EXISTS, modify)

### Project Structure Notes

- **Directory Structure**: Match exactly as defined in Architecture document - [Source: docs/architecture.md#Project-Structure]
  - `app/routes/convert.py` - Add String endpoint (EXISTS, modify)
  - `tests/integration/test_endpoints.py` - Add String tests (EXISTS, modify)
- **Route Registration**: String endpoint in same Blueprint as other endpoints
- **No Conflicts Detected**: Structure aligns perfectly with Architecture specifications

### Testing Standards

- Integration tests in `tests/integration/test_endpoints.py` - [Source: docs/testing-strategy.md#Test-Structure]
- Use Flask test client for endpoint testing - [Source: docs/testing-strategy.md#Integration-Test-Template]
- Test success path, error paths, Content-Type headers, response format
- Follow Arrange-Act-Assert pattern - [Source: docs/testing-strategy.md#Best-Practices]

### References

- **Epic Breakdown**: [docs/epics.md#Story-2.4] - Story 2.4 acceptance criteria and user story
- **Architecture**: [docs/architecture.md#API-Contracts] - API contract specifications
- **Architecture**: [docs/architecture.md#Error-Response-Format] - Error response format
- **Testing Strategy**: [docs/testing-strategy.md] - Testing patterns
- **Previous Story**: [docs/stories/2-2-post-endpoint-for-xml-to-csv.md] - Endpoint pattern reference
- **Previous Story**: [docs/stories/2-3-xml-to-string-plain-text-conversion-engine.md] - String converter service

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

