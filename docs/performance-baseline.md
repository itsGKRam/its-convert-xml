# Performance Baseline

**Generated:** 2025-01-27  
**Project:** its-convert-xml  
**Story:** 1.7 - Performance Optimization for Large Files

## Overview

This document establishes performance baselines for XML-to-JSON conversion across various file sizes. These baselines are used to validate that the API meets performance requirements and to track performance over time.

## Performance Targets

Based on Story 1.7 acceptance criteria:

- **Response Time Target**: < 30 seconds for 300MB files (AC3)
- **Memory Efficiency**: Memory usage stays within acceptable limits during processing (AC4)
- **Streaming Support**: Streaming/chunked processing for files > 10MB (AC1, AC2)

## Performance Characteristics

### File Size Thresholds

The system automatically selects parsing strategy based on file size:

- **Standard Parser** (`parse_xml()`): Files ≤ 10MB
  - Faster for small files due to lower overhead
  - Single-pass parsing
  
- **Streaming Parser** (`parse_xml_streaming()`): Files > 10MB
  - Memory-efficient incremental parsing using `lxml.etree.iterparse()`
  - Reduces peak memory usage during parsing process
  - Recommended for files approaching the 300MB limit

### Expected Performance by File Size

Based on testing and architecture requirements:

| File Size | Expected Response Time | Parser Used | Notes |
|-----------|------------------------|-------------|-------|
| 1MB       | < 1 second            | Standard    | Fast processing |
| 10MB      | < 3 seconds           | Standard    | Approaching threshold |
| 100MB     | < 15 seconds           | Streaming   | Large file processing |
| 300MB     | < 30 seconds          | Streaming   | Maximum file size limit |

**Note**: Actual performance will vary based on:
- System resources (CPU, memory)
- Network latency (if applicable)
- XML structure complexity
- System load

## Performance Monitoring

The API includes built-in performance monitoring that logs:

- **Processing Time**: Time taken to convert XML to JSON (seconds)
- **File Size**: Size of processed XML file (bytes)
- **Memory Usage**: Memory before/after processing (MB) - if psutil available
- **Memory Delta**: Memory difference during processing (MB)

Performance logs are emitted at INFO level with structured format:
```
Conversion successful: endpoint=/convert/xml-to-json, file_size_bytes=314572800, processing_time_seconds=25.432, status=success, memory_before_mb=150.5, memory_after_mb=450.2, memory_delta_mb=299.7
```

## Testing

Performance tests are located in `tests/performance/test_large_files.py`:

- `test_performance_1mb_file`: Validates 1MB file processing
- `test_performance_10mb_file`: Validates 10MB file processing
- `test_performance_100mb_file`: Validates 100MB file processing (marked @pytest.mark.slow)
- `test_performance_300mb_file`: Validates 300MB file processing (marked @pytest.mark.very_slow)
- `test_streaming_vs_standard_parser`: Compares parsing strategies

### Running Performance Tests

Run all performance tests:
```bash
pytest tests/performance/ -v
```

Run only fast performance tests (excludes slow/very_slow):
```bash
pytest tests/performance/ -v -m "not slow"
```

Run slow tests separately (recommended for CI/CD):
```bash
pytest tests/performance/ -v -m slow
```

## Memory Considerations

### Streaming Parser Benefits

The streaming parser (`parse_xml_streaming`) provides memory efficiency benefits:

1. **Incremental Processing**: Elements are processed as they are parsed
2. **Reduced Peak Memory**: Lower peak memory usage during tree construction
3. **Large File Support**: Enables processing of files up to 300MB limit

### Memory Usage Patterns

For large files (300MB), typical memory usage:

- **Input XML**: ~300MB in memory (request body)
- **Parsed Tree**: ~300-600MB (XML tree structure)
- **JSON Output**: ~300-600MB (converted JSON structure)
- **Peak Memory**: ~1-1.5GB during conversion

**Note**: Memory usage may vary based on XML structure complexity. Deeply nested or highly structured XML may require more memory.

## Performance Optimization Strategies

1. **Automatic Parser Selection**: System automatically uses streaming parser for files > 10MB
2. **Early Size Validation**: Request size checked before parsing (Story 1.6)
3. **Efficient Parsing**: lxml iterparse for incremental processing
4. **Memory Management**: Elements cleared after processing where possible

## Future Considerations

Potential optimizations for future stories:

- Response streaming for very large outputs
- Caching for frequently processed XML structures
- Parallel processing for independent XML elements
- Compression for input/output

## References

- **Story**: [1-7-performance-optimization-for-large-files.md](./stories/1-7-performance-optimization-for-large-files.md)
- **Architecture**: [architecture.md](./architecture.md#Performance-Considerations)
- **Epic**: [epics.md](./epics.md#Story-1.7)

