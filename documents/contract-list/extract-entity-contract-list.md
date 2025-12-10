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
Output must be a valid JSON file containing an array of entity objects.

### Entity Schema
Each entity must follow this structure:

```json
{
  "id": "<type>:<unique_name>",
  "type": "<entity_type>",
  "name": "<human_readable_name>",
  "parent_module": "module:contract-list",
  "<property_name>": "<property_value>",
  "source_file": "<relative_path_to_source_file>"
}
```

### Required Fields
- **id**: Unique identifier in format `<type>:<name>` (e.g., `screen:contract_list_main`)
- **type**: Entity type from the taxonomy below
- **name**: The extracted name
- **parent_module**: Always `"module:contract-list"` for this extraction
- **source_file**: Source file path for traceability
- **Additional fields**: Type-specific properties (see entity taxonomy) as direct fields

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
- **Fields:** form_id, form_bean_class, scope, submission_action
- **Notes:** Struts form beans used for request/response handling. Form fields should be extracted as separate `form_field` entities.

### 5. Form Field Entities
- **Type ID:** `form_field`
- **Fields:** field_name, field_type, required, validation_rules, form_id
- **Notes:** Individual form fields extracted separately from form entities for better relationship modeling.

### 6. Session Entities
- **Type ID:** `session`
- **Fields:** session_key, scope, lifecycle, stored_data
- **Notes:** Session attributes used to maintain state across requests

### 7. Function Entities
- **Type ID:** `function`
- **Fields:** function_name, parameters (stringified JSON), return_type, business_logic, used_database_tables
- **Notes:** The function is mentioned in the "ctc-data-en/contract-list/overview-en.md" and listed in "ctc-data-en/contract-list/functions" as:
  + **1. List Initialization Feature**
  + **2. Contract Deletion Feature**

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
- - **DO NOT reference database entities** - The relationship will be build later
---

## Specific Focus for This Task

**Primary Objective:** Extract all **Entities** from the contract-list module.

### Important Notes

1. **Screen Extraction Source**: All screens navigable from this module are documented in `ctc-data-en/contract-list/screen-flow-en.md`. Extract each screen mentioned in the "Main Features" section as a separate screen entity, including:
   - Contract List Screen (keiyakuListInit)
   - Contract Type Selection (keiyakuListAssign)
   - Additional Contract Creation (tsuikaKeiyakuDispatch)
   - Contract Modification (henkoKeiyakuDispatch)
   - Contract Deletion (keiyakuDelete)
   - After-Sales Contract (yuusyouKeiyakuListAssign)
   - Multiple Orders (moushideSelectInit)
   - Contract Details (anchorKeiyakuDispatch)

2. **Database Tables**: DO NOT create separate database entities or reference tables in entity properties

3. **Layered Architecture**: Component entities (Action, Delegate, Facade, Product, DAO) are documented separately in `extract-component-entity-contract-list.md` and will not be listed in this task

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
  "source_file": "ctc-data-en/contract-list/overview-en.md"
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
  "source_file": "ctc-data-en/contract-list/overview-en.md"
}
```

### Example Form Entity
```json
{
  "id": "form:anken_card_form",
  "type": "form",
  "name": "Project Card Form",
  "parent_module": "module:contract-list",
  "form_id": "anken_cardForm",
  "form_bean_class": "AnkenCardForm",
  "scope": "request",
  "submission_action": "/keiyakuListInit.do",
  "description": "Form for project context data used in screen initialization",
  "source_file": "ctc-data-en/contract-list/components/form-fields-en.md"
}
```

### Example Form Field Entity
```json
{
  "id": "form_field:anken_no",
  "type": "form_field",
  "name": "Project Number Field",
  "parent_module": "module:contract-list",
  "field_name": "ankenNo",
  "field_type": "String",
  "required": true,
  "form_id": "anken_cardForm",
  "validation_rules": "ankenNo is required for screen initialization",
  "source_file": "ctc-data-en/contract-list/components/form-fields-en.md"
}
```
---

## Task Execution

1. **Read** all markdown files in the `ctc-data-en/contract-list/` directory
2. **Identify** all entities according to the taxonomy (excluding database table entities and component entities)
3. **Extract** entity information according to the schema
   - For screens: Use `ctc-data-en/contract-list/screen-flow-en.md` as the primary source
   - For functions: Use `ctc-data-en/contract-list/functions` as the primary source
   - For forms and form fields: Use `ctc-data-en/contract-list/components/form-fields-en.md` as the primary source
   - **Create separate entities for form fields** with relationships to parent forms
   - **Convert array fields to semicolon-separated strings** (e.g., fields, validation_rules)
   - **Convert complex parameters to stringified JSON** for function entities

4. **Validate** JSON structure and required fields
5. **Output** entities to appropriate JSON files:
   - Main entities: `json/contract-list-entities.json`

**Format Guidelines:**
- No nested properties - all fields at root level
- Arrays converted to semicolon-separated strings
- Complex objects (like function parameters) as stringified JSON
- Forms and form fields as separate entities for better relationship modeling

Focus on precision, completeness, and maintaining the semantic meaning from the source documentation. 