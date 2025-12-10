# Entity Relationship Extraction Instruction: Contract List Module

## Role & Context
You are a professional knowledge graph architect specializing in entity relationship modeling for enterprise software systems.

**Project Goal:** Build a comprehensive knowledge graph RAG system for a contract management system by extracting and modeling all relationships between entities across presentation, business logic, data access, and UI layers.

**Current Task:** Extract all relationships between entities from three existing entity files to create a unified relationship graph that captures the complete system architecture and interaction flows.

---

## Input Specification

### Source Entity Files

You must use these three JSON files as input:

1. **`json/contract-list-entities.json`** - Core entities
   - Modules, Screens, Functions, Forms, Value Objects, Sessions
   - Total: ~60 entities

2. **`json/contract-list-component-entities.json`** - Component entities with internal relationships
   - Actions, Delegates, Facades, Products, DAOs
   - Total: ~30 entities
   - Note: Contains internal component relationships already

3. **`json/contract-list-ui-interaction-entities.json`** - UI & Interaction entities
   - Views, Buttons, Routes, Action Types, Events, Flags
   - Total: ~49 entities

4. **`json/contract-list-database-relationships.json`** - Database relationships (already created)
   - DAO-to-Table relationships
   - Function-to-Query relationships
   - Funtcion-to-Database table
   - Note: Do NOT duplicate these relationships

4. **`json/contract-list-database-entities.json`** - Database entities (already created)
   - Database table
   - SQL query
   - Note: No need for relationship build

---

## Output Specification

### Format
Output must be a valid JSON file containing one top-level array: `relationships`.

**IMPORTANT:** The format is Neo4j-compatible with flattened properties. Neo4j does NOT support nested property objects, so all properties must be at the top level of each relationship object.

### File Name
`json/contract-list-cross-layer-relationships.json`

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

### Required Fields
- **source**: Entity ID from source entity file
- **target**: Entity ID from target entity file
- **relationship_type**: Type from taxonomy below
- **property fields**: Type-specific properties (flattened at top level)

---

## Relationship Taxonomy

### Category 1: Screen-to-Action Flow Relationships

#### 1.1 Screen Uses Route
**Relationship Type:** `USES_ROUTE`

**Direction:** `screen` → `route`

**Purpose:** Links a screen to the route that loads it.

**Example:**
```json
{
  "source": "screen:contract_list_main",
  "target": "route:keiyaku_list_init",
  "relationship_type": "USES_ROUTE",
  "is_primary_route": true
}
```

#### 1.2 Screen Displays View
**Relationship Type:** `DISPLAYS_VIEW`

**Direction:** `screen` → `view`

**Purpose:** Links a screen to the JSP view it renders.

**Example:**
```json
{
  "source": "screen:contract_list_main",
  "target": "view:keiyaku_list_jsp",
  "relationship_type": "DISPLAYS_VIEW",
  "view_type": "main"
}
```

#### 1.3 Screen Uses Form
**Relationship Type:** `USES_FORM`

**Direction:** `screen` → `form`

**Purpose:** Links a screen to the form bean it uses for data binding.

**Example:**
```json
{
  "source": "screen:contract_list_main",
  "target": "form:anken_card_form",
  "relationship_type": "USES_FORM",
  "form_scope": "request"
}
```

---

### Category 2: UI Interaction Flow Relationships

#### 2.1 View Contains Button
**Relationship Type:** `CONTAINS_BUTTON`

**Direction:** `view` → `button`

**Purpose:** Links a view to the buttons it contains.

**Example:**
```json
{
  "source": "view:keiyaku_list_jsp",
  "target": "button:new_contract",
  "relationship_type": "CONTAINS_BUTTON",
  "button_position": "top_action_bar"
}
```

#### 2.2 Button Triggers Event
**Relationship Type:** `TRIGGERS_EVENT`

**Direction:** `button` → `event`

**Purpose:** Links a button to the event it triggers when clicked.

**Example:**
```json
{
  "source": "button:new_contract",
  "target": "event:new_contract_button_click",
  "relationship_type": "TRIGGERS_EVENT",
  "javascript_function": "keiyakuList_submit(1)"
}
```

#### 2.3 Event Invokes Action Type
**Relationship Type:** `INVOKES_ACTION_TYPE`

**Direction:** `event` → `action_type`

**Purpose:** Links an event to the action type it invokes.

**Example:**
```json
{
  "source": "event:new_contract_button_click",
  "target": "action_type:new_contract",
  "relationship_type": "INVOKES_ACTION_TYPE",
  "action_type_parameter": "new_contract"
}
```

#### 2.4 Action Type Routes To Action
**Relationship Type:** `ROUTES_TO_ACTION`

**Direction:** `action_type` → `action`

**Purpose:** Links an action type to the Action class it routes to.

**Example:**
```json
{
  "source": "action_type:new_contract",
  "target": "action:keiyaku_list_dispatch_action",
  "relationship_type": "ROUTES_TO_ACTION",
  "dispatch_method": "new_contract"
}
```

---

### Category 3: Route-to-Action Relationships

#### 3.1 Route Maps To Action
**Relationship Type:** `MAPS_TO_ACTION`

**Direction:** `route` → `action`

**Purpose:** Links an HTTP route to the Action class that handles it.

**Example:**
```json
{
  "source": "route:keiyaku_list_init",
  "target": "action:keiyaku_list_init_action",
  "relationship_type": "MAPS_TO_ACTION",
  "http_methods": ["GET", "POST"]
}
```

#### 3.2 Route Forwards To Route
**Relationship Type:** `FORWARDS_TO_ROUTE`

**Direction:** `route` → `route`

**Purpose:** Links routes that forward to other routes.

**Example:**
```json
{
  "source": "route:keiyaku_delete",
  "target": "route:keiyaku_list_init",
  "relationship_type": "FORWARDS_TO_ROUTE",
  "forward_condition": "success"
}
```

#### 3.3 Route Initializes Screen
**Relationship Type:** `INITIALIZES_SCREEN`

**Direction:** `route` → `screen`

**Purpose:** Links a route to the screen it initializes/loads.

**Example:**
```json
{
  "source": "route:keiyaku_list_assign",
  "target": "screen:contract_type_selection",
  "relationship_type": "INITIALIZES_SCREEN"
}
```

---

### Category 4: Action-to-Function Relationships

#### 4.1 Action Implements Function
**Relationship Type:** `IMPLEMENTS_FUNCTION`

**Direction:** `action` → `function`

**Purpose:** Links an Action class to the business function it implements.

**Example:**
```json
{
  "source": "action:keiyaku_list_init_action",
  "target": "function:list_initialization",
  "relationship_type": "IMPLEMENTS_FUNCTION"
}
```

#### 4.2 Action Forwards To Route
**Relationship Type:** `FORWARDS_TO_ROUTE`

**Direction:** `action` → `route`

**Purpose:** Links an Action class to the route it forwards to after processing.

**Example:**
```json
{
  "source": "action:keiyaku_list_dispatch_action",
  "target": "route:keiyaku_list_assign",
  "relationship_type": "FORWARDS_TO_ROUTE",
  "forward_name": "new_contract",
  "condition": "on_new_contract"
}
```

#### 4.3 Function Uses Form
**Relationship Type:** `USES_FORM`

**Direction:** `function` → `form`

**Purpose:** Links a function to the form it uses for input.

**Example:**
```json
{
  "source": "function:list_initialization",
  "target": "form:anken_card_form",
  "relationship_type": "USES_FORM",
  "input_output": "input"
}
```

---

### Category 5: Form-to-ValueObject Relationships

#### 5.1 Form Maps To Value Object
**Relationship Type:** `MAPS_TO_VO`

**Direction:** `form` → `value_object`

**Purpose:** Links a form bean to the Value Object it maps to.

**Example:**
```json
{
  "source": "form:anken_card_form",
  "target": "value_object:anken_vo",
  "relationship_type": "MAPS_TO_VO",
  "mapping_direction": "bidirectional"
}
```

---

### Category 6: Session-to-ValueObject Relationships

#### 6.1 Session Stores Value Object
**Relationship Type:** `STORES_VO`

**Direction:** `session` → `value_object`

**Purpose:** Links a session attribute to the Value Object it stores.

**Example:**
```json
{
  "source": "session:contract_keiyaku_vo",
  "target": "value_object:keiyaku_vo",
  "relationship_type": "STORES_VO",
  "scope": "session",
  "lifecycle": "user_session"
}
```

---

### Category 7: Flag Control Relationships

#### 7.1 Flag Controls Button Visibility
**Relationship Type:** `CONTROLS_VISIBILITY`

**Direction:** `flag` → `button`

**Purpose:** Links a flag to the button whose visibility it controls.

**Example:**
```json
{
  "source": "flag:shinki_keiyaku_sakusei_kahi",
  "target": "button:new_contract",
  "relationship_type": "CONTROLS_VISIBILITY",
  "visible_when": "true",
  "control_type": "visibility"
}
```

#### 7.2 Flag Stored In Session
**Relationship Type:** `STORED_IN_SESSION`

**Direction:** `flag` → `session`

**Purpose:** Links a flag to the session attribute where it's stored.

**Example:**
```json
{
  "source": "flag:shinki_keiyaku_sakusei_kahi",
  "target": "session:business_flag_shinki_keiyaku_sakusei_kahi",
  "relationship_type": "STORED_IN_SESSION",
  "session_key": "CONTRACT_SHINKI_KEIYAKU_SAKUSEI_KAHI_FLG"
}
```

#### 7.3 Flag Controls Button State
**Relationship Type:** `CONTROLS_STATE`

**Direction:** `flag` → `button`

**Purpose:** Links a flag to the button whose enabled/disabled state it controls.

**Example:**
```json
{
  "source": "flag:anken_bunrui_cd",
  "target": "button:delete_contract",
  "relationship_type": "CONTROLS_STATE",
  "disabled_when": "30,40",
  "control_type": "enabled_state"
}
```

---

### Category 8: Component Layer Relationships (Note: Already in component file)

**IMPORTANT:** The following relationships are already defined in `json/contract-list-component-entities_v2.json`:
- Action → Delegate (CALLS)
- Delegate → Facade (CALLS)
- Facade → Product (CALLS)
- Product → DAO (CALLS)
- DAO → Database Table (ACCESSES) - **These are in database-relationships.json**

**Do NOT duplicate these relationships.**

---

### Category 9: Screen Navigation Relationships

#### 9.1 Action Type Navigates To Screen
**Relationship Type:** `NAVIGATES_TO_SCREEN`

**Direction:** `action_type` → `screen`

**Purpose:** Links an action type to the screen it navigates to.

**Example:**
```json
{
  "source": "action_type:new_contract",
  "target": "screen:contract_type_selection",
  "relationship_type": "NAVIGATES_TO_SCREEN",
  "forward_name": "new_contract"
}
```

#### 9.2 Screen Returns To Screen
**Relationship Type:** `RETURNS_TO_SCREEN`

**Direction:** `screen` → `screen`

**Purpose:** Links screens in a return navigation flow.

**Example:**
```json
{
  "source": "screen:contract_deletion",
  "target": "screen:contract_list_main",
  "relationship_type": "RETURNS_TO_SCREEN",
  "return_condition": "after_deletion"
}
```

---

### Category 10: View Composition Relationships

#### 10.1 View Includes View
**Relationship Type:** `INCLUDES_VIEW`

**Direction:** `view` → `view`

**Purpose:** Links a parent view to child views it includes.

**Example:**
```json
{
  "source": "view:keiyaku_list_jsp",
  "target": "view:keiyaku_list_body_jsp",
  "relationship_type": "INCLUDES_VIEW",
  "inclusion_method": "tiles"
}
```

#### 10.2 View Displays Session Data
**Relationship Type:** `DISPLAYS_SESSION_DATA`

**Direction:** `view` → `session`

**Purpose:** Links a view to the session data it displays.

**Example:**
```json
{
  "source": "view:keiyaku_list_body_jsp",
  "target": "session:contract_option_keiyaku_ichiran_vo_list",
  "relationship_type": "DISPLAYS_SESSION_DATA",
  "display_method": "iterate"
}
```

---

## Extraction Guidelines

### 1. Completeness
- Extract ALL relationships between entities from the three source files
- Cross-reference entity IDs across files
- Include relationships even if they seem implicit
- Do not skip relationships marked as "out of scope" - model them anyway

### 2. Consistency
- Use exact entity IDs from source files (case-sensitive)
- Apply consistent relationship naming conventions (UPPERCASE_UNDERSCORE)
- Maintain uniform property structures
- Follow the metadata pattern for all relationships

### 3. Accuracy
- Verify source and target entity IDs exist in source files
- Ensure relationship direction is correct
- Validate property values match documentation
- Cross-check with source documentation files

### 4. Avoid Duplication
- **Do NOT duplicate relationships already in component file:**
  - Action → Delegate → Facade → Product → DAO (internal component flow)
- **Do NOT duplicate relationships in database relationships file:**
  - DAO → Database Table
  - Function → SQL Query
  - SQL Query → Database Table

---

## Relationship Priority Matrix

### High Priority (Must Extract)

1. **UI Event Chain:**
   - Button → Event → Action Type → Action → Function

2. **Screen Navigation:**
   - Screen → Route → Action → Screen

3. **Action Forwarding:**
   - Action → Route (for dispatch/redirect flows)
   - Action → Function (implementation)

4. **Form Data Flow:**
   - Form → Value Object → Session

5. **Permission Control:**
   - Flag → Button (visibility/state)
   - Flag → Session

6. **View Rendering:**
   - Screen → View → Button
   - View → Session Data

### Medium Priority (Should Extract)

1. **Screen-Form Binding:**
   - Screen → Form

2. **Function-Form Usage:**
   - Function → Form

3. **Action Type Routing:**
   - Action Type → Action

4. **Route Forwarding:**
   - Route → Route

5. **View Composition:**
   - View → View (includes)

### Low Priority (Nice to Have)

1. **Cross-module references**
2. **Documentation links**
3. **Configuration relationships**

---

## Extraction Workflow

### Step 1: Load Entity Files
Read all three entity JSON files:
- `json/contract-list-entities_v4.json`
- `json/contract-list-component-entities_v2.json`
- `json/contract-list-ui-interaction-entities.json`

### Step 2: Build Entity Index
Create an index of all entity IDs and their types for quick lookup.

### Step 3: Extract UI Event Chain Relationships
For each button:
1. Button → Event (TRIGGERS_EVENT)
2. Event → Action Type (INVOKES_ACTION_TYPE)
3. Action Type → Action (ROUTES_TO_ACTION)

### Step 4: Extract Screen Navigation Relationships
For each screen:
1. Screen → Route (USES_ROUTE)
2. Screen → View (DISPLAYS_VIEW)
3. Screen → Form (USES_FORM)
4. Action Type → Screen (NAVIGATES_TO_SCREEN)

### Step 5: Extract Route Mapping Relationships
For each route:
1. Route → Action (MAPS_TO_ACTION)
2. Route → Route (FORWARDS_TO_ROUTE)
3. Route → Screen (INITIALIZES_SCREEN) - for routes that load screens

### Step 6: Extract Action-Function Relationships
For each action:
1. Action → Function (IMPLEMENTS_FUNCTION)
2. Action → Route (FORWARDS_TO_ROUTE) - for dispatch actions

### Step 7: Extract Form-VO Relationships
For each form:
1. Form → Value Object (MAPS_TO_VO)

### Step 8: Extract Session Relationships
For each session:
1. Session → Value Object (STORES_VO)
2. Flag → Session (STORED_IN_SESSION)

### Step 9: Extract Permission Control Relationships
For each flag:
1. Flag → Button (CONTROLS_VISIBILITY or CONTROLS_STATE)

### Step 10: Extract View Relationships
For each view:
1. View → Button (CONTAINS_BUTTON)
2. View → View (INCLUDES_VIEW)
3. View → Session (DISPLAYS_SESSION_DATA)

### Step 11: Validate Output
- Check for missing entity IDs
- Verify no duplicate relationships
- Ensure all required properties present
- Validate JSON structure

---

## Example Output Structure

Neo4j-compatible format with flattened properties:

```json
{
  "relationships": [
    {
      "source": "button:new_contract",
      "target": "event:new_contract_button_click",
      "relationship_type": "TRIGGERS_EVENT",
      "javascript_function": "keiyakuList_submit(1)"
    },
    {
      "source": "event:new_contract_button_click",
      "target": "action_type:new_contract",
      "relationship_type": "INVOKES_ACTION_TYPE",
      "action_type_parameter": "new_contract"
    },
    {
      "source": "action_type:new_contract",
      "target": "action:keiyaku_list_dispatch_action",
      "relationship_type": "ROUTES_TO_ACTION",
      "dispatch_method": "new_contract"
    },
    {
      "source": "action:keiyaku_list_dispatch_action",
      "target": "route:keiyaku_list_assign",
      "relationship_type": "FORWARDS_TO_ROUTE",
      "forward_name": "new_contract",
      "condition": "on_new_contract"
    },
    {
      "source": "action:keiyaku_list_init_action",
      "target": "function:list_initialization",
      "relationship_type": "IMPLEMENTS_FUNCTION"
    }
  ]
}
```

---

## Validation Checklist

Before submitting the output, verify:

- [ ] All entity IDs referenced exist in source files
- [ ] No relationships duplicate those in component or database files
- [ ] Relationship directions are correct (source → target)
- [ ] Properties match the relationship type requirements
- [ ] **All properties are flattened (no nested `properties` or `metadata` layers)**
- [ ] JSON is valid and properly formatted
- [ ] High priority relationships are all extracted
- [ ] No orphaned entities (entities with no relationships)
- [ ] **Neo4j compatibility: All properties at top level, no nested objects**

---

## Output File Location

**Path:** `json/contract-list-cross-layer-relationships.json`

This file complements:
- `json/contract-list-component-entities_v2.json` (contains internal component relationships)
- `json/contract-list-database-relationships.json` (contains database-specific relationships)

Together, these three files provide a complete relationship graph for the knowledge RAG system.

---

## Critical Relationships for Complete Flow Coverage

### Missing Relationships to Add

Based on the documentation analysis, ensure these critical relationships are extracted:

#### 1. Action Forwarding Flows
```json
{
  "source": "action:keiyaku_list_dispatch_action",
  "target": "route:keiyaku_list_assign",
  "relationship_type": "FORWARDS_TO_ROUTE",
  "forward_name": "new_contract",
  "condition": "when_action_type_is_new_contract"
}
```

**Required forwards from KeiyakuListDispatchAction:**
- → `route:keiyaku_list_assign` (new_contract)
- → `route:tsuika_keiyaku_dispatch` (add_contract)
- → `route:henko_keiyaku_dispatch` (update_contract)
- → `route:keiyaku_delete` (delete_contract)
- → `route:yuusyou_keiyaku_list_assign` (new_yuusyou_contract)
- → `route:moushide_select_init` (new_yuusyou_after_contract)
- → `route:anchor_keiyaku_dispatch` (keiyaku_card_anchor)

#### 2. Route Screen Initialization
```json
{
  "source": "route:keiyaku_list_assign",
  "target": "screen:contract_type_selection",
  "relationship_type": "INITIALIZES_SCREEN"
}
```

**Required route-to-screen mappings:**
- `route:keiyaku_list_assign` → `screen:contract_type_selection`
- `route:yuusyou_keiyaku_list_assign` → `screen:after_contract_creation`
- `route:moushide_select_init` → `screen:multiple_order_selection`

#### 3. Action-Function Implementation
```json
{
  "source": "action:keiyaku_list_init_action",
  "target": "function:list_initialization",
  "relationship_type": "IMPLEMENTS_FUNCTION"
}
```

**Required action-function mappings:**
- `action:keiyaku_list_init_action` → `function:list_initialization`
- `action:keiyaku_delete_action` → `function:contract_deletion`

#### 4. Additional Route Forwards
```json
{
  "source": "route:keiyaku_list_assign",
  "target": "route:keiyaku_list_init",
  "relationship_type": "FORWARDS_TO_ROUTE",
  "forward_condition": "after_contract_creation"
}
```

**Required return forwards:**
- `route:keiyaku_list_assign` → `route:keiyaku_list_init` (after contract created)
- `route:tsuika_keiyaku_dispatch` → `route:keiyaku_list_init` (after additional contract)
- `route:henko_keiyaku_dispatch` → `route:keiyaku_list_init` (after modification)
- `route:yuusyou_keiyaku_list_assign` → `route:keiyaku_list_init` (after after-sales)
- `route:moushide_select_init` → `route:keiyaku_list_init` (after multiple orders)
- `route:anchor_keiyaku_dispatch` → `route:keiyaku_list_init` (after viewing details)

---

## Complete Flow Example

With all relationships in place, a complete user flow should be traceable:

```
USER CLICKS "New Contract" BUTTON:

1. view:keiyaku_list_jsp 
   → CONTAINS_BUTTON → button:new_contract

2. button:new_contract 
   → TRIGGERS_EVENT → event:new_contract_button_click

3. event:new_contract_button_click 
   → INVOKES_ACTION_TYPE → action_type:new_contract

4. action_type:new_contract 
   → ROUTES_TO_ACTION → action:keiyaku_list_dispatch_action

5. action:keiyaku_list_dispatch_action 
   → FORWARDS_TO_ROUTE → route:keiyaku_list_assign

6. route:keiyaku_list_assign 
   → MAPS_TO_ACTION → action:keiyaku_list_assign_action

7. route:keiyaku_list_assign 
   → INITIALIZES_SCREEN → screen:contract_type_selection

8. screen:contract_type_selection 
   → DISPLAYS_VIEW → view:keiyaku_list_assign_jsp

(User completes contract creation)

9. route:keiyaku_list_assign 
   → FORWARDS_TO_ROUTE → route:keiyaku_list_init

10. route:keiyaku_list_init 
    → MAPS_TO_ACTION → action:keiyaku_list_init_action

11. action:keiyaku_list_init_action 
    → IMPLEMENTS_FUNCTION → function:list_initialization

12. route:keiyaku_list_init 
    → INITIALIZES_SCREEN → screen:contract_list_main
```

This complete 12-hop flow shows the full round-trip journey from button click to processing to return.
