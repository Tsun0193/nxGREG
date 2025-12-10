# Component Entity and Relationship Extraction: Contract List Module

## Role & Context
You are a professional technical document analyzer extracting **component-level entities** (Action, Delegate, Facade, Product, DAO, ...) and **their internal relationships** from the contract-list module documentation.

**Parent Document:** `extract-entity-contract-list.md`

**Current Task:** Extract architectural component entities AND build relationships between them within the component group. This focuses on internal component dependencies and interactions within the contract-list module.

---

## What's New in This Version

### Previous Version (v1)
- ✅ Extracted component entities only
- ✅ Documented properties for each component type
- ❌ No relationship information
- ❌ Component connections not explicit

### Current Version (v2)
- ✅ Extracts component entities with full properties
- ✅ **NEW: Builds relationships between components**
- ✅ **NEW: Documents architectural flow (Action → Delegate → Facade → Product → DAO)**
- ✅ **NEW: Captures data access patterns (DAO → Database Tables)**
- ✅ **NEW: Maps navigation flows (Action forwards)**
- ✅ **NEW: Tracks form usage patterns**
- ✅ **Scope: Internal relationships within contract-list module only**

### Future Enhancement (v3)
- 🔄 Will add external relationships to other modules
- 🔄 Will connect contract-list components to housing/simple contract modules
- 🔄 Will build cross-module dependency graph

---

## Output Structure Change

### Previous JSON Structure (v1)
```json
[
  { "id": "...", "type": "...", "name": "...", ... },
  { "id": "...", "type": "...", "name": "...", ... }
]
```

### New JSON Structure (v2)
```json
{
  "entities": [
    { "id": "...", "type": "...", "name": "...", "property_name": "value", ... }
  ],
  "relationships": [
    { "source": "...", "target": "...", "relationship_type": "...", "property_name": "value", ... }
  ]
}
```

**Key Changes:** 
1. The output has TWO top-level arrays: `entities` and `relationships`
2. **Neo4j Compatibility:** All properties are flattened to single level (no nested `properties` or `metadata` objects)
3. **Relationships as Data:** Dependencies, forwards, and table accesses are expressed as relationships, not nested arrays

---

## Input Specification

### Source Files
Primary source for component identification:
- `ctc-data-en/contract-list/overview-en.md` - Main Features section lists components
- `ctc-data-en/contract-list/functions/init-screen/function-overview-en.md` - Init function components
- `ctc-data-en/contract-list/functions/delete-contract/function-overview-en.md` - Delete function components
- `ctc-data-en/contract-list/data-architecture-en.md` - Architecture overview

### Component Identification Pattern
Look for sections labeled **"Main Components"** in function overviews. Example:
```
- **Main Components**: `KeiyakuDeleteAction`, `KeiyakuDeleteDelegate`, `KeiyakuDeleteFacadeBean`, `KeiyakuDeleteProduct`
```

---

## Entity Taxonomy for Components

### 1. Action Entities
- **Type ID:** `action`
- **Properties (flattened):** 
  - `action_name`: Name of the Struts action class
  - `action_path`: URL path (e.g., `/keiyakuListInit`)
  - `http_method`: HTTP method (GET/POST)
  - `form_bean`: Associated form bean (use USES_FORM relationship instead for Neo4j)
  - `validation_enabled`: Whether validation is enabled
  - `package`: Java package path
  - `source_file_0`: Primary source file path (flattened from metadata)
- **Removed Properties:** 
  - ❌ `forward_destinations`: Use FORWARDS_TO relationships instead
  - ❌ `dispatch_methods`: Use FORWARDS_TO relationships with conditions
- **Notes:** Extract all Struts action classes including dispatch actions, init actions, and specialized actions. Forward destinations and dispatch methods are now expressed as relationships.

**Example:**
```json
{
  "id": "action:keiyaku_list_init_action",
  "type": "action",
  "name": "Contract List Init Action",
  "parent_module": "module:contract-list",
  "action_name": "KeiyakuListInitAction",
  "action_path": "/keiyakuListInit",
  "http_method": "GET/POST",
  "form_bean": "anken_cardForm",
  "validation_enabled": false,
  "package": "jp.co.daiwahouse.dsmart.application.contract.keiyakuList.keiyakuListInit",
  "source_file_0": "ctc-data-en/contract-list/functions/init-screen/function-overview-en.md"
}
```

### 2. Delegate Entities
- **Type ID:** `delegate`
- **Properties (flattened):** 
  - `delegate_name`: Name of the delegate class
  - `purpose`: Business purpose description
  - `package`: Java package path
  - `source_file_0`: Primary source file path (flattened from metadata)
- **Removed Properties:** 
  - ❌ `facade_dependencies`: Use CALLS relationships instead
- **Notes:** Delegate layer classes that bridge Actions and Facades. Dependencies are now expressed as CALLS relationships.

**Example:**
```json
{
  "id": "delegate:keiyaku_list_find_delegate",
  "type": "delegate",
  "name": "Contract List Find Delegate",
  "parent_module": "module:contract-list",
  "delegate_name": "KeiyakuListFindDelegate",
  "purpose": "Retrieve contract list from business layer",
  "package": "jp.co.daiwahouse.dsmart.delegate.contract.keiyakuList",
  "source_file_0": "ctc-data-en/contract-list/functions/init-screen/function-overview-en.md"
}
```

### 3. Facade Entities
- **Type ID:** `facade`
- **Properties (flattened):** 
  - `facade_name`: Name of the facade bean class
  - `purpose`: Business orchestration purpose
  - `package`: Java package path
  - `source_file_0`: Primary source file path (flattened from metadata)
- **Removed Properties:** 
  - ❌ `product_dependencies`: Use CALLS relationships instead
- **Notes:** Facade layer classes that orchestrate business logic. Dependencies are now expressed as CALLS relationships.

**Example:**
```json
{
  "id": "facade:keiyaku_list_find_facade_bean",
  "type": "facade",
  "name": "Contract List Find Facade Bean",
  "parent_module": "module:contract-list",
  "facade_name": "KeiyakuListFindFacadeBean",
  "purpose": "Facade for contract list retrieval",
  "package": "jp.co.daiwahouse.dsmart.service.contract.keiyakuList",
  "source_file_0": "ctc-data-en/contract-list/functions/init-screen/function-overview-en.md"
}
```

### 4. Product Entities
- **Type ID:** `product`
- **Properties (flattened):** 
  - `product_name`: Name of the product class
  - `purpose`: Core business logic purpose
  - `package`: Java package path
  - `source_file_0`: Primary source file path (flattened from metadata)
- **Removed Properties:** 
  - ❌ `dao_dependencies`: Use CALLS relationships instead
- **Notes:** Product layer classes containing core business logic. DAO dependencies are now expressed as CALLS relationships.

**Example:**
```json
{
  "id": "product:keiyaku_list_find_product",
  "type": "product",
  "name": "Contract List Find Product",
  "parent_module": "module:contract-list",
  "product_name": "KeiyakuListFindProduct",
  "purpose": "Business logic for contract list retrieval",
  "package": "jp.co.daiwahouse.dsmart.service.contract.product.keiyakuList",
  "source_file_0": "ctc-data-en/contract-list/functions/init-screen/function-overview-en.md"
}
```

### 5. DAO Entities
- **Type ID:** `dao`
- **Properties (flattened):** 
  - `dao_name`: Name of the DAO class
  - `purpose`: Data access purpose
  - `package`: Java package path
  - `source_file_0`: Primary source file path (flattened from metadata)
- **Removed Properties:** 
  - ❌ `target_tables`: Use individual ACCESSES relationships for each table
  - ❌ `operations`: Include operation type in each ACCESSES relationship
- **Notes:** Data Access Object classes. Table access is now expressed as individual ACCESSES relationships (one per table), not as a nested array.

**Example:**
```json
{
  "id": "dao:keiyaku_ichiran_find_dao",
  "type": "dao",
  "name": "Contract List Find DAO",
  "parent_module": "module:contract-list",
  "dao_name": "KeiyakuIchiranFindDAO",
  "purpose": "Query for contract list",
  "package": "jp.co.daiwahouse.dsmart.domain.contract.find",
  "source_file_0": "ctc-data-en/contract-list/functions/init-screen/function-overview-en.md"
}
```

### 6. Database Table Entities
- **Type ID:** `database_table`
- **Properties (flattened):** 
  - `table_name`: Name of the database table
  - `parent_module`: Parent module reference
- **Notes:** Database tables accessed by DAOs. These are extracted from the documentation's database table lists and create explicit nodes in the graph for data lineage tracking.

**Example:**
```json
{
  "id": "database_table:t_keiyaku",
  "type": "database_table",
  "name": "T_KEIYAKU",
  "table_name": "t_keiyaku",
  "parent_module": "module:contract-list"
}
```

---

## Relationship Taxonomy

### Relationship Types Within Component Group

Extract relationships between components to capture the architectural flow and dependencies. Focus on **internal relationships** within the contract-list module only.

#### 1. CALLS Relationship
- **Source:** Action, Delegate, Facade, Product
- **Target:** Delegate, Facade, Product, DAO
- **Description:** Represents method invocation or component usage
- **Properties (flattened):**
  - `relationship_type`: "CALLS"
  - `purpose`: Brief description of why this call is made
  - `call_context`: Context in which the call occurs (e.g., "initialization", "validation", "deletion")

**Example:**
```json
{
  "source": "action:keiyaku_list_init_action",
  "target": "delegate:keiyaku_list_find_delegate",
  "relationship_type": "CALLS",
  "purpose": "Retrieve contract list for display",
  "call_context": "initialization"
}
```

#### 2. DEPENDS_ON Relationship
- **Source:** Any component
- **Target:** Any component
- **Description:** Represents dependency where source needs target to function
- **Properties (flattened):**
  - `relationship_type`: "DEPENDS_ON"
  - `dependency_type`: Type of dependency ("data", "business_logic", "validation")

**Example:**
```json
{
  "source": "facade:keiyaku_list_find_facade_bean",
  "target": "product:keiyaku_list_find_product",
  "relationship_type": "DEPENDS_ON",
  "dependency_type": "business_logic"
}
```

#### 3. ACCESSES Relationship
- **Source:** DAO entity
- **Target:** Database table entity (database_table:table_name)
- **Description:** Represents data access patterns. **CRITICAL: Create one relationship per table, not a single relationship with array of tables.**
- **Properties (flattened):**
  - `relationship_type`: "ACCESSES"
  - `access_type`: "READ", "WRITE", "UPDATE", or "DELETE"
  - `target`: Database table entity ID (e.g., "database_table:t_keiyaku")

**Example (one DAO accessing multiple tables requires multiple relationships):**
```json
{
  "source": "dao:keiyaku_ichiran_find_dao",
  "target": "database_table:t_keiyaku",
  "relationship_type": "ACCESSES",
  "access_type": "READ"
},
{
  "source": "dao:keiyaku_ichiran_find_dao",
  "target": "database_table:t_anken",
  "relationship_type": "ACCESSES",
  "access_type": "READ"
},
{
  "source": "dao:keiyaku_ichiran_find_dao",
  "target": "database_table:t_keiyaku_kokyaku_kankei",
  "relationship_type": "ACCESSES",
  "access_type": "READ"
}
```

#### 4. FORWARDS_TO Relationship
- **Source:** Action
- **Target:** Another Action or JSP page (as string reference)
- **Description:** Represents navigation flow between screens/actions
- **Properties (flattened):**
  - `relationship_type`: "FORWARDS_TO"
  - `forward_name`: The forward destination name
  - `target_view`: JSP or action path
  - `condition`: Condition under which forward occurs (optional)

**Example:**
```json
{
  "source": "action:keiyaku_list_init_action",
  "relationship_type": "FORWARDS_TO",
  "forward_name": "success",
  "target_view": "/contract/keiyaku_list.jsp"
}
```

#### 5. USES_FORM Relationship
- **Source:** Action
- **Target:** Form bean (referenced as string)
- **Description:** Represents form bean usage by action
- **Properties (flattened):**
  - `relationship_type`: "USES_FORM"
  - `form_bean_name`: Name of the form bean

**Example:**
```json
{
  "source": "action:keiyaku_list_init_action",
  "relationship_type": "USES_FORM",
  "form_bean_name": "anken_cardForm"
}
```

### Relationship Extraction Rules

1. **Layered Architecture Pattern**: Extract relationships following the standard flow:
   - Action → Delegate (CALLS)
   - Delegate → Facade (CALLS)
   - Facade → Product (CALLS)
   - Product → DAO (CALLS)
   - All layers DEPEND_ON their next layer

2. **Data Access Pattern**: For DAOs:
   - Create **individual ACCESSES relationship for each table** (do not bundle tables in arrays)
   - Include operation type (READ, WRITE, UPDATE, DELETE) in each relationship
   - Example: If DAO accesses 3 tables, create 3 separate ACCESSES relationships

3. **Navigation Pattern**: For Actions:
   - Create FORWARDS_TO for each forward destination
   - Create USES_FORM for form bean usage

4. **Completeness**: For each component entity, extract:
   - All direct method calls to other components
   - All dependencies mentioned in documentation
   - All data access patterns (for DAOs)
   - All navigation flows (for Actions)

### Relationship Extraction Strategies

#### Finding CALLS Relationships

Look for these indicators in documentation:

1. **Explicit Component Lists**: In function overview documents, look for sections like:
   ```
   Main Components:
   - Action: KeiyakuListInitAction
   - Delegate: KeiyakuListFindDelegate
   - Facade: KeiyakuListFindFacadeBean
   - Product: KeiyakuListFindProduct
   ```
   This indicates: Action CALLS Delegate, Delegate CALLS Facade, Facade CALLS Product

2. **Component Tables**: Look for tables with Layer/Class columns:
   ```
   | Layer    | Class                    |
   |----------|--------------------------|
   | Action   | KeiyakuListInitAction    |
   | Delegate | KeiyakuListFindDelegate  |
   ```
   Extract relationships between consecutive layers

3. **Dependency Properties**: In extracted entities, look at:
   - `facade_dependencies` in Delegate entities → CALLS relationships
   - `product_dependencies` in Facade entities → CALLS relationships
   - `dao_dependencies` in Product entities → CALLS relationships

4. **Method Descriptions**: Look for text like:
   - "calls the delegate"
   - "invokes the facade"
   - "uses the product"
   - "queries via DAO"

#### Finding ACCESSES Relationships

For each DAO entity:
1. Look for table names in documentation (often in component descriptions or data architecture sections)
2. Identify operation types (READ, WRITE, UPDATE, DELETE) from DAO purpose/descriptions
3. **Create database_table entity for each unique table**
4. **Create individual ACCESSES relationship for each table:**
   - `source`: the DAO entity ID
   - `target`: the database_table entity ID (e.g., "database_table:t_keiyaku")
   - `access_type`: the operation type
   - **CRITICAL:** One relationship per table, NOT one relationship with array of tables

**Example:** If `KeiyakuIchiranFindDAO` accesses 3 tables, create 3 relationships:
```json
{ "source": "dao:keiyaku_ichiran_find_dao", "target": "database_table:t_keiyaku", "relationship_type": "ACCESSES", "access_type": "READ" },
{ "source": "dao:keiyaku_ichiran_find_dao", "target": "database_table:t_anken", "relationship_type": "ACCESSES", "access_type": "READ" },
{ "source": "dao:keiyaku_ichiran_find_dao", "target": "database_table:t_keiyaku_kokyaku_kankei", "relationship_type": "ACCESSES", "access_type": "READ" }
```

#### Finding FORWARDS_TO Relationships

For each Action entity:
1. Look for forward mapping descriptions in documentation (e.g., "forwards to success", "on error forwards to...")
2. Check struts-config.xml references if available
3. Look for dispatch method routing information
4. Create individual FORWARDS_TO for each destination:
   - `source`: the Action entity ID
   - `forward_name`: the forward key (e.g., "success", "error")
   - `target_view`: the JSP or next action path (if documented)
   - `condition`: when this forward is triggered (for dispatch actions)

#### Finding Dispatch Patterns

For DispatchAction entities:
1. Look for dispatch method descriptions in documentation
2. Each dispatch method may forward to different actions/views
3. Create separate FORWARDS_TO relationships for each dispatch destination
4. Document in `condition` property which dispatch method/actionType triggers the forward
5. Example: `"condition": "when actionType=delete_contract"`

### Relationship Quality Guidelines

1. **Accuracy**: Only create relationships explicitly documented or clearly implied by architecture
2. **Completeness**: Every component should have at least one relationship (input or output)
3. **Consistency**: Use consistent relationship types and property structures
4. **Traceability**: Include source information in relationship properties when available
5. **Scope**: Stay within the contract-list module boundaries

---

## Extraction Guidelines

### Component Discovery Process

1. **Identify Functions**: Look for function sections in `overview-en.md` (e.g., "List Initialization Feature", "Contract Deletion Feature")

2. **Extract Component Lists**: Find "Main Components" sections that list Action, Delegate, Facade, Product, and DAO classes

3. **Find Detailed Information**: Check function-specific documentation in `functions/*/function-overview-en.md` for:
   - Component table with Layer/Class/Package/Purpose columns
   - Package paths
   - Dependencies between layers

4. **Map Architecture**: Follow the layered architecture pattern:
   ```
   Action → Delegate → Facade → Product → DAO → [Database Tables]
   ```

### Visual Example: Complete Function Mapping

For the **List Initialization Feature**, extract the following structure:

```
┌─────────────────────────────────────────────────────────────┐
│ Action Layer                                                 │
│  KeiyakuListInitAction (/keiyakuListInit)                   │
│    - USES_FORM: anken_cardForm                              │
│    - FORWARDS_TO: success → /contract/keiyaku_list.jsp      │
└────────────────┬───────────────────────┬────────────────────┘
                 │ CALLS                 │ CALLS
                 ▼                       ▼
┌────────────────────────────┐  ┌──────────────────────────┐
│ Delegate Layer             │  │ Delegate Layer           │
│  KeiyakuListFindDelegate   │  │  AnkenFindDelegate       │
└────────────┬───────────────┘  └───────────┬──────────────┘
             │ CALLS                        │ CALLS
             ▼                              ▼
┌────────────────────────────┐  ┌──────────────────────────┐
│ Facade Layer               │  │ Facade Layer             │
│  KeiyakuListFindFacadeBean │  │  AnkenFindFacadeBean     │
└────────────┬───────────────┘  └───────────┬──────────────┘test
             │ CALLS                        │ CALLS
             ▼                              ▼
┌────────────────────────────┐  ┌──────────────────────────┐
│ Product Layer              │  │ Product Layer            │
│  KeiyakuListFindProduct    │  │  AnkenFindProduct        │
└────────────┬───────────────┘  └───────────┬──────────────┘
             │ CALLS                        │ CALLS
             ▼                              ▼
┌────────────────────────────┐  ┌──────────────────────────┐
│ DAO Layer                  │  │ DAO Layer                │
│  KeiyakuIchiranFindDAO     │  │  AnkenFindDAO            │
│    - ACCESSES:             │  │    - ACCESSES:           │
│      * t_keiyaku [READ]    │  │      * t_anken [READ]    │
│      * t_anken [READ]      │  │                          │
└────────────────────────────┘  └──────────────────────────┘
```

**This translates to:**

**Entities (6 total):**
1. KeiyakuListInitAction (action)
2. KeiyakuListFindDelegate (delegate)
3. AnkenFindDelegate (delegate)
4. KeiyakuListFindFacadeBean (facade)
5. AnkenFindFacadeBean (facade)
6. KeiyakuIchiranFindDAO (dao)
... (and more Products)

**Relationships (10+ total):**
1. KeiyakuListInitAction CALLS KeiyakuListFindDelegate
2. KeiyakuListInitAction CALLS AnkenFindDelegate
3. KeiyakuListInitAction USES_FORM anken_cardForm
4. KeiyakuListInitAction FORWARDS_TO success
5. KeiyakuListFindDelegate CALLS KeiyakuListFindFacadeBean
6. AnkenFindDelegate CALLS AnkenFindFacadeBean
7. KeiyakuListFindFacadeBean CALLS KeiyakuListFindProduct
8. AnkenFindFacadeBean CALLS AnkenFindProduct
9. KeiyakuListFindProduct CALLS KeiyakuIchiranFindDAO
10. KeiyakuIchiranFindDAO ACCESSES [t_keiyaku, t_anken]
... (and more)

### Required Components for Contract List Module

Based on `overview-en.md`, extract components for these functions:

#### 1. List Initialization Feature
- `KeiyakuListInitAction`
- `KeiyakuListFindDelegate`
- `KeiyakuListFindFacadeBean`
- `KeiyakuListFindProduct`
- Plus supporting delegates/facades/products for:
  - `SyouninUserFindDelegate`, `SyouninUserFindFacadeBean`, `SyouninUserFindProduct`
  - `AnkenFindDelegate`, `AnkenFindFacadeBean`, `AnkenFindProduct`
- DAOs: `SyouninUserFindDAO`, `AnkenFindDAO`, `KeiyakuIchiranFindDAO`

#### 2. Contract Deletion Feature
- `KeiyakuDeleteAction`
- `KeiyakuDeleteDelegate`
- `KeiyakuDeleteFacadeBean`
- `KeiyakuDeleteProduct`
- DAOs: `KeiyakuDAO`, `KoujiDAO`, `KeiyakuShijisyoKankeiDAO`, `ChintaisyakuKeiyakuKankeiDAO`, and others

#### 3. Dispatch Action (Routing)
- `KeiyakuListDispatchAction`
- This action routes to other actions based on `actionType`

### Completeness Checklist

For each function documented, ensure you extract:
- [ ] All Action entities
- [ ] All Delegate entities mentioned
- [ ] All Facade entities mentioned
- [ ] All Product entities mentioned
- [ ] All DAO entities mentioned
- [ ] Individual ACCESSES relationships for each table accessed by each DAO

---

## Output Specification

### Format
Output must be a valid JSON file containing both component entities and their relationships.

### File Name
`json/contract-list-component-entities.json`

### JSON Structure (Neo4j Compatible - Flattened)
```json
{
  "entities": [
    {
      "id": "entity_id",
      "type": "entity_type",
      "name": "Entity Name",
      "parent_module": "module:contract-list",
      "property_name_1": "value1",
      "property_name_2": "value2",
      "source_file_0": "path/to/source.md"
    }
  ],
  "relationships": [
    {
      "source": "source_entity_id",
      "target": "target_entity_id",
      "relationship_type": "RELATIONSHIP_TYPE",
      "property_name_1": "value1",
      "property_name_2": "value2"
    }
  ]
}
```

**Key Points:**
- ✅ All properties are at the top level (no nested `properties` or `metadata` objects)
- ✅ Source files use `source_file_0`, `source_file_1`, etc. naming
- ✅ Relationships have properties at the top level
- ✅ No array properties for dependencies or tables (use relationships instead)

### Validation Requirements

#### For Entities:
- Each entity must have required fields: `id`, `type`, `name`, `parent_module`
- All properties must be at top level (no nested `properties` or `metadata` objects)
- Component names must match exactly as documented
- Entity IDs must be unique and follow the pattern: `type:lowercase_name`
- Package paths must be complete and accurate
- Source files should use `source_file_0`, `source_file_1`, etc.
- Do NOT include dependency arrays (`facade_dependencies`, `dao_dependencies`, `target_tables`, etc.)

#### For Relationships:
- Each relationship must have: `source`, `relationship_type`, and usually `target`
- All relationship properties must be at top level (no nested `properties` object)
- Source must reference valid entity ID from the entities array
- Relationship types must be one of: `CALLS`, `DEPENDS_ON`, `ACCESSES`, `FORWARDS_TO`, `USES_FORM`
- For ACCESSES relationships: `target` must be a database_table entity ID (e.g., "database_table:t_keiyaku"), create one relationship per table
- For FORWARDS_TO and USES_FORM: `target` can be a string reference (JSP path, form name)
- For CALLS and DEPENDS_ON: `target` must be a valid entity ID

#### Completeness:
- Every Action must have at least one CALLS relationship to a Delegate
- Every Delegate must have at least one CALLS relationship to a Facade
- Every Facade must have at least one CALLS relationship to a Product
- Every Product must have at least one CALLS relationship to a DAO
- Every DAO must have at least one ACCESSES relationship
- Document all forward destinations and form bean usage for Actions

---

## Task Execution Steps

### Phase 1: Entity Extraction
1. **Read** `ctc-data-en/contract-list/overview-en.md` and identify all functions with "Main Components"
2. **Read** detailed function overviews in `functions/*/function-overview-en.md`
3. **Extract** all Action, Delegate, Facade, Product, and DAO entities
4. **Document** entity properties: names, packages, purposes, and layer-specific attributes
5. **Extract** all database table names from documentation
6. **Create** database_table entities for each unique table

### Phase 2: Relationship Extraction
6. **Map** CALLS relationships following the layered architecture:
   - Identify which Action calls which Delegate(s)
   - Identify which Delegate calls which Facade(s)
   - Identify which Facade calls which Product(s)
   - Identify which Product calls which DAO(s)
7. **Map** DEPENDS_ON relationships for component dependencies
8. **Map** ACCESSES relationships for DAO-to-table access patterns:
   - **Create one relationship per table** (not one relationship with array)
   - Include `access_type` for each relationship
9. **Map** FORWARDS_TO relationships for Action navigation flows
10. **Map** USES_FORM relationships for Action form bean usage

### Phase 3: Validation and Output
11. **Validate** entity completeness and uniqueness
12. **Validate** relationship integrity (source/target references)
13. **Verify** architectural pattern completeness
14. **Output** to `json/contract-list-component-entities.json`

### Extraction Priority

Focus on capturing:
1. **Complete layered architecture** with accurate component names, packages, and purposes
2. **All component-to-component relationships** within the module
3. **Data access patterns** showing how DAOs interact with database tables
4. **Navigation flows** showing how Actions forward to different destinations
5. **Form usage patterns** showing form beans used by Actions

### Important Notes

- **Neo4j Compatibility**: All properties must be flattened (no nested objects)
  - ❌ NO: `"properties": { "action_name": "..." }`
  - ✅ YES: `"action_name": "..."`
  
- **Database Tables**: DO NOT create separate database entities. Create individual ACCESSES relationships:
  - ❌ NO: One relationship with `"tables": ["t_keiyaku", "t_anken"]`
  - ✅ YES: Two relationships, each with `"target": "t_keiyaku"` and `"target": "t_anken"`
  
- **Dependency Arrays**: DO NOT include dependency arrays in entities
  - ❌ NO: `"dao_dependencies": ["DAO1", "DAO2"]`
  - ✅ YES: Create CALLS relationships to each DAO

- **Relationship Scope**: Focus ONLY on internal relationships within the contract-list module. External module relationships will be handled in a separate phase.

- **Relationship Documentation**: Extract relationships from:
  - Component table showing Layer → Class mappings
  - Dependency lists (e.g., "facade_dependencies", "product_dependencies")
  - Architecture flow diagrams
  - Method descriptions mentioning component calls

### Complete Example (Neo4j Compatible - Flattened Structure)

Here's how a function should be documented with entities and relationships:

```json
{
  "entities": [
    {
      "id": "database_table:t_keiyaku",
      "type": "database_table",
      "name": "T_KEIYAKU",
      "table_name": "t_keiyaku",
      "parent_module": "module:contract-list"
    },
    {
      "id": "database_table:t_anken",
      "type": "database_table",
      "name": "T_ANKEN",
      "table_name": "t_anken",
      "parent_module": "module:contract-list"
    } 
  ],
  "relationships": [
    {
      "source": "action:keiyaku_list_init_action",
      "target": "delegate:keiyaku_list_find_delegate",
      "relationship_type": "CALLS",
      "purpose": "Retrieve contract list for display",
      "call_context": "initialization"
    },
    {
      "source": "action:keiyaku_list_init_action",
      "relationship_type": "USES_FORM",
      "form_bean_name": "anken_cardForm"
    }
  ]
}
```

---

## Common Patterns and Examples

### Pattern 1: Simple CRUD Function
A typical CRUD function will have this structure:
- **1 Action** → **1 Delegate** → **1 Facade** → **1 Product** → **1-3 DAOs**
- Action has USES_FORM and FORWARDS_TO relationships
- Each layer CALLS the next layer
- DAOs ACCESSES database tables

### Pattern 2: Complex Initialization Function
Complex functions may call multiple delegates:
- **1 Action** → **3+ Delegates** (parallel)
- Each Delegate → Facade → Product → DAO chain
- Example: KeiyakuListInitAction calls SyouninUserFindDelegate, AnkenFindDelegate, and KeiyakuListFindDelegate

### Pattern 3: Dispatch Action
Dispatch actions route to different operations:
- **1 DispatchAction** → **Multiple Actions** (via FORWARDS_TO)
- Each dispatch method may have different CALLS chains
- Document dispatch_methods in properties

### Pattern 4: Multi-Table DAO
DAOs often access multiple related tables:
- **1 DAO** → ACCESSES → **Multiple Tables**
- Tables are joined in queries (e.g., t_keiyaku + t_anken + t_keiyaku_kokyaku_kankei)
- Include all tables in ACCESSES relationship

---

## Troubleshooting and Edge Cases

### Q: What if a component calls multiple components in the same layer?
**A:** Create multiple CALLS relationships. Example:
```json
{
  "source": "action:keiyaku_list_init_action",
  "target": "delegate:keiyaku_list_find_delegate",
  "relationship_type": "CALLS",
  "call_context": "get contract list"
},
{
  "source": "action:keiyaku_list_init_action",
  "target": "delegate:anken_find_delegate",
  "relationship_type": "CALLS",
  "call_context": "get project info"
}
```

### Q: What if the documentation doesn't explicitly state all relationships?
**A:** Use architectural patterns to infer:
- If components are listed in same function's Main Components list, they're connected in sequence
- Follow the standard layer flow: Action → Delegate → Facade → Product → DAO
- Look for component names that match (e.g., KeiyakuListFindDelegate likely calls KeiyakuListFindFacadeBean)

### Q: Should I create DEPENDS_ON and CALLS for the same pair?
**A:** Yes, if both are applicable:
- CALLS = actual method invocation
- DEPENDS_ON = architectural dependency
- Example: Product CALLS DAO (method invocation) and DEPENDS_ON DAO (can't function without it)

### Q: How to handle shared components (e.g., AnkenFindDelegate used by multiple functions)?
**A:** 
- Create the entity once with a unique ID
- Create multiple CALLS relationships from different Actions to this shared component
- This shows the component is reusable across functions

### Q: What about external library calls (e.g., Commons Lang, Struts framework)?
**A:** 
- Do NOT create entities for external libraries
- Do NOT create relationships to framework components
- Focus only on application-level components within contract-list module

### Q: How to document conditional relationships?
**A:** Use the `condition` property at the top level:
```json
{
  "source": "action:dispatch_action",
  "target": "delegate:delete_delegate",
  "relationship_type": "CALLS",
  "call_context": "delete operation",
  "condition": "when actionType=delete_contract"
}
```

---

## Validation Checklist

Before submitting the JSON output, verify:

### Entity Validation
- [ ] All entities have unique IDs following pattern `type:lowercase_name`
- [ ] All entities have required fields: id, type, name, parent_module
- [ ] All properties are at top level (no nested `properties` or `metadata` objects)
- [ ] All component names match documentation exactly
- [ ] All packages are complete and accurate
- [ ] Entity count matches expected components from documentation
- [ ] Source files use `source_file_0`, `source_file_1` naming
- [ ] No dependency arrays in entities (use relationships instead)

### Relationship Validation
- [ ] All CALLS relationships follow layered architecture (no skipping layers)
- [ ] Every Action has at least one CALLS to a Delegate
- [ ] Every Delegate has at least one CALLS to a Facade
- [ ] Every Facade has at least one CALLS to a Product
- [ ] Every Product has at least one CALLS to a DAO
- [ ] Every DAO has at least one ACCESSES relationship (one per table accessed)
- [ ] All relationship properties are at top level (no nested `properties` object)
- [ ] All relationship sources reference valid entity IDs
- [ ] Relationship types are valid: CALLS, DEPENDS_ON, ACCESSES, FORWARDS_TO, USES_FORM
- [ ] ACCESSES relationships have individual `target` for each table (not arrays)
- [ ] Each table access has its own separate relationship

### Completeness Validation
- [ ] All functions from overview-en.md are covered
- [ ] All Main Components from each function are extracted
- [ ] All forward destinations are documented
- [ ] All form beans are documented
- [ ] All database tables are referenced in DAO ACCESSES relationships

### Quality Validation
- [ ] Relationship purposes are clear and specific
- [ ] Call contexts provide meaningful information
- [ ] No duplicate relationships (same source + target + type)
- [ ] JSON is properly formatted and valid
- [ ] No orphaned entities (entities with no relationships)

---

## Success Metrics

A complete extraction should have:
- **Entities**: 20-50 components depending on module complexity
- **Relationships**: 3-5x the number of entities (most components have multiple relationships)
- **Coverage**: 100% of documented functions
- **Connectivity**: Every entity connected to at least one other entity
- **Architectural Integrity**: Clear flow from Action layer down to DAO layer
