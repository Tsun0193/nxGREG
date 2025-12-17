# Entity Extraction Instruction: Contract List Module

## Role & Context
You are a professional technical document analyzer and knowledge graph database expert specializing in system documentation analysis.

**Project Goal:** Build a comprehensive knowledge graph RAG system for a contract management system by extracting entities and their relationships from structured markdown documentation.

**Current Task:** Phase 1 - Entity Extraction. Extract all entities with their properties from the contract-list module documentation to a JSON file before establishing relationships in Phase 2.

---

## Input Specification

### Source Directory
**Path:** `ctc-data-en/contract-list/`

**Structure:**
```
ctc-data-en/contract-list/
├── components/
│   ├── description-ui-en.md
│   ├── form-fields-en.md
│   └── validation-rules-en.md
├── data-architecture-en.md
├── functions/
│   ├── delete-contract/
│   │   ├── function-overview-en.md
│   │   ├── sequence-diagram-en.md
│   │   ├── sql-queries-en.md
│   │   └── sql-statements-en.md
│   └── init-screen/
│       ├── function-overview-en.md
│       ├── sequence-diagram-en.md
│       └── sql-queries-en.md
├── overview-en.md
├── screen-flow-en.md
└── screen-specification/
    ├── display-conditions-en.md
    └── event_handling_rules-en.md
```

**Module Hierarchy:**
- **Parent Module:** `contract-list`
- **Child Modules:** `housing`, `simple` (This will only be used as reference in this task, not actual result)

---

## Output Specification

### Format
Output must be a valid JSON file with TWO top-level arrays: `entities` and `relationships`.

### JSON Structure (Neo4j Compatible)
```json
{
  "entities": [
    {
      "id": "<type>:<unique_name>",
      "type": "<entity_type>",
      "name": "<human_readable_name>",
      "parent_module": "module:contract-list",
      "property_name": "property_value",
      "source_file_0": "<relative_path_to_source_file>"
    }
  ],
  "relationships": [
    {
      "source": "<source_entity_id>",
      "target": "<target_entity_id>",
      "relationship_type": "<RELATIONSHIP_TYPE>",
      "property_name": "property_value"
    }
  ]
}
```

### Entity Schema Requirements
- **id**: Unique identifier in format `<type>:<name>` (e.g., `screen:contract_list_main`)
- **type**: Entity type from the taxonomy below
- **name**: Human-readable name
- **parent_module**: Always `"module:contract-list"` for this extraction
- **source_file_0**: Primary source file path (use `source_file_0`, `source_file_1` for multiple sources)
- **All properties at top level**: No nested `properties` or `metadata` objects
- **DO NOT include relationship fields**: No `parent_screen_id`, `parent_module_id` - use relationships array instead

### Relationship Schema Requirements
- **source**: Entity ID that initiates the relationship
- **target**: Entity ID that receives the relationship
- **relationship_type**: Type of relationship (see taxonomy below)
- **All properties at top level**: No nested objects

---

## Entity Taxonomy

Extract the following entity types (included but not limited to):

### 1. Module Entities
- **Type ID:** `module`
- **Fields:** module_name, dependencies, child_modules
- **Notes:** Extract the main module and any sub-modules defined in the documentation

### 2. Screen Entities
- **Type ID:** `screen`
- **Fields:** screen_id, title, url_pattern, access_level, layout_type
- **Notes:** All screens navigable from this module are documented in `ctc-data-en/contract-list/screen-flow-en.md`. Extract each screen as a separate entity even if it transitions to different modules.

### 3. Value Object Entities
- **Type ID:** `value_object`
- **Fields:** object_name, fields (semicolon-separated string), validation_rules
- **Notes:** VOs used for data transfer between layers (e.g., KeiyakuVO, AnkenVO, AuthorityVO). Fields should be concatenated with semicolon separator.

### 4. Form Entities
- **Type ID:** `form`
- **Fields:** form_id, form_bean_class, scope, submission_action, description, fields (semicolon-separated list of field names)
- **Notes:** Struts form beans used for request/response handling. Include all form fields as a semicolon-separated list in the `fields` property. Keep the original form bean class name in the ID (e.g., `form:anken_cardForm`).
- **DO NOT include:** `parent_module_id` - use BELONGS_TO relationship instead

### 5. Session Entities
- **Type ID:** `session`
- **Fields:** session_key, scope, lifecycle, stored_data, description
- **Notes:** Session attributes used to maintain state across requests

### 6. Function Entities
- **Type ID:** `function`
- **Fields:** function_name, parameters (stringified JSON), return_type, business_logic, url, validation_rules, output_success, output_failure
- **Notes:** The function is mentioned in the "ctc-data-en/contract-list/overview-en.md" and listed in "ctc-data-en/contract-list/functions" as:
  + **1. List Initialization Feature**
  + **2. Contract Deletion Feature**
- **DO NOT include:** `used_database_tables` - use ACCESSES relationship instead

---

## Relationship Taxonomy

Extract the following relationship types between entities:

### 1. BELONGS_TO Relationship
- **Source:** Screen, Function, Form, Session
- **Target:** Module
- **Description:** Represents hierarchical ownership/containment
- **Properties:**
  - `relationship_type`: "BELONGS_TO"

**Examples:**
```json
{
  "source": "screen:contract_list_main",
  "target": "module:contract-list",
  "relationship_type": "BELONGS_TO"
},
{
  "source": "function:init_screen",
  "target": "module:contract-list",
  "relationship_type": "BELONGS_TO"
}
```

### 2. PROVIDES Relationship
- **Source:** Screen
- **Target:** Function
- **Description:** Screen provides specific functionality
- **Properties:**
  - `relationship_type`: "PROVIDES"
  - `function_category`: Type of function provided

**Example:**
```json
{
  "source": "screen:contract_list_main",
  "target": "function:contract_deletion",
  "relationship_type": "PROVIDES",
  "function_category": "contract_management"
}
```

### 3. USES_FORM Relationship
- **Source:** Function, Screen
- **Target:** Form
- **Description:** Component uses a form for data input/submission
- **Properties:**
  - `relationship_type": "USES_FORM"
  - `usage_context`: How the form is used

**Example:**
```json
{
  "source": "function:contract_deletion",
  "target": "form:anken_cardForm",
  "relationship_type": "USES_FORM",
  "usage_context": "Contract context data"
}
```

### 4. STORES Relationship
- **Source:** Function, Screen
- **Target:** Session
- **Description:** Component stores data in session
- **Properties:**
  - `relationship_type`: "STORES"
  - `storage_purpose`: Why data is stored

**Example:**
```json
{
  "source": "function:init_screen",
  "target": "session:keiyakuListVO",
  "relationship_type": "STORES",
  "storage_purpose": "Preserve contract list data across requests"
}
```

### 5. NAVIGATES_TO Relationship
- **Source:** Screen, Function
- **Target:** Screen
- **Description:** Navigation flow between screens
- **Properties:**
  - `relationship_type`: "NAVIGATES_TO"
  - `trigger`: What triggers navigation
  - `condition`: Under what condition navigation occurs

**Example:**
```json
{
  "source": "screen:contract_list_main",
  "target": "screen:housing_contract",
  "relationship_type": "NAVIGATES_TO",
  "trigger": "Housing contract selection",
  "condition": "User selects housing contract type"
}
```

### Relationship Extraction Rules

1. **Hierarchy Pattern:** Extract BELONGS_TO relationships for all containment hierarchies:
   - Screen → Module
   - Function → Module
   - Form → Module
   - Session → Module

2. **Functional Relationships:** Extract PROVIDES for Screen→Function to show which functions are available in which screens

3. **Data Flow:** Use USES_FORM and STORES for functions that work with forms and sessions

4. **Navigation Flow:** Use NAVIGATES_TO for all screen transitions mentioned in documentation

5. **Completeness:** For each entity, extract:
   - At least one BELONGS_TO relationship (except Module)
   - All functional relationships (PROVIDES, USES_FORM, etc.)
   - All navigation flows (NAVIGATES_TO)
   - All data dependencies (STORES)

---

## Entities Extracted to Separate Files

### Component Entities
**For Action, Delegate, Facade, Product, and DAO entities**, refer to:
**📄 [Component Entity Extraction Guide](extract-component-entity-contract-list.md)**

These architectural component entities have been moved to a separate instruction file to reduce token usage. They include:
- Action Entities (Struts actions)
- Delegate Entities (business delegates)
- Facade Entities (facade beans)
- Product Entities (business logic products)
- DAO Entities (data access objects)

**Note**: Do not create the component entities in this task

### UI & Interaction Entities
**For View, Button, Route, Action Type, Event, and Flag entities**, refer to:
**📄 [UI & Interaction Entity Extraction Guide](extract-ui-interaction-entity-contract-list.md)**

These UI and interaction entities have been moved to a separate instruction file. They include:
- View/UI Entities (JSP files and view templates)
- Button Entities (UI action buttons)
- Route/URL Entities (HTTP endpoints)
- Action Type Entities (dispatch action types)
- Event Entities (user interaction events)
- Business/Control Flag Entities (permission and display flags)

**Note**: Do not create the UI/interaction entities in this task

---

## Extraction Guidelines

### 1. Completeness
- Extract **all** entities found in the documentation
- Include entities even if they have minimal information
- Do not skip entities marked as "to be implemented" or "deprecated"

### 2. Detail Level
- Include all properties available in the source documentation
- Capture technical details (IDs, names, types, configurations)

### 3. Consistency
- Use consistent naming conventions (snake_case for IDs, Title Case for names)
- Maintain uniform date formats (ISO 8601)
- Apply consistent terminology from the source documentation

### 4. Accuracy
- Extract information verbatim where possible
- Do not infer relationships (saved for Phase 2)
- Mark uncertain information with `"confidence": "low"` in metadata

### 5. Traceability
- Always include `source_file` as a direct field
- Maintain original terminology and avoid paraphrasing technical terms

### 6. Database Table References
- **DO NOT create separate database entities** - database tables will be maintained in a shared database schema file 
- **DO NOT reference database entities** - The relationship will be built later

---

## Specific Focus for This Task

**Primary Objective:** Extract all **Entities and Relationships** from the contract-list module.

### Important Notes

1. **Module Structure**: The contract-list module is a list/table-based module without tabs. It focuses on displaying and managing contracts in a tabular format with functions for initialization and deletion.

2. **Screen Extraction Source**: All screens navigable from this module are documented in `ctc-data-en/contract-list/screen-flow-en.md`. Extract each screen mentioned in the "Main Features" section as a separate screen entity, including:
   - Contract List Screen (keiyakuListInit)
   - Contract Type Selection (keiyakuListAssign)
   - Additional Contract Creation (tsuikaKeiyakuDispatch)
   - Contract Modification (henkoKeiyakuDispatch)
   - Contract Deletion (keiyakuDelete)
   - After-Sales Contract (yuusyouKeiyakuListAssign)
   - Multiple Orders (moushideSelectInit)
   - Contract Details (anchorKeiyakuDispatch)

3. **Function Focus**: The contract-list module has two main functions:
   - **List Initialization Feature**: Documented in `ctc-data-en/contract-list/functions/init-screen/`
   - **Contract Deletion Feature**: Documented in `ctc-data-en/contract-list/functions/delete-contract/`
   
4. **Database Tables**: DO NOT create separate database entities or reference tables in entity properties

5. **Layered Architecture**: Component entities (Action, Delegate, Facade, Product, DAO) are documented separately in `extract-component-entity-contract-list.md` and will not be listed in this task

### Example Screen Entity
```json
{
  "id": "screen:contract_list_main",
  "type": "screen",
  "name": "Contract List Main Screen",
  "parent_module": "module:contract-list",
  "screen_id": "GCNT90001",
  "title": "Contract List",
  "url_pattern": "/dsmart/contract/keiyakuList/keiyakuListInit.do",
  "access_level": "authenticated_user",
  "layout_type": "data_table",
  "has_search": true,
  "has_filter": true,
  "pagination": false,
  "main_jsp": "keiyakuList.jsp",
  "action_class": "KeiyakuListInitAction",
  "source_file_0": "ctc-data-en/contract-list/overview-en.md"
}
```

### Example Function Entity
```json
{
    "id": "function:contract_deletion",
    "type": "function",
    "name": "Contract Deletion Feature",
    "parent_module": "module:contract_list",
    "function_name": "Contract Deletion",
    "url": "/dsmart/contract/keiyakuList/keiyakuListDispatch.do?actionType=delete_contract",
    "parameters": "{\"actionType\":{\"name\":\"actionType\",\"type\":\"String\",\"value\":\"delete_contract\",\"required\":true},\"keiyakuKey\":{\"name\":\"keiyakuKey\",\"type\":\"Long\",\"description\":\"Selected contract key to delete\",\"required\":true}}",
    "return_type": "Forward",
    "output_success": "/keiyakuListInit.do",
    "output_failure": "/keiyakuListInit.do and error message",
    "description": "Performs logical deletion of selected contract and updates related data",
    "validation_rules": "Contract must exist; Only non-main/non-linked contracts can be deleted",
    "source_file": "ctc-data-en/contract-list/functions/delete-contract/function-overview-en.md"
}
```

### Example Value Object Entity
```json
{
  "id": "value_object:keiyaku_vo",
  "type": "value_object",
  "name": "Contract Value Object",
  "parent_module": "module:contract-list",
  "object_name": "KeiyakuVO",
  "fields": "keiyakuKey;keiyakuNo;keiyakuStatusCd;keiyakuCardSyubetsuCd;keiyakuUkagaiKbn",
  "purpose": "Transfer contract data between layers",
  "source_file_0": "ctc-data-en/contract-list/overview-en.md"
}
```

### Example Form Entity
```json
{
  "id": "form:anken_cardForm",
  "type": "form",
  "name": "Project Card Form",
  "parent_module": "module:contract-list",
  "form_id": "anken_cardForm",
  "form_bean_class": "AnkenCardForm",
  "scope": "request",
  "submission_action": "/keiyakuListInit.do",
  "description": "Form for project context data used in screen initialization",
  "fields": "ankenNo;keiyakuKey;contractType",
  "source_file_0": "ctc-data-en/contract-list/components/form-fields-en.md"
}
```

---

## Example Entities and Relationships

**Entities Array:**
```json
{
  "entities": [
    {
      "id": "screen:contract_list_main",
      "type": "screen",
      "name": "Contract List Main Screen",
      "parent_module": "module:contract-list",
      "screen_id": "GCNT90001",
      "title": "Contract List",
      "url_pattern": "/dsmart/contract/keiyakuList/keiyakuListInit.do",
      "layout_type": "data_table",
      "main_jsp": "keiyakuList.jsp",
      "action_class": "KeiyakuListInitAction",
      "description": "Main contract list screen displaying all contracts in tabular format",
      "source_file_0": "ctc-data-en/contract-list/overview-en.md"
    },
    {
      "id": "function:contract_deletion",
      "type": "function",
      "name": "Contract Deletion Feature",
      "parent_module": "module:contract-list",
      "function_name": "delete-contract",
      "url": "/dsmart/contract/keiyakuList/keiyakuListDispatch.do?actionType=delete_contract",
      "parameters": "{\"actionType\":{\"name\":\"actionType\",\"type\":\"String\",\"value\":\"delete_contract\",\"required\":true},\"keiyakuKey\":{\"name\":\"keiyakuKey\",\"type\":\"Long\",\"description\":\"Selected contract key to delete\",\"required\":true}}",
      "return_type": "Forward",
      "output_success": "/keiyakuListInit.do",
      "description": "Performs logical deletion of selected contract",
      "source_file_0": "ctc-data-en/contract-list/functions/delete-contract/function-overview-en.md"
    },
    {
      "id": "form:anken_cardForm",
      "type": "form",
      "name": "Project Card Form",
      "parent_module": "module:contract-list",
      "form_id": "anken_cardForm",
      "form_bean_class": "AnkenCardForm",
      "scope": "request",
      "fields": "ankenNo;keiyakuKey;contractType",
      "description": "Form for project context data",
      "source_file_0": "ctc-data-en/contract-list/components/form-fields-en.md"
    }
  ],
  "relationships": [
    {
      "source": "screen:contract_list_main",
      "target": "module:contract-list",
      "relationship_type": "BELONGS_TO"
    },
    {
      "source": "function:contract_deletion",
      "target": "module:contract-list",
      "relationship_type": "BELONGS_TO"
    },
    {
      "source": "screen:contract_list_main",
      "target": "function:contract_deletion",
      "relationship_type": "PROVIDES",
      "function_category": "contract_management"
    },
    {
      "source": "function:contract_deletion",
      "target": "form:anken_cardForm",
      "relationship_type": "USES_FORM",
      "usage_context": "Contract context data"
    },
    {
      "source": "screen:contract_list_main",
      "target": "screen:housing_contract",
      "relationship_type": "NAVIGATES_TO",
      "trigger": "Housing contract selection",
      "condition": "User selects housing contract type"
    }
  ]
}
```

**Key Points:**
- Entities have NO relationship fields (`parent_screen_id`, `parent_module_id`, etc.)
- Relationships are stored in a separate array
- All properties are at the top level (no nesting)
- Form IDs use original bean class names (e.g., `form:anken_cardForm`)
- Function names match folder names (e.g., `delete-contract`, `init-screen`)

---

## Task Execution

1. **Read** all markdown files in the `ctc-data-en/contract-list/` directory
2. **Identify** all entities according to the taxonomy (excluding database table entities and component entities)
3. **Extract** entity information according to the schema:
   - For screens: Use `ctc-data-en/contract-list/screen-flow-en.md` as the primary source
   - For functions: Use `ctc-data-en/contract-list/functions/` as the primary source (init-screen and delete-contract)
   - For forms: Use `ctc-data-en/contract-list/components/form-fields-en.md` as the primary source
   - For sessions: Extract session attributes from function overviews and overview documents
   - **DO NOT include relationship fields** like `parent_screen_id`, `parent_module_id`

4. **Extract** relationships according to the relationship taxonomy:
   - BELONGS_TO: For all hierarchical relationships (Screen→Module, Function→Module, etc.)
   - PROVIDES: For Screen→Function relationships
   - USES_FORM: For Function→Form relationships
   - STORES: For Function/Screen→Session relationships
   - NAVIGATES_TO: For Screen→Screen navigation flows

5. **Validate** JSON structure and required fields
6. **Output** to `json/contract-list/contract-list-entities.json` with structure:
   ```json
   {
     "entities": [ /* array of entity objects */ ],
     "relationships": [ /* array of relationship objects */ ]
   }
   ```

**Format Guidelines:**
- **All properties at top level** - no nested `properties` or `metadata` objects
- **Source files** use `source_file_0`, `source_file_1` naming
- **Arrays** converted to semicolon-separated strings where appropriate
- **Complex parameters** as stringified JSON for function entities
- **NO relationship fields** in entities - use relationships array only
- **Relationships are separate** from entities in the JSON structure
- **Form IDs** use original bean class names (e.g., `form:anken_cardForm`)

Focus on precision, completeness, and maintaining the semantic meaning from the source documentation. 