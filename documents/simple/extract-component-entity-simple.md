# Component Entity and Relationship Extraction: Simple Contract Module

## Role & Context
You are a professional technical document analyzer extracting **component-level entities** (Action, Delegate, Facade, Product, DAO, Edit, Check) and **their internal relationships** from the simple contract module documentation.

**Parent Document:** `extract-entity-simple.md`

**Current Task:** Extract architectural component entities AND build relationships between them within the component group. This focuses on internal component dependencies and interactions within the simple module.

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
- ✅ **NEW: Documents architectural flow (Action → Delegate → Facade → Product → Edit/Check → DAO)**
- ✅ **NEW: Captures data access patterns (DAO → Database Tables)**
- ✅ **NEW: Maps navigation flows (Action forwards)**
- ✅ **NEW: Tracks form usage patterns**
- ✅ **Scope: Internal relationships within simple module only**

### Future Enhancement (v3)
- 🔄 Will add external relationships to other modules
- 🔄 Will connect simple components to contract-list/housing modules
- 🔄 Will build cross-module dependency graph

---

## Output Structure

### JSON Structure (v2)
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

**Key Features:** 
1. The output has TWO top-level arrays: `entities` and `relationships`
2. **Neo4j Compatibility:** All properties are flattened to single level (no nested `properties` or `metadata` objects)
3. **Relationships as Data:** Dependencies, forwards, and table accesses are expressed as relationships, not nested arrays

---

## Input Specification

### Source Files
Primary source for component identification:
- `ctc-data-en/simple/simple-contract-overview-en.md` - Module overview
- `ctc-data-en/simple/yuusyou-kihon/overview-en.md` - Basic Information tab overview
- `ctc-data-en/simple/yuusyou-kihon/functions/init-screen/function-overview-en.md` - Init function components
- `ctc-data-en/simple/yuusyou-kihon/functions/register-contract/function-overview-en.md` - Register function components
- `ctc-data-en/simple/yuusyou-kihon/functions/update-customer/function-overview-en.md` - Update customer function components
- `ctc-data-en/simple/yuusyou-kihon/functions/validation-contract/function-overview-en.md` - Validation function components
- `ctc-data-en/simple/yuusyou-kihon/functions/*/sequence-diagram-en.md` - Component interaction flows

### Component Identification Pattern
Look for sections labeled **"Main Components"** in function overview documents. Example:
```
| Layer | Class/Component | Package | Purpose | Usage |
|-------|----------------|---------|---------|-------|
| **Presentation Layer** | **KihonInitAction** | `jp.co.daiwahouse...` | Main controller | ... |
| **Product Layer** | **YuusyouKihonProduct** | `jp.co.daiwahouse...` | Contract product | ... |
```

---

## Entity Taxonomy for Components

### 1. Action Entities
- **Type ID:** `action`
- **Properties (flattened):** 
  - `action_name`: Name of the Struts action class
  - `action_path`: URL path (e.g., `/kihonInit`)
  - `http_method`: HTTP method (GET/POST)
  - `form_bean`: Associated form bean (use USES_FORM relationship instead for Neo4j)
  - `validation_enabled`: Whether validation is enabled
  - `package`: Java package path
  - `layer`: Always "Presentation Layer" for actions
  - `source_file_0`: Primary source file path (flattened from metadata)
- **Removed Properties:** 
  - ❌ `forward_destinations`: Use FORWARDS_TO relationships instead
  - ❌ `dispatch_methods`: Use FORWARDS_TO relationships with conditions
- **Notes:** Extract all Struts action classes including dispatch actions, init actions, registration actions, and customer management actions. Forward destinations are now expressed as relationships.

**Example:**
```json
{
  "id": "action:kihon_init_action",
  "type": "action",
  "name": "Basic Information Init Action",
  "parent_module": "module:simple",
  "action_name": "KihonInitAction",
  "action_path": "/kihonInit",
  "http_method": "GET/POST",
  "form_bean": "yuusyou_keiyaku_newtmp_kihon_form",
  "validation_enabled": false,
  "layer": "Presentation Layer",
  "package": "jp.co.daiwahouse.dsmart.application.contract.yuusyou.keiyakuNewtmp.kihon",
  "purpose": "Contract screen initialization",
  "source_file_0": "ctc-data-en/simple/yuusyou-kihon/functions/init-screen/function-overview-en.md"
}
```

### 2. Delegate Entities
- **Type ID:** `delegate`
- **Properties (flattened):** 
  - `delegate_name`: Name of the delegate class
  - `purpose`: Business purpose description
  - `package`: Java package path
  - `layer`: "Delegate Layer" or "Business Layer"
  - `source_file_0`: Primary source file path (flattened from metadata)
- **Removed Properties:** 
  - ❌ `facade_dependencies`: Use CALLS relationships instead
- **Notes:** Delegate layer classes that bridge Actions and Facades. In simple module, common delegates like `BaseDelegate` and `IBaseDelegate` are used.

**Example:**
```json
{
  "id": "delegate:base_delegate",
  "type": "delegate",
  "name": "Base Delegate",
  "parent_module": "module:simple",
  "delegate_name": "BaseDelegate",
  "purpose": "Data transformation and facade orchestration",
  "layer": "Delegate Layer",
  "package": "jp.co.daiwahouse.dsmart.delegate",
  "source_file_0": "ctc-data-en/simple/yuusyou-kihon/functions/register-contract/function-overview-en.md"
}
```

### 3. Facade Entities
- **Type ID:** `facade`
- **Properties (flattened):** 
  - `facade_name`: Name of the facade bean class
  - `purpose`: Business orchestration purpose
  - `package`: Java package path
  - `layer`: "Facade Layer" or "Business Layer"
  - `source_file_0`: Primary source file path (flattened from metadata)
- **Removed Properties:** 
  - ❌ `product_dependencies`: Use CALLS relationships instead
- **Notes:** Facade layer classes that orchestrate business logic. Common facades include `CommonFacadeBean` and `ShinkaikeiFacadeBean`.

**Example:**
```json
{
  "id": "facade:common_facade_bean",
  "type": "facade",
  "name": "Common Facade Bean",
  "parent_module": "module:simple",
  "facade_name": "CommonFacadeBean",
  "purpose": "Simplified interface for contract operations",
  "layer": "Facade Layer",
  "package": "jp.co.daiwahouse.dsmart.service.contract.facade",
  "source_file_0": "ctc-data-en/simple/yuusyou-kihon/functions/register-contract/function-overview-en.md"
}
```

### 4. Product Entities
- **Type ID:** `product`
- **Properties (flattened):** 
  - `product_name`: Name of the product class
  - `purpose`: Core business logic purpose
  - `package`: Java package path
  - `layer`: "Product Layer" or "Business Layer"
  - `source_file_0`: Primary source file path (flattened from metadata)
- **Removed Properties:** 
  - ❌ `dao_dependencies`: Use CALLS relationships instead
  - ❌ `edit_dependencies`: Use CALLS relationships instead
- **Notes:** Product layer classes containing core business logic. Key products include `YuusyouKihonProduct`, `UkeoiKihonProduct`, `KojinTasyaKeiyakuKbnProduct`.

**Example:**
```json
{
  "id": "product:yuusyou_kihon_product",
  "type": "product",
  "name": "Simple Contract Basic Information Product",
  "parent_module": "module:simple",
  "product_name": "YuusyouKihonProduct",
  "purpose": "Core business logic for simple contract processing",
  "layer": "Product Layer",
  "package": "jp.co.daiwahouse.dsmart.service.contract.product.yuusyou",
  "source_file_0": "ctc-data-en/simple/yuusyou-kihon/functions/init-screen/function-overview-en.md"
}
```

### 5. Edit Entities
- **Type ID:** `edit`
- **Properties (flattened):** 
  - `edit_name`: Name of the edit class
  - `purpose`: Edit control purpose
  - `package`: Java package path
  - `layer`: "Product Layer" or "Edit Layer"
  - `source_file_0`: Primary source file path (flattened from metadata)
- **Notes:** Edit layer classes providing specialized editing and control logic. Key edit classes include `YuusyouKihonEdit`, `CommonEdit`.

**Example:**
```json
{
  "id": "edit:yuusyou_kihon_edit",
  "type": "edit",
  "name": "Simple Contract Basic Information Edit",
  "parent_module": "module:simple",
  "edit_name": "YuusyouKihonEdit",
  "purpose": "Edit control logic for simple contracts",
  "layer": "Product Layer",
  "package": "jp.co.daiwahouse.dsmart.service.contract.product.yuusyou",
  "source_file_0": "ctc-data-en/simple/yuusyou-kihon/functions/register-contract/function-overview-en.md"
}
```

### 6. Check Entities
- **Type ID:** `check`
- **Properties (flattened):** 
  - `check_name`: Name of the check class
  - `purpose`: Validation/check purpose
  - `package`: Java package path
  - `layer`: "Check Layer" or "Business Layer"
  - `source_file_0`: Primary source file path (flattened from metadata)
- **Notes:** Check layer classes providing business validation logic. Key check classes include `CheckAcceptance`, `CheckCommon`, `CheckYuusyouAfterKeiyaku`, `CheckUkeoi`, `CheckBunjou`, `CheckTochi`.

**Example:**
```json
{
  "id": "check:check_acceptance",
  "type": "check",
  "name": "Acceptance Check",
  "parent_module": "module:simple",
  "check_name": "CheckAcceptance",
  "purpose": "Business validation for contract approval",
  "layer": "Check Layer",
  "package": "jp.co.daiwahouse.dsmart.service.contract.product",
  "source_file_0": "ctc-data-en/simple/yuusyou-kihon/functions/validation-contract/function-overview-en.md"
}
```

### 7. DAO Entities
- **Type ID:** `dao`
- **Properties (flattened):** 
  - `dao_name`: Name of the DAO class
  - `purpose`: Data access purpose
  - `package`: Java package path
  - `layer`: "Data Layer" or "DAO Layer"
  - `source_file_0`: Primary source file path (flattened from metadata)
- **Removed Properties:** 
  - ❌ `target_tables`: Use individual ACCESSES relationships for each table
  - ❌ `operations`: Include operation type in each ACCESSES relationship
- **Notes:** Data Access Object classes that provide the abstraction layer between Product/Edit components and database tables. **Critical:** DAOs are often implied in sequence diagrams (Product→DB means Product→DAO→DB). Extract DAO entities based on table operations mentioned. Key DAOs include `KeiyakuDAO`, `JyutyuDAO`, `AnkenDAO`, `KoujiDAO`, `TochiDAO`, `SyainKankeiDAO`, and their Find counterparts.

**Common DAO Naming Patterns:**
- `<EntityName>DAO` - For main CRUD operations (e.g., `KeiyakuDAO`)
- `<EntityName>FindDAO` - For complex queries (e.g., `KeiyakuFindDAO`)
- `<EntityName>KankeiDAO` - For relationship tables (e.g., `KeiyakuSyainKankeiDAO`)

**Example:**
```json
{
  "id": "dao:keiyaku_dao",
  "type": "dao",
  "name": "Contract DAO",
  "parent_module": "module:simple",
  "dao_name": "KeiyakuDAO",
  "purpose": "Data access for contract table operations",
  "layer": "Data Layer",
  "package": "jp.co.daiwahouse.dsmart.domain.contract.persistence",
  "source_file_0": "ctc-data-en/simple/yuusyou-kihon/functions/register-contract/sequence-diagram-en.md"
}
```

### 8. Lock Manager Entities
- **Type ID:** `lock_manager`
- **Properties (flattened):** 
  - `manager_name`: Name of the lock manager class
  - `purpose`: Lock management purpose
  - `package`: Java package path
  - `layer`: "Infrastructure Layer" or "Utility Layer"
  - `source_file_0`: Primary source file path
- **Notes:** Lock management components that handle database locking for transaction integrity. Typically uses `SELECT FOR UPDATE NOWAIT` pattern.

**Example:**
```json
{
  "id": "lock_manager:lock_manager",
  "type": "lock_manager",
  "name": "Lock Manager",
  "parent_module": "module:simple",
  "manager_name": "LockManager",
  "purpose": "Pessimistic locking for concurrent update control",
  "layer": "Infrastructure Layer",
  "package": "jp.co.daiwahouse.dsmart.infrastructure",
  "source_file_0": "ctc-data-en/simple/yuusyou-kihon/functions/register-contract/sequence-diagram-en.md"
}
```

---

## Relationship Taxonomy

### Relationship Types Within Component Group

Extract relationships between components to capture the architectural flow and dependencies. Focus on **internal relationships** within the simple module only.

#### 1. CALLS Relationship
- **Source:** Action, Delegate, Facade, Product, Edit, Check, Lock Manager
- **Target:** Delegate, Facade, Product, DAO, Edit, Check, Lock Manager
- **Description:** Represents method invocation or component usage
- **Properties (flattened):**
  - `relationship_type`: "CALLS"
  - `purpose`: Brief description of why this call is made
  - `call_context`: Context in which the call occurs (e.g., "initialization", "validation", "registration", "update")
  - `method_name`: Specific method being called (optional, if documented)

**Example:**
```json
{
  "source": "action:kihon_init_action",
  "target": "delegate:base_delegate",
  "relationship_type": "CALLS",
  "purpose": "Retrieve contract data for display",
  "method_name": "find",
  "call_context": "initialization"
}
```

#### 2. DEPENDS_ON Relationship
- **Source:** Any component
- **Target:** Any component
- **Description:** Represents dependency where source needs target to function
- **Properties (flattened):**
  - `relationship_type`: "DEPENDS_ON"
  - `dependency_type`: Type of dependency ("data", "business_logic", "validation", "edit_control")

**Example:**
```json
{
  "source": "product:yuusyou_kihon_product",
  "target": "edit:yuusyou_kihon_edit",
  "relationship_type": "DEPENDS_ON",
  "dependency_type": "edit_control"
}
```

#### 3. FORWARDS_TO Relationship
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
  "source": "action:kihon_init_action",
  "relationship_type": "FORWARDS_TO",
  "forward_name": "success",
  "target_view": "/contract/yuusyou/keiyakuNewtmp/kihon.jsp"
}
```

#### 4. USES_FORM Relationship
- **Source:** Action
- **Target:** Form bean (referenced as string)
- **Description:** Represents form bean usage by action
- **Properties (flattened):**
  - `relationship_type`: "USES_FORM"
  - `form_bean_name`: Name of the form bean

**Example:**
```json
{
  "source": "action:kihon_register_action",
  "relationship_type": "USES_FORM",
  "form_bean_name": "yuusyou_keiyaku_newtmp_kihon_form"
}
```

#### 5. ACCESSES Relationship
- **Source:** DAO, Lock Manager
- **Target:** Database table entity (string reference to table name)
- **Description:** Represents database table access operations
- **Properties (flattened):**
  - `relationship_type`: "ACCESSES"
  - `operation`: Type of database operation ("SELECT", "INSERT", "UPDATE", "DELETE", "LOCK", "SELECT_FOR_UPDATE_NOWAIT")
  - `table_name`: Physical table name
  - `purpose`: Purpose of the access (e.g., "lock contract record", "update land data", "delete instruction relationship")
  - `condition`: Condition under which access occurs (optional)

**Example:**
```json
{
  "source": "dao:keiyaku_dao",
  "relationship_type": "ACCESSES",
  "table_name": "t_keiyaku",
  "operation": "UPDATE",
  "purpose": "Update main contract data"
}
```

**Lock Example:**
```json
{
  "source": "lock_manager:lock_manager",
  "relationship_type": "ACCESSES",
  "table_name": "t_keiyaku",
  "operation": "SELECT_FOR_UPDATE_NOWAIT",
  "purpose": "Lock contract record for concurrent update control",
  "condition": "Normal edit mode"
}
```

### Relationship Extraction Rules

1. **Layered Architecture Pattern**: Extract relationships following the standard flow:
   - Action → Delegate (CALLS)
   - Delegate → Facade (CALLS)
   - Facade → Product (CALLS)
   - Product → Edit/Check (CALLS)
   - Product → DAO (CALLS)
   - Product → Lock Manager (CALLS) - for locking operations
   - DAO → Database Tables (ACCESSES)
   - Lock Manager → Database Tables (ACCESSES with operation="SELECT_FOR_UPDATE_NOWAIT")
   - All layers DEPEND_ON their next layer

2. **Navigation Pattern**: For Actions:
   - Create FORWARDS_TO for each forward destination
   - Create USES_FORM for form bean usage

3. **Data Access Pattern**: For database operations:
   - **NEVER** create direct Product→DB relationships
   - **ALWAYS** insert DAO layer: Product→DAO→DB
   - When sequence diagram shows "Product→DB: UPDATE t_keiyaku"
     - Create: Product→DAO (CALLS)
     - Create: DAO→t_keiyaku (ACCESSES with operation="UPDATE")
   - Group operations by DAO type (e.g., all t_keiyaku operations go through KeiyakuDAO)

4. **Lock Pattern**: For locking operations:
   - Extract Lock Manager component
   - Create: Product→LockManager (CALLS)
   - Create: LockManager→Table (ACCESSES with operation="SELECT_FOR_UPDATE_NOWAIT")
   - Lock operations typically happen before UPDATE operations

5. **Completeness**: For each component entity, extract:
   - All direct method calls to other components
   - All dependencies mentioned in documentation
   - All navigation flows (for Actions)
   - All database operations (via DAO layer)

### Relationship Extraction Strategies

#### Finding CALLS Relationships

Look for these indicators in documentation:

1. **Explicit Component Lists**: In function overview documents, look for "Main Components" tables:
   ```
   | Layer    | Class/Component        | Purpose           |
   |----------|------------------------|-------------------|
   | Action   | KihonInitAction        | Main controller   |
   | Product  | YuusyouKihonProduct    | Business logic    |
   ```
   This indicates: Action CALLS Product

2. **Sequence Diagrams**: Look in `sequence-diagram-en.md` files for interaction flows:
   ```
   Action->>Delegate: find(formMap, vo)
   Delegate->>Facade: update(vo)
   Facade->>Product: doUpdate(vo)
   Product->>Edit: editControlRegister(vo)
   Product->>Product: updateKeiyaku(vo)
   ```
   **IMPORTANT:** When you see `Product->>DB:` operations, infer the DAO layer:
   - `Product->>DB: UPDATE t_keiyaku` means:
     - Product CALLS KeiyakuDAO
     - KeiyakuDAO ACCESSES t_keiyaku (operation="UPDATE")

3. **Method Descriptions**: Look for text like:
   - "calls the delegate"
   - "invokes the facade"
   - "uses the product"
   - "queries via DAO"
   - "delegates to"
   - "updates via DAO" (inferred from database operations)

#### Finding DAO Entities and ACCESSES Relationships

**Critical Pattern Recognition:**

When sequence diagrams show database operations like:
```
Product->>DB: UPDATE t_tochi, t_keiyaku_tochi (land data)
Product->>DB: UPDATE t_jyutyu, t_jyutyu_tatemono (order/construction data)
Product->>DB: UPDATE t_keiyaku_syain_kankei (contract-employee relationships)
Product->>DB: DELETE from t_keiyaku_shijisyo_kankei (contract instruction relationships)
Lock->>DB: SELECT FOR UPDATE NOWAIT on t_keiyaku
```

**Extract the following:**

1. **Infer DAO Entity** based on table name:
   - `t_keiyaku` → `KeiyakuDAO`
   - `t_jyutyu` → `JyutyuDAO`
   - `t_tochi` → `TochiDAO`
   - `t_keiyaku_syain_kankei` → `KeiyakuSyainKankeiDAO`
   - Pattern: Convert table name to PascalCase + "DAO"

2. **Create Product→DAO CALLS relationship**:
   ```json
   {
     "source": "product:yuusyou_kihon_product",
     "target": "dao:keiyaku_dao",
     "relationship_type": "CALLS",
     "purpose": "Update contract data",
     "method_name": "updateKeiyaku"
   }
   ```

3. **Create DAO→Table ACCESSES relationship** for each table:
   ```json
   {
     "source": "dao:keiyaku_dao",
     "relationship_type": "ACCESSES",
     "table_name": "t_keiyaku",
     "operation": "UPDATE",
     "purpose": "Update main contract data"
   }
   ```

4. **For composite operations** (multiple tables in one update):
   - Example: `UPDATE t_tochi, t_keiyaku_tochi (land data)`
   - Create separate ACCESSES for each table:
     - `TochiDAO ACCESSES t_tochi`
     - `TochiDAO ACCESSES t_keiyaku_tochi`

5. **For Lock operations**:
   - `Lock->>DB: SELECT FOR UPDATE NOWAIT on t_keiyaku`
   - Create LockManager entity if not exists
   - Create: Product→LockManager (CALLS)
   - Create: LockManager→t_keiyaku (ACCESSES with operation="SELECT_FOR_UPDATE_NOWAIT")

#### Finding FORWARDS_TO Relationships

For each Action entity:
1. Look for forward mapping descriptions in documentation (e.g., "Success → `kihon.jsp`", "Redirects to `/kihonInit.do`")
2. Look for Output sections in function-overview-en.md files
3. Create individual FORWARDS_TO for each destination:
   - `source`: the Action entity ID
   - `forward_name`: the forward key (e.g., "success", "error")
   - `target_view`: the JSP or next action path
   - `condition`: when this forward is triggered (for dispatch actions)

#### Finding Dispatch Patterns

For DispatchAction entities (e.g., `KihonTabDispatchAction`):
1. Look for dispatch routing logic in documentation
2. Each `actionType` routes to different actions
3. Create separate FORWARDS_TO relationships for each route
4. Document in `condition` property which actionType triggers the forward
5. Example: `"condition": "when actionType=register"`

### Relationship Quality Guidelines

1. **Accuracy**: Only create relationships explicitly documented or clearly implied by architecture
2. **Completeness**: Every component should have at least one relationship (input or output)
3. **Consistency**: Use consistent relationship types and property structures
4. **Traceability**: Include source information in relationship properties when available
5. **Scope**: Stay within the simple module boundaries

---

## Extraction Guidelines

### Component Discovery Process

1. **Identify Functions**: Look for function folders in `ctc-data-en/simple/yuusyou-kihon/functions/`:
   - `init-screen` - Screen Initialization Feature
   - `register-contract` - Simple Contract Registration Feature
   - `update-customer` - Customer/Contractor Update Feature
   - `validation-contract` - Contract Validation Feature

2. **Extract Component Lists**: Find "Main Components" sections in each function's `function-overview-en.md` that list:
   - Layer (Presentation, Delegate, Facade, Product, Check, Data)
   - Class/Component name
   - Package path
   - Purpose

3. **Map Architecture**: Follow the layered architecture pattern:
   ```
   Action → Delegate → Facade → Product → Edit/Check → DAO → [Database Tables]
   ```

4. **Extract Relationships**: Use sequence diagrams in `sequence-diagram-en.md` to identify component interactions

### Visual Example: Complete Function Mapping

For the **Simple Contract Registration Feature**, extract the following structure:

```
┌─────────────────────────────────────────────────────────────┐
│ Action Layer                                                 │
│  KihonRegisterAction (/kihonRegister)                       │
│    - USES_FORM: yuusyou_keiyaku_newtmp_kihon_form           │
│    - FORWARDS_TO: success → /kihonInit.do                   │
└────────────────┬────────────────────────────────────────────┘
                 │ CALLS
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ Delegate Layer                                               │
│  BaseDelegate                                                │
└────────────────┬────────────────────────────────────────────┘
                 │ CALLS
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ Facade Layer                                                 │
│  CommonFacadeBean                                            │
└────────────────┬────────────────────────────────────────────┘
                 │ CALLS
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ Product Layer                                                │
│  YuusyouKihonProduct                                         │
│    - CALLS: YuusyouKihonEdit                                 │
│    - CALLS: UkeoiKihonProduct                                │
│    - CALLS: LockManager (for pessimistic locking)           │
│    - CALLS: Multiple DAOs (for data persistence)            │
└────┬───────┬──────────────┬──────────────┬─────────────────┘
     │       │              │              │ CALLS
     │       │              │              ▼
     │       │              │      ┌──────────────────────────┐
     │       │              │      │ Lock Manager             │
     │       │              │      │  LockManager             │
     │       │              │      └──────┬───────────────────┘
     │       │              │             │ ACCESSES (LOCK)
     │       │              │             ▼
     │       │              │      ┌──────────────────────────┐
     │       │              │      │ Database Tables          │
     │       │              │      │  t_keiyaku, t_jyutyu,    │
     │       │              │      │  t_kouji (for locking)   │
     │       │              │      └──────────────────────────┘
     │       │              │
     │       │ CALLS        │ CALLS
     │       ▼              ▼
     │  ┌────────┐  ┌──────────────────────────┐
     │  │ Edit   │  │ DAO Layer                │
     │  │ Layer  │  │  KeiyakuDAO              │
     │  │        │  │  JyutyuDAO               │
     │  │ Yuusyou│  │  KoujiDAO                │
     │  │ Kihon  │  │  TochiDAO                │
     │  │ Edit   │  │  KeiyakuSyainKankeiDAO   │
     │  │        │  │  AnkenSyainKankeiDAO     │
     │  │        │  │  KeiyakuShijisyoKankeiDAO│
     │  │        │  │  UkeoiJigyoutaiKankeiDAO │
     │  │        │  │  KyoudouJyutyuDAO        │
     │  └────────┘  └──────┬───────────────────┘
     │                     │ ACCESSES
     │ CALLS               ▼
     ▼              ┌──────────────────────────┐
┌──────────┐       │ Database Tables          │
│ Product  │       │  t_keiyaku               │
│ Layer    │       │  t_jyutyu                │
│          │       │  t_kouji                 │
│ Ukeoi    │       │  t_tochi                 │
│ Kihon    │       │  t_keiyaku_tochi         │
│ Product  │       │  t_jyutyu_tatemono       │
└──────────┘       │  t_keiyaku_syain_kankei  │
                   │  t_anken_syain_kankei    │
                   │  t_keiyaku_hosoku        │
                   │  t_keiyaku_koutei        │
                   │  t_ukeoi_jigyoutai_kankei│
                   │  t_kyoudou_jyutyu        │
                   │  t_keiyaku_shijisyo_kankei│
                   └──────────────────────────┘
```

**Key Points:**
1. **DAO Layer is MANDATORY** - Never skip it even if sequence diagrams show direct DB access
2. **Lock Manager** - Separate component for pessimistic locking pattern
3. **One DAO per Table/Entity** - Group related operations under appropriate DAO
4. **ACCESSES relationships** - Connect DAOs to specific database tables with operation types

### Required Components for Simple Module

Based on function documentation, extract components for these functions:

#### 1. Screen Initialization Feature (init-screen)
- `KihonInitAction`
- `IBaseDelegate` or `BaseDelegate`
- `YuusyouKihonProduct`
- `YuusyouKihonEdit`
- Plus supporting components as documented

#### 2. Simple Contract Registration Feature (register-contract)
- `KihonRegisterAction`
- `BaseDelegate`
- `CommonFacadeBean`
- `YuusyouKihonProduct`
- `YuusyouKihonEdit`
- `UkeoiKihonProduct`
- `CommonEdit`
- `CheckCommon`
- `LockManager`
- DAOs (inferred from sequence diagram):
  - `KeiyakuDAO` - for t_keiyaku operations
  - `JyutyuDAO` - for t_jyutyu operations
  - `KoujiDAO` - for t_kouji operations
  - `TochiDAO` - for t_tochi, t_keiyaku_tochi operations
  - `KeiyakuSyainKankeiDAO` - for t_keiyaku_syain_kankei operations
  - `AnkenSyainKankeiDAO` - for t_anken_syain_kankei operations
  - `KeiyakuHosokuDAO` - for t_keiyaku_hosoku operations
  - `KeiyakuKouteiDAO` - for t_keiyaku_koutei operations
  - `UkeoiJigyoutaiKankeiDAO` - for t_ukeoi_jigyoutai_kankei operations
  - `KyoudouJyutyuDAO` - for t_kyoudou_jyutyu operations
  - `KeiyakuShijisyoKankeiDAO` - for t_keiyaku_shijisyo_kankei operations

#### 3. Customer/Contractor Update Feature (update-customer)
- `KihonTabDispatchAction` (router)
- `KeiyakusakiMainAction`, `KeiyakusakiSubAction`, `KeiyakusakiDeleteAction`
- `KenchikunushiMainAction`, `KenchikunushiSubAction`, `KenchikunushiDeleteAction`
- `BaseDelegate`
- `CommonFacadeBean`
- `YuusyouKihonProduct`
- `KojinTasyaKeiyakuKbnProduct`

#### 4. Contract Validation Feature (validation-contract)
- `KihonRegisterAction`
- `BaseDelegate`
- `ShinkaikeiFacadeBean`
- `ShinkiAcceptanceProduct`, `HenkouAcceptanceProduct`, `AbstractAcceptanceProduct`
- Check components: `CheckAcceptance`, `CheckCommon`, `CheckYuusyouAfterKeiyaku`, `CheckUkeoi`, `CheckBunjou`, `CheckTochi`
- DAOs: `KeiyakuDAO`, `JyutyuDAO`, `AnkenDAO`, `KoujiDAO`, `SnapShotDAO`, etc.

### Completeness Checklist

For each function documented, ensure you extract:
- [ ] All Action entities
- [ ] All Delegate entities mentioned
- [ ] All Facade entities mentioned
- [ ] All Product entities mentioned
- [ ] All Edit entities mentioned
- [ ] All Check entities mentioned
- [ ] All DAO entities mentioned
- [ ] CALLS relationships from sequence diagrams
- [ ] FORWARDS_TO relationships from navigation flows
- [ ] USES_FORM relationships for form beans

---

## Output Specification

### Format
Output must be a valid JSON file containing both component entities and their relationships.

### File Name
`json/simple-component-entities.json`

### JSON Structure (Neo4j Compatible - Flattened)
```json
{
  "entities": [
    {
      "id": "entity_id",
      "type": "entity_type",
      "name": "Entity Name",
      "parent_module": "module:simple",
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

**Critical Requirements:**
1. **All properties at root level** - No nested `properties` or `metadata` objects
2. **Consistent IDs** - Use format `<type>:<snake_case_name>`
3. **Complete architecture** - Capture all layers: Action → Delegate → Facade → Product → Edit/Check → DAO

**Note:** Database table entities and their relationships with DAOs are extracted separately using the database extraction instruction (`extract-database-entity-simple-complete.md`). This instruction focuses only on architectural components.

---

## Task Execution

1. **Read** all markdown files in `ctc-data-en/simple/yuusyou-kihon/functions/`
2. **Identify** all component entities from "Main Components" tables
3. **Extract** sequence flows from `sequence-diagram-en.md` files
4. **Build** relationships following the layered architecture
5. **Validate** JSON structure and relationship completeness
6. **Output** to `json/simple/simple-component-entities.json`

**Note:** Database table extraction is handled separately. See `extract-database-entity-simple-complete.md` for database-specific extraction.

Focus on precision, completeness, and maintaining the semantic meaning from the source documentation.
