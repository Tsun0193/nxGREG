# Entity Extraction Instruction: Simple Contract Module

## Role & Context
You are a professional technical document analyzer and knowledge graph database expert specializing in system documentation analysis.

**Project Goal:** Build a comprehensive knowledge graph RAG system for a contract management system by extracting entities and their relationships from structured markdown documentation.

**Current Task:** Extract all entities with their properties AND their relationships from the simple module documentation. Output format follows Neo4j-compatible structure with separate entities and relationships arrays.

---

## Input Specification

### Source Directory
**Path:** `ctc-data-en/simple/`

**Structure:**
```
ctc-data-en/simple/
├── accounting-info-simple-contract/
│   └── description_accounting_init_screen-en.md
├── cancel-info-simple-contract/
│   └── description_cancel_init_screen-en.md
├── order-info-simple-contract/
│   └── description_jyutyu_init_screen-en.md
├── simple-contract-overview-en.md
└── yuusyou-kihon/
    ├── components/
    │   ├── description-ui-en.md
    │   ├── form-fields-en.md
    │   └── validation-rules-en.md
    ├── data-architecture-en.md
    ├── functions/
    │   ├── init-screen/
    │   │   ├── function-overview-en.md
    │   │   ├── sequence-diagram-en.md
    │   │   └── sql-queries-en.md
    │   ├── register-contract/
    │   │   ├── function-overview-en.md
    │   │   ├── sequence-diagram-en.md
    │   │   └── sql-queries-en.md
    │   ├── update-customer/
    │   │   ├── function-overview-en.md
    │   │   ├── sequence-diagram-en.md
    │   │   └── sql-queries-en.md
    │   └── validation-contract/
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
- **Main Module:** `simple` (Simple Contract / Paid Contract)
- **Tab Screens:** 4 tab-based screens representing different aspects of contract management
- **Sibling Modules:** `contract-list`, `housing`

**Documentation Organization:**
The simple module contains 4 folders corresponding to the 4 tab screens:
1. **yuusyou-kihon/** - Tab 1: Basic Information (most comprehensive documentation)
2. **order-info-simple-contract/** - Tab 2: Order Information (impact analysis from Tab 1)
3. **accounting-info-simple-contract/** - Tab 3: Accounting Information (impact analysis from Tab 1)
4. **cancel-info-simple-contract/** - Tab 4: Cancellation Information (impact analysis from Tab 1)

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
      "parent_module": "module:simple",
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
- **id**: Unique identifier in format `<type>:<name>` (e.g., `screen:simple_contract_main`)
- **type**: Entity type from the taxonomy below
- **name**: Human-readable name
- **parent_module**: Always `"module:simple"` for this extraction
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
- **Notes:** Extract only the main module (simple). This is NOT a nested module structure - it's a tab-based interface with 4 screens

### 2. Screen Entities
- **Type ID:** `screen`
- **Fields:** screen_id, title, url_pattern, access_level, layout_type, tab_code, gcnt_id, main_jsp, action_class, has_tabs, tab_count
- **Notes:** All screens navigable from this module are documented in `ctc-data-en/simple/yuusyou-kihon/screen-flow-en.md`. Extract each screen as a separate entity including the 4 main tabs:
  - Tab 1: Basic Information (GCNT19001)
  - Tab 2: Order Information (GCNT19002)
  - Tab 3: Accounting Information (GCNT19009)
  - Tab 4: Cancellation Information (GCNT19012)
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
- **Notes:** The functions are documented in "ctc-data-en/simple/yuusyou-kihon/functions" as:
  + **1. Screen Initialization Feature** (init-screen)
  + **2. Simple Contract Registration Feature** (register-contract)
  + **3. Customer/Contractor Update Feature** (update-customer)
  + **4. Contract Validation Feature** (validation-contract)
- Keep the function name as the same as the folder name
- **DO NOT include:** `parent_tab_id`, `used_database_tables` - use BELONGS_TO and ACCESSES relationships instead

### 6. Tab Entities
- **Type ID:** `tab`
- **Fields:** tab_code, tab_name, tab_index, gcnt_id, associated_screen_id, action_class, documentation_folder, documentation_type, key_functions
- **Notes:** The simple contract system uses a tab-based interface with 4 main tabs. Extract each tab as a separate entity.
- **DO NOT include:** `parent_screen_id`, `affected_by` - use BELONGS_TO and AFFECTS relationships instead

### 7. Form Field Entities
- **Type ID:** `form_field`
- **Fields:** field_name, field_type, required, validation_rules, form_id
- **Notes:** Individual form fields extracted from form documentation
- **DO NOT include:** Nested in forms - create as separate entities with BELONGS_TO relationship

---

## Relationship Taxonomy

Extract the following relationship types between entities:

### 1. BELONGS_TO Relationship
- **Source:** Screen, Tab, Function, Form, Form Field, Session
- **Target:** Module, Screen, Tab, Form
- **Description:** Represents hierarchical ownership/containment
- **Properties:**
  - `relationship_type`: "BELONGS_TO"

**Examples:**
```json
{
  "source": "screen:simple_contract_main",
  "target": "module:simple",
  "relationship_type": "BELONGS_TO"
},
{
  "source": "tab:basic_information",
  "target": "screen:simple_contract_main",
  "relationship_type": "BELONGS_TO"
},
{
  "source": "function:init_screen",
  "target": "tab:basic_information",
  "relationship_type": "BELONGS_TO"
},
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
  "source": "screen:simple_contract_main",
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
  "target": "form:yuusyou_keiyakuNewtmp_kihonForm",
  "relationship_type": "USES_FORM",
  "usage_context": "Contract data submission"
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
  "target": "screen:simple_contract_main",
  "relationship_type": "NAVIGATES_TO",
  "trigger": "New Simple Contract button click",
  "condition": "User has create permission"
}
```

### Relationship Extraction Rules

1. **Hierarchy Pattern:** Extract BELONGS_TO relationships for all containment hierarchies:
   - Screen → Module
   - Tab → Screen  
   - Function → Tab
   - Form Field → Form
   - Session → Module

2. **Bidirectional Clarity:** Use both BELONGS_TO and HAS_TAB for Screen↔Tab to make relationships explicit in both directions

3. **Data Flow:** Use AFFECTS for tabs that influence each other (e.g., Basic Information affects Order, Accounting, Cancellation tabs)

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
**📄 [Component Entity Extraction Guide](extract-component-entity-simple.md)**

These architectural component entities have been moved to a separate instruction file to reduce token usage. They include:
- Action Entities (Struts actions)
- Delegate Entities (business delegates)
- Facade Entities (facade beans)
- Product Entities (business logic products)
- DAO Entities (data access objects)

**Note**: Do not create the component entities in this task

### UI & Interaction Entities
**For View, Button, Route, Action Type, Event, and Flag entities**, refer to:
**📄 [UI & Interaction Entity Extraction Guide](extract-ui-interaction-entity-simple.md)**

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

**Primary Objective:** Extract all **Entities** from the simple module.

### Important Notes

1. **Module Structure**: The simple module is NOT nested - it's a single module with a tab-based interface:
   - **Main Module**: `simple` (Simple Contract / Paid Contract)
   - **4 Tab Screens**: Basic Information, Order Information, Accounting Information, Cancellation Information
   - The `yuusyou-kihon` folder contains the most detailed documentation for Tab 1 (Basic Information)
   - The other 3 folders contain impact analysis documents showing how Tab 1 affects Tabs 2, 3, and 4

2. **Screen Extraction Source**: All screens navigable from this module are documented in `ctc-data-en/simple/yuusyou-kihon/screen-flow-en.md`. The module uses ONE main JSP (`kihon.jsp`) that displays 4 different tabs. Extract:
   - Simple Input Contract Screen (kihon.jsp) - Main container screen with GCNT19101
   - Tab 1: Basic Information (GCNT19001) - Primary documentation in `yuusyou-kihon/`
   - Tab 2: Order Information (GCNT19002) - Impact analysis in `order-info-simple-contract/`
   - Tab 3: Accounting Information (GCNT19009) - Impact analysis in `accounting-info-simple-contract/`
   - Tab 4: Cancellation Information (GCNT19012) - Impact analysis in `cancel-info-simple-contract/`
   - Entry point screens from contract-list module (Contract List, Sales Selection, Case Screen, Contract Search)

3. **Tab-Based Interface**: This module uses a tab-based navigation system where all 4 tabs share the same JSP file (`kihon.jsp`) but show different content. Extract tab entities separately with their associated properties (tab_code, gcnt_id, action_class, etc.)

4. **Database Tables**: DO NOT create separate database entities or reference tables in entity properties

5. **Layered Architecture**: Component entities (Action, Delegate, Facade, Product, DAO) are documented separately in `extract-component-entity-simple.md` and will not be listed in this task

---

### Example Entities and Relationships

**Entities Array:**
```json
{
  "entities": [
    {
      "id": "screen:simple_contract_main",
      "type": "screen",
      "name": "Simple Input Contract Screen",
      "parent_module": "module:simple",
      "screen_id": "GCNT19101",
      "title": "Simple Input (Contract Card)",
      "url_pattern": "/dsmart/contract/yuusyouKeiyaku/kihonInit.do",
      "main_jsp": "kihon.jsp",
      "action_class": "KihonInitAction",
      "layout_type": "tab_based_interface",
      "has_tabs": true,
      "tab_count": 4,
      "description": "Main screen for simple contract management with 4 tabs",
      "source_file_0": "ctc-data-en/simple/yuusyou-kihon/screen-flow-en.md"
    },
    {
      "id": "tab:basic_information",
      "type": "tab",
      "name": "Basic Information Tab",
      "parent_module": "module:simple",
      "tab_code": "TABCD_KEIYAKUKIHONJYOUHOU",
      "tab_name": "Contract Basic Information",
      "tab_index": 1,
      "gcnt_id": "GCNT19001",
      "associated_screen_id": "kihon.jsp",
      "action_class": "KihonInitAction",
      "documentation_folder": "yuusyou-kihon",
      "key_functions": "Contract initialization; New contract registration; Customer/contractor update; Contract validation",
      "description": "Primary tab - manages contract basic information with contractor and building owner management",
      "source_file_0": "ctc-data-en/simple/yuusyou-kihon/screen-flow-en.md"
    },
    {
      "id": "tab:order_information",
      "type": "tab",
      "name": "Order Information Tab",
      "parent_module": "module:simple",
      "tab_code": "TABCD_HONTAIJUTYU",
      "tab_name": "Main Order",
      "tab_index": 2,
      "gcnt_id": "GCNT19002",
      "associated_screen_id": "kihon.jsp",
      "action_class": "JyutyuInitAction",
      "documentation_folder": "order-info-simple-contract",
      "documentation_type": "impact_analysis",
      "description": "Displays order/purchase information - affected by changes made in Basic Information tab",
      "source_file_0": "ctc-data-en/simple/order-info-simple-contract/description_jyutyu_init_screen-en.md"
    },
    {
      "id": "function:register_contract",
      "type": "function",
      "name": "Simple Contract Registration Feature",
      "parent_module": "module:simple",
      "function_name": "register-contract",
      "url": "/dsmart/contract/yuusyouKeiyaku/kihonDispatch.do?actionType=register_contract",
      "parameters": "{\"actionType\":{\"name\":\"actionType\",\"type\":\"String\",\"value\":\"register_contract\",\"required\":true}}",
      "return_type": "Forward",
      "output_success": "/kihonInit.do",
      "output_failure": "/kihonInit.do with error message",
      "description": "Registers new simple contract with basic information, validates data, and creates contract records",
      "validation_rules": "All required fields must be filled; Contract dates must be valid; Customer information must exist",
      "source_file_0": "ctc-data-en/simple/yuusyou-kihon/functions/register-contract/function-overview-en.md"
    }
  ],
  "relationships": [
    {
      "source": "screen:simple_contract_main",
      "target": "module:simple",
      "relationship_type": "BELONGS_TO"
    },
    {
      "source": "tab:basic_information",
      "target": "screen:simple_contract_main",
      "relationship_type": "BELONGS_TO"
    },
    {
      "source": "screen:simple_contract_main",
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

1. **Read** all markdown files in the `ctc-data-en/simple/` directory (including all 4 subdirectories)
2. **Identify** all entities according to the taxonomy (excluding database table entities and component entities)
3. **Extract** entity information according to the schema:
   - For module: Extract only ONE module entity (simple) - this is NOT a nested structure
   - For screens: Use `ctc-data-en/simple/yuusyou-kihon/screen-flow-en.md` as the primary source
   - For tabs: Extract each of the 4 tabs with their action classes and documentation sources
   - For functions: Use `ctc-data-en/simple/yuusyou-kihon/functions/` as the primary source (Tab 1 only)
   - For forms: Use `ctc-data-en/simple/yuusyou-kihon/components/form-fields-en.md` as the primary source
   - For form fields: Extract individual fields as separate entities
   - For sessions: Extract session attributes from function overviews and overview documents
   - **DO NOT include relationship fields** like `parent_screen_id`, `parent_tab_id`, `parent_module_id`

4. **Extract** relationships according to the relationship taxonomy:
   - BELONGS_TO: For all hierarchical relationships (Screen→Module, Tab→Screen, Function→Tab, etc.)
   - HAS_TAB: For Screen→Tab relationships (bidirectional with BELONGS_TO)
   - PROVIDES: For Tab/Screen→Function relationships
   - USES_FORM: For Function→Form relationships
   - AFFECTS: For Tab→Tab impact relationships
   - STORES: For Function/Tab→Session relationships
   - NAVIGATES_TO: For Screen→Screen navigation flows

5. **Validate** JSON structure and required fields
6. **Output** to `json/simple/simple-entities.json` with structure:
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
