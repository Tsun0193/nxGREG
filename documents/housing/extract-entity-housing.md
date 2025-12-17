# Entity Extraction Instruction: Housing Contract Module

## Role & Context
You are a professional technical document analyzer and knowledge graph database expert specializing in system documentation analysis.

**Project Goal:** Build a comprehensive knowledge graph RAG system for a contract management system by extracting entities and their relationships from structured markdown documentation.

**Current Task:** Extract all entities with their properties AND their relationships from the housing module documentation. Output format follows Neo4j-compatible structure with separate entities and relationships arrays.

---

## Input Specification

### Source Directory
**Path:** `ctc-data-en/housing/`

**Structure:**
```
ctc-data-en/housing/
├── housing-contract-overview-en.md
├── basic-info-housing-contract/
│   ├── overview-en.md
│   ├── data-architecture-en.md
│   ├── screen-flow-en.md
│   ├── components/
│   │   ├── description-ui-en.md
│   │   ├── form-fields-en.md
│   │   └── validation-rules-en.md
│   ├── functions/
│   │   ├── init-screen/
│   │   │   ├── function-overview-en.md
│   │   │   ├── sequence-diagram-en.md
│   │   │   └── sql-queries-en.md
│   │   ├── register-contract/
│   │   │   ├── function-overview-en.md
│   │   │   ├── sequence-diagram-en.md
│   │   │   └── sql-queries-en.md
│   │   ├── update-participants/
│   │   │   ├── function-overview-en.md
│   │   │   ├── sequence-diagram-en.md
│   │   │   └── sql-queries-en.md
│   │   └── validation-contract/
│   │       ├── function-overview-en.md
│   │       ├── sequence-diagram-en.md
│   │       └── sql-queries-en.md
│   └── screen-specification/
│       ├── display-conditions-en.md
│       └── event_handling_rules-en.md
├── order-info/
│   └── description_jyutyu_init_screen-en.md
├── contruction-planning/
│   └── description_koutei_init_screen-en.md
├── accounting-registration/
│   └── description_keiri_init_screen-en.md
├── loan-info/
│   └── description_loan_init_screen-en.md
├── supplementary-contract-info/
│   └── description_hokan_init_screen-en.md
├── collection-conditions/
│   └── description_shuukin_init_screen-en.md
├── various-expenses-&-special-terms/
│   └── description_zatsuhi_init_screen-en.md
├── obstacle-factors/
│   └── description_shougai_init_screen-en.md
├── cancellation-info/
│   └── description_kaiyaku_init_screen-en.md
└── change-info/
    └── description_henkou_init_screen-en.md
```

**Module Hierarchy:**
- **Main Module:** `housing` (Housing Contract)
- **Tab Screens:** 11 tab-based screens representing different aspects of housing contract management
- **Sibling Modules:** `contract-list`, `simple`

**Documentation Organization:**
The housing module contains 11 folders corresponding to the 11 tab screens:
1. **basic-info-housing-contract/** - Tab 1: Basic Information (most comprehensive documentation)
2. **order-info/** - Tab 2: Order Information (impact analysis from Tab 1)
3. **contruction-planning/** - Tab 3: Process Planning (impact analysis from Tab 1)
4. **accounting-registration/** - Tab 4: Accounting Registration (impact analysis from Tab 1)
5. **loan-info/** - Tab 5: Loan Information (impact analysis from Tab 1)
6. **supplementary-contract-info/** - Tab 6: Supplementary Matters (impact analysis from Tab 1)
7. **collection-conditions/** - Tab 7: Collection Conditions (impact analysis from Tab 1)
8. **various-expenses-&-special-terms/** - Tab 8: Miscellaneous Expenses (impact analysis from Tab 1)
9. **obstacle-factors/** - Tab 9: Obstacle Factors (impact analysis from Tab 1)
10. **cancellation-info/** - Tab 10: Cancellation Information (impact analysis from Tab 1)
11. **change-info/** - Tab 11: Change Information (impact analysis from Tab 1)

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
      "parent_module": "module:housing",
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
- **id**: Unique identifier in format `<type>:<name>` (e.g., `screen:housing_contract_main`)
- **type**: Entity type from the taxonomy below
- **name**: Human-readable name
- **parent_module**: Always `"module:housing"` for this extraction
- **source_file_0**: Primary source file path (use `source_file_0`, `source_file_1` for multiple sources)
- **All properties at top level**: No nested `properties` or `metadata` objects
- **DO NOT include relationship fields**: No `parent_screen_id`, `parent_tab_id`, `parent_module_id` - use relationships array instead

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
- **Fields:** module_name, dependencies, description, tab_based_interface, main_screens
- **Notes:** Extract only the main module (housing). This is NOT a nested module structure - it's a tab-based interface with 11 screens

### 2. Screen Entities
- **Type ID:** `screen`
- **Fields:** screen_id, title, url_pattern, access_level, layout_type, tab_code, gcnt_id, main_jsp, action_class, has_tabs, tab_count
- **Notes:** All screens navigable from this module are documented in `ctc-data-en/housing/basic-info-housing-contract/screen-flow-en.md`. Extract each screen as a separate entity including the 11 main tabs:
  - Tab 1: Basic Information (Contract Basic Information)
  - Tab 2: Order Information (Main Order)
  - Tab 3: Process Planning (Process Planning)
  - Tab 4: Accounting Registration (For Accounting Registration)
  - Tab 5: Loan Information (Loan/Public Housing)
  - Tab 6: Supplementary Matters (Contractor Supplementary Information)
  - Tab 7: Collection Conditions (Collection Conditions)
  - Tab 8: Miscellaneous Expenses (Expenses/Special Terms)
  - Tab 9: Obstacle Factors (Obstacle Factors)
  - Tab 10: Cancellation Information (Cancellation Information)
  - Tab 11: Change Information (Change Information)
- **DO NOT include:** `parent_module_id` - use BELONGS_TO relationship instead

### 3. Form Entities
- **Type ID:** `form`
- **Fields:** form_id, form_bean_class, scope, submission_action, description, fields (semicolon-separated list of field names)
- **Notes:** Struts form beans used for request/response handling. Include all form fields as a semicolon-separated list in the `fields` property.

### 4. Session Entities
- **Type ID:** `session`
- **Fields:** session_key, scope, lifecycle, stored_data, description
- **Notes:** Session attributes used to maintain state across requests

### 5. Function Entities
- **Type ID:** `function`
- **Fields:** function_name, parameters (stringified JSON), return_type, business_logic, url, validation_rules, output_success, output_failure
- **Notes:** The functions are documented in "ctc-data-en/housing/basic-info-housing-contract/functions" as:
  + **1. Housing Contract Screen Initialization** (init-screen)
  + **2. Housing Contract Registration** (register-contract)
  + **3. Contract Partner/Building Owner Update** (update-participants)
  + **4. Housing Contract Validation** (validation-contract)
- Keep the function name as the same as the folder name
- **DO NOT include:** `parent_tab_id`, `used_database_tables` - use BELONGS_TO and ACCESSES relationships instead

### 6. Tab Entities
- **Type ID:** `tab`
- **Fields:** tab_code, tab_name, tab_index, gcnt_id, associated_screen_id, action_class, documentation_folder, documentation_type, key_functions
- **Notes:** The housing contract system uses a tab-based interface with 11 main tabs. Extract each tab as a separate entity.
- **DO NOT include:** `parent_screen_id`, `affected_by` - use BELONGS_TO and AFFECTS relationships instead

---

## Relationship Taxonomy

Extract the following relationship types between entities:

### 1. BELONGS_TO Relationship
- **Source:** Screen, Tab, Function, Form, Session
- **Target:** Module, Screen, Tab, Form
- **Description:** Represents hierarchical ownership/containment
- **Properties:**
  - `relationship_type`: "BELONGS_TO"

**Examples:**
```json
{
  "source": "screen:housing_contract_main",
  "target": "module:housing",
  "relationship_type": "BELONGS_TO"
},
{
  "source": "tab:basic_information",
  "target": "screen:housing_contract_main",
  "relationship_type": "BELONGS_TO"
},
{
  "source": "function:init_screen",
  "target": "tab:basic_information",
  "relationship_type": "BELONGS_TO"
}
```

### 2. HAS_TAB Relationship
- **Source:** Screen
- **Target:** Tab
- **Description:** Screen contains multiple tabs (inverse of BELONGS_TO for clarity)
- **Properties:**
  - `relationship_type`: "HAS_TAB"
  - `tab_index`: Position of tab in the interface
  - `is_default`: Whether this is the default tab

**Example:**
```json
{
  "source": "screen:housing_contract_main",
  "target": "tab:basic_information",
  "relationship_type": "HAS_TAB",
  "tab_index": 1,
  "is_default": true
}
```

### 3. PROVIDES Relationship
- **Source:** Tab, Screen
- **Target:** Function
- **Description:** Tab or screen provides specific functionality
- **Properties:**
  - `relationship_type`: "PROVIDES"
  - `function_category`: Type of function provided

**Example:**
```json
{
  "source": "tab:basic_information",
  "target": "function:register_contract",
  "relationship_type": "PROVIDES",
  "function_category": "contract_registration"
}
```

### 4. USES_FORM Relationship
- **Source:** Function, Screen, Tab
- **Target:** Form
- **Description:** Component uses a form for data input/submission
- **Properties:**
  - `relationship_type": "USES_FORM"
  - `usage_context`: How the form is used

**Example:**
```json
{
  "source": "function:register_contract",
  "target": "form:jutakuKeiyakuKihonForm",
  "relationship_type": "USES_FORM",
  "usage_context": "Housing contract data submission"
}
```

### 5. AFFECTS Relationship
- **Source:** Tab
- **Target:** Tab
- **Description:** Changes in source tab impact target tab
- **Properties:**
  - `relationship_type`: "AFFECTS"
  - `impact_type`: Type of impact (data, display, validation, etc.)
  - `description`: How the source affects the target

**Example:**
```json
{
  "source": "tab:basic_information",
  "target": "tab:order_information",
  "relationship_type": "AFFECTS",
  "impact_type": "data",
  "description": "Basic information changes update order data display"
}
```

### 6. STORES Relationship
- **Source:** Function, Screen, Tab
- **Target:** Session
- **Description:** Component stores data in session
- **Properties:**
  - `relationship_type`: "STORES"
  - `storage_purpose`: Why data is stored

**Example:**
```json
{
  "source": "function:init_screen",
  "target": "session:mainVO",
  "relationship_type": "STORES",
  "storage_purpose": "Preserve contract data across tabs"
}
```

### 7. NAVIGATES_TO Relationship
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
  "source": "screen:contract_list",
  "target": "screen:housing_contract_main",
  "relationship_type": "NAVIGATES_TO",
  "trigger": "New Housing Contract button click",
  "condition": "User has create permission"
}
```

### Relationship Extraction Rules

1. **Hierarchy Pattern:** Extract BELONGS_TO relationships for all containment hierarchies:
   - Screen → Module
   - Tab → Screen  
   - Function → Tab
   - Session → Module

2. **Bidirectional Clarity:** Use both BELONGS_TO and HAS_TAB for Screen↔Tab to make relationships explicit in both directions

3. **Data Flow:** Use AFFECTS for tabs that influence each other (e.g., Basic Information affects all other 10 tabs)

4. **Session Management:** Use STORES for functions/tabs that save data to session entities

5. **Completeness:** For each entity, extract:
   - At least one BELONGS_TO relationship (except Module)
   - All functional relationships (PROVIDES, USES_FORM, etc.)
   - All navigation flows (NAVIGATES_TO)
   - All data dependencies (AFFECTS, STORES)

---

## Entities Extracted to Separate Files

### Component Entities
**For Action, Delegate, Facade, Product, and DAO entities**, refer to:
**📄 [Component Entity Extraction Guide](extract-component-entity-housing.md)**

These architectural component entities have been moved to a separate instruction file to reduce token usage. They include:
- Action Entities (Struts actions)
- Delegate Entities (business delegates)
- Facade Entities (facade beans)
- Product Entities (business logic products)
- DAO Entities (data access objects)

**Note**: Do not create the component entities in this task

### UI & Interaction Entities
**For View, Button, Route, Action Type, Event, and Flag entities**, refer to:
**📄 [UI & Interaction Entity Extraction Guide](extract-ui-interaction-entity-housing.md)**

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

**Primary Objective:** Extract all **Entities** from the housing module.

### Important Notes

1. **Module Structure**: The housing module is NOT nested - it's a single module with a tab-based interface:
   - **Main Module**: `housing` (Housing Contract)
   - **11 Tab Screens**: Basic Information, Order Information, Process Planning, Accounting Registration, Loan Information, Supplementary Matters, Collection Conditions, Miscellaneous Expenses, Obstacle Factors, Cancellation Information, Change Information
   - The `basic-info-housing-contract` folder contains the most detailed documentation for Tab 1 (Basic Information)
   - The other 10 folders contain impact analysis documents showing how Tab 1 affects the remaining tabs

2. **Screen Extraction Source**: All screens navigable from this module are documented in `ctc-data-en/housing/basic-info-housing-contract/screen-flow-en.md`. The module uses ONE main JSP that displays 11 different tabs. Extract:
   - Housing Contract Main Screen - Main container screen
   - Tab 1: Basic Information - Primary documentation in `basic-info-housing-contract/`
   - Tab 2-11: Impact analysis tabs in their respective folders

3. **Tab-Based Interface**: This module uses a tab-based navigation system where all 11 tabs share the same JSP file but show different content. Extract tab entities separately with their associated properties (tab_code, gcnt_id, action_class, etc.)

4. **Database Tables**: DO NOT create separate database entities or reference tables in entity properties

5. **Layered Architecture**: Component entities (Action, Delegate, Facade, Product, DAO) are documented separately in `extract-component-entity-housing.md` and will not be listed in this task

---

### Example Entities and Relationships

**Entities Array:**
```json
{
  "entities": [
    {
      "id": "screen:housing_contract_main",
      "type": "screen",
      "name": "Housing Contract Main Screen",
      "parent_module": "module:housing",
      "screen_id": "GCNT18101",
      "title": "Housing Contract (Contract Card)",
      "url_pattern": "/dsmart/contract/jutakuKeiyaku/kihonInit.do",
      "main_jsp": "kihon.jsp",
      "action_class": "KihonInitAction",
      "layout_type": "tab_based_interface",
      "has_tabs": true,
      "tab_count": 11,
      "description": "Main screen for housing contract management with 11 tabs",
      "source_file_0": "ctc-data-en/housing/basic-info-housing-contract/screen-flow-en.md"
    },
    {
      "id": "tab:basic_information",
      "type": "tab",
      "name": "Basic Information Tab",
      "parent_module": "module:housing",
      "tab_code": "TABCD_KEIYAKUKIHONJYOUHOU",
      "tab_name": "Contract Basic Information",
      "tab_index": 1,
      "gcnt_id": "GCNT18001",
      "associated_screen_id": "kihon.jsp",
      "action_class": "KihonInitAction",
      "documentation_folder": "basic-info-housing-contract",
      "key_functions": "Housing contract initialization; New contract registration; Contract partner/building owner update; Housing contract validation",
      "description": "Primary tab - manages housing contract basic information with contractor and building owner management",
      "source_file_0": "ctc-data-en/housing/basic-info-housing-contract/screen-flow-en.md"
    },
    {
      "id": "tab:order_information",
      "type": "tab",
      "name": "Order Information Tab",
      "parent_module": "module:housing",
      "tab_code": "TABCD_HONTAIJUTYU",
      "tab_name": "Main Order",
      "tab_index": 2,
      "gcnt_id": "GCNT18002",
      "associated_screen_id": "kihon.jsp",
      "action_class": "JyutyuInitAction",
      "documentation_folder": "order-info",
      "documentation_type": "impact_analysis",
      "description": "Displays order/purchase information for housing contracts - affected by changes made in Basic Information tab",
      "source_file_0": "ctc-data-en/housing/order-info/description_jyutyu_init_screen-en.md"
    },
    {
      "id": "function:register_contract",
      "type": "function",
      "name": "Housing Contract Registration Feature",
      "parent_module": "module:housing",
      "function_name": "register-contract",
      "url": "/dsmart/contract/jutakuKeiyaku/kihonDispatch.do?actionType=register_contract",
      "parameters": "{\"actionType\":{\"name\":\"actionType\",\"type\":\"String\",\"value\":\"register_contract\",\"required\":true}}",
      "return_type": "Forward",
      "output_success": "/kihonInit.do",
      "output_failure": "/kihonInit.do with error message",
      "description": "Registers new housing contract with basic information, validates data, and creates contract records",
      "validation_rules": "All required fields must be filled; Contract dates must be valid; Customer information must exist",
      "source_file_0": "ctc-data-en/housing/basic-info-housing-contract/functions/register-contract/function-overview-en.md"
    }
  ],
  "relationships": [
    {
      "source": "screen:housing_contract_main",
      "target": "module:housing",
      "relationship_type": "BELONGS_TO"
    },
    {
      "source": "tab:basic_information",
      "target": "screen:housing_contract_main",
      "relationship_type": "BELONGS_TO"
    },
    {
      "source": "screen:housing_contract_main",
      "target": "tab:basic_information",
      "relationship_type": "HAS_TAB",
      "tab_index": 1,
      "is_default": true
    },
    {
      "source": "tab:basic_information",
      "target": "tab:order_information",
      "relationship_type": "AFFECTS",
      "impact_type": "data",
      "description": "Basic information changes update order data display"
    },
    {
      "source": "function:register_contract",
      "target": "tab:basic_information",
      "relationship_type": "BELONGS_TO"
    },
    {
      "source": "tab:basic_information",
      "target": "function:register_contract",
      "relationship_type": "PROVIDES",
      "function_category": "contract_registration"
    }
  ]
}
```

**Key Points:**
- Entities have NO relationship fields (`parent_screen_id`, `parent_tab_id`, etc.)
- Relationships are stored in a separate array
- All properties are at the top level (no nesting)
- Bidirectional relationships (BELONGS_TO + HAS_TAB) make graph traversal easier
- Impact relationships (AFFECTS) show data dependencies between tabs

---

## Task Execution

1. **Read** all markdown files in the `ctc-data-en/housing/` directory (including all 11 subdirectories)
2. **Identify** all entities according to the taxonomy (excluding database table entities and component entities)
3. **Extract** entity information according to the schema:
   - For module: Extract only ONE module entity (housing) - this is NOT a nested structure
   - For screens: Use `ctc-data-en/housing/basic-info-housing-contract/screen-flow-en.md` as the primary source
   - For tabs: Extract each of the 11 tabs with their action classes and documentation sources
   - For functions: Use `ctc-data-en/housing/basic-info-housing-contract/functions/` as the primary source (Tab 1 only)
   - For forms: Use `ctc-data-en/housing/basic-info-housing-contract/components/form-fields-en.md` as the primary source
   - For sessions: Extract session attributes from function overviews and overview documents
   - **DO NOT include relationship fields** like `parent_screen_id`, `parent_tab_id`, `parent_module_id`

4. **Extract** relationships according to the relationship taxonomy:
   - BELONGS_TO: For all hierarchical relationships (Screen→Module, Tab→Screen, Function→Tab, etc.)
   - HAS_TAB: For Screen→Tab relationships (bidirectional with BELONGS_TO)
   - PROVIDES: For Tab/Screen→Function relationships
   - USES_FORM: For Function→Form relationships
   - AFFECTS: For Tab→Tab impact relationships (Basic Information affects all other 10 tabs)
   - STORES: For Function/Tab→Session relationships
   - NAVIGATES_TO: For Screen→Screen navigation flows

5. **Validate** JSON structure and required fields
6. **Output** to `json/housing/housing-entities.json` with structure:
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

Focus on precision, completeness, and maintaining the semantic meaning from the source documentation.
