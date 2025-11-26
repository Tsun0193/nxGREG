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
  "properties": {
    "<property_name>": "<property_value>"
  },
  "metadata": {
    "source_file": "<relative_path_to_source_file>",
  }
}
```

### Required Fields
- **id**: Unique identifier in format `<type>:<name>` (e.g., `screen:contract_list_main`)
- **type**: Entity type from the taxonomy below
- **name**: The extracted name
- **parent_module**: Always `"module:contract-list"` for this extraction
- **properties**: Type-specific properties (see entity taxonomy)
- **metadata**: Source tracking information

---

## Entity Taxonomy

Extract the following entity types (included but not limited to):

### 1. Module Entities
- **Type ID:** `module`
- **Properties:** module_name, dependencies, child_modules
- **Notes:** Extract the main module and any sub-modules defined in the documentation

### 2. Screen Entities
- **Type ID:** `screen`
- **Properties:** screen_id, title, url_pattern, access_level, layout_type
- **Notes:** All screens navigable from this module are documented in `ctc-data-en/contract-list/screen-flow-en.md`. Extract each screen as a separate entity even if it transitions to different modules.

### 3. Value Object Entities
- **Type ID:** `value_object`
- **Properties:** object_name, fields, validation_rules
- **Notes:** VOs used for data transfer between layers (e.g., KeiyakuVO, AnkenVO, AuthorityVO)

### 4. Form Entities
- **Type ID:** `form`
- **Properties:** form_id, fields, validation_rules, submission_action
- **Notes:** Struts form beans used for request/response handling. All forms can be found in `ctc-data-en/contract-list/components/form-fields-en.md`. There are three total form:
  + 1. `anken_cardForm`
  + 2. `keiyaku_cardForm`
  + 3. `keiyakuListKensakuForm`

### 5. Session Entities
- **Type ID:** `session`
- **Properties:** session_key, scope, lifecycle, stored_data
- **Notes:** Session attributes used to maintain state across requests

### 6. View/UI Entities
- **Type ID:** `view`
- **Properties:** view_name, template, display_conditions, bound_data
- **Notes:** JSP files and view templates

### 7. Function Entities
- **Type ID:** `function`
- **Properties:** function_name, parameters, return_type, business_logic, used_database_tables
- **Notes:**: The function is mention in the "ctc-data-en/contract-list/overview-en.md" and listed in "ctc-data-en/contract-list/functions" as 
  + **1. List Initialization Feature**
  + **2. Contract Deletion Feature**

### 8. Action Type Entities
- **Type ID:** `action_type`
- **Properties:** action type name, Description, spExecuteKbn, Requirements
- **Notes:** The function is mailly mention in the "ctc-data-en/contract-list/screen-specification/display-conditions-en.md" at Action Types and Screen Transitions

### 9. Business/Control Flag
- **Type ID:** `flag`
- **Properties:**  Name, Purpose, Value, Impact
- **Notes:** The function is mailly mention in the "ctc-data-en/contract-list/screen-specification"

---

## Component Entities (Extracted to Separate File)

**For Action, Delegate, Facade, Product, and DAO entities**, refer to:
**📄 [Component Entity Extraction Guide](extract-component-entity-contract-list.md)**

These architectural component entities have been moved to a separate instruction file to reduce token usage. They include:
- Action Entities (Struts actions)
- Delegate Entities (business delegates)
- Facade Entities (facade beans)
- Product Entities (business logic products)
- DAO Entities (data access objects)

**Note**: Do not create the component-entity in this task

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
- Always include `source_file` in metadata
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
  "properties": {
    "screen_id": "GCNT90001",
    "title": "Contract List",
    "url_pattern": "/dsmart/contract/keiyakuList/keiyakuListInit.do",
    "access_level": "authenticated_user",
    "layout_type": "data_table",
    "has_search": true,
    "has_filter": true,
    "pagination": false,
    "main_jsp": "keiyakuList.jsp",
    "action_class": "KeiyakuListInitAction"
  },
  "metadata": {
    "source_file": "ctc-data-en/contract-list/overview-en.md",
  }
}
```

### Example Function Entity with Database References
```json
    {
        "id": "function:contract_deletion",
        "type": "function",
        "name": "Contract Deletion Feature",
        "parent_module": "module:contract_list",
        "properties": {
            "function_name": "Contract Deletion",
            "url": "/dsmart/contract/keiyakuList/keiyakuListDispatch.do?actionType=delete_contract",
            "parameters": [
                {
                    "name": "actionType",
                    "type": "String",
                    "value": "delete_contract",
                    "required": true
                },
                {
                    "name": "keiyakuKey",
                    "type": "Long",
                    "description": "Selected contract key to delete",
                    "required": true
                }
            ],
            "return_type": "Forward",
            "output_success": "/keiyakuListInit.do",
            "output_failure": "/keiyakuListInit.do and error message",
            "description": "Performs logical deletion of selected contract and updates related data",
            "validation_rules": [
                "Contract must exist",
                "Only non-main/non-linked contracts can be deleted"
            ]
        },
        "metadata": {
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
  "properties": {
    "object_name": "KeiyakuVO",
    "fields": ["keiyakuKey", "keiyakuNo", "keiyakuStatusCd", "keiyakuCardSyubetsuCd", "keiyakuUkagaiKbn"],
    "purpose": "Transfer contract data between layers"
  },
  "metadata": {
    "source_file": "ctc-data-en/contract-list/overview-en.md"
  }
}
```
---

## Task Execution

1. **Read** all markdown files in the `ctc-data-en/contract-list/` directory
2. **Identify** all entities according to the taxonomy (excluding database table entities and component entities)
3. **Extract** entity information according to the schema
   - For screens: Use `ctc-data-en/contract-list/screen-flow-en.md` as the primary source
   - For function: Use `ctc-data-en/contract-list/functions` as the primary source
   - For form: Use `ctc-data-en/contract-list/components/form-fields-en.md` as the primary source

4. **Validate** JSON structure and required fields
5. **Output** entities to appropriate JSON files:
   - Main entities: `json/contract-list-entities.json`

Focus on precision, completeness, and maintaining the semantic meaning from the source documentation. 