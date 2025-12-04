# UI & Interaction Entity Extraction Instruction: Contract List Module

## Role & Context
This document specifies the extraction of UI and interaction-related entities from the contract-list module documentation. These entities complement the main entity extraction and focus on user interface components, routing, and user interactions.

**Parent Document:** `extract-entity-contract-list.md`

**Current Task:** Extract UI and interaction entities including Views, Buttons, Routes, Action Types, Events, and Flags.

---

## Input Specification

### Source Directory
**Path:** `ctc-data-en/contract-list/`

**Primary Source Files:**
- `screen-specification/display-conditions-en.md` - Action types, flags, display conditions
- `screen-specification/event_handling_rules-en.md` - Events, button behaviors
- `screen-flow-en.md` - Routes, screen transitions
- `components/description-ui-en.md` - UI components, views
- `overview-en.md` - General UI structure

---

## Neo4j Compatibility Requirements

**CRITICAL:** All extracted entities must be flattened to a single level for Neo4j database compatibility.

### Flattening Rules:

1. **NO Nested Objects:** All properties must be at the top level of the entity object
   - ❌ `"properties": { "prop_name": "value" }`
   - ✅ `"prop_name": "value"`

2. **NO Metadata Nesting:** Source file information goes directly on the entity
   - ❌ `"metadata": { "source_file": "path" }`
   - ✅ `"source_file_0": "path"`

3. **Array Conversion:**
   - Simple lists → semicolon-separated strings
     - Example: `["value1", "value2"]` → `"value1; value2"`
   - Complex objects → stringified JSON
     - Example: `[{"name": "x"}]` → `"[{\"name\":\"x\"}]"`

4. **Remove Relationship Arrays:** 
   - Properties like `bound_data`, `included_components`, `controls` that represent relationships should either:
     - Be converted to semicolon-separated string references, OR
     - Be removed and expressed as separate relationship objects in a future relationship file

5. **Source File Naming:**
   - Use `source_file_0`, `source_file_1`, etc. for multiple sources
   - Never nest under `metadata` object

---

## Entity Taxonomy

### 1. View/UI Entities
- **Type ID:** `view`
- **Properties (flattened):** 
  - `view_name`: Name of the JSP file
  - `template_path`: Full path to the JSP template
  - `display_conditions`: String describing conditions (convert array to semicolon-separated string)
  - `description`: Description of the view purpose
  - `source_file_0`: Primary source file path (flattened from metadata)
- **Removed Properties:** 
  - ❌ `bound_data`: Use BINDS_DATA relationships instead to connect view to data entities
  - ❌ `included_components`: Use INCLUDES relationships instead to connect to fragment views
- **Notes:** JSP files and view templates that render the user interface. All properties are flattened to single level for Neo4j compatibility. Data bindings and component inclusions are now expressed as relationships.
- **Source:** `ctc-data-en/contract-list/components/description-ui-en.md`

**Example:**
```json
{
  "id": "view:keiyaku_list_jsp",
  "type": "view",
  "name": "Contract List View",
  "parent_module": "module:contract-list",
  "view_name": "keiyakuList.jsp",
  "template_path": "docroot/contract/keiyakuList/keiyakuList.jsp",
  "display_conditions": "User must be authenticated; Project must exist",
  "description": "Main JSP view for displaying contract list with action buttons",
  "source_file_0": "ctc-data-en/contract-list/components/description-ui-en.md"
}
```

---

### 2. Button Entities
- **Type ID:** `button`
- **Properties (flattened):** 
  - `button_id`: HTML/DOM identifier for the button
  - `label`: Display text on the button
  - `button_type`: Type of button (action, submit, link)
  - `trigger_event`: Event entity ID this button triggers (use TRIGGERS relationship)
  - `trigger_action_type`: Action type entity ID (use TRIGGERS relationship)
  - `enabled_condition`: String describing when button is enabled
  - `visibility_flag`: Flag entity ID controlling visibility (use CONTROLLED_BY relationship)
  - `position`: Position on screen (top_action_bar, row_action, etc.)
  - `description`: Description of button purpose
  - `source_file_0`: Primary source file path (flattened from metadata)
- **Notes:** UI buttons that trigger actions on screens. All properties are flattened to single level for Neo4j compatibility.
- **Source:** `ctc-data-en/contract-list/screen-specification/event_handling_rules-en.md`

**Example:**
```json
{
  "id": "button:new_contract",
  "type": "button",
  "name": "New Contract Button",
  "parent_module": "module:contract-list",
  "button_id": "btnNewContract",
  "label": "New Contract",
  "button_type": "action",
  "trigger_event": "new_contract_button_click",
  "trigger_action_type": "new_contract",
  "enabled_condition": "ankenNo exists and project is active",
  "visibility_flag": "CONTRACT_SHINKI_KEIYAKU_SAKUSEI_KAHI_FLG",
  "position": "top_action_bar",
  "description": "Button to initiate new contract creation workflow",
  "source_file_0": "ctc-data-en/contract-list/screen-specification/event_handling_rules-en.md"
}
```

---

### 3. Route/URL Entities
- **Type ID:** `route`
- **Properties (flattened):** 
  - `route_path`: URL path for the route
  - `http_method`: Comma-separated HTTP methods (e.g., "GET, POST")
  - `mapped_action`: Action entity ID this route maps to (use MAPS_TO relationship)
  - `requires_authentication`: Boolean for authentication requirement
  - `parameters`: Stringified JSON array of parameter objects
  - `forward_destinations`: Stringified JSON array of forward destination objects
  - `description`: Description of route purpose
  - `source_file_0`: Primary source file path (flattened from metadata)
- **Notes:** HTTP endpoints that map requests to Actions. All properties are flattened to single level for Neo4j compatibility. Complex arrays are stringified JSON.
- **Source:** `ctc-data-en/contract-list/screen-flow-en.md`

**Example:**
```json
{
  "id": "route:keiyaku_list_init",
  "type": "route",
  "name": "Contract List Initialization Route",
  "parent_module": "module:contract-list",
  "route_path": "/dsmart/contract/keiyakuList/keiyakuListInit.do",
  "http_method": "GET, POST",
  "mapped_action": "KeiyakuListInitAction",
  "requires_authentication": true,
  "parameters": "[{\"name\":\"ankenNo\",\"type\":\"Long\",\"required\":true,\"description\":\"Project number to load contract list\"}]",
  "forward_destinations": "[{\"name\":\"success\",\"target\":\"/contract/keiyakuList/keiyakuList.jsp\"},{\"name\":\"error\",\"target\":\"/contract/error.jsp\"}]",
  "description": "Entry point for displaying contract list screen",
  "source_file_0": "ctc-data-en/contract-list/screen-flow-en.md"
}
```

---

### 4. Action Type Entities
- **Type ID:** `action_type`
- **Properties (flattened):** 
  - `action_type_name`: Name of the action type
  - `description`: Description of the action type purpose
  - `sp_execute_kbn`: Special execution classification code
  - `requirements`: Semicolon-separated string of requirements
  - `triggered_by`: Button entity ID that triggers this action type (use TRIGGERED_BY relationship)
  - `forwards_to`: Target route/action path
  - `validation_rules`: Semicolon-separated string of validation rules
  - `source_file_0`: Primary source file path (flattened from metadata)
- **Notes:** Dispatch action types that determine routing behavior in KeiyakuListDispatchAction. All properties are flattened to single level for Neo4j compatibility.
- **Source:** `ctc-data-en/contract-list/screen-specification/display-conditions-en.md` at "Action Types and Screen Transitions"

**Example:**
```json
{
  "id": "action_type:new_contract",
  "type": "action_type",
  "name": "New Contract Action Type",
  "parent_module": "module:contract-list",
  "action_type_name": "new_contract",
  "description": "Action type for creating a new contract",
  "sp_execute_kbn": "1",
  "requirements": "User must have new contract creation permission; Project must be in valid status",
  "triggered_by": "button:new_contract",
  "forwards_to": "/keiyakuListAssign.do",
  "validation_rules": "ankenNo must exist; shinkiKeiyakuSakuseiKahiFlg must be true",
  "source_file_0": "ctc-data-en/contract-list/screen-specification/display-conditions-en.md"
}
```

---

### 5. Event Entities
- **Type ID:** `event`
- **Properties (flattened):** 
  - `event_name`: Name of the event
  - `event_type`: Type of event (button_click, form_submit, link_click)
  - `triggered_by`: Button/UI element entity ID that triggers this event (use TRIGGERED_BY relationship)
  - `triggers_action`: Action type entity ID triggered by this event (use TRIGGERS relationship)
  - `event_handler`: Route/handler that processes the event
  - `parameters`: Stringified JSON array of parameter objects
  - `description`: Description of event purpose
  - `source_file_0`: Primary source file path (flattened from metadata)
- **Notes:** User interaction events (clicks, submits) that trigger business actions. All properties are flattened to single level for Neo4j compatibility.
- **Source:** `ctc-data-en/contract-list/screen-specification/event_handling_rules-en.md`

**Example:**
```json
{
  "id": "event:new_contract_button_click",
  "type": "event",
  "name": "New Contract Button Click Event",
  "parent_module": "module:contract-list",
  "event_name": "new_contract_button_click",
  "event_type": "button_click",
  "triggered_by": "button:new_contract",
  "triggers_action": "action_type:new_contract",
  "event_handler": "keiyakuListDispatch.do",
  "parameters": "[{\"name\":\"actionType\",\"value\":\"new_contract\"}]",
  "description": "User clicks the New Contract button to create a new contract",
  "source_file_0": "ctc-data-en/contract-list/screen-specification/event_handling_rules-en.md"
}
```

---

### 6. Business/Control Flag Entities
- **Type ID:** `flag`
- **Properties (flattened):** 
  - `flag_name`: Name of the flag variable
  - `purpose`: Purpose of the flag
  - `data_type`: Data type (Boolean, String, Integer)
  - `possible_values`: Semicolon-separated string of possible values
  - `default_value`: Default value of the flag
  - `controls`: Semicolon-separated string of UI elements controlled (use CONTROLS relationships for graph connections)
  - `source_table`: Database table where flag value originates
  - `storage_location`: Where flag is stored (session, request, database)
  - `impact`: Description of flag's impact on behavior
  - `source_file_0`: Primary source file path (flattened from metadata)
- **Removed Properties:** 
  - ❌ Nested `controls` array: Use CONTROLS relationships instead to connect flag to controlled UI elements
- **Notes:** Boolean flags or status codes that control feature visibility, permissions, and business logic. All properties are flattened to single level for Neo4j compatibility.
- **Source:** `ctc-data-en/contract-list/screen-specification/display-conditions-en.md`

**Example:**
```json
{
  "id": "flag:shinki_keiyaku_sakusei_kahi",
  "type": "flag",
  "name": "New Contract Creation Permission Flag",
  "parent_module": "module:contract-list",
  "flag_name": "shinkiKeiyakuSakuseiKahiFlg",
  "purpose": "Controls whether user has permission to create new contracts",
  "data_type": "Boolean",
  "possible_values": "true; false",
  "default_value": "false",
  "controls": "button:new_contract visibility",
  "source_table": "t_syounin_user",
  "storage_location": "session:CONTRACT_SHINKI_KEIYAKU_SAKUSEI_KAHI_FLG",
  "impact": "When true, displays New Contract button; when false, hides it",
  "source_file_0": "ctc-data-en/contract-list/screen-specification/display-conditions-en.md"
}
```

---

## Extraction Guidelines

### 1. UI Component Extraction
- Extract all JSP views mentioned in the documentation
- Include both main views and included fragments (body.jsp, header.jsp, etc.)
- Capture display conditions and bound data sources

### 2. Button Extraction
- Extract all action buttons mentioned in event handling rules
- Include visibility conditions tied to permission flags
- Document the action type each button triggers

### 3. Route Extraction
- Extract all URL patterns from screen flow documentation
- Map routes to their corresponding Action classes
- Include HTTP methods, parameters, and forward destinations

### 4. Action Type Extraction
- Extract all action types from display conditions and screen transitions
- Document the dispatch logic and routing behavior
- Include validation requirements and prerequisites

### 5. Event Extraction
- Extract all user interaction events (button clicks, form submits, link clicks)
- Map events to their triggers and handlers
- Document the event flow from UI to Action

### 6. Flag Extraction
- Extract all permission flags, display flags, and control flags
- Document the source of flag values (database, session, calculation)
- Map flags to the UI components they control

---

## Common Buttons to Extract

Based on the contract-list module documentation, extract these button entities:

1. **New Contract Button** - Creates new contract
2. **Additional Contract Button** - Creates additional contract
3. **Modify Contract Button** - Modifies existing contract
4. **Delete Contract Button** - Deletes selected contract
5. **After-Sales Contract Button** - Creates after-sales contract
6. **Multiple Orders Button** - Creates multiple orders
7. **Return Button** - Returns to previous screen
8. **Contract Number Link** - Navigates to contract details (hyperlink, treated as button)

---

## Common Routes to Extract

Extract all route entities from the screen flow, including:

1. `/keiyakuListInit.do` - Initial screen load
2. `/keiyakuListFromAfterScreanInit.do` - Return from after-sales screen
3. `/keiyakuListDispatch.do` - Action dispatcher
4. `/keiyakuDelete.do` - Contract deletion
5. `/keiyakuListAssign.do` - Contract type selection
6. `/tsuikaKeiyakuDispatch.do` - Additional contract creation
7. `/henkoKeiyakuDispatch.do` - Contract modification
8. `/yuusyouKeiyakuListAssign.do` - After-sales contract
9. `/moushideSelectInit.do` - Multiple orders
10. `/anchorKeiyakuDispatch.do` - Contract details

---

## Common Action Types to Extract

Extract all action types from display conditions:

1. `new_contract` - New contract creation
2. `add_contract` - Additional contract creation
3. `update_contract` - Contract modification
4. `delete_contract` - Contract deletion
5. `new_yuusyou_contract` - After-sales contract creation
6. `new_yuusyou_after_contract` - Multiple orders creation
7. `keiyaku_card_anchor` - Contract details display
8. `returnAnken` - Return to project
9. `compliance_mikan` - Compliance check incomplete

---

## Common Flags to Extract

Extract all permission and control flags:

### Permission Flags:
1. `shinkiKeiyakuSakuseiKahiFlg` - New contract creation permission
2. `tsuikaKeiyakuSakuseiKahiFlg` - Additional contract creation permission
3. `keiyakuDataHenkoKahiFlg` - Contract modification permission
4. `kaniKeiyakuSakuseiKahiFlg` - After-sales contract creation permission
5. `hukusuJyutyuSakuseiHyoujiFlg` - Multiple orders display permission

### Control Flags:
1. `ankenBunruiCd` - Project classification code
2. `keiyakuCardSyubetsuCd` - Contract card type code
3. `keiyakuUkagaiKbn` - External contract flag
4. `tuikaKbn` - Additional contract classification
5. `preScrean` - Previous screen indicator

---

## Output Specification

### Output File
- **Path:** `json/contract-list-ui-interaction-entities.json`

### JSON Structure (Neo4j Compatible - Flattened)

**CRITICAL: All properties must be at the top level of each entity object. No nested `properties` or `metadata` objects.**

```json
[
  {
    "id": "view:keiyaku_list_jsp",
    "type": "view",
    "name": "Contract List View",
    "parent_module": "module:contract-list",
    "view_name": "keiyakuList.jsp",
    "template_path": "docroot/contract/keiyakuList/keiyakuList.jsp",
    "display_conditions": "User must be authenticated; Project must exist",
    "description": "Main JSP view for displaying contract list with action buttons",
    "source_file_0": "ctc-data-en/contract-list/components/description-ui-en.md"
  },
  {
    "id": "button:new_contract",
    "type": "button",
    "name": "New Contract Button",
    "parent_module": "module:contract-list",
    "button_id": "btnNewContract",
    "label": "New Contract",
    "button_type": "action",
    "trigger_event": "new_contract_button_click",
    "trigger_action_type": "new_contract",
    "enabled_condition": "ankenNo exists and project is active",
    "visibility_flag": "CONTRACT_SHINKI_KEIYAKU_SAKUSEI_KAHI_FLG",
    "position": "top_action_bar",
    "description": "Button to initiate new contract creation workflow",
    "source_file_0": "ctc-data-en/contract-list/screen-specification/event_handling_rules-en.md"
  }
]
```

**Key Points:**
- ✅ All properties are at the top level (no nested `properties` or `metadata` objects)
- ✅ Source files use `source_file_0`, `source_file_1`, etc. naming
- ✅ Arrays converted to strings: semicolon-separated for simple lists, stringified JSON for complex objects
- ✅ No dependency arrays (use relationships in separate file if needed)

### Validation Requirements

#### For All Entities:
- Each entity must have required fields: `id`, `type`, `name`, `parent_module`
- All properties must be at top level (no nested `properties` or `metadata` objects)
- Entity IDs must be unique and follow the pattern: `type:lowercase_name`
- Source files should use `source_file_0`, `source_file_1`, etc.

#### For Specific Entity Types:

**View Entities:**
- `display_conditions` must be semicolon-separated string (not array)
- Do NOT include `bound_data` or `included_components` arrays

**Button Entities:**
- All string properties, no nested objects

**Route Entities:**
- `http_method` must be comma-separated string (e.g., "GET, POST")
- `parameters` must be stringified JSON array
- `forward_destinations` must be stringified JSON array

**Action Type Entities:**
- `requirements` must be semicolon-separated string
- `validation_rules` must be semicolon-separated string

**Event Entities:**
- `parameters` must be stringified JSON array

**Flag Entities:**
- `possible_values` must be semicolon-separated string
- `controls` must be semicolon-separated string

---

## Integration with Main Entities

These UI/Interaction entities complement the main entities extracted via `extract-entity-contract-list.md`. Together they provide:

- **Main Entities:** Business logic, data structures, session management
- **UI/Interaction Entities:** User interface, routing, events, controls

Both files will be used to build comprehensive relationships in Phase 2.

---

## Task Execution

1. **Read** screen specification files in `ctc-data-en/contract-list/screen-specification/`
2. **Identify** all UI and interaction entities according to this taxonomy
3. **Extract** entity information with ALL properties at top level (flattened)
4. **Convert** arrays to appropriate string formats:
   - Simple lists → semicolon-separated strings
   - Complex objects → stringified JSON
5. **Validate** JSON structure and required fields (no nested properties/metadata)
6. **Output** to `json/contract-list-ui-interaction-entities.json`

Focus on capturing the complete user interaction flow from UI elements through routing to business actions.
