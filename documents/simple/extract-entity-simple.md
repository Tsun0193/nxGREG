# Entity Extraction Instruction: Simple Contract Module

## Role & Context
You are a professional technical document analyzer and knowledge graph database expert specializing in system documentation analysis.

**Project Goal:** Build a comprehensive knowledge graph RAG system for a contract management system by extracting entities and their relationships from structured markdown documentation.

**Current Task:** Phase 1 - Entity Extraction. Extract all entities with their properties from the simple module documentation to a JSON file before establishing relationships in Phase 2.

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
Output must be a valid JSON file containing an array of entity objects.

### Entity Schema
Each entity must follow this structure:

```json
{
  "id": "<type>:<unique_name>",
  "type": "<entity_type>",
  "name": "<human_readable_name>",
  "parent_module": "module:simple",
  "<property_name>": "<property_value>",
  "source_file": "<relative_path_to_source_file>"
}
```

### Required Fields
- **id**: Unique identifier in format `<type>:<name>` (e.g., `screen:simple_contract_basic_info`)
- **type**: Entity type from the taxonomy below
- **name**: The extracted name
- **parent_module**: Always `"module:simple"` for this extraction
- **source_file**: Source file path for traceability
- **Additional fields**: Type-specific properties (see entity taxonomy) as direct fields

---

## Entity Taxonomy

Extract the following entity types (included but not limited to):

### 1. Module Entities
- **Type ID:** `module`
- **Fields:** module_name, dependencies, description, tab_based_interface, main_screens
- **Notes:** Extract only the main module (simple). This is NOT a nested module structure - it's a tab-based interface with 4 screens

### 2. Screen Entities
- **Type ID:** `screen`
- **Fields:** screen_id, title, url_pattern, access_level, layout_type, tab_code, gcnt_id, main_jsp
- **Notes:** All screens navigable from this module are documented in `ctc-data-en/simple/yuusyou-kihon/screen-flow-en.md`. Extract each screen as a separate entity including the 4 main tabs:
  - Tab 1: Basic Information (GCNT19001)
  - Tab 2: Order Information (GCNT19002)
  - Tab 3: Accounting Information (GCNT19009)
  - Tab 4: Cancellation Information (GCNT19012)

### 3. Form Entities
- **Type ID:** `form`
- **Fields:** form_id, form_bean_class, scope, submission_action, description
- **Notes:** Struts form beans used for request/response handling. Form fields should be extracted as separate `form_field` entities.

### 4. Form Field Entities
- **Type ID:** `form_field`
- **Fields:** field_name, field_type, required, validation_rules, form_id, description
- **Notes:** Individual form fields extracted separately from form entities for better relationship modeling.

### 5. Session Entities
- **Type ID:** `session`
- **Fields:** session_key, scope, lifecycle, stored_data, description
- **Notes:** Session attributes used to maintain state across requests

### 6. Function Entities
- **Type ID:** `function`
- **Fields:** function_name, parameters (stringified JSON), return_type, business_logic, used_database_tables, url, validation_rules
- **Notes:** The functions are documented in "ctc-data-en/simple/yuusyou-kihon/functions" as:
  + **1. Screen Initialization Feature** (init-screen)
  + **2. Simple Contract Registration Feature** (register-contract)
  + **3. Customer/Contractor Update Feature** (update-customer)
  + **4. Contract Validation Feature** (validation-contract)
- Keep the function name as the same as the folder name

### 7. Tab Entities
- **Type ID:** `tab`
- **Fields:** tab_code, tab_name, tab_index, gcnt_id, associated_screen_id, description
- **Notes:** The simple contract system uses a tab-based interface with 4 main tabs. Extract each tab as a separate entity.

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

### Example Module Entity
```json
{
  "id": "module:simple",
  "type": "module",
  "name": "Simple Contract Module",
  "parent_module": "module:contract_system",
  "module_name": "simple",
  "description": "Simple Contract (Paid Contract) - Manages paid contracts for commercial transactions in construction and real estate fields with a tab-based interface",
  "tab_based_interface": true,
  "main_screens": "Basic Information (Tab 1); Order Information (Tab 2); Accounting Information (Tab 3); Cancellation Information (Tab 4)",
  "main_jsp": "kihon.jsp",
  "key_features": "Manages four main aspects: basic information, orders, accounting, and cancellation; Tab-based navigation system; Integration with project and customer management systems",
  "documentation_structure": "yuusyou-kihon (primary); order-info-simple-contract (impact analysis); accounting-info-simple-contract (impact analysis); cancel-info-simple-contract (impact analysis)",
  "source_file": "ctc-data-en/simple/simple-contract-overview-en.md"
}
```

### Example Screen Entity (Main Screen)
```json
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
  "description": "Main screen for simple contract management with 4 tabs: Basic Information, Order Information, Accounting Information, and Cancellation Information",
  "source_file": "ctc-data-en/simple/yuusyou-kihon/screen-flow-en.md"
}
```

### Example Tab Entity (Tab 1)
```json
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
  "description": "Primary tab with the most comprehensive documentation - manages contract basic information with contractor and building owner management",
  "source_file": "ctc-data-en/simple/yuusyou-kihon/screen-flow-en.md"
}
```

### Example Tab Entity (Tab 2)
```json
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
  "affected_by": "tab:basic_information",
  "description": "Displays order/purchase information - affected by changes made in Basic Information tab",
  "source_file": "ctc-data-en/simple/order-info-simple-contract/description_jyutyu_init_screen-en.md"
}
```

### Example Function Entity
```json
{
  "id": "function:simple_contract_registration",
  "type": "function",
  "name": "Simple Contract Registration Feature",
  "parent_module": "module:simple",
  "function_name": "Simple Contract Registration",
  "url": "/dsmart/contract/yuusyouKeiyaku/kihonDispatch.do?actionType=register_contract",
  "parameters": "{\"actionType\":{\"name\":\"actionType\",\"type\":\"String\",\"value\":\"register_contract\",\"required\":true},\"kihonForm\":{\"name\":\"kihonForm\",\"type\":\"KihonForm\",\"description\":\"Form data containing contract information\",\"required\":true}}",
  "return_type": "Forward",
  "output_success": "/kihonInit.do",
  "output_failure": "/kihonInit.do with error message",
  "description": "Registers new simple contract with basic information, validates data, and creates contract records",
  "validation_rules": "All required fields must be filled; Contract dates must be valid; Customer information must exist",
  "source_file": "ctc-data-en/simple/yuusyou-kihon/functions/register-contract/function-overview-en.md"
}
```

### Example Form Entity
```json
{
  "id": "form:kihon_form",
  "type": "form",
  "name": "Basic Information Form",
  "parent_module": "module:simple",
  "form_id": "kihon_form",
  "form_bean_class": "KihonForm",
  "scope": "request",
  "submission_action": "/kihonDispatch.do",
  "description": "Form for simple contract basic information input and submission",
  "source_file": "ctc-data-en/simple/yuusyou-kihon/components/form-fields-en.md"
}
```

### Example Form Field Entity
```json
{
  "id": "form_field:keiyaku_no",
  "type": "form_field",
  "name": "Contract Number Field",
  "parent_module": "module:simple",
  "field_name": "keiyakuNo",
  "field_type": "String",
  "required": true,
  "form_id": "kihon_form",
  "validation_rules": "Must be unique; Maximum 20 characters; Alphanumeric only",
  "description": "Unique identifier for the contract",
  "source_file": "ctc-data-en/simple/yuusyou-kihon/components/form-fields-en.md"
}
```

### Example Session Entity
```json
{
  "id": "session:kihon_form_data",
  "type": "session",
  "name": "Basic Information Form Data Session",
  "parent_module": "module:simple",
  "session_key": "kihonFormData",
  "scope": "session",
  "lifecycle": "Maintained across tab navigation within contract editing session",
  "stored_data": "KihonForm object containing contract basic information",
  "description": "Preserves form data when navigating between tabs in simple contract screen",
  "source_file": "ctc-data-en/simple/yuusyou-kihon/overview-en.md"
}
```

---

## Task Execution

1. **Read** all markdown files in the `ctc-data-en/simple/` directory (including all 4 subdirectories)
2. **Identify** all entities according to the taxonomy (excluding database table entities and component entities)
3. **Extract** entity information according to the schema
   - For module: Extract only ONE module entity (simple) - this is NOT a nested structure
   - For screens: Use `ctc-data-en/simple/yuusyou-kihon/screen-flow-en.md` as the primary source
   - For tabs: Extract each of the 4 tabs with their action classes and documentation sources:
     * Tab 1 (Basic Information): Primary documentation in `yuusyou-kihon/`
     * Tab 2 (Order Information): Impact analysis in `order-info-simple-contract/`
     * Tab 3 (Accounting Information): Impact analysis in `accounting-info-simple-contract/`
     * Tab 4 (Cancellation Information): Impact analysis in `cancel-info-simple-contract/`
   - For functions: Use `ctc-data-en/simple/yuusyou-kihon/functions/` as the primary source (Tab 1 only)
   - For forms and form fields: Use `ctc-data-en/simple/yuusyou-kihon/components/form-fields-en.md` as the primary source
   - **Create separate entities for form fields** with relationships to parent forms
   - **Create separate entities for tabs** with their navigation properties and action classes
   - **Convert array fields to semicolon-separated strings** (e.g., fields, validation_rules)
   - **Convert complex parameters to stringified JSON** for function entities

4. **Validate** JSON structure and required fields
5. **Output** entities to appropriate JSON files:
   - Main entities: `json/simple-entities.json`

**Format Guidelines:**
- No nested properties - all fields at root level
- Arrays converted to semicolon-separated strings
- Complex objects (like function parameters) as stringified JSON
- Forms and form fields as separate entities for better relationship modeling
- Tabs as separate entities linked to their parent screen

Focus on precision, completeness, and maintaining the semantic meaning from the source documentation.
