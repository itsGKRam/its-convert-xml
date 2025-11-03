# XPath Guide for XML-to-CSV Conversion

## What is XPath?

XPath is a query language for selecting elements from XML documents. **You don't need to specify the full path** - XPath searches the entire document to find matching elements.

## Key XPath Patterns

### 1. `//element` - Find elements anywhere (most common)

This finds **ALL elements** with that name, no matter where they are in the XML tree.

**Example for your `example-complex.xml`:**

```xml
<env:Envelope>
  <env:Body>
    <wd:Get_Job_Requisitions_Response>
      <wd:Response_Data>
        <wd:Job_Requisition>...</wd:Job_Requisition>  ← Array item 1
        <wd:Job_Requisition>...</wd:Job_Requisition>  ← Array item 2
        <wd:Job_Requisition>...</wd:Job_Requisition>  ← Array item 3
        ...
      </wd:Response_Data>
    </wd:Get_Job_Requisitions_Response>
  </env:Body>
</env:Envelope>
```

**XPath:** `//wd:Job_Requisition`

**What it does:** Finds ALL `<wd:Job_Requisition>` elements anywhere in the document (49 items in your case)

**Result:** 49 CSV rows (one per Job_Requisition)

### 2. `/path/to/element` - Exact path (if you want to be specific)

This only finds elements at the **exact path** from root.

**Example:**

```xml
<root>
  <items>
    <item id="1">Item 1</item>
    <item id="2">Item 2</item>
  </items>
  <other>
    <item id="3">Item 3</item>  ← Won't match /root/items/item
  </other>
</root>
```

**XPath:** `/root/items/item`

**What it does:** Only finds `<item>` elements directly under `/root/items/`

**Result:** 2 CSV rows (Items 1 and 2 only)

## For Your Use Case

### You want to extract array items (like Job_Requisition)

**Simple answer:** Use `//element_name` to find ALL matching elements

### Example 1: Simple Array

```xml
<root>
  <header>Metadata</header>
  <items>
    <item id="1"><name>A</name></item>
    <item id="2"><name>B</name></item>
  </items>
</root>
```

**XPath:** `//item`

**Result:**

- Finds both `<item>` elements
- Excludes `<header>` element
- Returns 2 CSV rows

### Example 2: Your Workday XML

```xml
<env:Envelope>
  <env:Body>
    <wd:Get_Job_Requisitions_Response>
      <wd:Response_Filter>...</wd:Response_Filter>  ← Header/metadata
      <wd:Response_Group>...</wd:Response_Group>    ← Header/metadata
      <wd:Response_Results>...</wd:Response_Results> ← Header/metadata
      <wd:Response_Data>
        <wd:Job_Requisition>...</wd:Job_Requisition>
        <wd:Job_Requisition>...</wd:Job_Requisition>
        ... (49 total)
      </wd:Response_Data>
    </wd:Get_Job_Requisitions_Response>
  </env:Body>
</env:Envelope>
```

**XPath:** `//wd:Job_Requisition`

**With Namespace:** `{"wd": "urn:com.workday/bsvc"}`

**What happens:**

1. XPath searches the entire XML document
2. Finds ALL `<wd:Job_Requisition>` elements (49 of them)
3. Each one becomes a CSV row
4. Header/metadata (`Response_Filter`, `Response_Group`, etc.) are **ignored**

**Result:** 49 CSV rows (only the array items, no headers)

## Common XPath Patterns

### Find all elements with a specific name

```xpath
//item              ← All <item> elements anywhere
//wd:Job_Requisition ← All <wd:Job_Requisition> elements (with namespace)
```

### Find elements at a specific path

```xpath
/root/items/item    ← Only <item> under /root/items/
```

### Find elements with attributes

```xpath
//item[@id]         ← All <item> elements that have an "id" attribute
//item[@id='1']     ← All <item> elements where id='1'
```

### Find elements by position

```xpath
//item[1]           ← First <item> element
//item[last()]      ← Last <item> element
```

## Why Namespaces Are Required

### The Problem with Prefixed Elements

When XML uses prefixes like `wd:` or `env:`, those are just **shortcuts/labels**. The actual element is identified by:

- **Namespace URI** (e.g., `"urn:com.workday/bsvc"`)
- **Local name** (e.g., `"Job_Requisition"`)

**Example from your XML:**

```xml
<wd:Job_Requisition xmlns:wd="urn:com.workday/bsvc">
  ...
</wd:Job_Requisition>
```

- `wd:` is just a **label/shorthand**
- The **real** element = namespace `"urn:com.workday/bsvc"` + name `"Job_Requisition"`

### Why XPath Needs Namespace Mapping

XPath doesn't automatically know what `wd:` means. You must tell it:

```json
{ "wd": "urn:com.workday/bsvc" }
```

This says: _"When you see 'wd:' in my XPath, it means namespace 'urn:com.workday/bsvc'"_

### What Happens Without Namespace?

**XPath:** `//wd:Job_Requisition`  
**Namespace:** Not provided

**Result:** ❌ **ERROR** - `"wd" prefix not defined`

**XPath:** `//Job_Requisition`  
**Namespace:** Not needed (no prefix)

**Result:** ❌ **NOTHING FOUND** - Because your element is `<wd:Job_Requisition>` not `<Job_Requisition>`

### What Happens With Namespace?

**XPath:** `//wd:Job_Requisition`  
**Namespace:** `{"wd": "urn:com.workday/bsvc"}`

**Result:** ✅ **Finds all elements** where:

- Namespace = `"urn:com.workday/bsvc"`
- Local name = `"Job_Requisition"`

### When Do You Need Namespaces?

| XML Element                                    | XPath                  | Namespace Needed?         |
| ---------------------------------------------- | ---------------------- | ------------------------- |
| `<item>...</item>`                             | `//item`               | ❌ No (no prefix)         |
| `<wd:Job_Requisition>...</wd:Job_Requisition>` | `//wd:Job_Requisition` | ✅ Yes (has `wd:` prefix) |
| `<root:Item xmlns:root="...">`                 | `//root:Item`          | ✅ Yes (has prefix)       |

## How XPath Works in This API

1. **You provide XPath** → e.g., `//wd:Job_Requisition`
2. **You provide namespaces** (if XPath uses prefixes) → e.g., `{"wd": "urn:com.workday/bsvc"}`
3. **API maps prefixes** → `wd:` → `urn:com.workday/bsvc`
4. **API finds all matching elements** → Searches entire XML
5. **Each match = 1 CSV row** → 49 matches = 49 rows
6. **Headers/metadata are automatically excluded** → Only matched elements appear

## Answer to Your Question

**"Do I need to pass where the array has started in XPath?"**

**NO!** You don't need to specify the path. Just use `//element_name`:

- ✅ **Correct:** `//wd:Job_Requisition` (finds all of them automatically)
- ❌ **Not needed:** `/env:Envelope/env:Body/wd:Get_Job_Requisitions_Response/wd:Response_Data/wd:Job_Requisition`

The `//` means "search everywhere" - XPath will find all matching elements regardless of their position in the XML tree.

## Quick Reference for Your XML

```bash
# For example-complex.xml
curl -X POST "http://localhost:5000/convert/xml-to-csv-xpath?xpath=//wd:Job_Requisition&namespaces=%7B%22wd%22%3A%22urn%3Acom.workday/bsvc%22%7D" \
  -H "Content-Type: application/xml" \
  --data-binary @tests/data/example-complex.xml
```

**XPath:** `//wd:Job_Requisition`

- Finds: All Job_Requisition elements (49 items)
- Excludes: Response_Filter, Response_Group, Response_Results (headers)
- Result: 49 clean CSV rows

## Advanced XPath Patterns for Attributes

### Selecting Elements with Attribute Filters

You can use XPath predicates to select elements based on attribute values:

**Example for IDs:**

```xpath
//wd:Job_Requisition/wd:Job_Requisition_Data/wd:Hiring_Requirement_Data/wd:Job_Profile_Reference/wd:ID[@wd:type='Job_Profile_ID']
```

This selects only `<wd:ID>` elements where the `wd:type` attribute equals `'Job_Profile_ID'`.

**Result:** CSV will contain the filtered ID values with proper column headers.

### Selecting Attribute Values Directly

You can extract attribute values directly using `@attribute_name`:

**Example for Descriptors:**

```xpath
//wd:Job_Requisition/wd:Job_Requisition_Data/wd:Hiring_Requirement_Data/wd:Job_Profile_Reference/@wd:Descriptor
```

This selects the `wd:Descriptor` attribute value directly.

**Result:** CSV with a single column named `value` containing the attribute values.

## Column Ordering

Columns appear in **document order** (order of first appearance in XML), not alphabetical:

- ✅ **Document order**: `item/name, item/value, item/category` (1, 2, 3...)
- ❌ **Old behavior**: `item/category, item/name, item/value` (alphabetical: 2, 3, 1)

Columns are ordered based on when they first appear in the XML structure.

## Tips

1. **Use `//` for arrays** - It's the easiest and most flexible
2. **Namespace is required** - If your XML uses prefixes like `wd:`, provide the namespace mapping
3. **One element = One row** - Each matched element becomes exactly one CSV row
4. **Headers auto-excluded** - XPath only matches what you specify, so headers won't appear
5. **Attribute XPaths** - Use `@attribute_name` to extract attribute values directly
6. **Attribute filters** - Use `[@attr='value']` to filter elements by attribute values
