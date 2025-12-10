# Database Entity Extraction Instruction: Simple Contract Module - Complete Extraction

## Role & Context
You are a professional database schema analyst and knowledge graph expert specializing in database documentation analysis for contract management systems.

**Project Goal:** Build a comprehensive knowledge graph RAG system for a contract management system by extracting database entities (tables) and their relationships (function-table relationships) from the Simple Contract module documentation.

**Current Task:** Extract all database table entities and their relationships with functions from the simple module's function documentation to create a structured JSON output for the knowledge graph.

---

## Input Specification

### Source Directory
**Path:** `ctc-data-en/simple/yuusyou-kihon/functions/`

**Structure:**
```
ctc-data-en/simple/yuusyou-kihon/functions/
├── init-screen/
│   └── function-overview-en.md
├── register-contract/
│   └── function-overview-en.md
├── update-customer/
│   └── function-overview-en.md
└── validation-contract/
    └── function-overview-en.md
```

**Primary Documentation Files:**
- `function-overview-en.md` - Contains "Database Tables Used" section with CRUD operations

**Module Context:**
- **Parent Module:** `module:simple`
- **Functions:** `init-screen`, `register-contract`, `update-customer`, `validation-contract`

---

## Prerequisites

### Existing Function Entities

Functions are already defined in `json/simple-entities.json` with IDs:
- `function:init_screen` - Screen Initialization Feature
- `function:register_contract` - Simple Contract Registration Feature
- `function:update_customer` - Customer/Contractor Update Feature
- `function:validation_contract` - Contract Validation Feature

These function IDs will be used as sources in relationships.

---

## Database Naming Conventions

### Table Prefixes

| Prefix | Type | Description | Examples |
|--------|------|-------------|----------|
| **M_** | Master | Static/reference data tables | `m_user`, `m_eigyousyo`, `m_keiyaku_kbn` |
| **T_** | Transaction | Business transaction data tables | `t_keiyaku`, `t_anken`, `t_jyutyu` |
| **T_C_** | Transaction Change | Change/cache tables for edit mode | `t_c_keiyaku`, `t_c_jyutyu` |
| **V_** | View | Database views (read-only) | `v_m_keiyaku_status`, `v_m_anken_bunrui` |

### Column Naming Patterns

| Suffix | Type | Description | Examples |
|--------|------|-------------|----------|
| **_kbn** | Classification | Classification/type code | `keiyaku_kbn`, `sakujyo_kbn`, `main_kbn` |
| **_cd** | Code | Code value | `anken_bunrui_cd`, `keiyaku_status_cd` |
| **_no** | Number | Sequential number/identifier | `anken_no`, `keiyaku_no`, `kokyaku_no` |
| **_key** | Key | Primary/foreign key | `keiyaku_key`, `kouji_key`, `anken_no` |
| **_date** | Date | Date field | `touroku_date`, `koushin_date` |
| **_user_id** | User ID | User identifier | `touroku_user_id`, `koushin_user_id` |
| **_flg** | Flag | Boolean flag | `syounin_flg`, `sakusei_kahi_flg` |
| **_name** | Name | Text name field | `anken_name`, `kokyaku_name` |
| **_kana** | Kana | Japanese phonetic reading | `kokyaku_name_kana` |

---

## Output Specification

### Format
Output must be a valid JSON file containing two top-level arrays: `entities` and `relationships`.

### JSON Structure
The format is Neo4j-compatible with flattened properties (no nested `properties` or `metadata` layers):

```json
{
  "entities": [
    {
      "id": "<type>:<unique_name>",
      "type": "<entity_type>",
      "name": "<human_readable_name>",
      "parent_module": "module:simple",
      "source_file": "<relative_path_to_source_file>",
      "<property_name>": "<property_value>"
    }
  ],
  "relationships": [
    {
      "source": "<source_entity_id>",
      "target": "<target_entity_id>",
      "relationship_type": "<relationship_type>",
      "<property_name>": "<property_value>"
    }
  ]
}
```

---

## Entity Extraction Rules

### Database Table Entities

#### Type ID: `database_table`

**Flat Properties (Neo4j compatible):**
- `table_name`: Full table name (e.g., `t_keiyaku`, `m_user`, `t_c_keiyaku`)
- `table_type`: One of `master`, `transaction`, `transaction_change`, `view`
- `description`: Purpose/description of the table from documentation
- `source_file`: Path to source documentation file

**Example:**
```json
{
  "id": "database_table:t_keiyaku",
  "type": "database_table",
  "name": "Contract Main Table",
  "parent_module": "module:simple",
  "table_name": "t_keiyaku",
  "table_type": "transaction",
  "description": "Main contract table - Center of the system",
  "source_file": "ctc-data-en/simple/yuusyou-kihon/functions/init-screen/function-overview-en.md"
}
```

**Extraction Rules:**
1. Read the "Database Tables Used" section in each `function-overview-en.md`
2. Extract table names from the table's first column
3. Extract description from the "Description" column
4. Identify table type from prefix:
   - `t_c_*` → `transaction_change`
   - `t_*` → `transaction`
   - `m_*` → `master`
   - `v_*` → `view`
5. **KEEP full table name with prefix in entity ID** (e.g., `t_keiyaku` → ID: `database_table:t_keiyaku`)
6. If a table appears in multiple functions, create ONE entity and list the first occurrence in source_file
7. Convert table names to lowercase for entity IDs (e.g., `T_KEIYAKU` → `database_table:t_keiyaku`)

---

## Relationship Extraction Rules

### Function-Table Relationship

**Relationship Type:** `uses_table`

**Direction:** `function` → `database_table`

**Purpose:** Direct link from a function to the database tables it uses, showing which operations are performed.

**Flat Properties (Neo4j compatible):**
- `operation_type`: Comma-separated list of operations performed on the table by this function (e.g., "read", "write", "delete", "create", "create,read", "read,write,delete")

**Example:**
```json
{
  "source": "function:init_screen",
  "target": "database_table:t_keiyaku",
  "relationship_type": "uses_table",
  "operation_type": "read"
}
```

**Extraction Rules:**

1. Read the "Database Tables Used" section in `function-overview-en.md` for each function
2. This section contains a table with columns: Table Name, Description, Create, Read, Update, Delete
3. For each table row where any operation column has a mark (○, 〇, or ✓):
   - Create `uses_table` relationship from function to database_table
   - Determine `operation_type` based on marked columns:
     - Create marked → include "create" in operation_type
     - Read marked → include "read" in operation_type
     - Update marked → include "write" in operation_type
     - Delete marked → include "delete" in operation_type
   - Combine multiple operations with commas (e.g., "read,write")
4. Map table names to database_table entity IDs:
   - Convert to lowercase
   - Prefix with `database_table:`
   - Example: `t_keiyaku` → `database_table:t_keiyaku`
5. Use existing function entity IDs from `json/simple-entities.json`:
   - `function:init_screen`
   - `function:register_contract`
   - `function:update_customer`
   - `function:validation_contract`

**Operation Type Mapping:**

| Documentation Column | Operation Type Value |
|----------------------|---------------------|
| Create (marked) | `create` |
| Read (marked) | `read` |
| Update (marked) | `write` |
| Delete (marked) | `delete` |

**Example Extraction:**

From init-screen function-overview-en.md:
```
| **t_keiyaku** | Main contract table - System core | | ✓ |  | |
```

This indicates the function performs only Read operation on t_keiyaku, so create:
```json
{
  "source": "function:init_screen",
  "target": "database_table:t_keiyaku",
  "relationship_type": "uses_table",
  "operation_type": "read"
}
```

From register-contract function-overview-en.md:
```
| **t_keiyaku** | Main contract table - Center of the system | | | 〇 | |
```

This indicates the function performs only Update operation, so create:
```json
{
  "source": "function:register_contract",
  "target": "database_table:t_keiyaku",
  "relationship_type": "uses_table",
  "operation_type": "write"
}
```

From register-contract function-overview-en.md:
```
| **t_kouji** | Construction table | 〇 | | 〇 | |
```

This indicates the function performs both Create and Update operations, so create:
```json
{
  "source": "function:register_contract",
  "target": "database_table:t_kouji",
  "relationship_type": "uses_table",
  "operation_type": "create,write"
}
```

---

## Extraction Workflow

### Step 1: Prepare Function Mapping
Read `json/simple-entities.json` to get the list of function IDs:
- `function:init_screen`
- `function:register_contract`
- `function:update_customer`
- `function:validation_contract`

### Step 2: Read Function Documentation
For each function, read its `function-overview-en.md` file:
1. `ctc-data-en/simple/yuusyou-kihon/functions/init-screen/function-overview-en.md`
2. `ctc-data-en/simple/yuusyou-kihon/functions/register-contract/function-overview-en.md`
3. `ctc-data-en/simple/yuusyou-kihon/functions/update-customer/function-overview-en.md`
4. `ctc-data-en/simple/yuusyou-kihon/functions/validation-contract/function-overview-en.md`

### Step 3: Extract Database Tables
For each function's documentation:
1. Locate the "Database Tables Used" section
2. Extract each table row with columns: Table Name, Description, Create, Read, Update, Delete
3. Create database_table entity for each unique table:
   - Extract table name (remove bold formatting)
   - Extract description
   - Determine table type from prefix
   - Convert to lowercase for ID
   - Set source_file to current function-overview-en.md path

### Step 4: Create Function-Table Relationships
For each function and its tables:
1. Check which operation columns are marked (○, 〇, ✓)
2. Build operation_type string:
   - Create marked → add "create"
   - Read marked → add "read"
   - Update marked → add "write"
   - Delete marked → add "delete"
   - Join multiple operations with commas in order: create,read,write,delete
3. Create `uses_table` relationship from function to database_table

### Step 5: Deduplicate Table Entities
- If the same table appears in multiple functions, keep only ONE entity
- Use the first occurrence's source_file
- Create separate relationships for each function that uses the table

### Step 6: Validate Output
- Ensure all entity IDs are unique
- Ensure all relationship sources and targets reference valid entity IDs
- Check that parent_module is set to "module:simple" for all entities
- Verify all required properties are present
- Check for duplicate relationships

---

## Special Cases

### 1. Logical Delete Operations
When the Delete column is marked, it typically means logical deletion:
- The system sets `sakujyo_kbn = "1"` or `botsu_kbn = "1"`
- Data is not physically removed from the database
- Still map as `operation_type: "delete"` in relationships

### 2. Change/Cache Tables (T_C_ prefix)
Tables with `t_c_` prefix are change/cache tables used in edit mode:
- Example: `t_c_keiyaku`, `t_c_jyutyu`, `t_c_anken`
- Type: `transaction_change`
- These store temporary changes before formal approval

### 3. View Tables (V_ prefix)
Views are read-only and join multiple master tables:
- Example: `v_m_keiyaku_status`, `v_m_anken_bunrui`
- Type: `view`
- Always have only "read" operation_type

### 4. Master Tables (M_ prefix)
Master tables contain reference data:
- Example: `m_user`, `m_eigyousyo`, `m_keiyaku_kbn`
- Type: `master`
- Usually only have "read" operation_type in functions

### 5. Empty Operation Cells
If all operation columns (Create, Read, Update, Delete) are empty for a table:
- The table is mentioned but not directly used by this function
- Do NOT create a relationship for this table
- You may still create the entity if it's explicitly listed

### 6. Multiple Functions Using Same Table
When the same table appears in multiple functions with different operations:
- Create ONE entity for the table
- Create separate relationships for each function
- Each relationship can have different operation_type values

Example:
```json
{
  "id": "database_table:t_keiyaku",
  "type": "database_table",
  "name": "Contract Main Table",
  "parent_module": "module:simple",
  "table_name": "t_keiyaku",
  "table_type": "transaction",
  "description": "Main contract table - Center of the system",
  "source_file": "ctc-data-en/simple/yuusyou-kihon/functions/init-screen/function-overview-en.md"
}
```

Relationships:
```json
[
  {
    "source": "function:init_screen",
    "target": "database_table:t_keiyaku",
    "relationship_type": "uses_table",
    "operation_type": "read"
  },
  {
    "source": "function:register_contract",
    "target": "database_table:t_keiyaku",
    "relationship_type": "uses_table",
    "operation_type": "write"
  },
  {
    "source": "function:update_customer",
    "target": "database_table:t_keiyaku",
    "relationship_type": "uses_table",
    "operation_type": "read,write"
  }
]
```

---

## Output Requirements

### File Naming
- **Output file:** `json/simple/simple-database-complete.json`

### Completeness Checklist

**Entities:**
- ✅ All database tables from all 4 functions extracted
- ✅ All entity IDs are unique and follow format `database_table:<table_name_lowercase>`
- ✅ All entities have parent_module set to "module:simple"
- ✅ All entities have source_file as top-level field (flattened)
- ✅ All entity IDs use full table names with prefixes (e.g., `database_table:t_keiyaku`, `database_table:t_c_keiyaku`)
- ✅ All table_type values are one of: master, transaction, transaction_change, view
- ✅ All properties are at top level (no nested properties/metadata layers)
- ✅ No duplicate entities

**Relationships:**
- ✅ All function→table relationships created (uses_table)
- ✅ All relationship sources reference valid function IDs from simple-entities.json
- ✅ All relationship targets reference valid database_table IDs in entities array
- ✅ All relationship operation_type values are accurate
- ✅ All properties are flattened (no nested layers)
- ✅ No duplicate relationships (same source, target, and type)

### Quality Standards
1. **Accuracy:** Table names must match exactly (case-insensitive, but preserve original format in table_name property)
2. **Completeness:** Extract ALL tables from all 4 functions
3. **Consistency:** Use consistent naming for entity IDs (lowercase with underscores, including table prefixes)
4. **Traceability:** Every entity must have source_file as top-level field (Neo4j compatible)
5. **Full Table Names in IDs:** Entity IDs must include the complete table name with prefix (e.g., `database_table:t_keiyaku`, `database_table:t_c_keiyaku`)
6. **Flat Structure:** All properties must be at top level for Neo4j compatibility (no nested properties/metadata layers)
7. **Operation Accuracy:** operation_type must accurately reflect the marked columns in documentation

---

## Example Output Structure

Neo4j-compatible format with flattened properties:

```json
{
  "entities": [
    {
      "id": "database_table:t_keiyaku",
      "type": "database_table",
      "name": "Contract Main Table",
      "parent_module": "module:simple",
      "table_name": "t_keiyaku",
      "table_type": "transaction",
      "description": "Main contract table - System core",
      "source_file": "ctc-data-en/simple/yuusyou-kihon/functions/init-screen/function-overview-en.md"
    },
    {
      "id": "database_table:t_c_keiyaku",
      "type": "database_table",
      "name": "Contract Change Table",
      "parent_module": "module:simple",
      "table_name": "t_c_keiyaku",
      "table_type": "transaction_change",
      "description": "Contract change table",
      "source_file": "ctc-data-en/simple/yuusyou-kihon/functions/register-contract/function-overview-en.md"
    },
    {
      "id": "database_table:m_keiyaku_kbn",
      "type": "database_table",
      "name": "Contract Type Master",
      "parent_module": "module:simple",
      "table_name": "m_keiyaku_kbn",
      "table_type": "master",
      "description": "Contract type (master)",
      "source_file": "ctc-data-en/simple/yuusyou-kihon/functions/init-screen/function-overview-en.md"
    },
    {
      "id": "database_table:v_m_keiyaku_status",
      "type": "database_table",
      "name": "Contract Status View",
      "parent_module": "module:simple",
      "table_name": "v_m_keiyaku_status",
      "table_type": "view",
      "description": "Contract status (view)",
      "source_file": "ctc-data-en/simple/yuusyou-kihon/functions/init-screen/function-overview-en.md"
    },
    {
      "id": "database_table:t_anken",
      "type": "database_table",
      "name": "Case Table",
      "parent_module": "module:simple",
      "table_name": "t_anken",
      "table_type": "transaction",
      "description": "Case table linked to contract",
      "source_file": "ctc-data-en/simple/yuusyou-kihon/functions/init-screen/function-overview-en.md"
    },
    {
      "id": "database_table:t_jyutyu",
      "type": "database_table",
      "name": "Order Table",
      "parent_module": "module:simple",
      "table_name": "t_jyutyu",
      "table_type": "transaction",
      "description": "Order table linked to contract",
      "source_file": "ctc-data-en/simple/yuusyou-kihon/functions/init-screen/function-overview-en.md"
    },
    {
      "id": "database_table:t_kouji",
      "type": "database_table",
      "name": "Construction Table",
      "parent_module": "module:simple",
      "table_name": "t_kouji",
      "table_type": "transaction",
      "description": "Construction table",
      "source_file": "ctc-data-en/simple/yuusyou-kihon/functions/register-contract/function-overview-en.md"
    }
  ],
  "relationships": [
    {
      "source": "function:init_screen",
      "target": "database_table:t_keiyaku",
      "relationship_type": "uses_table",
      "operation_type": "read"
    },
    {
      "source": "function:init_screen",
      "target": "database_table:m_keiyaku_kbn",
      "relationship_type": "uses_table",
      "operation_type": "read"
    },
    {
      "source": "function:init_screen",
      "target": "database_table:v_m_keiyaku_status",
      "relationship_type": "uses_table",
      "operation_type": "read"
    },
    {
      "source": "function:init_screen",
      "target": "database_table:t_anken",
      "relationship_type": "uses_table",
      "operation_type": "read"
    },
    {
      "source": "function:register_contract",
      "target": "database_table:t_keiyaku",
      "relationship_type": "uses_table",
      "operation_type": "write"
    },
    {
      "source": "function:register_contract",
      "target": "database_table:t_c_keiyaku",
      "relationship_type": "uses_table",
      "operation_type": "write"
    },
    {
      "source": "function:register_contract",
      "target": "database_table:t_jyutyu",
      "relationship_type": "uses_table",
      "operation_type": "write"
    },
    {
      "source": "function:register_contract",
      "target": "database_table:t_kouji",
      "relationship_type": "uses_table",
      "operation_type": "create,write"
    },
    {
      "source": "function:update_customer",
      "target": "database_table:t_keiyaku",
      "relationship_type": "uses_table",
      "operation_type": "read,write"
    },
    {
      "source": "function:validation_contract",
      "target": "database_table:t_keiyaku",
      "relationship_type": "uses_table",
      "operation_type": "read,write"
    }
  ]
}
```

---

## Validation Checklist

Before finalizing the output, verify:

### 1. Entity Validation
- ✅ All entity IDs follow format `database_table:<table_name_lowercase>`
- ✅ All entity IDs include full table names with prefixes (t_, m_, v_, t_c_)
- ✅ All entities have required properties: id, type, name, parent_module, table_name, table_type, description, source_file
- ✅ All properties are at top level (no nested structures)
- ✅ No duplicate entity IDs
- ✅ All table_type values are valid (master, transaction, transaction_change, view)

### 2. Relationship Validation
- ✅ All relationship sources match existing function IDs in simple-entities.json
- ✅ All relationship targets match entity IDs in the entities array
- ✅ All relationships have required properties: source, target, relationship_type, operation_type
- ✅ All operation_type values are valid combinations of: create, read, write, delete
- ✅ No duplicate relationships (same source, target, and type)
- ✅ All properties are at top level (no nested structures)

### 3. Completeness Validation
- ✅ All tables from init-screen function extracted
- ✅ All tables from register-contract function extracted
- ✅ All tables from update-customer function extracted
- ✅ All tables from validation-contract function extracted
- ✅ Each function has relationships to all its tables

### 4. Consistency Validation
- ✅ Entity IDs use consistent lowercase format
- ✅ Table prefixes preserved in entity IDs (t_, m_, v_, t_c_)
- ✅ All source_file paths are relative and correctly formatted
- ✅ parent_module is "module:simple" for all entities

---

## Success Criteria

A successful extraction should:
1. ✅ Capture all database tables from all 4 functions (init-screen, register-contract, update-customer, validation-contract)
2. ✅ Create unique entities for each table (no duplicates)
3. ✅ Map all functions to their database tables with accurate operations
4. ✅ Include accurate table types based on prefixes
5. ✅ Provide complete traceability through source_file references
6. ✅ Generate valid Neo4j-compatible JSON with flattened structure
7. ✅ Use only the defined relationship type (uses_table)
8. ✅ Preserve full table names with prefixes in entity IDs

The output will serve as the foundation for:
- Understanding data dependencies in the Simple Contract module
- Identifying which functions access which tables
- Supporting impact analysis (which functions are affected by table changes)
- Building automated documentation
- Enabling graph-based queries over the system architecture
- Integrating with the broader contract system knowledge graph

---

## Notes and Considerations

### Module Differences from Contract-List
Unlike the contract-list module which has detailed SQL documentation (sql-queries-en.md, sql-statements-en.md), the simple module:
- Only has function-overview-en.md files
- Does NOT have separate SQL query documentation
- Tables are listed with CRUD operations in the "Database Tables Used" section
- Relationships are at the function-table level only (no query-level relationships)

### Integration with Existing Entities
The output should integrate with:
- `json/simple-entities.json` - Contains function, form, and form_field entities
- The function IDs in simple-entities.json are used as sources in relationships
- The new database entities and relationships will extend the knowledge graph

### Future Enhancements
This extraction focuses on:
- Database table entities
- Function-to-table relationships
- Operation types (create, read, write, delete)

Future enhancements could include:
- Extracting SQL queries if detailed documentation becomes available
- Adding DAO class entities and relationships
- Including column-level details if available in other documentation
- Cross-module table dependency analysis
