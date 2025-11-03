# Story 2.1: XML-to-CSV Conversion Engine

Status: review

## Story

As an API consumer,
I want to convert XML data to CSV format,
So that I can use the data in spreadsheet applications and data analysis tools.

## Acceptance Criteria

1. Conversion function transforms XML to CSV format - [Source: docs/epics.md#Story-2.1]
2. Handles flat XML structures (rows as elements, columns as child elements or attributes) - [Source: docs/epics.md#Story-2.1]
3. Handles nested structures appropriately (flattening strategy documented) - [Source: docs/epics.md#Story-2.1]
4. CSV output follows RFC 4180 standard (proper escaping, quoting) - [Source: docs/epics.md#Story-2.1]
5. Handles XML namespaces in column naming - [Source: docs/epics.md#Story-2.1]
6. Unit tests verify accurate CSV conversion for various XML structures - [Source: docs/epics.md#Story-2.1]
7. Error handling consistent with Epic 1 patterns - [Source: docs/epics.md#Story-2.1]

## Tasks / Subtasks

- [x] Task 1: Implement XML-to-CSV conversion function (AC: 1, 2, 3, 4, 5)

  - [x] Create `app/services/csv_converter.py` - [Source: docs/architecture.md#Project-Structure]
  - [x] Import xml.etree.ElementTree or use parsed XML from xml_parser service - [Source: docs/architecture.md#Decision-Summary]
  - [x] Implement `convert_xml_to_csv()` function signature matching JSON converter pattern - [Source: docs/stories/1-3-xml-to-json-conversion-engine.md#File-List]
  - [x] Handle flat XML structures: rows as elements, columns as child elements or attributes
  - [x] Handle nested structures: implement flattening strategy (document approach)
  - [x] Use Python csv module (stdlib) for CSV generation - [Source: docs/architecture.md#Decision-Summary]
  - [x] Ensure CSV output follows RFC 4180 standard (proper escaping, quoting)
  - [x] Handle XML namespaces in column naming (e.g., prefix namespace or include namespace URI)
  - [x] Handle edge cases: empty elements, missing attributes, special characters in data
  - [x] Return CSV string output

- [x] Task 2: Write comprehensive unit tests (AC: 6)

  - [x] Create `tests/unit/test_csv_converter.py` - [Source: docs/testing-strategy.md#Test-Structure]
  - [x] Test flat XML structure conversion (simple rows/columns)
  - [x] Test nested XML structure conversion (verify flattening strategy)
  - [x] Test namespace handling in column names
  - [x] Test RFC 4180 compliance (quoting, escaping special characters)
  - [x] Test edge cases: empty XML, single element, attributes only, mixed content
  - [x] Test complex XML with multiple namespaces (example-complex.xml) - [Source: tests/data/example-complex.xml]
  - [x] Use test fixtures from `tests/data/` directory - [Source: docs/testing-strategy.md#Test-Fixtures]
  - [x] Achieve > 80% coverage target for csv_converter.py - [Source: docs/testing-strategy.md#Coverage-Target]
  - [x] Test error handling consistent with Epic 1 patterns

- [x] Task 3: Integrate error handling patterns from Epic 1 (AC: 7)
  - [x] Review error handling in `app/services/json_converter.py` for patterns - [Source: docs/stories/1-5-error-handling-and-structured-error-responses.md#File-List]
  - [x] Apply same error handling approach to CSV converter
  - [x] Use custom exceptions if needed (from `app/exceptions.py`) - [Source: docs/stories/1-5-error-handling-and-structured-error-responses.md#File-List]
  - [x] Ensure consistent error messages and structure

## Dev Notes

### Requirements Context Summary

This story implements the core XML-to-CSV conversion engine that transforms XML data into CSV format. The conversion must handle various XML structures (flat and nested), properly format CSV output according to RFC 4180 standards, and maintain consistency with Epic 1 error handling patterns. This service will be used by the POST endpoint in Story 2.2.

**Key Requirements:**

- XML-to-CSV conversion function with flat and nested structure support - [Source: docs/epics.md#Story-2.1]
- RFC 4180 compliant CSV output - [Source: docs/epics.md#Story-2.1]
- XML namespace handling in column naming - [Source: docs/epics.md#Story-2.1]
- Comprehensive unit test coverage - [Source: docs/epics.md#Story-2.1]
- Error handling consistent with Epic 1 - [Source: docs/epics.md#Story-2.1]

### Structure Alignment Summary

**Project Structure Alignment:**

- Follow exact directory structure from Architecture document - [Source: docs/architecture.md#Project-Structure]
- `app/services/csv_converter.py` - New service module (NEW) - [Source: docs/architecture.md#Project-Structure]
- `tests/unit/test_csv_converter.py` - Unit test file (NEW) - [Source: docs/testing-strategy.md#Test-Structure]
- Reuse XML parsing from `app/services/xml_parser.py` - [Source: docs/stories/1-2-xml-parsing-and-validation-core.md#File-List]
- Follow patterns from `app/services/json_converter.py` - [Source: docs/stories/1-3-xml-to-json-conversion-engine.md#File-List]

**Component Boundaries:**

- CSV Converter: XML-to-CSV transformation logic
- XML Parser: Reuse existing parsing service (no changes needed)
- Error Handling: Consistent with Epic 1 error patterns
- Testing: Unit tests following established patterns

**Naming Conventions:**

- Service file: `csv_converter.py` (snake_case) - [Source: docs/architecture.md#Naming-Patterns]
- Function name: `convert_xml_to_csv()` (snake_case) - [Source: docs/architecture.md#Naming-Patterns]
- Test file: `test_csv_converter.py` - [Source: docs/testing-strategy.md#Test-Naming-Conventions]

### Learnings from Previous Story

**From Story 1.10 (Status: done)**

- **Service Pattern**: JSON converter service established at `app/services/json_converter.py` - follow same pattern for CSV converter - [Source: docs/stories/1-3-xml-to-json-conversion-engine.md#File-List]
- **Testing Infrastructure**: Unit test structure in `tests/unit/` established - follow same patterns - [Source: docs/stories/1-8-testing-infrastructure-and-coverage.md#File-List]
- **Error Handling**: Error handling patterns established in Epic 1 - reuse same approach - [Source: docs/stories/1-5-error-handling-and-structured-error-responses.md#File-List]
- **XML Parser**: XML parsing service available at `app/services/xml_parser.py` - reuse for XML input - [Source: docs/stories/1-2-xml-parsing-and-validation-core.md#File-List]

**From Epic 1 Completion:**

- **Service Architecture**: Services in `app/services/` directory with clear separation - follow same pattern - [Source: docs/architecture.md#Project-Structure]
- **Test Coverage**: Target > 80% coverage for core conversion logic - [Source: docs/testing-strategy.md#Coverage-Target]
- **Error Patterns**: Custom exceptions in `app/exceptions.py` - use if needed - [Source: docs/stories/1-5-error-handling-and-structured-error-responses.md#File-List]

**Files to Reference:**

- `app/services/json_converter.py` - Conversion service pattern (EXISTS, reference)
- `app/services/xml_parser.py` - XML parsing service (EXISTS, reuse)
- `app/exceptions.py` - Custom exceptions (EXISTS, use if needed)
- `tests/unit/test_json_converter.py` - Test patterns (EXISTS, reference)

### Project Structure Notes

- **Directory Structure**: Match exactly as defined in Architecture document - [Source: docs/architecture.md#Project-Structure]
  - `app/services/csv_converter.py` - CSV conversion service (NEW)
  - `tests/unit/test_csv_converter.py` - Unit tests (NEW)
- **Reuse Existing Components**: XML parser, error handling, test infrastructure from Epic 1
- **No Conflicts Detected**: Structure aligns perfectly with Architecture specifications

### Testing Standards

- Unit tests in `tests/unit/test_csv_converter.py` - [Source: docs/testing-strategy.md#Test-Structure]
- Use test fixtures from `tests/data/` directory - [Source: docs/testing-strategy.md#Test-Fixtures]
- Target > 80% coverage for csv_converter.py - [Source: docs/testing-strategy.md#Coverage-Target]
- Test flat structures, nested structures, namespaces, RFC 4180 compliance
- Follow Arrange-Act-Assert pattern - [Source: docs/testing-strategy.md#Best-Practices]

## Change Log

- 2025-10-31: Story drafted by SM agent - Initial story creation from epics and architecture
- 2025-10-31: Story context generated by SM agent - Technical context XML created
- 2025-10-31: Story implemented by DEV agent - All tasks completed, ready for review
  - Created `app/services/csv_converter.py` with XML-to-CSV conversion service
  - Created `tests/unit/test_csv_converter.py` with 20 comprehensive unit tests
  - Added test for complex XML file (example-complex.xml) with multiple namespaces
  - Test coverage: 94% (exceeds 80% target)
  - All acceptance criteria satisfied

### References

- **Epic Breakdown**: [docs/epics.md#Story-2.1] - Story 2.1 acceptance criteria and user story
- **Architecture**: [docs/architecture.md#Project-Structure] - Project structure and service locations
- **Architecture**: [docs/architecture.md#Decision-Summary] - Technology stack decisions (csv stdlib, lxml for XML)
- **Testing Strategy**: [docs/testing-strategy.md] - Testing patterns and coverage targets
- **Previous Story**: [docs/stories/1-3-xml-to-json-conversion-engine.md] - JSON converter pattern reference
- **Previous Story**: [docs/stories/1-2-xml-parsing-and-validation-core.md] - XML parser service
- **Previous Story**: [docs/stories/1-5-error-handling-and-structured-error-responses.md] - Error handling patterns

## Dev Agent Record

### Context Reference

- `docs/stories/2-1-xml-to-csv-conversion-engine.context.xml`

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

**Implementation Approach:**

- Created CSV converter service following JSON converter pattern with `convert_xml_to_csv(xml_root: etree._Element) -> str` signature
- Implemented flattening strategy:

  - **Flat structures**: Root with multiple children of same name → each child becomes a CSV row
  - **Nested structures**: Single path → flattened into one row with underscore-separated column names (e.g., "level1_level2_level3")
  - **Attributes**: Become columns directly, namespaces included in column names as "prefix:name"
  - **Child elements**: Text content becomes column values, nested children flattened with path prefixes

- Used Python `csv` module with `QUOTE_MINIMAL` for RFC 4180 compliance (automatic quoting/escaping)
- Namespace handling: Extracts namespace prefix from lxml element and includes in column names (e.g., "ex:child" or "child" for default namespace)
- Error handling: Reuses `XMLValidationError` from `xml_parser` service, consistent with JSON converter pattern
- Wrapper function: `convert_xml_string_to_csv()` provided for convenience (parses XML then converts)

**Test Coverage:**

- 20 comprehensive unit tests covering all acceptance criteria
- Test coverage: 94% (exceeds 80% target)
- Added test for complex XML file (example-complex.xml) with multiple namespaces and deeply nested structures
- All tests pass: flat structures, nested structures, namespaces, RFC 4180 compliance, edge cases, complex XML, error handling
- No regressions: All 154 existing tests continue to pass

**Key Implementation Details:**

- `_flatten_element()`: Main flattening logic that detects flat vs nested structures
- `_collect_row_data()`: Helper function that recursively collects element data into row dictionary
- `_extract_local_name_and_prefix()`: Extracts element/attribute names and namespace prefixes
- `_build_column_name()`: Constructs CSV column names with namespace and path prefixes

### File List

**New Files:**

- `app/services/csv_converter.py` - XML-to-CSV conversion service (NEW)
- `tests/unit/test_csv_converter.py` - Comprehensive unit tests for CSV converter (NEW)

**Modified Files:**

- None (no existing files modified)
