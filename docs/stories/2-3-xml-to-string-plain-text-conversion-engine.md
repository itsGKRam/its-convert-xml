# Story 2.3: XML-to-String (Plain Text) Conversion Engine

Status: drafted

## Story

As an API consumer,
I want to convert XML data to plain text string format,
So that I can extract text content for simple text processing or display.

## Acceptance Criteria

1. Conversion function extracts text content from XML elements - [Source: docs/epics.md#Story-2.3]
2. Conversion handles nested structures (concatenates text appropriately) - [Source: docs/epics.md#Story-2.3]
3. Strips XML tags and preserves only text content - [Source: docs/epics.md#Story-2.3]
4. Handles whitespace and formatting appropriately (configurable) - [Source: docs/epics.md#Story-2.3]
5. Conversion handles attributes if needed (user-selectable option) - [Source: docs/epics.md#Story-2.3]
6. Unit tests verify accurate string extraction for various XML structures - [Source: docs/epics.md#Story-2.3]
7. Error handling consistent with Epic 1 patterns - [Source: docs/epics.md#Story-2.3]

## Tasks / Subtasks

- [ ] Task 1: Implement XML-to-String conversion function (AC: 1, 2, 3, 4, 5)
  - [ ] Create `app/services/string_converter.py` - [Source: docs/architecture.md#Project-Structure]
  - [ ] Import xml.etree.ElementTree or use parsed XML from xml_parser service - [Source: docs/architecture.md#Decision-Summary]
  - [ ] Implement `convert_xml_to_string()` function signature matching JSON/CSV converter patterns
  - [ ] Extract text content from XML elements recursively
  - [ ] Handle nested structures: concatenate text from child elements appropriately
  - [ ] Strip XML tags and preserve only text content
  - [ ] Handle whitespace: trim leading/trailing, normalize internal whitespace (configurable)
  - [ ] Add option to include attributes in output (user-selectable parameter)
  - [ ] Handle edge cases: empty elements, mixed content, CDATA sections
  - [ ] Return plain text string output

- [ ] Task 2: Write comprehensive unit tests (AC: 6)
  - [ ] Create `tests/unit/test_string_converter.py` - [Source: docs/testing-strategy.md#Test-Structure]
  - [ ] Test simple XML text extraction
  - [ ] Test nested structure text concatenation
  - [ ] Test whitespace handling and normalization
  - [ ] Test attribute inclusion option
  - [ ] Test edge cases: empty elements, mixed content, CDATA
  - [ ] Use test fixtures from `tests/data/` directory - [Source: docs/testing-strategy.md#Test-Fixtures]
  - [ ] Achieve > 80% coverage target for string_converter.py - [Source: docs/testing-strategy.md#Coverage-Target]
  - [ ] Test error handling consistent with Epic 1 patterns

- [ ] Task 3: Integrate error handling patterns from Epic 1 (AC: 7)
  - [ ] Review error handling in `app/services/json_converter.py` for patterns - [Source: docs/stories/1-5-error-handling-and-structured-error-responses.md#File-List]
  - [ ] Apply same error handling approach to String converter
  - [ ] Use custom exceptions if needed (from `app/exceptions.py`) - [Source: docs/stories/1-5-error-handling-and-structured-error-responses.md#File-List]
  - [ ] Ensure consistent error messages and structure

## Dev Notes

### Requirements Context Summary

This story implements the core XML-to-String conversion engine that extracts plain text content from XML documents. The conversion must handle nested structures, properly format whitespace, optionally include attributes, and maintain consistency with Epic 1 error handling patterns. This service will be used by the POST endpoint in Story 2.4.

**Key Requirements:**

- Text content extraction from XML elements - [Source: docs/epics.md#Story-2.3]
- Nested structure handling with text concatenation - [Source: docs/epics.md#Story-2.3]
- Whitespace and formatting handling (configurable) - [Source: docs/epics.md#Story-2.3]
- Optional attribute inclusion - [Source: docs/epics.md#Story-2.3]
- Comprehensive unit test coverage - [Source: docs/epics.md#Story-2.3]
- Error handling consistent with Epic 1 - [Source: docs/epics.md#Story-2.3]

### Structure Alignment Summary

**Project Structure Alignment:**

- Follow exact directory structure from Architecture document - [Source: docs/architecture.md#Project-Structure]
- `app/services/string_converter.py` - New service module (NEW) - [Source: docs/architecture.md#Project-Structure]
- `tests/unit/test_string_converter.py` - Unit test file (NEW) - [Source: docs/testing-strategy.md#Test-Structure]
- Reuse XML parsing from `app/services/xml_parser.py` - [Source: docs/stories/1-2-xml-parsing-and-validation-core.md#File-List]
- Follow patterns from `app/services/json_converter.py` and `app/services/csv_converter.py`

**Component Boundaries:**

- String Converter: XML-to-String transformation logic
- XML Parser: Reuse existing parsing service (no changes needed)
- Error Handling: Consistent with Epic 1 error patterns
- Testing: Unit tests following established patterns

**Naming Conventions:**

- Service file: `string_converter.py` (snake_case) - [Source: docs/architecture.md#Naming-Patterns]
- Function name: `convert_xml_to_string()` (snake_case) - [Source: docs/architecture.md#Naming-Patterns]
- Test file: `test_string_converter.py` - [Source: docs/testing-strategy.md#Test-Naming-Conventions]

### Learnings from Previous Story

**From Story 2.2 (Status: drafted)**

- **Endpoint Pattern**: POST endpoint pattern established - String endpoint will follow same pattern in Story 2.4 - [Source: docs/stories/2-2-post-endpoint-for-xml-to-csv.md#File-List]

**From Story 2.1 (Status: drafted)**

- **Service Pattern**: CSV converter service established at `app/services/csv_converter.py` - follow same pattern for String converter - [Source: docs/stories/2-1-xml-to-csv-conversion-engine.md#File-List]

**From Epic 1 Completion:**

- **Service Architecture**: Services in `app/services/` directory with clear separation - follow same pattern - [Source: docs/architecture.md#Project-Structure]
- **Test Coverage**: Target > 80% coverage for core conversion logic - [Source: docs/testing-strategy.md#Coverage-Target]
- **Error Patterns**: Custom exceptions in `app/exceptions.py` - use if needed - [Source: docs/stories/1-5-error-handling-and-structured-error-responses.md#File-List]
- **XML Parser**: XML parsing service available at `app/services/xml_parser.py` - reuse for XML input - [Source: docs/stories/1-2-xml-parsing-and-validation-core.md#File-List]

**Files to Reference:**

- `app/services/csv_converter.py` - Conversion service pattern (EXISTS after 2.1, reference)
- `app/services/json_converter.py` - Conversion service pattern (EXISTS, reference)
- `app/services/xml_parser.py` - XML parsing service (EXISTS, reuse)
- `app/exceptions.py` - Custom exceptions (EXISTS, use if needed)
- `tests/unit/test_csv_converter.py` - Test patterns (WILL EXIST after 2.1, reference)

### Project Structure Notes

- **Directory Structure**: Match exactly as defined in Architecture document - [Source: docs/architecture.md#Project-Structure]
  - `app/services/string_converter.py` - String conversion service (NEW)
  - `tests/unit/test_string_converter.py` - Unit tests (NEW)
- **Reuse Existing Components**: XML parser, error handling, test infrastructure from Epic 1 and Stories 2.1-2.2
- **No Conflicts Detected**: Structure aligns perfectly with Architecture specifications

### Testing Standards

- Unit tests in `tests/unit/test_string_converter.py` - [Source: docs/testing-strategy.md#Test-Structure]
- Use test fixtures from `tests/data/` directory - [Source: docs/testing-strategy.md#Test-Fixtures]
- Target > 80% coverage for string_converter.py - [Source: docs/testing-strategy.md#Coverage-Target]
- Test text extraction, nested structures, whitespace handling, attribute options
- Follow Arrange-Act-Assert pattern - [Source: docs/testing-strategy.md#Best-Practices]

### References

- **Epic Breakdown**: [docs/epics.md#Story-2.3] - Story 2.3 acceptance criteria and user story
- **Architecture**: [docs/architecture.md#Project-Structure] - Project structure and service locations
- **Architecture**: [docs/architecture.md#Decision-Summary] - Technology stack decisions (xml.etree.ElementTree for text extraction)
- **Testing Strategy**: [docs/testing-strategy.md] - Testing patterns and coverage targets
- **Previous Story**: [docs/stories/2-1-xml-to-csv-conversion-engine.md] - Conversion service pattern reference
- **Previous Story**: [docs/stories/1-2-xml-parsing-and-validation-core.md] - XML parser service

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

