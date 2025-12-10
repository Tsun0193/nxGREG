# Database Entity Extraction Instruction: Contract List Module - Entities Only

## Role & Context
You are a professional database schema analyst and knowledge graph expert specializing in database documentation analysis for contract management systems.

**Project Goal:** Build a comprehensive knowledge graph RAG system for a contract management system by extracting database entities (tables, SQL queries) from SQL documentation.

**Current Task:** Extract all database-related entities including tables and SQL queries from the contract-list module's function documentation to create a structured JSON output for the knowledge graph.

---

## Input Specification

### Source Directory
**Path:** `ctc-data-en/contract-list/functions/`

**Structure:**
```
ctc-data-en/contract-list/functions/
├── init-screen/
│   ├── function-overview-en.md
│   ├── sequence-diagram-en.md
│   └── sql-queries-en.md
└── delete-contract/
    ├── function-overview-en.md
    ├── sequence-diagram-en.md
    ├── sql-queries-en.md
    └── sql-statements-en.md
```

**Primary SQL Documentation Files:**
- `sql-queries-en.md` - Summary tables of SQL queries with DAO classes and purposes
- `sql-statements-en.md` - Full SQL statement definitions with table structures

**Module Context:**
- **Parent Module:** `contract-list`
- **Functions:** `init-screen`, `delete-contract`

---

## Database Naming Conventions

### Table Prefixes

| Prefix | Type | Description | Examples |
|--------|------|-------------|----------|
| **M_** | Master | Static/reference data tables | `m_user`, `m_jigyousyo`, `m_syutoku_kbn` |
| **T_** | Transaction | Business transaction data tables | `t_anken`, `t_keiyaku`, `t_kouji` |
| **V_** | View | Database views (read-only) | `v_m_anken_bunrui`, `v_m_syutoku_keitai` |
| **S_** | Sequence | Sequence generators | `s_keiyaku_no` |
| **IDX_** | Index | Database indexes | `idx_keiyaku_anken_no` |

### Column Naming Patterns

| Suffix | Type | Description | Examples |
|--------|------|-------------|----------|
| **_kbn** | Classification | Classification/type code | `botsu_kbn`, `sakujyo_kbn`, `keiyaku_kbn_cd` |
| **_cd** | Code | Code value | `anken_bunrui_cd`, `keiyaku_status_cd` |
| **_no** | Number | Sequential number/identifier | `anken_no`, `keiyaku_no`, `kokyaku_no` |
| **_key** | Key | Primary/foreign key | `keiyaku_key`, `kouji_key` |
| **_date** | Date | Date field | `touroku_date`, `koushin_date`, `sakujyo_date` |
| **_user_id** | User ID | User identifier | `touroku_user_id`, `koushin_user_id` |
| **_flg** | Flag | Boolean flag | `hyouji_flg`, `sakusei_kahi_flg` |
| **_name** | Name | Text name field | `anken_name`, `kokyaku_name`, `jigyousyo_name` |
| **_kana** | Kana | Japanese phonetic reading | `kokyaku_name_kana` |
| **_ryaku** | Abbreviation | Abbreviated name | `jigyousyo_name_ryaku` |

---

## Output Specification

### Format
Output must be a valid JSON file containing one top-level array: `entities`.

### JSON Structure
The format is Neo4j-compatible with flattened properties (no nested `properties` or `metadata` layers):

```json
{
  "entities": [
    {
      "id": "<type>:<unique_name>",
      "type": "<entity_type>",
      "name": "<human_readable_name>",
      "parent_module": "module:contract-list",
      "source_file": "<relative_path_to_source_file>",
      "<property_name>": "<property_value>"
    }
  ]
}
```

---

## Entity Taxonomy

### 1. Database Table Entities

#### Type ID: `database_table`

**Flat Properties (Neo4j compatible):**
- `table_name`: Full table name (e.g., `t_keiyaku`, `m_user`)
- `table_type`: One of `master`, `transaction`, `view`
- `description`: Purpose/description of the table
- `primary_key`: Primary key column(s) as stringified JSON array (e.g., `"[\"keiyaku_key\"]"` as a string)
- `key_columns`: List of key columns used in joins as stringified JSON array (e.g., `"[\"keiyaku_key\", \"anken_no\"]"` as a string)
- `source_file`: Path to source documentation file

**Example:**
```json
{
  "id": "database_table:t_keiyaku",
  "type": "database_table",
  "name": "Contract Table",
  "parent_module": "module:contract-list",
  "table_name": "t_keiyaku",
  "table_type": "transaction",
  "description": "Main contract transaction table storing contract information",
  "primary_key": "[\"keiyaku_key\"]",
  "key_columns": "[\"keiyaku_key\", \"anken_no\", \"keiyaku_no\"]",
  "source_file": "ctc-data-en/contract-list/functions/delete-contract/sql-statements-en.md"
}
```

**Extraction Rules:**
- Extract table names from FROM clauses and JOIN statements
- Identify table type from prefix (T_, M_, V_)
- Extract primary keys from WHERE clauses with `=` conditions and convert to stringified JSON
- Extract key columns used in JOIN conditions and convert to stringified JSON
- Include all tables referenced in SQL queries, even if from other modules
- **KEEP full table name with prefix in entity ID** (e.g., `t_keiyaku` → ID: `database_table:t_keiyaku`, `v_m_kokyaku_kbn` → ID: `database_table:v_m_kokyaku_kbn`)
  - This ensures consistency between entity IDs and relationship target references in Neo4j
  - The full table name including prefix must be preserved in the ID for proper graph linking
- **Do NOT include** function information in database table entities (this is reflected in relationships)

---

### 2. SQL Query Entities

#### Type ID: `sql_query`

**Flat Properties (Neo4j compatible):**
- `query_name`: SQL identifier (e.g., `ANKEN_SQL_03`, `KEIYAKU_SQL_04`)
- `query_type`: One of `SELECT`, `INSERT`, `UPDATE`, `DELETE`
- `operation_type`: One of `read`, `write`, `delete`, `soft_delete`
- `source_file`: Path to source documentation file

**Note:** The `name` field already serves as the purpose description, so the `purpose` field is removed. The function that uses this query is captured in relationships, not in the entity itself.

**Example:**
```json
{
  "id": "sql_query:anken_sql_03",
  "type": "sql_query",
  "name": "Retrieve contract business information",
  "parent_module": "module:contract-list",
  "query_name": "ANKEN_SQL_03",
  "query_type": "SELECT",
  "operation_type": "read",
  "source_file": "ctc-data-en/contract-list/functions/delete-contract/sql-queries-en.md"
}
```

**Extraction Rules:**
- Extract from sql-queries-en.md summary tables
- Query type from SQL statement (SELECT/INSERT/UPDATE/DELETE)
- For UPDATE with `sakujyo_kbn` or `botsu_kbn` → operation_type = `soft_delete`
- For DELETE → operation_type = `delete`
- For UPDATE (other) → operation_type = `write`
- For SELECT → operation_type = `read`
- For INSERT → operation_type = `write`
- **Do NOT include** function information in SQL query entities (this is reflected in relationships)
- **Do NOT include** purpose field (the `name` field already describes the purpose)

---

## Extraction Workflow

### Step 1: Read SQL Query Summary
Read `sql-queries-en.md` to extract:
- SQL query names
- Query purposes
- DAO classes and methods

### Step 2: Read SQL Statements
Read `sql-statements-en.md` (or infer from queries) to extract:
- Full SQL statements
- Table names from FROM/JOIN clauses
- Join relationships from WHERE clauses
- Key columns used in joins

### Step 3: Analyze Table Types
For each table found:
- Identify prefix (T_, M_, V_)
- Classify as transaction/master/view
- Extract primary key columns from WHERE clauses
- Extract key columns used in JOIN conditions

### Step 4: Create Entities
- Create database_table entities for all tables found
- Create sql_query entities for all queries found
- Flatten all properties to top level (Neo4j compatibility)
- Include source_file as a top-level field
- Convert primary_key and key_columns to stringified JSON arrays (as strings)
- Remove table prefixes (t_, m_, v_) from entity IDs
- For database tables: remove function field if present
- For SQL queries: remove function and purpose fields

### Step 5: Validate Output
- Ensure all IDs are unique
- Check that parent_module is set correctly
- Validate JSON structure
- Verify all required properties are present

---

## Special Extraction Rules

### Soft Delete Pattern
When you find UPDATE statements with `sakujyo_kbn` or `botsu_kbn`:
- Mark as `operation_type: "soft_delete"`
- These don't physically remove data

**Example:**
```sql
UPDATE t_keiyaku SET sakujyo_kbn = '1' WHERE keiyaku_key = ?
UPDATE t_keiyaku SET botsu_kbn = '1' WHERE keiyaku_key = ?
```
→ Extract as soft delete operation

---

### Hard Delete Pattern
When you find DELETE statements:
- Mark as `operation_type: "delete"`
- These physically remove data

**Example:**
```sql
DELETE FROM t_keiyaku_shijisyo_kankei WHERE keiyaku_key = ?
```
→ Extract as hard delete operation

---

### Oracle Outer Join Notation
Oracle uses `(+)` for outer joins:
- `table1.column(+) = table2.column` → Left outer join notation
- This indicates optional relationships between tables

---

### View Tables
Views (V_ prefix) should be extracted as:
- `table_type: "view"`
- They are read-only
- Often join multiple master tables

---

### Column Aliases
When columns use aliases in SELECT statements:
```sql
SELECT t_keiyaku.anken_no, v_m_keiyaku_status.name AS keiyaku_status_name
```
- Extract both the original column (`name`) and note the alias in description
- The column belongs to the source table (`v_m_keiyaku_status`)

---

## Output Requirements

### File Naming
- **Output file:** `json/contract-list-database-entities.json`

### Completeness Checklist
- ✅ All tables from all SQL queries extracted
- ✅ All SQL queries documented
- ✅ All entity IDs are unique and follow format
- ✅ All entities have parent_module set to "module:contract-list"
- ✅ All entities have source_file as top-level field (flattened)
- ✅ All primary_key and key_columns are stringified JSON arrays (as strings)
- ✅ All entity IDs use full table names with prefixes (e.g., `database_table:t_keiyaku`, `database_table:v_m_kokyaku_kbn`)
- ✅ All properties are at top level (no nested properties/metadata layers)
- ✅ SQL query entities do NOT include function or purpose fields
- ✅ Database table entities do NOT include function fields

### Quality Standards
1. **Accuracy:** Table names must match exactly
2. **Completeness:** Extract ALL tables, even from master/view tables
3. **Consistency:** Use consistent naming for entity IDs (lowercase with underscores, including table prefixes)
4. **Traceability:** Every entity must have source_file as top-level field (Neo4j compatible)
5. **JSON Formatting:** Primary keys and key columns must be stringified JSON arrays (as string type, not nested objects)
6. **Full Table Names in IDs:** Entity IDs must include the complete table name with prefix (e.g., `database_table:t_keiyaku`, `database_table:v_m_kokyaku_kbn`, not stripped versions)
  - This ensures relationships in Neo4j correctly link entities by matching IDs
  - Relationships reference the full table name, so entity IDs must match exactly
7. **Table Classification:** Accurately identify table types from prefixes
8. **Flat Structure:** All properties must be at top level for Neo4j compatibility (no nested properties/metadata layers)
9. **Field Removal:** SQL queries exclude function and purpose; Database tables exclude function

---

## Example Output Structure

Neo4j-compatible format with flattened properties:

```json
{
  "entities": [
    {
      "id": "database_table:anken",
      "type": "database_table",
      "name": "Project Table",
      "parent_module": "module:contract-list",
      "table_name": "t_anken",
      "table_type": "transaction",
      "description": "Main project table storing project information",
      "primary_key": "[\"anken_no\"]",
      "key_columns": "[\"anken_no\"]",
      "source_file": "ctc-data-en/contract-list/functions/delete-contract/sql-statements-en.md"
    },
    {
      "id": "sql_query:syounin_user_sql_01",
      "type": "sql_query",
      "name": "Get user permissions by userId",
      "parent_module": "module:contract-list",
      "query_name": "SYOUNIN_USER_SQL_01",
      "query_type": "SELECT",
      "operation_type": "read",
      "source_file": "ctc-data-en/contract-list/functions/init-screen/sql-queries-en.md"
    },
    {
      "id": "sql_query:keiyaku_dao_update",
      "type": "sql_query",
      "name": "Soft deletion of contract",
      "parent_module": "module:contract-list",
      "query_name": "KEIYAKU_DAO_UPDATE",
      "query_type": "UPDATE",
      "operation_type": "soft_delete",
      "source_file": "ctc-data-en/contract-list/functions/delete-contract/sql-statements-en.md"
    }
  ]
}
```

---

## Notes and Considerations

### Multi-Function Coverage
- Extract from **both** `init-screen` and `delete-contract` functions
- Mark each entity with the function it appears in
- If a table appears in multiple functions, create one entity and list all functions in metadata

### View Expansion
- Views (V_) often aggregate multiple tables
- Extract the view itself, but don't try to expand its internal structure
- Note which queries use views

### Handling Multiple Functions
- If the same table appears in both init-screen and delete-contract:
  - Create only ONE table entity
  - Include all relevant source files in a single metadata.source_file field (comma-separated if needed)

---

## Success Criteria

A successful extraction should:
1. ✅ Capture all database tables accessed in the functions
2. ✅ Map all SQL queries with their purposes
3. ✅ Distinguish between soft delete and hard delete operations
4. ✅ Provide complete traceability through metadata
5. ✅ Generate valid JSON that can be loaded into a knowledge graph
6. ✅ Include accurate table types and key column identification

The output will serve as the foundation for:
- Understanding data schema and structure
- Identifying database entities
- Supporting query analysis
- Building automated documentation
- Enabling semantic search over database operations
