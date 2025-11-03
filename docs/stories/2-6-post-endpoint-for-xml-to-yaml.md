# Story 2.6: POST Endpoint for XML-to-YAML

Status: drafted

## Story

As an API consumer,
I want to send XML data via POST request and receive YAML response,
So that I can integrate YAML conversion into my applications.

## Acceptance Criteria

1. POST endpoint `/convert/xml-to-yaml` accepts XML in request body - [Source: docs/epics.md#Story-2.6]
2. Endpoint reuses XML parsing and validation from Epic 1 - [Source: docs/epics.md#Story-2.6]
3. Endpoint calls YAML conversion function from Story 2.5 - [Source: docs/epics.md#Story-2.6]
4. Returns HTTP 200 with YAML response body on success - [Source: docs/epics.md#Story-2.6]
5. Returns appropriate Content-Type header (`application/x-yaml` or `text/yaml`) - [Source: docs/epics.md#Story-2.6]
6. Error handling consistent with other conversion endpoints - [Source: docs/epics.md#Story-2.6]
7. Integration tests verify end-to-end YAML conversion flow - [Source: docs/epics.md#Story-2.6]

## Tasks / Subtasks

- [ ] Task 1: Add YAML endpoint to routes (AC: 1, 2, 3, 4, 5)
  - [ ] Open `app/routes/convert.py` - [Source: docs/stories/2-4-post-endpoint-for-xml-to-string.md#File-List]
  - [ ] Import yaml_converter service from `app/services/yaml_converter.py`
  - [ ] Create new route handler `convert_xml_to_yaml()` following other endpoint patterns
  - [ ] Register route `/convert/xml-to-yaml` with POST method
  - [ ] Reuse XML parsing and validation from Epic 1 (call xml_parser service)
  - [ ] Call YAML conversion function from yaml_converter service
  - [ ] Return HTTP 200 with YAML response body
  - [ ] Set Content-Type header to `application/x-yaml` or `text/yaml` - [Source: docs/architecture.md#API-Contracts]
  - [ ] Ensure error handling matches other endpoint patterns

- [ ] Task 2: Integrate error handling consistency (AC: 6)
  - [ ] Review error handling in other conversion endpoints - [Source: docs/stories/2-4-post-endpoint-for-xml-to-string.md#File-List]
  - [ ] Apply same error handling approach to YAML endpoint
  - [ ] Verify HTTP 400 for client errors (malformed XML, invalid Content-Type)
  - [ ] Verify HTTP 413 for requests exceeding 300MB size limit
  - [ ] Verify HTTP 500 for server errors with generic message
  - [ ] Ensure error responses use JSON format (consistent with Epic 1) - [Source: docs/architecture.md#Error-Response-Format]

- [ ] Task 3: Write integration tests (AC: 7)
  - [ ] Create or update `tests/integration/test_endpoints.py` - [Source: docs/testing-strategy.md#Test-Structure]
  - [ ] Add test for successful YAML conversion: `test_xml_to_yaml_endpoint_success()`
  - [ ] Add test for malformed XML: `test_xml_to_yaml_endpoint_malformed_xml()`
  - [ ] Add test for invalid Content-Type: `test_xml_to_yaml_endpoint_invalid_content_type()`
  - [ ] Add test for size limit enforcement: `test_xml_to_yaml_endpoint_size_limit()`
  - [ ] Verify response Content-Type header is `application/x-yaml` or `text/yaml`
  - [ ] Verify response body is valid YAML format
  - [ ] Use Flask test client following integration test patterns - [Source: docs/testing-strategy.md#Integration-Test-Template]

## Dev Notes

### Requirements Context Summary

This story creates the POST endpoint for XML-to-YAML conversion that exposes the YAML conversion service via HTTP API. The endpoint must reuse the XML parsing and validation infrastructure from Epic 1, call the YAML conversion service from Story 2.5, and maintain consistent error handling and response structure with other conversion endpoints.

**Key Requirements:**

- POST endpoint `/convert/xml-to-yaml` - [Source: docs/epics.md#Story-2.6]
- Reuse XML parsing/validation from Epic 1 - [Source: docs/epics.md#Story-2.6]
- Call YAML conversion function - [Source: docs/epics.md#Story-2.6]
- Return YAML with `application/x-yaml` or `text/yaml` Content-Type - [Source: docs/epics.md#Story-2.6]
- Consistent error handling - [Source: docs/epics.md#Story-2.6]
- Integration tests - [Source: docs/epics.md#Story-2.6]

### Structure Alignment Summary

**Project Structure Alignment:**

- Follow exact directory structure from Architecture document - [Source: docs/architecture.md#Project-Structure]
- `app/routes/convert.py` - Modify existing file to add YAML endpoint - [Source: docs/stories/2-4-post-endpoint-for-xml-to-string.md#File-List]
- `app/services/yaml_converter.py` - Use service from Story 2.5 (EXISTS after 2.5)
- `tests/integration/test_endpoints.py` - Add integration tests (EXISTS, modify) - [Source: docs/testing-strategy.md#Test-Structure]

**Component Boundaries:**

- Route Handler: HTTP endpoint implementation
- YAML Service: Reuse conversion service from Story 2.5
- XML Parser: Reuse parsing service from Epic 1
- Error Handling: Consistent with other endpoints

**Naming Conventions:**

- Route function: `convert_xml_to_yaml()` (snake_case) - [Source: docs/architecture.md#Naming-Patterns]
- Route path: `/convert/xml-to-yaml` (kebab-case) - [Source: docs/architecture.md#Naming-Patterns]
- Test function: `test_xml_to_yaml_endpoint_*` - [Source: docs/testing-strategy.md#Test-Naming-Conventions]

### Learnings from Previous Story

**From Story 2.5 (Status: drafted)**

- **YAML Service**: YAML converter service will be available at `app/services/yaml_converter.py` - import and use `convert_xml_to_yaml()` function - [Source: docs/stories/2-5-xml-to-yaml-conversion-engine.md#File-List]

**From Story 2.4 (Status: drafted)**

- **Route Pattern**: String endpoint pattern established at `app/routes/convert.py` - follow same pattern for YAML endpoint - [Source: docs/stories/2-4-post-endpoint-for-xml-to-string.md#File-List]
- **Route Structure**: Routes registered via Flask Blueprint - add YAML route to same blueprint
- **Error Handling**: Error handling pattern established - reuse same approach

**Files to Reference:**

- `app/routes/convert.py` - Route handler pattern (EXISTS, modify)
- `app/services/yaml_converter.py` - YAML conversion service (WILL EXIST after Story 2.5)
- `app/services/xml_parser.py` - XML parsing service (EXISTS, reuse)
- `tests/integration/test_endpoints.py` - Integration test patterns (EXISTS, modify)

### Project Structure Notes

- **Directory Structure**: Match exactly as defined in Architecture document - [Source: docs/architecture.md#Project-Structure]
  - `app/routes/convert.py` - Add YAML endpoint (EXISTS, modify)
  - `tests/integration/test_endpoints.py` - Add YAML tests (EXISTS, modify)
- **Route Registration**: YAML endpoint in same Blueprint as other endpoints
- **No Conflicts Detected**: Structure aligns perfectly with Architecture specifications

### Testing Standards

- Integration tests in `tests/integration/test_endpoints.py` - [Source: docs/testing-strategy.md#Test-Structure]
- Use Flask test client for endpoint testing - [Source: docs/testing-strategy.md#Integration-Test-Template]
- Test success path, error paths, Content-Type headers, response format
- Follow Arrange-Act-Assert pattern - [Source: docs/testing-strategy.md#Best-Practices]

### References

- **Epic Breakdown**: [docs/epics.md#Story-2.6] - Story 2.6 acceptance criteria and user story
- **Architecture**: [docs/architecture.md#API-Contracts] - API contract specifications
- **Architecture**: [docs/architecture.md#Error-Response-Format] - Error response format
- **Testing Strategy**: [docs/testing-strategy.md] - Testing patterns
- **Previous Story**: [docs/stories/2-4-post-endpoint-for-xml-to-string.md] - Endpoint pattern reference
- **Previous Story**: [docs/stories/2-5-xml-to-yaml-conversion-engine.md] - YAML converter service

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### References

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

