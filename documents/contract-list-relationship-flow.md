# Contract List Module - Relationship Flow

## Overview
This document maps the complete relationship flow for the contract-list module to support knowledge graph RAG queries about code structure, data flow, and system dependencies.

---

## 1. Screen to View Relationships

### 1.1 Main Screen Flow
```
screen:contract_list_main
  → view:keiyaku_list_jsp
    → component:contract_list_table
    → component:action_buttons
    → component:search_form
    → component:error_block
```

### 1.2 Screen Components
```
view:keiyaku_list_jsp
  → jsp_file:/webapp/dsmart/docroot/contract/keiyakuList/keiyakuList.jsp
    → includes:body.jsp
    → includes:/common/error.txt
    → uses:struts_logic_iterate
    → uses:struts_html_button
```

---

## 2. UI Interaction Flow

### 2.1 New Contract Flow
```
screen:contract_list_main
  → view:keiyaku_list_jsp
    → button:new_contract
      → event:new_contract_button_click
        → javascript:keiyakuList_submit(1)
          → sets:actionType=new_contract
          → submits:form:keiyaku_cardForm
            → action:keiyaku_list_dispatch_action
              → url:/dsmart/contract/keiyakuList/keiyakuListDispatch.do
                → forwards_to:keiyaku_list_assign_action
                  → screen:contract_type_selection
                    → on_complete:screen:contract_list_main
```

### 2.2 Add Contract Flow
```
screen:contract_list_main
  → view:keiyaku_list_jsp
    → button:add_contract
      → event:add_contract_button_click
        → javascript:keiyakuList_submit(3)
          → validates:radio_selection
          → sets:actionType=add_contract
          → sets:keiyakuKey
          → submits:form:keiyaku_cardForm
            → action:keiyaku_list_dispatch_action
              → forwards_to:tsuika_keiyaku_dispatch_action
                → screen:additional_contract_creation
                  → on_complete:screen:contract_list_main
```

### 2.3 Update Contract Flow
```
screen:contract_list_main
  → view:keiyaku_list_jsp
    → button:update_contract
      → event:update_contract_button_click
        → javascript:keiyakuList_submit(2)
          → validates:radio_selection
          → sets:actionType=update_contract
          → sets:keiyakuKey
          → submits:form:keiyaku_cardForm
            → action:keiyaku_list_dispatch_action
              → forwards_to:henko_keiyaku_dispatch_action
                → screen:contract_modification
                  → on_complete:screen:contract_list_main
```

### 2.4 Delete Contract Flow
```
screen:contract_list_main
  → view:keiyaku_list_jsp
    → button:delete_contract
      → event:delete_contract_button_click
        → javascript:keiyakuList_submit(4)
          → validates:radio_selection
          → shows:confirmation_dialog:comDeleteConfirm
            → on_confirm:
              → sets:actionType=delete_contract
              → sets:keiyakuKey
              → submits:form:keiyaku_cardForm
                → action:keiyaku_list_dispatch_action
                  → forwards_to:keiyaku_delete_action
                    → processes:contract_deletion
                      → forwards_to:keiyaku_list_init_action
                        → reloads:screen:contract_list_main
```

### 2.5 Contract Details Display Flow
```
screen:contract_list_main
  → view:keiyaku_list_jsp
    → link:contract_number_link
      → event:contract_link_click
        → javascript:keiyakuAnchor_submit()
          → sets:actionType=keiyaku_card_anchor
          → sets:keiyakuKey
          → submits:form:keiyaku_cardForm
            → action:keiyaku_list_dispatch_action
              → forwards_to:anchor_keiyaku_dispatch_action
                → determines:contract_type
                  → screen:contract_details
                    → on_complete:screen:contract_list_main
```

### 2.6 After-Sales Contract Flow
```
screen:contract_list_main
  → view:keiyaku_list_jsp
    → button:new_yuusyou_contract
      → event:after_sales_contract_button_click
        → javascript:keiyakuList_submit(5)
          → sets:actionType=new_yuusyou_contract
          → submits:form:keiyaku_cardForm
            → action:keiyaku_list_dispatch_action
              → forwards_to:yuusyou_keiyaku_list_assign_action
                → screen:simple_contract_creation
                  → on_complete:screen:contract_list_main
```

### 2.7 Multiple Orders Flow
```
screen:contract_list_main
  → view:keiyaku_list_jsp
    → button:multiple_orders
      → event:multiple_orders_button_click
        → javascript:doFukusujyutyuSakusei()
          → sets:actionType=multipleOrder
          → submits:form:keiyaku_cardForm
            → action:keiyaku_list_dispatch_action
              → forwards_to:moushide_select_init_action
                → screen:multiple_orders_creation
                  → on_complete:screen:contract_list_main
```

---

## 3. Action Layer Relationships

### 3.1 Initialize Screen Action
```
action:keiyaku_list_init_action
  → class:KeiyakuListInitAction
    → package:jp.co.daiwahouse.dsmart.application.contract.keiyakuList.keiyakuListInit
    → url:/dsmart/contract/keiyakuList/keiyakuListInit.do
    → receives:form:anken_cardForm
    → receives:param:ankenNo
    → calls:delegate:syounin_user_find_delegate
    → calls:delegate:anken_find_delegate
    → calls:delegate:keiyaku_list_find_delegate
    → sets:session:CONTRACT_KEIYAKU_VO
    → sets:session:CONTRACT_AUTHORITY_VO
    → sets:session:CONTRACT_OPTION_KEIYAKU_ICHIRAN_VO_LIST
    → sets:session:CONTRACT_ANKEN_VO
    → sets:session:CONTRACT_SHINKI_KEIYAKU_SAKUSEI_KAHI_FLG
    → sets:session:CONTRACT_TSUIKA_KEIYAKU_SAKUSEI_KAHI_FLG
    → sets:session:CONTRACT_KEIYAKU_DATA_HENKO_KAHI_FLG
    → sets:session:CONTRACT_KANI_KEIYAKU_SAKUSEI_KAHI_FLG
    → sets:session:CONTRACT_HUKUSU_JYUTYU_SAKUSEI_HYOUJI_FLG
    → forwards_to:view:keiyaku_list_jsp
```

### 3.2 Dispatch Action
```
action:keiyaku_list_dispatch_action
  → class:KeiyakuListDispatchAction
    → package:jp.co.daiwahouse.dsmart.application.contract.keiyakuList
    → url:/dsmart/contract/keiyakuList/keiyakuListDispatch.do
    → receives:form:keiyaku_cardForm
    → reads:param:actionType
    → routes_by:actionType
      → actionType=new_contract
        → forwards_to:keiyaku_list_assign_action
      → actionType=add_contract
        → forwards_to:tsuika_keiyaku_dispatch_action
      → actionType=update_contract
        → forwards_to:henko_keiyaku_dispatch_action
      → actionType=delete_contract
        → forwards_to:keiyaku_delete_action
      → actionType=keiyaku_card_anchor
        → forwards_to:anchor_keiyaku_dispatch_action
      → actionType=new_yuusyou_contract
        → forwards_to:yuusyou_keiyaku_list_assign_action
      → actionType=multipleOrder
        → forwards_to:moushide_select_init_action
      → actionType=returnAnken
        → forwards_to:keiyaku_list_init_action
      → actionType=compliance_mikan
        → forwards_to:compliance_check_kekka_jsp
```

### 3.3 Delete Action
```
action:keiyaku_delete_action
  → class:KeiyakuDeleteAction
    → package:jp.co.daiwahouse.dsmart.application.contract.keiyakuList
    → url:/dsmart/contract/keiyakuList/keiyakuDelete.do
    → receives:form:keiyaku_cardForm
    → receives:param:keiyakuKey
    → validates:contract_selection
    → calls:delegate:keiyaku_delete_delegate
    → on_success:
      → updates:session:CONTRACT_KEIYAKU_VO
      → updates:session:CONTRACT_ACTION_TYPE
      → forwards_to:keiyaku_list_init_action
    → on_error:
      → sets:error_messages
      → forwards_to:keiyaku_list_init_action
```

---

## 4. Delegate Layer Relationships

### 4.1 Find Delegates (Read Operations)
```
delegate:syounin_user_find_delegate
  → class:SyouninUserFindDelegate
    → package:jp.co.daiwahouse.dsmart.delegate.contract.keiyakuList
    → calls:facade:syounin_user_find_facade_bean
    → returns:vo:authority_vo

delegate:anken_find_delegate
  → class:AnkenFindDelegate
    → package:jp.co.daiwahouse.dsmart.delegate.contract.keiyakuList
    → calls:facade:anken_find_facade_bean
    → returns:vo:anken_vo

delegate:keiyaku_list_find_delegate
  → class:KeiyakuListFindDelegate
    → package:jp.co.daiwahouse.dsmart.delegate.contract.keiyakuList
    → calls:facade:keiyaku_list_find_facade_bean
    → returns:list:keiyaku_ichiran_vo_list
```

### 4.2 Delete Delegate (Write Operation)
```
delegate:keiyaku_delete_delegate
  → class:KeiyakuDeleteDelegate
    → package:jp.co.daiwahouse.dsmart.delegate.contract.keiyakuList
    → method:update(formMap, vo)
    → calls:facade:keiyaku_delete_facade_bean
    → returns:result_code
```

---

## 5. Facade Layer Relationships

### 5.1 Find Facades
```
facade:syounin_user_find_facade_bean
  → class:SyouninUserFindFacadeBean
    → package:jp.co.daiwahouse.dsmart.service.contract.keiyakuList
    → calls:product:syounin_user_find_product
    → orchestrates:permission_retrieval

facade:anken_find_facade_bean
  → class:AnkenFindFacadeBean
    → package:jp.co.daiwahouse.dsmart.service.contract.keiyakuList
    → calls:product:anken_find_product
    → orchestrates:project_retrieval

facade:keiyaku_list_find_facade_bean
  → class:KeiyakuListFindFacadeBean
    → package:jp.co.daiwahouse.dsmart.service.contract.keiyakuList
    → calls:product:keiyaku_list_find_product
    → orchestrates:contract_list_retrieval
```

### 5.2 Delete Facade
```
facade:keiyaku_delete_facade_bean
  → class:KeiyakuDeleteFacadeBean
    → package:jp.co.daiwahouse.dsmart.service.contract.keiyakuList
    → method:update(vo)
    → calls:product:keiyaku_delete_product
    → orchestrates:deletion_logic
    → manages:transaction
```

---

## 6. Product (Business Logic) Layer Relationships

### 6.1 Find Products
```
product:syounin_user_find_product
  → class:SyouninUserFindProduct
    → package:jp.co.daiwahouse.dsmart.service.contract.product.keiyakuList
    → implements:permission_business_logic
    → calls:dao:syounin_user_find_dao
    → validates:user_authority

product:anken_find_product
  → class:AnkenFindProduct
    → package:jp.co.daiwahouse.dsmart.service.contract.product.keiyakuList
    → implements:project_business_logic
    → calls:dao:anken_find_dao
    → validates:project_status

product:keiyaku_list_find_product
  → class:KeiyakuListFindProduct
    → package:jp.co.daiwahouse.dsmart.service.contract.product.keiyakuList
    → implements:contract_list_business_logic
    → calls:dao:keiyaku_ichiran_find_dao
    → validates:contract_data
```

### 6.2 Delete Product
```
product:keiyaku_delete_product
  → class:KeiyakuDeleteProduct
    → package:jp.co.daiwahouse.dsmart.service.contract.product.keiyakuList
    → method:updateMain(vo)
    → implements:deletion_business_logic
    → validates:deletion_constraints
      → checks:not_primary_contract
      → checks:no_linked_data
      → checks:contract_status
    → calls:dao:keiyaku_dao
    → calls:dao:kouji_dao
    → calls:dao:keiyaku_shijisyo_kankei_dao
    → calls:dao:chintaisyaku_keiyaku_kankei_dao
    → calls:util:zentai_koutei
    → calls:dao:kojin_tasya_keiyaku_kbn_dao
```

---

## 7. DAO Layer Relationships

### 7.1 Find DAOs (Read Operations)
```
dao:syounin_user_find_dao
  → class:SyouninUserFindDAO
    → package:jp.co.daiwahouse.dsmart.domain.contract.find
    → queries:table:t_syounin_user
    → method:findByUserId
    → returns:permission_data

dao:anken_find_dao
  → class:AnkenFindDAO
    → package:jp.co.daiwahouse.dsmart.domain.contract.find
    → queries:table:t_anken
    → queries:table:t_anken_syousai
    → queries:table:t_anken_mansion
    → queries:table:t_anken_kokyaku_kankei
    → method:findByAnkenNo
    → returns:project_data

dao:keiyaku_ichiran_find_dao
  → class:KeiyakuIchiranFindDAO
    → package:jp.co.daiwahouse.dsmart.domain.contract.find
    → queries:table:t_keiyaku
    → queries:table:t_c_keiyaku
    → queries:table:t_keiyaku_koutei
    → queries:table:t_keiyaku_kokyaku_kankei
    → queries:table:t_c_keiyaku_kokyaku_kankei
    → queries:table:t_keiyaku_kaikeitani_kankei
    → queries:table:t_kokyaku_kojin
    → queries:table:t_kokyaku_soshiki
    → queries:table:t_kigyou
    → queries:many:master_tables
    → method:findByAnkenNo
    → returns:contract_list
```

### 7.2 Persistence DAOs (Write Operations)
```
dao:keiyaku_dao
  → class:KeiyakuDAO
    → package:jp.co.daiwahouse.dsmart.domain.contract.persistence
    → updates:table:t_keiyaku
    → method:doUpdate
    → performs:logical_deletion
    → sets:delete_flag

dao:kouji_dao
  → class:KoujiDAO
    → package:jp.co.daiwahouse.dsmart.domain.contract.persistence
    → updates:table:t_kouji
    → method:doUpdate
    → updates:construction_data

dao:keiyaku_shijisyo_kankei_dao
  → class:KeiyakuShijisyoKankeiDAO
    → package:jp.co.daiwahouse.dsmart.domain.contract.persistence
    → deletes:table:t_keiyaku_shijisyo_kankei
    → method:doDelete
    → removes:directive_linkage

dao:chintaisyaku_keiyaku_kankei_dao
  → class:ChintaisyakuKeiyakuKankeiDAO
    → package:jp.co.daiwahouse.dsmart.domain.contract.persistence
    → deletes:table:t_chintaisyaku_keiyaku_kankei
    → method:doDelete
    → removes:rental_linkage

dao:kojin_tasya_keiyaku_kbn_dao
  → class:KojinTasyaKeiyakuKbnDAO
    → package:jp.co.daiwahouse.dsmart.domain.contract.persistence
    → updates:table:t_kokyaku_kojin
    → method:doUpdate
    → updates:customer_classification
```

### 7.3 Utility DAOs
```
util:zentai_koutei
  → class:ZentaiKoutei
    → package:jp.co.daiwahouse.dsmart.service.contract.product.util
    → deletes:table:t_keiyaku_koutei
    → deletes:table:t_jyutyu_koutei
    → deletes:table:t_ukagaisyo_teikeigai_koutei
    → method:deleteProcessData
    → removes:process_data
```

---

## 8. Database Table Relationships

### 8.1 Core Tables
```
table:t_anken (Project Main)
  → has_many:t_keiyaku
  → has_one:t_anken_syousai
  → has_one:t_anken_mansion
  → has_many:t_anken_kokyaku_kankei
  → read_by:anken_find_dao
  → key:anken_no

table:t_keiyaku (Contract Main)
  → belongs_to:t_anken
  → has_one:t_c_keiyaku
  → has_many:t_kouji
  → has_many:t_keiyaku_shijisyo_kankei
  → has_many:t_chintaisyaku_keiyaku_kankei
  → has_one:t_keiyaku_koutei
  → has_many:t_keiyaku_kokyaku_kankei
  → has_many:t_keiyaku_kaikeitani_kankei
  → read_by:keiyaku_ichiran_find_dao
  → updated_by:keiyaku_dao
  → key:keiyaku_key
  → foreign_key:anken_no
```

### 8.2 Related Tables
```
table:t_kouji (Construction)
  → belongs_to:t_keiyaku
  → updated_by:kouji_dao
  → key:kouji_key
  → foreign_key:keiyaku_key

table:t_keiyaku_shijisyo_kankei (Contract-Directive Link)
  → belongs_to:t_keiyaku
  → deleted_by:keiyaku_shijisyo_kankei_dao
  → foreign_key:keiyaku_key
  → foreign_key:shijisyo_no

table:t_chintaisyaku_keiyaku_kankei (Rental Contract Link)
  → belongs_to:t_keiyaku
  → deleted_by:chintaisyaku_keiyaku_kankei_dao
  → foreign_key:keiyaku_key
  → foreign_key:rental_no

table:t_keiyaku_koutei (Contract Process)
  → belongs_to:t_keiyaku
  → deleted_by:zentai_koutei
  → foreign_key:keiyaku_key

table:t_jyutyu_koutei (Order Process)
  → belongs_to:t_keiyaku
  → deleted_by:zentai_koutei

table:t_ukagaisyo_teikeigai_koutei (Non-standard Process)
  → belongs_to:t_keiyaku
  → deleted_by:zentai_koutei
```

### 8.3 Customer Tables
```
table:t_kokyaku_kojin (Individual Customer)
  → has_many:t_keiyaku_kokyaku_kankei
  → updated_by:kojin_tasya_keiyaku_kbn_dao
  → read_by:keiyaku_ichiran_find_dao
  → key:kokyaku_kojin_key

table:t_kokyaku_soshiki (Organization Customer)
  → has_many:t_keiyaku_kokyaku_kankei
  → read_by:keiyaku_ichiran_find_dao
  → key:kokyaku_soshiki_key

table:t_keiyaku_kokyaku_kankei (Contract-Customer Link)
  → belongs_to:t_keiyaku
  → belongs_to:t_kokyaku_kojin OR t_kokyaku_soshiki
  → read_by:keiyaku_ichiran_find_dao
  → foreign_key:keiyaku_key
```

### 8.4 Master Tables
```
table:m_user (User Master)
  → read_by:keiyaku_ichiran_find_dao
  → provides:user_information

table:m_jigyousyo (Business Office Master)
  → read_by:keiyaku_ichiran_find_dao
  → provides:office_information

table:m_keiyaku_kbn (Contract Classification Master)
  → read_by:keiyaku_ichiran_find_dao
  → provides:contract_types

table:v_m_keiyaku_status (Contract Status View)
  → read_by:keiyaku_ichiran_find_dao
  → provides:status_labels
```

---

## 9. Form and Data Flow

### 9.1 Form Relationships
```
form:anken_cardForm
  → used_by:keiyaku_list_init_action
  → contains:ankenNo
  → contains:jyutyuNo
  → contains:shijisyoNo
  → contains:zentaiKbn
  → maps_to:vo:anken_vo

form:keiyaku_cardForm
  → used_by:keiyaku_list_dispatch_action
  → used_by:keiyaku_delete_action
  → contains:ankenNo
  → contains:actionType
  → contains:keiyakuKey
  → contains:spExecuteKbn
  → contains:hanbaiBukkenNo
  → contains:keiyakuCardSyubetsuCd
  → contains:koujiKey
  → contains:tabCd
  → contains:jyutyuNo
  → contains:select[]
  → maps_to:vo:keiyaku_vo

form:keiyakuListKensakuForm
  → used_by:search_operations
  → contains:keiyakuNo
  → contains:koujiName
  → contains:keiyakuStatusCd
  → contains:keiyakusyaName
  → contains:eigyoTantousyaUserId
  → contains:keiyakuTeiketsuDateFrom
  → contains:keiyakuTeiketsuDateTo
  → validated_by:validation.xml
```

### 9.2 Session Data Flow
```
session:CONTRACT_KEIYAKU_VO
  → set_by:keiyaku_list_init_action
  → read_by:keiyaku_list_jsp
  → updated_by:keiyaku_delete_action

session:CONTRACT_AUTHORITY_VO
  → set_by:keiyaku_list_init_action
  → read_by:keiyaku_list_jsp
  → controls:button_visibility

session:CONTRACT_OPTION_KEIYAKU_ICHIRAN_VO_LIST
  → set_by:keiyaku_list_init_action
  → read_by:keiyaku_list_jsp
  → rendered_by:struts_logic_iterate

session:CONTRACT_ANKEN_VO
  → set_by:keiyaku_list_init_action
  → read_by:keiyaku_list_jsp
  → provides:project_context

session:CONTRACT_SHINKI_KEIYAKU_SAKUSEI_KAHI_FLG
  → set_by:keiyaku_list_init_action
  → controls:button:new_contract:enabled

session:CONTRACT_TSUIKA_KEIYAKU_SAKUSEI_KAHI_FLG
  → set_by:keiyaku_list_init_action
  → controls:button:add_contract:enabled

session:CONTRACT_KEIYAKU_DATA_HENKO_KAHI_FLG
  → set_by:keiyaku_list_init_action
  → controls:button:update_contract:enabled
```

---

## 10. Validation Flow

### 10.1 Client-Side Validation
```
javascript:keiyakuList_submit(type)
  → validates:radio_selection
    → checks:contract_selected
    → required_for:update|delete|add operations
  → validates:confirmation_dialog
    → shows:comDeleteConfirm
    → required_for:delete operation
  → sets:hidden_fields
    → actionType
    → keiyakuKey
  → submits:form

validation:radio_selection
  → element:input[name=radioButton]
  → checked_by:javascript
  → error:alert_message
```

### 10.2 Server-Side Validation
```
validation:form_validation
  → defined_in:validation.xml
  → validates:keiyakuNo (integer)
  → validates:koujiName (full-width)
  → validates:keiyakusyaName (full-width)
  → validates:keiyakuTeiketsuDateFrom/To (date, range)
  → validates:keiyakuKeijyouDateFrom/To (date, range)
  → executed_by:struts_validator

validation:business_rules
  → executed_by:product_layer
  → validates:contract_exists
  → validates:user_authority
  → validates:contract_status
  → validates:deletion_constraints
    → checks:not_primary_contract
    → checks:no_linked_data
    → checks:contract_deletable_status
```

---

## 11. Error Handling Flow

### 11.1 Error Display
```
error:display_flow
  → errors:stored_in:action_errors
  → errors:set_in:request_scope
  → errors:displayed_by:/common/error.txt
  → errors:rendered_in:keiyaku_list_jsp
```

### 11.2 Error Recovery
```
error:validation_error
  → returns_to:current_screen
  → displays:field_errors
  → preserves:form_data

error:business_error
  → logs:error_details
  → returns_to:keiyaku_list_init
  → displays:error_message
  → preserves:session_data

error:system_error
  → forwards_to:/contract/error.jsp
  → logs:stack_trace
  → displays:generic_message
```

---

## 12. Configuration Relationships

### 12.1 Struts Configuration
```
config:struts-config.xml
  → location:/WEB-INF/config/contract/keiyakuList/
  → defines:action_mappings
    → action:/keiyakuListInit.do
      → maps_to:KeiyakuListInitAction
      → forward:success → keiyaku_list_jsp
    → action:/keiyakuListDispatch.do
      → maps_to:KeiyakuListDispatchAction
      → forward:new_contract → keiyaku_list_assign
      → forward:delete_contract → keiyaku_delete
    → action:/keiyakuDelete.do
      → maps_to:KeiyakuDeleteAction
      → forward:success → keiyaku_list_init
  → defines:form_beans
    → form:anken_cardForm
    → form:keiyaku_cardForm
    → form:keiyakuListKensakuForm

config:validation.xml
  → location:/WEB-INF/config/contract/keiyakuList/
  → defines:validation_rules
    → form:keiyakuListKensakuForm
      → field:keiyakuNo → integer
      → field:koujiName → zenkaku
      → field:keiyakuTeiketsuDateFrom → date
```

---

## 13. Complete End-to-End Flow Examples

### 13.1 Contract Deletion Complete Flow
```
user:clicks_delete_button
  → javascript:keiyakuList_submit(4)
    → validates:radio_selection
      → if_invalid:shows_alert → STOP
    → shows:confirmation_dialog
      → if_cancelled:STOP
    → sets:actionType=delete_contract
    → sets:keiyakuKey=<selected>
    → submits:form:keiyaku_cardForm
      → url:/keiyakuListDispatch.do
        → action:KeiyakuListDispatchAction
          → reads:actionType=delete_contract
          → forwards_to:/keiyakuDelete.do
            → action:KeiyakuDeleteAction
              → validates:form_data
              → calls:delegate:KeiyakuDeleteDelegate
                → calls:facade:KeiyakuDeleteFacadeBean
                  → calls:product:KeiyakuDeleteProduct
                    → validates:business_rules
                      → checks:not_primary_contract
                      → checks:no_linked_data
                    → starts:transaction
                    → calls:dao:KeiyakuDAO
                      → updates:t_keiyaku (set delete_flag)
                    → calls:dao:KoujiDAO
                      → updates:t_kouji
                    → calls:dao:KeiyakuShijisyoKankeiDAO
                      → deletes:t_keiyaku_shijisyo_kankei
                    → calls:dao:ChintaisyakuKeiyakuKankeiDAO
                      → deletes:t_chintaisyaku_keiyaku_kankei
                    → calls:util:ZentaiKoutei
                      → deletes:t_keiyaku_koutei
                      → deletes:t_jyutyu_koutei
                      → deletes:t_ukagaisyo_teikeigai_koutei
                    → calls:dao:KojinTasyaKeiyakuKbnDAO
                      → updates:t_kokyaku_kojin
                    → commits:transaction
                  → returns:success
                → returns:success
              → updates:session:CONTRACT_KEIYAKU_VO
              → forwards_to:/keiyakuListInit.do
                → action:KeiyakuListInitAction
                  → reloads:contract_list
                  → forwards_to:keiyaku_list_jsp
                    → displays:updated_list
```

### 13.2 Screen Load Complete Flow
```
user:accesses_url:/keiyakuListInit.do?ankenNo=123
  → action:KeiyakuListInitAction
    → receives:param:ankenNo=123
    → calls:delegate:SyouninUserFindDelegate
      → calls:facade:SyouninUserFindFacadeBean
        → calls:product:SyouninUserFindProduct
          → calls:dao:SyouninUserFindDAO
            → queries:t_syounin_user
          → returns:authority_vo
        → returns:authority_vo
      → sets:session:CONTRACT_AUTHORITY_VO
    → calls:delegate:AnkenFindDelegate
      → calls:facade:AnkenFindFacadeBean
        → calls:product:AnkenFindProduct
          → calls:dao:AnkenFindDAO
            → queries:t_anken
            → queries:t_anken_syousai
            → queries:t_anken_mansion
            → queries:t_anken_kokyaku_kankei
          → returns:anken_vo
        → returns:anken_vo
      → sets:session:CONTRACT_ANKEN_VO
    → calls:delegate:KeiyakuListFindDelegate
      → calls:facade:KeiyakuListFindFacadeBean
        → calls:product:KeiyakuListFindProduct
          → calls:dao:KeiyakuIchiranFindDAO
            → queries:t_keiyaku
            → queries:t_c_keiyaku
            → queries:t_keiyaku_koutei
            → queries:t_keiyaku_kokyaku_kankei
            → queries:t_kokyaku_kojin
            → queries:t_kokyaku_soshiki
            → queries:master_tables
          → returns:contract_list
        → returns:contract_list
      → sets:session:CONTRACT_OPTION_KEIYAKU_ICHIRAN_VO_LIST
    → calculates:business_flags
      → sets:session:CONTRACT_SHINKI_KEIYAKU_SAKUSEI_KAHI_FLG
      → sets:session:CONTRACT_TSUIKA_KEIYAKU_SAKUSEI_KAHI_FLG
      → sets:session:CONTRACT_KEIYAKU_DATA_HENKO_KAHI_FLG
    → forwards_to:keiyaku_list_jsp
      → includes:body.jsp
        → renders:contract_list_table
          → iterates:CONTRACT_OPTION_KEIYAKU_ICHIRAN_VO_LIST
          → displays:each_contract_row
        → renders:action_buttons
          → enables_based_on:business_flags
        → includes:/common/error.txt
      → returns:html_to_browser
```

---

## 14. Cross-Cutting Concerns

### 14.1 Security/Authorization
```
security:user_authentication
  → checked_by:struts_filter
  → validated_by:session
  → required_for:all_actions

security:user_authorization
  → loaded_by:syounin_user_find_product
  → stored_in:CONTRACT_AUTHORITY_VO
  → controls:button_visibility
  → controls:action_execution
```

### 14.2 Transaction Management
```
transaction:boundary
  → started_by:facade_layer
  → managed_by:spring_transaction_manager
  → committed_on:success
  → rolled_back_on:error
```

### 14.3 Logging
```
logging:application_logs
  → logged_by:all_layers
  → logs:user_actions
  → logs:business_operations
  → logs:errors_and_exceptions
```

---

## 15. Testing Impact Analysis

### 15.1 Field Addition Impact
```
question:"Add Field1 to Screen B, which table is affected?"
  → trace:
    screen:contract_list_main
      → form:keiyaku_cardForm
        → add_field:field1
          → validate_in:validation.xml
          → process_in:KeiyakuListInitAction
            → store_in:session OR form
            → pass_to:delegate_layer
              → pass_to:facade_layer
                → pass_to:product_layer
                  → pass_to:dao_layer
                    → determine:target_table
                      → if related_to:contract
                        → updates:t_keiyaku
                      → if related_to:project
                        → updates:t_anken
      → check_affected_screens:
        → screen:contract_details (uses same table)
        → screen:contract_modification (uses same table)
```

### 15.2 Screen Modification Testing Checklist
```
question:"Which parts should be tested when modifying Screen F?"
  → test:
    layer:ui
      → test:field_rendering
      → test:button_functionality
      → test:validation_messages
      → test:javascript_functions
    layer:action
      → test:form_binding
      → test:action_routing
      → test:session_management
      → test:error_handling
    layer:business_logic
      → test:business_rules
      → test:data_validation
      → test:permission_checks
    layer:dao
      → test:sql_queries
      → test:data_retrieval
      → test:data_persistence
    layer:integration
      → test:end_to_end_flow
      → test:transaction_rollback
      → test:concurrent_access
```

### 15.3 Performance Troubleshooting
```
question:"Screen D is slow. Which process is heavy?"
  → analyze:
    layer:ui
      → check:javascript_execution
      → check:rendering_time
      → measure:DOM_complexity
    layer:action
      → check:action_processing_time
      → check:session_operations
    layer:dao
      → check:sql_execution_time
        → identify:slow_queries
        → check:missing_indexes
        → check:table_scans
      → check:result_set_size
      → check:n+1_query_problems
    layer:business_logic
      → check:loop_iterations
      → check:recursive_calls
      → check:collection_operations
```

---

## 16. Input Validation Traceability

### 16.1 Input Validation for Screen A
```
question:"Where is input validation for Screen A implemented?"
  → trace:
    validation:client_side
      → location:keiyakuList.jsp
      → javascript:keiyakuList_submit()
        → validates:radio_selection
        → validates:required_fields
    validation:server_side
      → location:validation.xml
        → defines:field_rules
          → keiyakuNo:integer
          → koujiName:zenkaku
          → dates:format_and_range
      → location:KeiyakuListInitAction
        → validates:form_data
        → calls:struts_validator
      → location:Product_Layer
        → validates:business_rules
          → validates:user_authority
          → validates:contract_status
          → validates:data_constraints
  → if_changed:
    affects:
      → client_validation:keiyakuList.jsp
      → server_validation:validation.xml
      → action_validation:KeiyakuListInitAction
      → business_validation:*Product classes
      → error_display:/common/error.txt
```

### 16.2 Function Update Traceability
```
question:"Which function updates STATUS in T_KEIYAKU?"
  → trace:
    table:t_keiyaku
      → column:status
      → updated_by:dao:KeiyakuDAO
        → called_by:product:KeiyakuDeleteProduct (deletion)
        → called_by:product:KeiyakuUpdateProduct (modification)
        → called_by:product:KeiyakuCreateProduct (creation)
          → called_by:facade:layer
            → called_by:delegate:layer
              → called_by:action:layer
                → triggered_by:ui:button_click
```

### 16.3 Save Process Internal Flow
```
question:"Explain internal flow of save process for Screen E"
  → flow:
    user:clicks_save_button
      → javascript:validation
        → submits:form_data
          → action:receives_request
            → validates:form_structure
            → calls:delegate
              → calls:facade
                → starts:transaction
                → calls:product
                  → validates:business_rules
                  → calls:multiple_daos_in_sequence
                    → dao1:save_main_data
                    → dao2:save_related_data
                    → dao3:update_relationships
                    → dao4:log_audit_trail
                  → returns:success_or_error
                → commits_or_rollback:transaction
              → returns:result
            → sets:success_message_or_errors
            → forwards:to_result_screen
```

---

## Summary

This relationship flow document provides:
1. **Complete traceability** from UI to database
2. **Bidirectional navigation** from any component to related components
3. **Impact analysis support** for understanding change effects
4. **Query support** for the 6 types of questions mentioned
5. **Testing guidance** for comprehensive test coverage

Use this as a reference to build your knowledge graph with entities and relationships that support automated RAG queries.
