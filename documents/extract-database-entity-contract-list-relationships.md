# Database Entity Extraction Instruction: Contract List Module - Relationships Only

## Role & Context
You are a professional database schema analyst and knowledge graph expert specializing in database documentation analysis for contract management systems.

**Project Goal:** Build a comprehensive knowledge graph RAG system for a contract management system by extracting relationships between database entities (functions, queries, DAOs, tables) from SQL documentation.

**Current Task:** Extract all relationships between existing entities (functions, SQL queries, DAO classes, database tables) from the contract-list module's function documentation to create a structured JSON output for the knowledge graph.

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

## Prerequisites

### Existing Entity Files

You must have already created or have access to:

1. **Function Entities** - Already exist with IDs:
   - `function:list_initialization` (init-screen)
   - `function:contract_deletion` (delete-contract)

2. **DAO Entities** - Already exist in `json/contract-list-component-entities_v2.json`:
 

3. **SQL Query Entities** - Created from entities extraction phase:
   - Format: `sql_query:<query_name_lowercase>`
   - Examples: `sql_query:anken_sql_03`, `sql_query:keiyaku_sql_04`

4. **Database Table Entities** - Created from entities extraction phase:
   - Format: `database_table:<table_name_lowercase>`
   - Examples: `database_table:t_keiyaku`, `database_table:t_anken`

---

## Output Specification

### Format
Output must be a valid JSON file containing one top-level array: `relationships`.

### JSON Structure
The format is Neo4j-compatible with flattened properties (no nested `properties` layer):

```json
{
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

## Relationship Taxonomy

This section defines the **4 types of relationships** to extract from the database documentation:

1. **uses_query** - Function → SQL Query
2. **executed_by** - SQL Query → DAO
3. **accesses_table** - SQL Query → Database Table (detailed, per-query table access)
4. **uses_table** - Function → Database Table (high-level, function-level table usage)

---

### 1. Function-Query Relationship

**Relationship Type:** `uses_query`

**Direction:** `function` → `sql_query`

**Purpose:** Links a function to the SQL queries it executes.

**Properties:** None required

**Example:**
```json
{
  "source": "function:contract_deletion",
  "target": "sql_query:anken_sql_03",
  "relationship_type": "uses_query"
}
```

**Extraction Rules:**
- Read `sql-queries-en.md` to identify which SQL queries are used
- Map each query name to its sql_query entity ID
- Use existing function IDs:
  - `function:list_initialization` for init-screen
  - `function:contract_deletion` for delete-contract
- Create one relationship per query used by the function

---

### 2. Query-DAO Relationship

**Relationship Type:** `executed_by`

**Direction:** `sql_query` → `dao_class`

**Purpose:** Links a SQL query to the DAO class that executes it.

**Flat Properties (Neo4j compatible):**
- `method_name`: DAO method used (e.g., doSelect, doUpdate, doDelete, doSelectList)

**Example:**
```json
{
  "source": "sql_query:anken_sql_03",
  "target": "dao:anken_find_dao",
  "relationship_type": "executed_by",
  "method_name": "doSelect"
}
```

**Extraction Rules:**
- Read `sql-queries-en.md` to identify which DAO class executes each query
- Map DAO class names to existing DAO entity IDs from `json/contract-list-component-entities_v2.json`
- DAO naming pattern: `<DaoClassName>` → `dao:<dao_class_name_lowercase>`
  - `AnkenFindDAO` → `dao:anken_find_dao`
  - `KeiyakuFindDAO` → `dao:keiyaku_find_dao`
  - `KeiyakuDAO` → `dao:keiyaku_dao`
- Extract method name from the "SQL Name / Method" column:
  - `doSelect` for SELECT queries
  - `doSelectList` for SELECT queries returning lists
  - `doUpdate` for UPDATE queries
  - `doDelete` for DELETE queries
  - `doInsert` for INSERT queries
- Use existing DAO entity IDs only - do not create new DAO entities

---

### 3. Query-Table Relationship

**Relationship Type:** `accesses_table`

**Direction:** `sql_query` → `database_table`

**Purpose:** Links a SQL query to the database tables it accesses.

**Flat Properties (Neo4j compatible):**
- `access_type`: One of `read`, `write`, `delete`
- `table_alias`: Alias used in SQL (if any), otherwise null

**Example:**
```json
{
  "source": "sql_query:anken_sql_03",
  "target": "database_table:t_anken",
  "relationship_type": "accesses_table",
  "access_type": "read",
  "table_alias": null
}
```

**Extraction Rules:**
- Read `sql-statements-en.md` to identify which tables each query accesses
- Determine access_type based on SQL operation:
  - `SELECT` → `access_type: "read"`
  - `INSERT` → `access_type: "write"`
  - `UPDATE` → `access_type: "write"`
  - `DELETE` → `access_type: "delete"`
- Extract table aliases from SQL statements:
  - `FROM t_anken` → alias: null
  - `FROM t_anken anken` → alias: "anken"
  - `FROM m_eigyousyo m_eigyousyo_jyutyu` → alias: "m_eigyousyo_jyutyu"
- Create one relationship per table accessed by the query
- Include all tables from FROM clause and JOIN clauses
- **Use full table names with prefixes in target ID** (e.g., `database_table:t_anken`, `database_table:v_m_kokyaku_kbn`)
  - This ensures relationships correctly reference the entity IDs in the entities file
  - Entity IDs must match exactly for Neo4j to establish the relationships

---

### 4. Function-Table Relationship

**Relationship Type:** `uses_table`

**Direction:** `function` → `database_table`

**Purpose:** Direct link from a function to the database tables it uses, providing a high-level view of data dependencies per function. This complements the detailed query→table relationships by showing which tables are relevant to each function overall.

**Flat Properties (Neo4j compatible):**
- `operation_type`: Comma-separated list of operations performed on the table by this function (e.g., "read", "write", "delete", "read,write", "read,delete")

**Example:**
```json
{
  "source": "function:contract_deletion",
  "target": "database_table:t_keiyaku",
  "relationship_type": "uses_table",
  "operation_type": "read,write"
}
```

**Extraction Rules:**
- Read the "DB Tables Used" section in `function-overview-en.md` for each function
- This section contains a table with columns: Table Name, Description, Create, Read, Update, Delete
- For each table row where any operation column (Create, Read, Update, Delete) has a mark (○ or 〇):
  - Create `uses_table` relationship from function to database_table
  - Determine `operation_type` based on marked columns:
    - Create marked → include "create" in operation_type
    - Read marked → include "read" in operation_type
    - Update marked → include "write" in operation_type
    - Delete marked → include "delete" in operation_type
  - Combine multiple operations with commas (e.g., "read,write")
- Map table names to database_table entity IDs:
  - `t_keiyaku` → `database_table:t_keiyaku`
  - `m_user` → `database_table:m_user`
  - `v_m_keiyaku_status` → `database_table:v_m_keiyaku_status`
- Use existing function entity IDs:
  - `function:list_initialization` for init-screen
  - `function:contract_deletion` for delete-contract

**Example Extraction:**

From the table:
```
| **t_keiyaku** | Contract main | | 〇 | 〇 | |
```

This indicates the function performs Read and Update operations on t_keiyaku, so create:
```json
{
  "source": "function:contract_deletion",
  "target": "database_table:t_keiyaku",
  "relationship_type": "uses_table",
  "operation_type": "read,write"
}
```

From the table:
```
| **t_keiyaku_koutei** | Contract process | | | | 〇 |
```

This indicates the function performs only Delete operation, so create:
```json
{
  "source": "function:contract_deletion",
  "target": "database_table:t_keiyaku_koutei",
  "relationship_type": "uses_table",
  "operation_type": "delete"
}
```

**Benefits:**
- Provides quick overview of which tables a function touches
- Enables high-level impact analysis (which functions use table X?)
- Complements the detailed query-level relationships
- Simplifies graph queries for function-level data dependencies

---

## Extraction Workflow

### Step 1: Read SQL Query Summary
Read `sql-queries-en.md` for both functions to extract:
- SQL query names
- DAO classes and methods
- Query purposes

### Step 2: Create Function-Query Relationships
For each query found:
- Determine which function uses it (init-screen or delete-contract)
- Create `uses_query` relationship from function to sql_query
- Use existing function entity IDs

### Step 3: Create Query-DAO Relationships
For each query found:
- Extract DAO class name from summary table
- Map to existing DAO entity ID
- Extract method name (doSelect, doUpdate, etc.)
- Create `executed_by` relationship from sql_query to dao

### Step 4: Read SQL Statements
Read `sql-statements-en.md` to extract:
- Full SQL statements for each query
- Table names from FROM/JOIN clauses
- Table aliases

### Step 5: Create Query-Table Relationships
For each query and table combination:
- Determine access type (read/write/delete)
- Extract table alias if present
- Create `accesses_table` relationship from sql_query to database_table

### Step 6: Read Function Overview for DB Tables Used
Read `function-overview-en.md` for each function to extract:
- "DB Tables Used" section with operation columns (Create, Read, Update, Delete)
- Table names and their operation marks (○ or 〇)

### Step 7: Create Function-Table Relationships
For each function and table combination with marked operations:
- Determine operation_type from marked columns
- Create `uses_table` relationship from function to database_table
- Combine multiple operations with commas

### Step 8: Validate Output
- Ensure all source and target entity IDs exist
- Verify all required properties are present
- Check for duplicate relationships
- Validate JSON structure

---

## DAO Name Mapping Guide

### Common DAO Naming Patterns

| DAO Class Name | Entity ID |
|----------------|-----------|
| SyouninUserFindDAO | dao:syounin_user_find_dao |
| AnkenFindDAO | dao:anken_find_dao |
| KeiyakuIchiranFindDAO | dao:keiyaku_ichiran_find_dao |
| KeiyakuFindDAO | dao:keiyaku_find_dao |
| KeiyakuDAO | dao:keiyaku_dao |
| KoujiFindDAO | dao:kouji_find_dao |
| KoujiDAO | dao:kouji_dao |
| KeiyakuShijisyoKankeiFindDAO | dao:keiyaku_shijisyo_kankei_find_dao |
| KeiyakuShijisyoKankeiDAO | dao:keiyaku_shijisyo_kankei_dao |
| ChintaisyakuKeiyakuKankeiFindDAO | dao:chintaisyaku_keiyaku_kankei_find_dao |
| ChintaisyakuKeiyakuKankeiDAO | dao:chintaisyaku_keiyaku_kankei_dao |
| GijyutsuAnkenKihonFindDAO | dao:gijyutsu_anken_kihon_find_dao |
| KeiyakuKokyakuKankeiFindDAO | dao:keiyaku_kokyaku_kankei_find_dao |
| KojinTasyaKeiyakuKbnFindDAO | dao:kojin_tasya_keiyaku_kbn_find_dao |
| KojinTasyaKeiyakuKbnDAO | dao:kojin_tasya_keiyaku_kbn_dao |

**Pattern:**
- Remove "DAO" suffix
- Convert to lowercase
- Replace camelCase with snake_case
- Prefix with "dao:"

---

## Special Cases

### 1. ORMappingBean Updates
When you see entries like:
```
doUpdate (ORMappingBean) | KeiyakuDAO, KeiyakuVO | Soft deletion of contract (t_keiyaku)
```

Create relationship:
- DAO: `dao:keiyaku_dao`
- Method: `doUpdate`
- Query ID: Create a descriptive ID like `sql_query:keiyaku_dao_update`

### 2. Multiple Tables in One Query
When a query accesses multiple tables:
```sql
SELECT * FROM t_keiyaku, t_kouji WHERE ...
```

Create separate relationships:
- `sql_query:xxx` → `database_table:t_keiyaku` (access_type: read)
- `sql_query:xxx` → `database_table:t_kouji` (access_type: read)

### 3. Table Aliases
When tables have aliases:
```sql
FROM m_eigyousyo m_eigyousyo_jyutyu
```

Include the alias as a flat property:
```json
{
  "source": "sql_query:xxx",
  "target": "database_table:eigyousyo",
  "relationship_type": "accesses_table",
  "access_type": "read",
  "table_alias": "m_eigyousyo_jyutyu"
}
```

**Note:** The target uses the clean table name without prefix (`eigyousyo`), while the alias captures the actual alias used in SQL.

### 4. Views
Views are treated as tables for relationship purposes:
```sql
FROM v_m_keiyaku_status
```

Create relationship to:
- `database_table:v_m_keiyaku_status`

---

## Output Requirements

### File Naming
- **Output file:** `json/contract-list-database-relationships.json`

### Completeness Checklist
- ✅ All function→query relationships created (uses_query)
- ✅ All query→DAO relationships created (executed_by)
- ✅ All query→table relationships created (accesses_table)
- ✅ All function→table relationships created (uses_table)
- ✅ All relationship sources and targets reference valid entity IDs
- ✅ All required properties are present and flattened (no nested layers)
- ✅ No duplicate relationships
- ✅ All table references use full names with prefixes (database_table:t_keiyaku not database_table:keiyaku)

### Quality Standards
1. **Accuracy:** All entity IDs must match existing entities exactly
2. **Completeness:** Extract ALL relationships from all queries
3. **Consistency:** Use consistent relationship types (only the 3 defined types)
4. **Validation:** All source and target IDs must exist in entity files
5. **Neo4j Compatible:** All properties must be at top level (no nested properties/metadata layers)
6. **Full Table Names:** All database_table references must use full table names with prefixes (e.g., `database_table:t_keiyaku`, `database_table:v_m_kokyaku_kbn`)
  - This ensures IDs match the entity definitions exactly
  - Neo4j will use these IDs to establish graph relationships

---

## Example Output Structure

Neo4j-compatible format with flattened properties:

```json
{
  "relationships": [
    {
      "source": "function:list_initialization",
      "target": "sql_query:syounin_user_sql_01",
      "relationship_type": "uses_query"
    },
    {
      "source": "sql_query:syounin_user_sql_01",
      "target": "dao:syounin_user_find_dao",
      "relationship_type": "executed_by",
      "method_name": "doSelect"
    },
    {
      "source": "sql_query:syounin_user_sql_01",
      "target": "database_table:user",
      "relationship_type": "accesses_table",
      "access_type": "read",
      "table_alias": null
    },
    {
      "source": "function:contract_deletion",
      "target": "sql_query:keiyaku_sql_04",
      "relationship_type": "uses_query"
    },
    {
      "source": "sql_query:keiyaku_sql_04",
      "target": "dao:keiyaku_find_dao",
      "relationship_type": "executed_by",
      "method_name": "doSelect"
    },
    {
      "source": "sql_query:keiyaku_sql_04",
      "target": "database_table:keiyaku",
      "relationship_type": "accesses_table",
      "access_type": "read",
      "table_alias": null
    },
    {
      "source": "sql_query:keiyaku_dao_update",
      "target": "dao:keiyaku_dao",
      "relationship_type": "executed_by",
      "method_name": "doUpdate"
    },
    {
      "source": "sql_query:keiyaku_dao_update",
      "target": "database_table:keiyaku",
      "relationship_type": "accesses_table",
      "access_type": "write",
      "table_alias": null
    },
    {
      "source": "function:list_initialization",
      "target": "database_table:t_syounin_user",
      "relationship_type": "uses_table",
      "operation_type": "read"
    },
    {
      "source": "function:list_initialization",
      "target": "database_table:t_anken",
      "relationship_type": "uses_table",
      "operation_type": "read"
    },
    {
      "source": "function:contract_deletion",
      "target": "database_table:t_keiyaku",
      "relationship_type": "uses_table",
      "operation_type": "read,write"
    },
    {
      "source": "function:contract_deletion",
      "target": "database_table:t_keiyaku_koutei",
      "relationship_type": "uses_table",
      "operation_type": "delete"
    }
  ]
}
```

---

## Validation Checklist

Before finalizing the output, verify:

1. **Entity ID Validation:**
   - ✅ All function IDs match existing function entities
   - ✅ All sql_query IDs match entities from entity extraction phase
   - ✅ All dao IDs match existing DAO entities from component file
   - ✅ All database_table IDs match entities from entity extraction phase

2. **Relationship Completeness:**
   - ✅ Every SQL query has a uses_query relationship from its function
   - ✅ Every SQL query has an executed_by relationship to its DAO
   - ✅ Every SQL query has at least one accesses_table relationship
   - ✅ Every function has uses_table relationships for all tables in its "DB Tables Used" section

3. **Property Validation:**
   - ✅ All executed_by relationships have method_name property (at top level, not nested)
   - ✅ All accesses_table relationships have access_type property (at top level)
   - ✅ All accesses_table relationships have table_alias property (at top level, even if null)
   - ✅ All uses_table relationships have operation_type property (at top level)
   - ✅ All properties are flattened (no nested properties layers)

4. **No Duplicates:**
   - ✅ No duplicate relationship definitions
   - ✅ Each unique source→target→type combination appears only once

---

## Success Criteria

A successful relationship extraction should:
1. ✅ Map all functions to their SQL queries
2. ✅ Link all queries to their executing DAO classes
3. ✅ Connect all queries to the tables they access
4. ✅ Link all functions directly to their database tables
5. ✅ Include accurate access types for all query-table relationships
6. ✅ Include accurate operation types for all function-table relationships
7. ✅ Reference only existing entity IDs
8. ✅ Generate valid JSON that can be merged with entities
9. ✅ Use only the 4 defined relationship types (uses_query, executed_by, accesses_table, uses_table)

The output will serve as the foundation for:
- Understanding data flow in contract operations
- Identifying data dependencies
- Supporting impact analysis (which functions are affected by table changes)
- Building automated documentation
- Enabling graph-based queries over the system architecture
