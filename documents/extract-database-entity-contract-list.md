# Database Entity Extraction Instruction: Contract List Module

## Role & Context
You are a professional database schema analyst and knowledge graph expert specializing in database documentation analysis for contract management systems.

**Project Goal:** Build a comprehensive knowledge graph RAG system for a contract management system by extracting database entities (tables, columns, relationships, queries) from SQL documentation.

**Current Task:** Extract all database-related entities including tables, columns, SQL queries, and their relationships from the contract-list module's function documentation to create a structured JSON output for the knowledge graph.

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
Output must be a valid JSON file containing two top-level arrays: `entities` and `relationships`.

### JSON Structure
```json
{
  "entities": [
    {
      "id": "<type>:<unique_name>",
      "type": "<entity_type>",
      "name": "<human_readable_name>",
      "parent_module": "module:contract-list",
      "properties": {
        "<property_name>": "<property_value>"
      },
      "metadata": {
        "source_file": "<relative_path_to_source_file>",
        "function": "<function_name>"
      }
    }
  ],
  "relationships": [
    {
      "source": "<source_entity_id>",
      "target": "<target_entity_id>",
      "relationship_type": "<relationship_type>",
      "properties": {
        "<property_name>": "<property_value>"
      },
      "metadata": {
        "source_file": "<relative_path_to_source_file>"
      }
    }
  ]
}
```

---

## Entity Taxonomy

### 1. Database Table Entities

#### Type ID: `database_table`

**Note:** Database columns are included as properties within the table entity rather than as separate entities.

**Properties:**
- `table_name`: Full table name (e.g., `t_keiyaku`, `m_user`)
- `table_type`: One of `master`, `transaction`, `view`
- `table_prefix`: Prefix part (e.g., `T_`, `M_`, `V_`)
- `description`: Purpose/description of the table
- `primary_key`: Primary key column(s) as array
- `key_columns`: List of key columns used in joins
- `columns`: Array of column objects, each containing:
  - `column_name`: Full column name
  - `data_type`: Inferred data type (string, number, date, flag)
  - `column_category`: Category based on suffix (kbn, cd, no, key, date, user_id, flg, name)
  - `description`: Purpose of the column
  - `is_key`: Whether column is part of a key
  - `is_nullable`: Whether column allows NULL (from `(+)` notation)

**Example:**
```json
{
  "id": "database_table:t_keiyaku",
  "type": "database_table",
  "name": "Contract Table",
  "parent_module": "module:contract-list",
  "properties": {
    "table_name": "t_keiyaku",
    "table_type": "transaction",
    "table_prefix": "T_",
    "description": "Main contract transaction table storing contract information",
    "primary_key": ["keiyaku_key"],
    "key_columns": ["keiyaku_key", "anken_no", "keiyaku_no"],
    "columns": [
      {
        "column_name": "keiyaku_key",
        "data_type": "string",
        "column_category": "key",
        "description": "Primary key for contract",
        "is_key": true,
        "is_nullable": false
      },
      {
        "column_name": "anken_no",
        "data_type": "string",
        "column_category": "no",
        "description": "Project number",
        "is_key": false,
        "is_nullable": false
      }
    ]
  },
  "metadata": {
    "source_file": "ctc-data-en/contract-list/functions/delete-contract/sql-statements-en.md",
  }
}
```

**Extraction Rules:**
- Extract table names from FROM clauses and JOIN statements
- Identify table type from prefix (T_, M_, V_)
- Extract primary keys from WHERE clauses with `=` conditions
- Include all tables referenced in SQL queries, even if from other modules
- Extract all columns from SELECT clauses and include in the columns array
- Infer data type from column suffix and usage:
  - `_date` → date
  - `_kbn`, `_flg` → flag/boolean
  - `_cd`, `_no` → string/code
  - `_key` → string (key)
  - `_name` → string
  - `_kingaku`, `_genka`, `_yosan` → number (currency)
- Mark columns with `(+)` as nullable (outer join notation)
- Categorize columns by suffix according to Column Naming Patterns table

---

### 2. SQL Query Entities

#### Type ID: `sql_query`

**Properties:**
- `query_name`: SQL identifier (e.g., `ANKEN_SQL_03`, `KEIYAKU_SQL_04`)
- `query_type`: One of `SELECT`, `INSERT`, `UPDATE`, `DELETE`
- `purpose`: Description of what the query does
- `operation_type`: One of `read`, `write`, `delete`, `soft_delete`

**Example:**
```json
{
  "id": "sql_query:anken_sql_03",
  "type": "sql_query",
  "name": "Retrieve contract business information",
  "parent_module": "module:contract-list",
  "properties": {
    "query_name": "ANKEN_SQL_03",
    "query_type": "SELECT",
    "purpose": "Retrieve contract business information (specified by ankenNo)",
    "operation_type": "read"
  },
  "metadata": {
    "source_file": "ctc-data-en/contract-list/functions/delete-contract/sql-statements-en.md",
  }
}
```

**Extraction Rules:**
- Extract from sql-queries-en.md summary tables
- Query type from SQL statement (SELECT/INSERT/UPDATE/DELETE)
- For UPDATE with `sakujyo_kbn` → operation_type = `soft_delete`
- For DELETE → operation_type = `delete`
- For UPDATE (other) → operation_type = `write`
- For SELECT → operation_type = `read`

---

**Note on DAO Classes:**
DAO class entities already exist in `json/contract-list-component-entities_v2.json`. Do not extract them again - only use existing DAO entity IDs (e.g., `dao:keiyaku_shijisyo_kankei_find_dao`) when creating relationships.

**Note on Functions:**
Function entities already exist with IDs:
- `function:list_initialization` (init-screen)
- `function:contract_deletion` (delete-contract)

Do not extract them again - only use these existing function entity IDs when creating relationships.


## Relationship Taxonomy

### 1. Function-Query Relationship

**Relationship Type:** `uses_query`

**Direction:** `function` → `sql_query`


**Example:**
```json
{
  "source": "function:contract_deletion",
  "target": "sql_query:anken_sql_03",
  "relationship_type": "uses_query",
  "metadata": {
    "source_file": "ctc-data-en/contract-list/functions/delete-contract/sql-queries-en.md"
  }
}
```

**Note:** Use existing function IDs:
- `function:list_initialization` for init-screen
- `function:contract_deletion` for delete-contract

---

### 2. Query-DAO Relationship

**Relationship Type:** `executed_by`

**Direction:** `sql_query` → `dao_class`

**Properties:**
- `method_name`: DAO method used (e.g., doSelect, doUpdate, doDelete)

**Example:**
```json
{
  "source": "sql_query:anken_sql_03",
  "target": "dao:anken_find_dao",
  "relationship_type": "executed_by",
  "properties": {
    "method_name": "doSelect"
  },
  "metadata": {
    "source_file": "ctc-data-en/contract-list/functions/delete-contract/sql-queries-en.md"
  }
}
```

**Note:** Use existing DAO entity IDs from `json/contract-list-component-entities_v2.json` (format: `dao:dao_name`)

---

### 3. Query-Table Relationship

**Relationship Type:** `accesses_table`

**Direction:** `sql_query` → `database_table`

**Properties:**
- `access_type`: One of `read`, `write`, `delete`
- `table_alias`: Alias used in SQL (if any)

**Example:**
```json
{
  "source": "sql_query:anken_sql_03",
  "target": "database_table:t_anken",
  "relationship_type": "accesses_table",
  "properties": {
    "access_type": "read",
    "table_alias": null
  },
  "metadata": {
    "source_file": "ctc-data-en/contract-list/functions/delete-contract/sql-statements-en.md"
  }
}
```

---

## Extraction Workflow

### Step 1: Read SQL Query Summary
Read `sql-queries-en.md` to extract:
- SQL query names
- Query purposes
- DAO classes and methods

### Step 2: Read SQL Statements
Read `sql-statements-en.md` to extract:
- Full SQL statements
- Table names from FROM/JOIN clauses
- Column names from SELECT clauses and include them in table properties
- Join relationships from WHERE clauses
- Parameter usage from WHERE conditions

### Step 3: Analyze Table Types
For each table found:
- Identify prefix (T_, M_, V_)
- Classify as transaction/master/view
- Extract primary key columns
- Extract all columns with their properties

### Step 4: Build Relationships
- Link functions to queries using existing function IDs (uses_query)
- Link queries to DAOs using existing DAO IDs (executed_by)
- Link queries to tables (accesses_table)

### Step 5: Validate Output
- Ensure all IDs are unique
- Verify all relationship sources and targets exist
- Check that parent_module is set correctly
- Validate JSON structure

---

## Special Extraction Rules

### Soft Delete Pattern
When you find UPDATE statements with `sakujyo_kbn`:
- Mark as `operation_type: "soft_delete"`
- These don't physically remove data

**Example:**
```sql
UPDATE t_keiyaku SET sakujyo_kbn = '1' WHERE keiyaku_key = ?
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
- `table1.column(+) = table2.column` → Left outer join from table2 to table1
- Mark relationship as `join_type: "left_outer"`

---

### View Tables
Views (V_ prefix) should be extracted as:
- `table_type: "view"`
- They are read-only
- Often join multiple master tables

---

## Output Requirements

### File Naming
- **Output file:** `json/contract-list-database-entities.json`

### Completeness Checklist
- ✅ All tables from all SQL queries extracted with columns included
- ✅ All columns from SELECT clauses included in table properties
- ✅ All SQL queries documented
- ✅ Function-to-query relationships established
- ✅ Query-to-DAO relationships established
- ✅ Query-to-table relationships established
- ✅ All entity IDs are unique and follow format
- ✅ All relationships reference valid entity IDs

### Quality Standards
1. **Accuracy:** Column names, table names must match exactly
2. **Completeness:** Extract ALL tables with ALL columns included as properties, even from master/view tables
3. **Consistency:** Use consistent naming for entity IDs
4. **Traceability:** Every entity must have source_file and function in metadata
5. **Relationships:** Only include the 3 relationship types: function→query (uses_query), query→DAO (executed_by), query→table (accesses_table)

---

## Example Output Structure

```json
{
  "entities": [
    {
      "id": "database_table:t_keiyaku",
      "type": "database_table",
      "name": "Contract Table",
      "parent_module": "module:contract-list",
      "properties": {
        "table_name": "t_keiyaku",
        "table_type": "transaction",
        "table_prefix": "T_",
        "description": "Main contract transaction table",
        "primary_key": ["keiyaku_key"],
        "key_columns": ["keiyaku_key", "anken_no"],
        "columns": [
          {
            "column_name": "keiyaku_key",
            "data_type": "string",
            "column_category": "key",
            "description": "Primary key for contract",
            "is_key": true,
            "is_nullable": false
          },
          {
            "column_name": "anken_no",
            "data_type": "string",
            "column_category": "no",
            "description": "Project number",
            "is_key": false,
            "is_nullable": false
          }
        ]
      },
      "metadata": {
        "source_file": "ctc-data-en/contract-list/functions/delete-contract/sql-statements-en.md",
        "function": "delete-contract"
      }
    },
    {
      "id": "sql_query:keiyaku_sql_04",
      "type": "sql_query",
      "name": "Retrieve contract information",
      "parent_module": "module:contract-list",
      "properties": {
        "query_name": "KEIYAKU_SQL_04",
        "query_type": "SELECT",
        "purpose": "Retrieve contract information (specified by ankenNo/keiyakuKey)",
        "operation_type": "read"
      },
      "metadata": {
        "source_file": "ctc-data-en/contract-list/functions/delete-contract/sql-queries-en.md",
        "function": "delete-contract"
      }
    }
  ],
  "relationships": [
    {
      "source": "function:contract_deletion",
      "target": "sql_query:keiyaku_sql_04",
      "relationship_type": "uses_query",
      "metadata": {
        "source_file": "ctc-data-en/contract-list/functions/delete-contract/sql-queries-en.md"
      }
    },
    {
      "source": "sql_query:keiyaku_sql_04",
      "target": "dao:keiyaku_find_dao",
      "relationship_type": "executed_by",
      "properties": {
        "method_name": "doSelect"
      },
      "metadata": {
        "source_file": "ctc-data-en/contract-list/functions/delete-contract/sql-queries-en.md"
      }
    },
    {
      "source": "sql_query:keiyaku_sql_04",
      "target": "database_table:t_keiyaku",
      "relationship_type": "accesses_table",
      "properties": {
        "access_type": "read",
        "table_alias": null
      },
      "metadata": {
        "source_file": "ctc-data-en/contract-list/functions/delete-contract/sql-statements-en.md"
      }
    }
  ]
}
```

---

## Notes and Considerations

### Multi-Function Coverage
- Extract from **both** `init-screen` and `delete-contract` functions
- Mark each entity with the function it appears in
- If an entity appears in multiple functions, list all functions

### Cross-Module Tables
- Tables referenced from other modules (housing, simple) should still be extracted
- Mark them as belonging to contract-list context even if defined elsewhere
- This captures the data access patterns of contract-list

### View Expansion
- Views (V_) often aggregate multiple tables
- Extract the view itself, but don't try to expand its internal structure
- Note which queries use views

### Comprehensive Column Extraction
- Extract ALL columns from SELECT clauses and include them in the table's columns array
- Even if there are 50+ columns, include all of them as properties of the table
- This is important for understanding the full data model
- Columns are categorized by suffix (key, classification, date, user tracking, business data)

---

## Success Criteria

A successful extraction should:
1. ✅ Capture all database tables accessed in the functions with columns as properties
2. ✅ Document all columns within their parent table properties
3. ✅ Map all SQL queries with their purposes
4. ✅ Link functions to queries, queries to DAOs, and queries to tables
5. ✅ Distinguish between soft delete and hard delete operations
6. ✅ Provide complete traceability through metadata
7. ✅ Generate valid JSON that can be loaded into a knowledge graph
8. ✅ Use only the 3 defined relationship types (uses_query, executed_by, accesses_table)

The output will serve as the foundation for:
- Understanding data flow in contract operations
- Identifying data dependencies
- Supporting query analysis and optimization
- Building automated documentation
- Enabling semantic search over database operations
