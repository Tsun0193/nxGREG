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

## Entity Taxonomy

### 1. View/UI Entities
- **Type ID:** `view`
- **Properties:** view_name, template_path, display_conditions, bound_data, included_components, description
- **Notes:** JSP files and view templates that render the user interface
- **Source:** `ctc-data-en/contract-list/components/description-ui-en.md`

**Example:**
```json
{
  "id": "view:keiyaku_list_jsp",
  "type": "view",
  "name": "Contract List View",
  "parent_module": "module:contract-list",
  "properties": {
    "view_name": "keiyakuList.jsp",
    "template_path": "docroot/contract/keiyakuList/keiyakuList.jsp",
    "display_conditions": ["User must be authenticated", "Project must exist"],
    "bound_data": ["CONTRACT_OPTION_KEIYAKU_ICHIRAN_VO_LIST", "CONTRACT_ANKEN_VO"],
    "included_components": ["body.jsp", "header.jsp"],
    "description": "Main JSP view for displaying contract list with action buttons"
  },
  "metadata": {
    "source_file": "ctc-data-en/contract-list/components/description-ui-en.md"
  }
}
```

---

### 2. Button Entities
- **Type ID:** `button`
- **Properties:** button_id, label, button_type, trigger_event, trigger_action_type, enabled_condition, visibility_flag, position, description
- **Notes:** UI buttons that trigger actions on screens
- **Source:** `ctc-data-en/contract-list/screen-specification/event_handling_rules-en.md`

**Example:**
```json
{
  "id": "button:new_contract",
  "type": "button",
  "name": "New Contract Button",
  "parent_module": "module:contract-list",
  "properties": {
    "button_id": "btnNewContract",
    "label": "New Contract",
    "button_type": "action",
    "trigger_event": "new_contract_button_click",
    "trigger_action_type": "new_contract",
    "enabled_condition": "ankenNo exists and project is active",
    "visibility_flag": "CONTRACT_SHINKI_KEIYAKU_SAKUSEI_KAHI_FLG",
    "position": "top_action_bar",
    "description": "Button to initiate new contract creation workflow"
  },
  "metadata": {
    "source_file": "ctc-data-en/contract-list/screen-specification/event_handling_rules-en.md"
  }
}
```

---

### 3. Route/URL Entities
- **Type ID:** `route`
- **Properties:** route_path, http_method, mapped_action, requires_authentication, parameters, forward_destinations, description
- **Notes:** HTTP endpoints that map requests to Actions
- **Source:** `ctc-data-en/contract-list/screen-flow-en.md`

**Example:**
```json
{
  "id": "route:keiyaku_list_init",
  "type": "route",
  "name": "Contract List Initialization Route",
  "parent_module": "module:contract-list",
  "properties": {
    "route_path": "/dsmart/contract/keiyakuList/keiyakuListInit.do",
    "http_method": ["GET", "POST"],
    "mapped_action": "KeiyakuListInitAction",
    "requires_authentication": true,
    "parameters": [
      {
        "name": "ankenNo",
        "type": "Long",
        "required": true,
        "description": "Project number to load contract list"
      }
    ],
    "forward_destinations": [
      {
        "name": "success",
        "target": "/contract/keiyakuList/keiyakuList.jsp"
      },
      {
        "name": "error",
        "target": "/contract/error.jsp"
      }
    ],
    "description": "Entry point for displaying contract list screen"
  },
  "metadata": {
    "source_file": "ctc-data-en/contract-list/screen-flow-en.md"
  }
}
```

---

### 4. Action Type Entities
- **Type ID:** `action_type`
- **Properties:** action_type_name, description, sp_execute_kbn, requirements, triggered_by, forwards_to, validation_rules
- **Notes:** Dispatch action types that determine routing behavior in KeiyakuListDispatchAction
- **Source:** `ctc-data-en/contract-list/screen-specification/display-conditions-en.md` at "Action Types and Screen Transitions"

**Example:**
```json
{
  "id": "action_type:new_contract",
  "type": "action_type",
  "name": "New Contract Action Type",
  "parent_module": "module:contract-list",
  "properties": {
    "action_type_name": "new_contract",
    "description": "Action type for creating a new contract",
    "sp_execute_kbn": "1",
    "requirements": [
      "User must have new contract creation permission",
      "Project must be in valid status"
    ],
    "triggered_by": "button:new_contract",
    "forwards_to": "/keiyakuListAssign.do",
    "validation_rules": ["ankenNo must exist", "shinkiKeiyakuSakuseiKahiFlg must be true"]
  },
  "metadata": {
    "source_file": "ctc-data-en/contract-list/screen-specification/display-conditions-en.md"
  }
}
```

---

### 5. Event Entities
- **Type ID:** `event`
- **Properties:** event_name, event_type, triggered_by, triggers_action, event_handler, parameters, description
- **Notes:** User interaction events (clicks, submits) that trigger business actions
- **Source:** `ctc-data-en/contract-list/screen-specification/event_handling_rules-en.md`

**Example:**
```json
{
  "id": "event:new_contract_button_click",
  "type": "event",
  "name": "New Contract Button Click Event",
  "parent_module": "module:contract-list",
  "properties": {
    "event_name": "new_contract_button_click",
    "event_type": "button_click",
    "triggered_by": "button:new_contract",
    "triggers_action": "action_type:new_contract",
    "event_handler": "keiyakuListDispatch.do",
    "parameters": [
      {
        "name": "actionType",
        "value": "new_contract"
      }
    ],
    "description": "User clicks the New Contract button to create a new contract"
  },
  "metadata": {
    "source_file": "ctc-data-en/contract-list/screen-specification/event_handling_rules-en.md"
  }
}
```

---

### 6. Business/Control Flag Entities
- **Type ID:** `flag`
- **Properties:** flag_name, purpose, data_type, possible_values, default_value, controls, source_table, storage_location, impact
- **Notes:** Boolean flags or status codes that control feature visibility, permissions, and business logic
- **Source:** `ctc-data-en/contract-list/screen-specification/display-conditions-en.md`

**Example:**
```json
{
  "id": "flag:shinki_keiyaku_sakusei_kahi",
  "type": "flag",
  "name": "New Contract Creation Permission Flag",
  "parent_module": "module:contract-list",
  "properties": {
    "flag_name": "shinkiKeiyakuSakuseiKahiFlg",
    "purpose": "Controls whether user has permission to create new contracts",
    "data_type": "Boolean",
    "possible_values": ["true", "false"],
    "default_value": "false",
    "controls": [
      "button:new_contract visibility"
    ],
    "source_table": "t_syounin_user",
    "storage_location": "session:CONTRACT_SHINKI_KEIYAKU_SAKUSEI_KAHI_FLG",
    "impact": "When true, displays New Contract button; when false, hides it"
  },
  "metadata": {
    "source_file": "ctc-data-en/contract-list/screen-specification/display-conditions-en.md"
  }
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

### JSON Structure
Same as main entities file - array of entity objects following the standard entity schema.

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
3. **Extract** entity information according to the standard entity schema
4. **Validate** JSON structure and required fields
5. **Output** to `json/contract-list-ui-interaction-entities.json`

Focus on capturing the complete user interaction flow from UI elements through routing to business actions.
