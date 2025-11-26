# Component Entity Extraction: Contract List Module

## Role & Context
You are a professional technical document analyzer extracting **component-level entities** (Action, Delegate, Facade, Product, DAO, ...) from the contract-list module documentation.

**Parent Document:** `extract-entity-contract-list.md`

**Current Task:** Extract architectural component entities from the layered architecture of the contract-list module.

---

## Input Specification

### Source Files
Primary source for component identification:
- `ctc-data-en/contract-list/overview-en.md` - Main Features section lists components
- `ctc-data-en/contract-list/functions/init-screen/function-overview-en.md` - Init function components
- `ctc-data-en/contract-list/functions/delete-contract/function-overview-en.md` - Delete function components
- `ctc-data-en/contract-list/data-architecture-en.md` - Architecture overview

### Component Identification Pattern
Look for sections labeled **"Main Components"** in function overviews. Example:
```
- **Main Components**: `KeiyakuDeleteAction`, `KeiyakuDeleteDelegate`, `KeiyakuDeleteFacadeBean`, `KeiyakuDeleteProduct`
```

---

## Entity Taxonomy for Components

### 1. Action Entities
- **Type ID:** `action`
- **Properties:** 
  - `action_name`: Name of the Struts action class
  - `action_path`: URL path (e.g., `/keiyakuListInit`)
  - `http_method`: HTTP method (GET/POST)
  - `form_bean`: Associated form bean
  - `forward_destinations`: Possible forward targets
  - `validation_enabled`: Whether validation is enabled
  - `dispatch_methods`: List of dispatch methods (for DispatchAction)
- **Notes:** Extract all Struts action classes including dispatch actions, init actions, and specialized actions

**Example:**
```json
{
  "id": "action:keiyaku_list_init_action",
  "type": "action",
  "name": "Contract List Init Action",
  "parent_module": "module:contract-list",
  "properties": {
    "action_name": "KeiyakuListInitAction",
    "action_path": "/keiyakuListInit",
    "http_method": "GET/POST",
    "form_bean": "anken_cardForm",
    "forward_destinations": ["success", "error"],
    "validation_enabled": false,
    "package": "jp.co.daiwahouse.dsmart.application.contract.keiyakuList.keiyakuListInit"
  },
  "metadata": {
    "source_file": "ctc-data-en/contract-list/functions/init-screen/function-overview-en.md"
  }
}
```

### 2. Delegate Entities
- **Type ID:** `delegate`
- **Properties:** 
  - `delegate_name`: Name of the delegate class
  - `purpose`: Business purpose description
  - `facade_dependencies`: List of facades called
  - `package`: Java package path
- **Notes:** Delegate layer classes that bridge Actions and Facades

**Example:**
```json
{
  "id": "delegate:keiyaku_list_find_delegate",
  "type": "delegate",
  "name": "Contract List Find Delegate",
  "parent_module": "module:contract-list",
  "properties": {
    "delegate_name": "KeiyakuListFindDelegate",
    "purpose": "Retrieve contract list from business layer",
    "facade_dependencies": ["KeiyakuListFindFacadeBean"],
    "package": "jp.co.daiwahouse.dsmart.delegate.contract.keiyakuList"
  },
  "metadata": {
    "source_file": "ctc-data-en/contract-list/functions/init-screen/function-overview-en.md"
  }
}
```

### 3. Facade Entities
- **Type ID:** `facade`
- **Properties:** 
  - `facade_name`: Name of the facade bean class
  - `purpose`: Business orchestration purpose
  - `product_dependencies`: List of products called
  - `package`: Java package path
- **Notes:** Facade layer classes that orchestrate business logic

**Example:**
```json
{
  "id": "facade:keiyaku_list_find_facade_bean",
  "type": "facade",
  "name": "Contract List Find Facade Bean",
  "parent_module": "module:contract-list",
  "properties": {
    "facade_name": "KeiyakuListFindFacadeBean",
    "purpose": "Facade for contract list retrieval",
    "product_dependencies": ["KeiyakuListFindProduct"],
    "package": "jp.co.daiwahouse.dsmart.service.contract.keiyakuList"
  },
  "metadata": {
    "source_file": "ctc-data-en/contract-list/functions/init-screen/function-overview-en.md"
  }
}
```

### 4. Product Entities
- **Type ID:** `product`
- **Properties:** 
  - `product_name`: Name of the product class
  - `purpose`: Core business logic purpose
  - `dao_dependencies`: List of DAOs used
  - `package`: Java package path
- **Notes:** Product layer classes containing core business logic

**Example:**
```json
{
  "id": "product:keiyaku_list_find_product",
  "type": "product",
  "name": "Contract List Find Product",
  "parent_module": "module:contract-list",
  "properties": {
    "product_name": "KeiyakuListFindProduct",
    "purpose": "Business logic for contract list retrieval",
    "dao_dependencies": ["KeiyakuIchiranFindDAO", "AnkenFindDAO"],
    "package": "jp.co.daiwahouse.dsmart.service.contract.product.keiyakuList"
  },
  "metadata": {
    "source_file": "ctc-data-en/contract-list/functions/init-screen/function-overview-en.md"
  }
}
```

### 5. DAO Entities
- **Type ID:** `dao`
- **Properties:** 
  - `dao_name`: Name of the DAO class
  - `purpose`: Data access purpose
  - `target_tables`: List of database tables accessed
  - `operations`: CRUD operations supported
  - `package`: Java package path
- **Notes:** Data Access Object classes. Reference database tables in `target_tables` property instead of creating separate database entities.

**Example:**
```json
{
  "id": "dao:keiyaku_ichiran_find_dao",
  "type": "dao",
  "name": "Contract List Find DAO",
  "parent_module": "module:contract-list",
  "properties": {
    "dao_name": "KeiyakuIchiranFindDAO",
    "purpose": "Query for contract list",
    "target_tables": ["t_keiyaku", "t_anken", "t_keiyaku_kokyaku_kankei"],
    "operations": ["READ"],
    "package": "jp.co.daiwahouse.dsmart.domain.contract.find"
  },
  "metadata": {
    "source_file": "ctc-data-en/contract-list/functions/init-screen/function-overview-en.md"
  }
}
```

---

## Extraction Guidelines

### Component Discovery Process

1. **Identify Functions**: Look for function sections in `overview-en.md` (e.g., "List Initialization Feature", "Contract Deletion Feature")

2. **Extract Component Lists**: Find "Main Components" sections that list Action, Delegate, Facade, Product, and DAO classes

3. **Find Detailed Information**: Check function-specific documentation in `functions/*/function-overview-en.md` for:
   - Component table with Layer/Class/Package/Purpose columns
   - Package paths
   - Dependencies between layers

4. **Map Architecture**: Follow the layered architecture pattern:
   ```
   Action → Delegate → Facade → Product → DAO
   ```

### Required Components for Contract List Module

Based on `overview-en.md`, extract components for these functions:

#### 1. List Initialization Feature
- `KeiyakuListInitAction`
- `KeiyakuListFindDelegate`
- `KeiyakuListFindFacadeBean`
- `KeiyakuListFindProduct`
- Plus supporting delegates/facades/products for:
  - `SyouninUserFindDelegate`, `SyouninUserFindFacadeBean`, `SyouninUserFindProduct`
  - `AnkenFindDelegate`, `AnkenFindFacadeBean`, `AnkenFindProduct`
- DAOs: `SyouninUserFindDAO`, `AnkenFindDAO`, `KeiyakuIchiranFindDAO`

#### 2. Contract Deletion Feature
- `KeiyakuDeleteAction`
- `KeiyakuDeleteDelegate`
- `KeiyakuDeleteFacadeBean`
- `KeiyakuDeleteProduct`
- DAOs: `KeiyakuDAO`, `KoujiDAO`, `KeiyakuShijisyoKankeiDAO`, `ChintaisyakuKeiyakuKankeiDAO`, and others

#### 3. Dispatch Action (Routing)
- `KeiyakuListDispatchAction`
- This action routes to other actions based on `actionType`

### Completeness Checklist

For each function documented, ensure you extract:
- [ ] All Action entity
- [ ] All Delegate entities mentioned
- [ ] All Facade entities mentioned
- [ ] All Product entities mentioned
- [ ] All DAO entities mentioned (with target_tables property)

---

## Output Specification

### Format
Output must be a valid JSON file containing an array of component entity objects.

### File Name
`json/contract-list-component-entities.json`

### Validation Requirements
- Each entity must have all required fields: `id`, `type`, `name`, `parent_module`, `properties`, `metadata`
- Component names must match exactly as documented
- Dependencies must reference other components by their class names
- DAOs must include `target_tables` property with database table references

---

## Task Execution Steps

1. **Read** `ctc-data-en/contract-list/overview-en.md` and identify all functions with "Main Components"
2. **Read** detailed function overviews in `functions/*/function-overview-en.md`
3. **Extract** all Action, Delegate, Facade, Product, and DAO entities
4. **Map** dependencies between layers
5. **Include** database table references in DAO entities
6. **Validate** JSON structure and completeness
7. **Output** to `json/contract-list-component-entities.json`

Focus on capturing the complete layered architecture with accurate component names, packages, and dependencies.

- When a function, DAO, or SQL query uses database tables, reference them in properties like `used_database_tables`, `target_tables`, or `tables_involved`
- Example: `"used_database_tables": ["t_keiyaku", "t_anken", "t_kouji"]`


2. **Database Tables**: DO NOT create separate database entities. Reference tables in entity properties:
   - For functions: use `used_database_tables` property
   - For DAOs: use `target_tables` property
   - For SQL queries: use `tables_involved` property
