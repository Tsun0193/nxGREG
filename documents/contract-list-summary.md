# Contract List Module - Entities and Relationships Summary

**Module:** Contract List (契約一覧)  
**Module ID:** `module:contract_list`  
**Generated:** December 3, 2025

---

## Table of Contents

1. [Entity Summary](#entity-summary)
2. [Relationship Summary](#relationship-summary)
3. [Complete Entity Listing](#complete-entity-listing)
4. [Complete Relationship Listing](#complete-relationship-listing)

---

## Entity Summary

### Entity Counts by Type

| Entity Type | Count | Description |
|------------|-------|-------------|
| **Screens** | 10 | UI screens and pages |
| **Views** | 3 | JSP view templates |
| **Buttons** | 9 | Interactive UI buttons |
| **Routes** | 10 | HTTP route mappings |
| **Actions** | 4 | Struts action classes |
| **Action Types** | 9 | Action type identifiers |
| **Events** | 9 | UI interaction events |
| **Flags** | 10 | Business logic control flags |
| **Forms** | 3 | Form beans for data binding |
| **Form Fields** | 17 | Individual form fields |
| **Value Objects** | 4 | Data transfer objects |
| **Sessions** | 9 | Session storage attributes |
| **Functions** | 9 | Business functions |
| **Delegates** | 4 | Business delegate classes |
| **Facades** | 4 | Facade layer classes |
| **Products** | 4 | Business logic products |
| **DAOs** | 16 | Data access objects |
| **Database Tables** | 12 | Database tables accessed |
| **Total Entities** | **146** | |

### Entity Categories

#### 1. Presentation Layer (31 entities)
- **Screens:** Contract List Main, Contract Type Selection, After Contract Creation, Multiple Order Selection, Contract Modification, Additional Contract Creation, Contract Details, Contract Deletion, Contract List From After Screen
- **Views:** keiyakuList.jsp, keiyakuList/body.jsp, keiyakuListAfter/body.jsp
- **Buttons:** New Contract, Add Contract, Update Contract, Delete Contract, After-Sales Contract, Multiple Orders, Contract Number Link, Contract Selection Radio, Return Button

#### 2. Application Layer (26 entities)
- **Routes:** keiyakuListInit, keiyakuListDispatch, keiyakuDelete, keiyakuListAssign, etc.
- **Actions:** KeiyakuListInitAction, KeiyakuListDispatchAction, KeiyakuDeleteAction
- **Action Types:** new_contract, add_contract, update_contract, delete_contract, new_yuusyou_contract, new_yuusyou_after_contract, keiyaku_card_anchor, returnAnken, compliance_mikan
- **Events:** Button click events, link click events, selection change events

#### 3. Business Layer (21 entities)
- **Functions:** List Initialization, Contract Deletion, New Contract Creation, Additional Contract Creation, Contract Modification, Contract Details Display, After-Sales Contract Creation, Multiple Order Creation
- **Delegates:** SyouninUserFindDelegate, AnkenFindDelegate, KeiyakuListFindDelegate, KeiyakuDeleteDelegate
- **Facades:** SyouninUserFindFacadeBean, AnkenFindFacadeBean, KeiyakuListFindFacadeBean, KeiyakuDeleteFacadeBean
- **Products:** SyouninUserFindProduct, AnkenFindProduct, KeiyakuListFindProduct, KeiyakuDeleteProduct

#### 4. Data Layer (40 entities)
- **Forms:** anken_cardForm, keiyaku_cardForm, keiyakuListKensakuForm
- **Form Fields:** 17 fields (ankenNo, keiyakuKey, actionType, etc.)
- **Value Objects:** KeiyakuVO, AnkenVO, AuthorityVO, KeiyakuIchiranVO
- **Sessions:** 9 session attributes for storing contract data, authority, flags
- **DAOs:** 16 DAOs for database operations
- **Database Tables:** 12 tables (t_keiyaku, t_anken, t_kouji, etc.)

#### 5. Control Layer (28 entities)
- **Flags:** 10 flags controlling UI visibility, button states, and business logic flow

---

## Relationship Summary

### Relationship Counts by Category

| Category | Relationship Type | Count | Description |
|----------|------------------|-------|-------------|
| **UI Event Chain** | Screen → View → Button → Event → Action Type → Action | 38 | Complete user interaction flow |
| **Screen Navigation** | Screen ↔ Route ↔ Screen | 15 | Screen-to-screen transitions |
| **Action Processing** | Action → Delegate → Facade → Product → DAO | 0* | Internal component layer (in component file) |
| **Route Mapping** | Route → Action → Function | 11 | HTTP route handling |
| **Form Data Flow** | Form ↔ Value Object ↔ Session | 8 | Data binding and storage |
| **Permission Control** | Flag → Button/Screen | 24 | Visibility and state control |
| **View Rendering** | View → Session → Data | 3 | Data display relationships |
| **Action Forwarding** | Action → Route | 7 | Action dispatch forwarding |
| **Route Forwarding** | Route → Route | 7 | Return navigation flows |
| **Database Access** | DAO → Table | 0* | In database relationships file |
| **Total Cross-Layer** | **119** | |

*Note: Component layer and database relationships are stored in separate files as per architecture.

### Key Relationship Flows

#### Flow 1: User Creates New Contract
```
User Click → button:new_contract 
  → TRIGGERS_EVENT → event:new_contract_button_click
  → INVOKES_ACTION_TYPE → action_type:new_contract
  → ROUTES_TO_ACTION → action:keiyaku_list_dispatch_action
  → FORWARDS_TO_ROUTE → route:keiyaku_list_assign
  → INITIALIZES_SCREEN → screen:contract_type_selection
  → RETURNS_TO_SCREEN → screen:contract_list_main
```

#### Flow 2: User Deletes Contract
```
User Click → button:delete_contract
  → TRIGGERS_EVENT → event:delete_contract_button_click
  → INVOKES_ACTION_TYPE → action_type:delete_contract
  → ROUTES_TO_ACTION → action:keiyaku_list_dispatch_action
  → FORWARDS_TO_ROUTE → route:keiyaku_delete
  → MAPS_TO_ACTION → action:keiyaku_delete_action
  → IMPLEMENTS_FUNCTION → function:contract_deletion
  → FORWARDS_TO_ROUTE → route:keiyaku_list_init
  → INITIALIZES_SCREEN → screen:contract_list_main
```

#### Flow 3: Flag Controls Button Visibility
```
Database → flag:shinki_keiyaku_sakusei_kahi
  → STORED_IN_SESSION → session:business_flag_shinki_keiyaku_sakusei_kahi
  → CONTROLS_VISIBILITY → button:new_contract
```

---

## Complete Entity Listing

### Screens (10)

1. **screen:contract_list_main** - Main contract list screen (GCNT90001)
2. **screen:contract_type_selection** - Contract type selection for new contracts
3. **screen:after_contract_creation** - After-sales contract creation screen (GCNT19001)
4. **screen:multiple_order_selection** - Multiple order selection screen (GCNT90014)
5. **screen:contract_modification** - Contract modification screen group
6. **screen:additional_contract_creation** - Additional contract creation screen group
7. **screen:contract_details** - Contract details display screen group
8. **screen:contract_deletion** - Contract deletion process
9. **screen:contract_list_from_after_screen** - Contract list when returning from after screen
10. **screen:contract_type_selection** - Contract type selection screen

### Views (3)

1. **view:keiyaku_list_jsp** - Main JSP view (keiyakuList.jsp)
2. **view:keiyaku_list_body_jsp** - Body template (keiyakuList/body.jsp)
3. **view:keiyaku_list_after_body_jsp** - After screen body (keiyakuListAfter/body.jsp)

### Buttons (9)

1. **button:new_contract** - New Contract button
2. **button:add_contract** - Additional Contract button
3. **button:update_contract** - Modify Contract button
4. **button:delete_contract** - Delete Contract button
5. **button:yuusyou_contract** - After-Sales Contract button
6. **button:multiple_orders** - Multiple Orders button
7. **button:contract_number_link** - Contract Number Link (clickable/text)
8. **button:contract_selection_radio** - Contract Selection Radio Button
9. **button:return_button** - Return Button

### Routes (10)

1. **route:keiyaku_list_init** - `/keiyakuListInit.do` - Contract list initialization
2. **route:keiyaku_list_from_after_screen_init** - `/keiyakuListFromAfterScreanInit.do` - From after screen
3. **route:keiyaku_list_dispatch** - `/keiyakuListDispatch.do` - Main dispatcher
4. **route:keiyaku_delete** - `/keiyakuDelete.do` - Contract deletion
5. **route:keiyaku_list_assign** - `/keiyakuListAssign.do` - Contract type selection
6. **route:tsuika_keiyaku_dispatch** - `/tsuikaKeiyakuDispatch.do` - Additional contract
7. **route:henko_keiyaku_dispatch** - `/henkoKeiyakuDispatch.do` - Contract modification
8. **route:yuusyou_keiyaku_list_assign** - `/yuusyouKeiyakuListAssign.do` - After-sales
9. **route:moushide_select_init** - `/moushideSelectInit.do` - Multiple orders
10. **route:anchor_keiyaku_dispatch** - `/anchorKeiyakuDispatch.do` - Contract details

### Actions (4)

1. **action:keiyaku_list_init_action** - KeiyakuListInitAction - Initialize contract list
2. **action:keiyaku_list_from_after_screen_init_action** - KeiyakuListFromAfterScreanInitAction - From after screen
3. **action:keiyaku_list_dispatch_action** - KeiyakuListDispatchAction - Main action dispatcher
4. **action:keiyaku_delete_action** - KeiyakuDeleteAction - Contract deletion

### Action Types (9)

1. **action_type:new_contract** - Create new contract
2. **action_type:add_contract** - Create additional contract
3. **action_type:update_contract** - Update contract data
4. **action_type:delete_contract** - Delete contract
5. **action_type:new_yuusyou_contract** - Create after-sales contract
6. **action_type:new_yuusyou_after_contract** - Create multiple orders
7. **action_type:keiyaku_card_anchor** - Display contract details
8. **action_type:returnAnken** - Return to project screen
9. **action_type:compliance_mikan** - Compliance check incomplete

### Events (9)

1. **event:new_contract_button_click** - New contract button clicked
2. **event:add_contract_button_click** - Add contract button clicked
3. **event:update_contract_button_click** - Update contract button clicked
4. **event:delete_contract_button_click** - Delete contract button clicked
5. **event:yuusyou_contract_button_click** - After-sales button clicked
6. **event:multiple_orders_button_click** - Multiple orders button clicked
7. **event:contract_number_link_click** - Contract number link clicked
8. **event:contract_selection_change** - Contract selection changed
9. **event:return_button_click** - Return button clicked

### Flags (10)

1. **flag:shinki_keiyaku_sakusei_kahi** - New contract creation permission
2. **flag:tuika_keiyaku_sakusei_kahi** - Additional contract creation permission
3. **flag:keiyaku_data_henko_kahi** - Contract data modification permission
4. **flag:kani_keiyaku_sakusei_kahi** - After-sales contract creation permission
5. **flag:hukusu_jyutyu_sakusei_hyouji** - Multiple order creation display
6. **flag:anken_bunrui_cd** - Project classification code
7. **flag:keiyaku_card_syubetsu_cd** - Contract card type code
8. **flag:keiyaku_ukagai_kbn** - External contract flag
9. **flag:tuika_kbn** - Contract classification (main/additional)
10. **flag:pre_screan** - Previous screen indicator
11. **flag:user_agent_device** - User agent device detection (iPad)

### Forms (3)

1. **form:anken_card_form** - AnkenCardForm - Project card form
2. **form:keiyaku_card_form** - KeiyakuCardForm - Contract card form
3. **form:keiyaku_list_kensaku_form** - KeiyakuListKensakuForm - Search form

### Form Fields (17)

**anken_cardForm fields:**
1. **form_field:anken_no** - Project Number (required)
2. **form_field:jyutyu_no** - Order Number
3. **form_field:shijisyo_no** - Instruction Sheet Number
4. **form_field:zentai_kbn** - Overall Classification

**keiyaku_cardForm fields:**
5. **form_field:keiyaku_anken_no** - Contract Project Number
6. **form_field:action_type** - Action Type (required)
7. **form_field:keiyaku_key** - Contract Key
8. **form_field:sp_execute_kbn** - Special Execution Classification
9. **form_field:hanbai_bukken_no** - Sales Property Number
10. **form_field:keiyaku_card_syubetsu_cd** - Contract Card Type Code
11. **form_field:kouji_key** - Construction Key
12. **form_field:tab_cd** - Tab Code
13. **form_field:keiyaku_jyutyu_no** - Contract Order Number
14. **form_field:select** - Selected Contract

**keiyakuListKensakuForm fields:**
15. **form_field:search_action_type** - Search Action Type
16. **form_field:jyutyu_jigyousyo_cd** - Order Office Code
17. **form_field:keiyaku_no** - Contract Number
18. **form_field:kouji_name** - Construction Name
19. **form_field:keiyaku_status_cd** - Contract Status Code

### Value Objects (4)

1. **value_object:keiyaku_vo** - KeiyakuVO - Contract data
2. **value_object:anken_vo** - AnkenVO - Project data
3. **value_object:authority_vo** - AuthorityVO - User authority data
4. **value_object:keiyaku_ichiran_vo** - KeiyakuIchiranVO - Contract list summary

### Sessions (9)

1. **session:contract_keiyaku_vo** - CONTRACT_KEIYAKU_VO - Contract main data
2. **session:contract_authority_vo** - CONTRACT_AUTHORITY_VO - User authority
3. **session:contract_option_keiyaku_ichiran_vo_list** - CONTRACT_OPTION_KEIYAKU_ICHIRAN_VO_LIST - Contract list
4. **session:contract_anken_vo** - CONTRACT_ANKEN_VO - Project information
5. **session:contract_action_type** - CONTRACT_ACTION_TYPE - Current action type
6. **session:business_flag_shinki_keiyaku_sakusei_kahi** - New contract creation flag
7. **session:business_flag_tsuika_keiyaku_sakusei_kahi** - Additional contract flag
8. **session:business_flag_keiyaku_data_henko_kahi** - Modification permission flag
9. **session:business_flag_kani_keiyaku_sakusei_kahi** - After-sales flag
10. **session:business_flag_hukusu_jyutyu_sakusei_hyouji** - Multiple order flag

### Functions (9)

1. **function:list_initialization** - Initialize and display contract list
2. **function:contract_deletion** - Delete contract (logical deletion)
3. **function:new_contract_creation** - Create new contract (transitions to other screen)
4. **function:additional_contract_creation** - Create additional contract (transitions)
5. **function:contract_modification** - Modify contract (transitions)
6. **function:contract_details_display** - Display contract details (transitions)
7. **function:after_sales_contract_creation** - Create after-sales contract (transitions)
8. **function:multiple_order_creation** - Create multiple orders (transitions)

### Delegates (4)

1. **delegate:syounin_user_find_delegate** - SyouninUserFindDelegate - User permissions
2. **delegate:anken_find_delegate** - AnkenFindDelegate - Project information
3. **delegate:keiyaku_list_find_delegate** - KeiyakuListFindDelegate - Contract list
4. **delegate:keiyaku_delete_delegate** - KeiyakuDeleteDelegate - Contract deletion

### Facades (4)

1. **facade:syounin_user_find_facade_bean** - SyouninUserFindFacadeBean
2. **facade:anken_find_facade_bean** - AnkenFindFacadeBean
3. **facade:keiyaku_list_find_facade_bean** - KeiyakuListFindFacadeBean
4. **facade:keiyaku_delete_facade_bean** - KeiyakuDeleteFacadeBean

### Products (4)

1. **product:syounin_user_find_product** - SyouninUserFindProduct
2. **product:anken_find_product** - AnkenFindProduct
3. **product:keiyaku_list_find_product** - KeiyakuListFindProduct
4. **product:keiyaku_delete_product** - KeiyakuDeleteProduct

### DAOs (16)

**Find DAOs:**
1. **dao:syounin_user_find_dao** - SyouninUserFindDAO - User permissions query
2. **dao:anken_find_dao** - AnkenFindDAO - Project query
3. **dao:keiyaku_ichiran_find_dao** - KeiyakuIchiranFindDAO - Contract list query
4. **dao:keiyaku_find_dao** - KeiyakuFindDAO - Contract query
5. **dao:kouji_find_dao** - KoujiFindDAO - Construction query
6. **dao:keiyaku_shijisyo_kankei_find_dao** - Contract-instruction relationship
7. **dao:chintaisyaku_keiyaku_kankei_find_dao** - Rental contract relationship
8. **dao:gijyutsu_anken_kihon_find_dao** - Technical project basics
9. **dao:keiyaku_kokyaku_kankei_find_dao** - Contract-customer relationship
10. **dao:kojin_tasya_keiyaku_kbn_find_dao** - Individual contract classification

**Update/Delete DAOs:**
11. **dao:keiyaku_dao** - KeiyakuDAO - Contract soft deletion
12. **dao:kouji_dao** - KoujiDAO - Construction soft deletion
13. **dao:keiyaku_shijisyo_kankei_dao** - Contract-instruction hard deletion
14. **dao:chintaisyaku_keiyaku_kankei_dao** - Rental contract hard deletion
15. **dao:kojin_tasya_keiyaku_kbn_dao** - Customer classification update

### Database Tables (12)

1. **database_table:t_syounin_user** - T_SYOUNIN_USER - User permissions
2. **database_table:t_anken** - T_ANKEN - Project table
3. **database_table:t_keiyaku** - T_KEIYAKU - Contract table
4. **database_table:t_kouji** - T_KOUJI - Construction table
5. **database_table:t_keiyaku_shijisyo_kankei** - Contract-instruction relationship
6. **database_table:t_chintaisyaku_keiyaku_kankei** - Rental contract relationship
7. **database_table:t_gijyutsu_anken_kihon** - Technical project basics
8. **database_table:t_keiyaku_kokyaku_kankei** - Contract-customer relationship
9. **database_table:t_kokyaku_kojin** - Individual customer
10. **database_table:t_keiyaku_koutei** - Contract process
11. **database_table:t_jyutyu_koutei** - Order process
12. **database_table:t_ukagaisyo_teikeigai_koutei** - Non-standard approval process

---

## Complete Relationship Listing

### Category 1: Screen-to-View-to-Form (8 relationships)

1. `screen:contract_list_main` → `USES_ROUTE` → `route:keiyaku_list_init`
2. `screen:contract_list_main` → `DISPLAYS_VIEW` → `view:keiyaku_list_jsp`
3. `screen:contract_list_main` → `USES_FORM` → `form:anken_card_form`
4. `screen:contract_type_selection` → `USES_ROUTE` → `route:keiyaku_list_assign`
5. `screen:after_contract_creation` → `USES_ROUTE` → `route:yuusyou_keiyaku_list_assign`
6. `screen:multiple_order_selection` → `USES_ROUTE` → `route:moushide_select_init`
7. `screen:contract_deletion` → `USES_ROUTE` → `route:keiyaku_delete`
8. `screen:contract_list_from_after_screen` → `USES_ROUTE` → `route:keiyaku_list_from_after_screen_init`

### Category 2: View-Contains-Button (9 relationships)

9. `view:keiyaku_list_jsp` → `CONTAINS_BUTTON` → `button:new_contract`
10. `view:keiyaku_list_jsp` → `CONTAINS_BUTTON` → `button:add_contract`
11. `view:keiyaku_list_jsp` → `CONTAINS_BUTTON` → `button:update_contract`
12. `view:keiyaku_list_jsp` → `CONTAINS_BUTTON` → `button:delete_contract`
13. `view:keiyaku_list_jsp` → `CONTAINS_BUTTON` → `button:yuusyou_contract`
14. `view:keiyaku_list_jsp` → `CONTAINS_BUTTON` → `button:multiple_orders`
15. `view:keiyaku_list_jsp` → `CONTAINS_BUTTON` → `button:return_button`
16. `view:keiyaku_list_body_jsp` → `CONTAINS_BUTTON` → `button:contract_number_link`
17. `view:keiyaku_list_body_jsp` → `CONTAINS_BUTTON` → `button:contract_selection_radio`

### Category 3: Button-Triggers-Event (9 relationships)

18. `button:new_contract` → `TRIGGERS_EVENT` → `event:new_contract_button_click`
19. `button:add_contract` → `TRIGGERS_EVENT` → `event:add_contract_button_click`
20. `button:update_contract` → `TRIGGERS_EVENT` → `event:update_contract_button_click`
21. `button:delete_contract` → `TRIGGERS_EVENT` → `event:delete_contract_button_click`
22. `button:yuusyou_contract` → `TRIGGERS_EVENT` → `event:yuusyou_contract_button_click`
23. `button:multiple_orders` → `TRIGGERS_EVENT` → `event:multiple_orders_button_click`
24. `button:contract_number_link` → `TRIGGERS_EVENT` → `event:contract_number_link_click`
25. `button:contract_selection_radio` → `TRIGGERS_EVENT` → `event:contract_selection_change`
26. `button:return_button` → `TRIGGERS_EVENT` → `event:return_button_click`

### Category 4: Event-Invokes-ActionType (8 relationships)

27. `event:new_contract_button_click` → `INVOKES_ACTION_TYPE` → `action_type:new_contract`
28. `event:add_contract_button_click` → `INVOKES_ACTION_TYPE` → `action_type:add_contract`
29. `event:update_contract_button_click` → `INVOKES_ACTION_TYPE` → `action_type:update_contract`
30. `event:delete_contract_button_click` → `INVOKES_ACTION_TYPE` → `action_type:delete_contract`
31. `event:yuusyou_contract_button_click` → `INVOKES_ACTION_TYPE` → `action_type:new_yuusyou_contract`
32. `event:multiple_orders_button_click` → `INVOKES_ACTION_TYPE` → `action_type:new_yuusyou_after_contract`
33. `event:contract_number_link_click` → `INVOKES_ACTION_TYPE` → `action_type:keiyaku_card_anchor`
34. `event:return_button_click` → `INVOKES_ACTION_TYPE` → `action_type:returnAnken`

### Category 5: ActionType-Routes-To-Action (8 relationships)

35. `action_type:new_contract` → `ROUTES_TO_ACTION` → `action:keiyaku_list_dispatch_action`
36. `action_type:add_contract` → `ROUTES_TO_ACTION` → `action:keiyaku_list_dispatch_action`
37. `action_type:update_contract` → `ROUTES_TO_ACTION` → `action:keiyaku_list_dispatch_action`
38. `action_type:delete_contract` → `ROUTES_TO_ACTION` → `action:keiyaku_list_dispatch_action`
39. `action_type:new_yuusyou_contract` → `ROUTES_TO_ACTION` → `action:keiyaku_list_dispatch_action`
40. `action_type:new_yuusyou_after_contract` → `ROUTES_TO_ACTION` → `action:keiyaku_list_dispatch_action`
41. `action_type:keiyaku_card_anchor` → `ROUTES_TO_ACTION` → `action:keiyaku_list_dispatch_action`
42. `action_type:returnAnken` → `ROUTES_TO_ACTION` → `action:keiyaku_list_dispatch_action`

### Category 6: Route-Maps-To-Action (4 relationships)

43. `route:keiyaku_list_init` → `MAPS_TO_ACTION` → `action:keiyaku_list_init_action`
44. `route:keiyaku_list_from_after_screen_init` → `MAPS_TO_ACTION` → `action:keiyaku_list_from_after_screen_init_action`
45. `route:keiyaku_list_dispatch` → `MAPS_TO_ACTION` → `action:keiyaku_list_dispatch_action`
46. `route:keiyaku_delete` → `MAPS_TO_ACTION` → `action:keiyaku_delete_action`

### Category 7: Route-Initializes-Screen (4 relationships)

47. `route:keiyaku_list_init` → `INITIALIZES_SCREEN` → `screen:contract_list_main`
48. `route:keiyaku_list_assign` → `INITIALIZES_SCREEN` → `screen:contract_type_selection`
49. `route:yuusyou_keiyaku_list_assign` → `INITIALIZES_SCREEN` → `screen:after_contract_creation`
50. `route:moushide_select_init` → `INITIALIZES_SCREEN` → `screen:multiple_order_selection`

### Category 8: Action-Implements-Function (2 relationships)

51. `action:keiyaku_list_init_action` → `IMPLEMENTS_FUNCTION` → `function:list_initialization`
52. `action:keiyaku_delete_action` → `IMPLEMENTS_FUNCTION` → `function:contract_deletion`

### Category 9: Action-Forwards-To-Route (7 relationships)

53. `action:keiyaku_list_dispatch_action` → `FORWARDS_TO_ROUTE` → `route:keiyaku_list_assign`
54. `action:keiyaku_list_dispatch_action` → `FORWARDS_TO_ROUTE` → `route:tsuika_keiyaku_dispatch`
55. `action:keiyaku_list_dispatch_action` → `FORWARDS_TO_ROUTE` → `route:henko_keiyaku_dispatch`
56. `action:keiyaku_list_dispatch_action` → `FORWARDS_TO_ROUTE` → `route:keiyaku_delete`
57. `action:keiyaku_list_dispatch_action` → `FORWARDS_TO_ROUTE` → `route:yuusyou_keiyaku_list_assign`
58. `action:keiyaku_list_dispatch_action` → `FORWARDS_TO_ROUTE` → `route:moushide_select_init`
59. `action:keiyaku_list_dispatch_action` → `FORWARDS_TO_ROUTE` → `route:anchor_keiyaku_dispatch`

### Category 10: Route-Forwards-To-Route (7 relationships)

60. `route:keiyaku_delete` → `FORWARDS_TO_ROUTE` → `route:keiyaku_list_init`
61. `route:keiyaku_list_assign` → `FORWARDS_TO_ROUTE` → `route:keiyaku_list_init`
62. `route:tsuika_keiyaku_dispatch` → `FORWARDS_TO_ROUTE` → `route:keiyaku_list_init`
63. `route:henko_keiyaku_dispatch` → `FORWARDS_TO_ROUTE` → `route:keiyaku_list_init`
64. `route:yuusyou_keiyaku_list_assign` → `FORWARDS_TO_ROUTE` → `route:keiyaku_list_init`
65. `route:moushide_select_init` → `FORWARDS_TO_ROUTE` → `route:keiyaku_list_init`
66. `route:anchor_keiyaku_dispatch` → `FORWARDS_TO_ROUTE` → `route:keiyaku_list_init`

### Category 11: Function-Uses-Form (2 relationships)

67. `function:list_initialization` → `USES_FORM` → `form:anken_card_form`
68. `function:contract_deletion` → `USES_FORM` → `form:keiyaku_card_form`

### Category 12: Form-Maps-To-VO (2 relationships)

69. `form:anken_card_form` → `MAPS_TO_VO` → `value_object:anken_vo`
70. `form:keiyaku_card_form` → `MAPS_TO_VO` → `value_object:keiyaku_vo`

### Category 13: Session-Stores-VO (4 relationships)

71. `session:contract_keiyaku_vo` → `STORES_VO` → `value_object:keiyaku_vo`
72. `session:contract_authority_vo` → `STORES_VO` → `value_object:authority_vo`
73. `session:contract_option_keiyaku_ichiran_vo_list` → `STORES_VO` → `value_object:keiyaku_ichiran_vo`
74. `session:contract_anken_vo` → `STORES_VO` → `value_object:anken_vo`

### Category 14: Flag-Controls-Visibility (5 relationships)

75. `flag:shinki_keiyaku_sakusei_kahi` → `CONTROLS_VISIBILITY` → `button:new_contract`
76. `flag:tuika_keiyaku_sakusei_kahi` → `CONTROLS_VISIBILITY` → `button:add_contract`
77. `flag:keiyaku_data_henko_kahi` → `CONTROLS_VISIBILITY` → `button:update_contract`
78. `flag:kani_keiyaku_sakusei_kahi` → `CONTROLS_VISIBILITY` → `button:yuusyou_contract`
79. `flag:hukusu_jyutyu_sakusei_hyouji` → `CONTROLS_VISIBILITY` → `button:multiple_orders`

### Category 15: Flag-Controls-State (10 relationships)

80. `flag:anken_bunrui_cd` → `CONTROLS_STATE` → `button:delete_contract`
81. `flag:keiyaku_card_syubetsu_cd` → `CONTROLS_STATE` → `button:contract_number_link`
82. `flag:keiyaku_card_syubetsu_cd` → `CONTROLS_VISIBILITY` → `button:contract_selection_radio`
83. `flag:keiyaku_ukagai_kbn` → `CONTROLS_STATE` → `button:contract_number_link`
84. `flag:keiyaku_ukagai_kbn` → `CONTROLS_STATE` → `button:contract_selection_radio`
85. `flag:user_agent_device` → `CONTROLS_VISIBILITY` → `button:new_contract`
86. `flag:user_agent_device` → `CONTROLS_VISIBILITY` → `button:add_contract`
87. `flag:user_agent_device` → `CONTROLS_VISIBILITY` → `button:update_contract`
88. `flag:user_agent_device` → `CONTROLS_VISIBILITY` → `button:delete_contract`
89. `flag:user_agent_device` → `CONTROLS_VISIBILITY` → `button:yuusyou_contract`
90. `flag:user_agent_device` → `CONTROLS_VISIBILITY` → `button:multiple_orders`
91. `flag:user_agent_device` → `CONTROLS_STATE` → `button:contract_number_link`

### Category 16: Flag-Stored-In-Session (5 relationships)

92. `flag:shinki_keiyaku_sakusei_kahi` → `STORED_IN_SESSION` → `session:business_flag_shinki_keiyaku_sakusei_kahi`
93. `flag:tuika_keiyaku_sakusei_kahi` → `STORED_IN_SESSION` → `session:business_flag_tsuika_keiyaku_sakusei_kahi`
94. `flag:keiyaku_data_henko_kahi` → `STORED_IN_SESSION` → `session:business_flag_keiyaku_data_henko_kahi`
95. `flag:kani_keiyaku_sakusei_kahi` → `STORED_IN_SESSION` → `session:business_flag_kani_keiyaku_sakusei_kahi`
96. `flag:hukusu_jyutyu_sakusei_hyouji` → `STORED_IN_SESSION` → `session:business_flag_hukusu_jyutyu_sakusei_hyouji`

### Category 17: View-Composition (2 relationships)

97. `view:keiyaku_list_jsp` → `INCLUDES_VIEW` → `view:keiyaku_list_body_jsp`
98. `view:keiyaku_list_body_jsp` → `DISPLAYS_SESSION_DATA` → `session:contract_option_keiyaku_ichiran_vo_list`

### Category 18: ActionType-Navigates-To-Screen (6 relationships)

99. `action_type:new_contract` → `NAVIGATES_TO_SCREEN` → `screen:contract_type_selection`
100. `action_type:add_contract` → `NAVIGATES_TO_SCREEN` → `screen:additional_contract_creation`
101. `action_type:update_contract` → `NAVIGATES_TO_SCREEN` → `screen:contract_modification`
102. `action_type:new_yuusyou_contract` → `NAVIGATES_TO_SCREEN` → `screen:after_contract_creation`
103. `action_type:new_yuusyou_after_contract` → `NAVIGATES_TO_SCREEN` → `screen:multiple_order_selection`
104. `action_type:keiyaku_card_anchor` → `NAVIGATES_TO_SCREEN` → `screen:contract_details`

### Category 19: Screen-Returns-To-Screen (7 relationships)

105. `screen:contract_deletion` → `RETURNS_TO_SCREEN` → `screen:contract_list_main`
106. `screen:contract_type_selection` → `RETURNS_TO_SCREEN` → `screen:contract_list_main`
107. `screen:additional_contract_creation` → `RETURNS_TO_SCREEN` → `screen:contract_list_main`
108. `screen:contract_modification` → `RETURNS_TO_SCREEN` → `screen:contract_list_main`
109. `screen:after_contract_creation` → `RETURNS_TO_SCREEN` → `screen:contract_list_main`
110. `screen:multiple_order_selection` → `RETURNS_TO_SCREEN` → `screen:contract_list_main`
111. `screen:contract_details` → `RETURNS_TO_SCREEN` → `screen:contract_list_main`

### Category 20: Screen-Uses-Form (7 relationships)

112. `screen:contract_type_selection` → `USES_FORM` → `form:keiyaku_card_form`
113. `screen:after_contract_creation` → `USES_FORM` → `form:keiyaku_card_form`
114. `screen:multiple_order_selection` → `USES_FORM` → `form:keiyaku_card_form`
115. `screen:contract_modification` → `USES_FORM` → `form:keiyaku_card_form`
116. `screen:additional_contract_creation` → `USES_FORM` → `form:keiyaku_card_form`
117. `screen:contract_details` → `USES_FORM` → `form:keiyaku_card_form`
118. `screen:contract_deletion` → `USES_FORM` → `form:keiyaku_card_form`

### Category 21: Flag-Controls-View (1 relationship)

119. `flag:pre_screan` → `CONTROLS_STATE` → `view:keiyaku_list_body_jsp`

---

## Statistics

- **Total Entities:** 146
- **Total Cross-Layer Relationships:** 119
- **Component Relationships:** Stored in `contract-list-component-entities.json`
- **Database Relationships:** Stored in `contract-list-database-relationships.json`
- **Average Relationships per Entity:** 1.6
- **Most Connected Entity:** `action:keiyaku_list_dispatch_action` (14 relationships)
- **Entity Types:** 18 different types
- **Relationship Types:** 21 different types

---

## Files Generated

1. **`json/contract-list-entities.json`** - Core entities (60 entities)
2. **`json/contract-list-component-entities.json`** - Component layer entities with internal relationships (30 entities)
3. **`json/contract-list-ui-interaction-entities.json`** - UI and interaction entities (49 entities)
4. **`json/contract-list-database-relationships.json`** - Database-specific relationships
5. **`json/contract-list-cross-layer-relationships.json`** - Cross-layer relationships (119 relationships) ✓ **Current File**

---

## Notes

- All properties are flattened at the top level for Neo4j compatibility
- No nested `properties` or `metadata` objects
- Relationships between component layers (Action→Delegate→Facade→Product→DAO) are in the component entities file
- Database access relationships (DAO→Table) are in the database relationships file
- This file focuses on cross-layer relationships that connect different architectural layers

---

**Document Version:** 1.0  
**Last Updated:** December 3, 2025  
**Format:** Neo4j-compatible flattened properties
