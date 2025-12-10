# Entity Types in Contract List Module

## Entity Reference Table

| Entity Type | Description | Source | Examples |
|---|---|---|---|
| **Module** | Top-level container representing the contract-list module and its features | `ctc-data-en/contract-list/overview-en.md` | `contract-list`, `housing`, `simple` |
| **Screen/Tabs** | User-facing screens and UI tabs for navigation and interaction | `ctc-data-en/contract-list/screen-flow-en.md` | Contract List Main (GCNT90001), Contract Type Selection, Contract Deletion, Contract Details |
| **Function** | Business operations/workflows that perform specific tasks | `ctc-data-en/contract-list/functions/*/function-overview-en.md` | List Initialization (keiyakuListInit), Contract Deletion (keiyakuDelete) |
| **Value Object** | Data transfer objects (VOs) used between layers | `ctc-data-en/contract-list/data-architecture-en.md` | KeiyakuVO, AnkenVO, AuthorityVO, KeiyakuIchiranVO |
| **Form** | Struts form beans for request/response handling | `ctc-data-en/contract-list/components/form-fields-en.md` | anken_cardForm, keiyaku_cardForm, keiyakuListKensakuForm |
| **Session** | Session attributes for maintaining state across requests | `ctc-data-en/contract-list/data-architecture-en.md` | CONTRACT_KEIYAKU_VO, CONTRACT_AUTHORITY_VO, CONTRACT_SHINKI_KEIYAKU_SAKUSEI_KAHI_FLG |
| **View/UI** | JSP view templates and UI components | `ctc-data-en/contract-list/components/description-ui-en.md` | keiyakuList.jsp, body.jsp, error.jsp |
| **Action** | Struts action controllers handling HTTP requests | `ctc-data-en/contract-list/functions/*/function-overview-en.md` | KeiyakuListInitAction, KeiyakuListDispatchAction, KeiyakuDeleteAction |
| **Delegate** | Business delegate layer bridging Actions and Facades | `ctc-data-en/contract-list/functions/*/function-overview-en.md` | KeiyakuListFindDelegate, KeiyakuDeleteDelegate, AnkenFindDelegate |
| **Facade** | Facade bean layer orchestrating business logic | `ctc-data-en/contract-list/functions/*/function-overview-en.md` | KeiyakuListFindFacadeBean, KeiyakuDeleteFacadeBean |
| **Product** | Product layer containing core business logic | `ctc-data-en/contract-list/functions/*/function-overview-en.md` | KeiyakuListFindProduct, KeiyakuDeleteProduct |
| **DAO** | Data Access Objects for database operations | `ctc-data-en/contract-list/data-architecture-en.md` | KeiyakuDAO, AnkenFindDAO, KeiyakuIchiranFindDAO |
| **Database** | Database tables used by the module | `ctc-data-en/contract-list/functions/*/sql-queries-en.md` | t_keiyaku, t_anken, t_keiyaku_kokyaku_kankei, m_user, m_jigyousyo |
<!-- | **Button** | UI buttons triggering actions on screens | `ctc-data-en/contract-list/screen-specification/event_handling_rules-en.md` | New Contract, Additional Contract, Modify Contract, Delete Contract, Multiple Orders | -->
| **Flag** | Boolean flags controlling feature visibility and permissions | `ctc-data-en/contract-list/data-architecture-en.md` | shinkiKeiyakuSakuseiKahiFlg, tsuikaKeiyakuSakuseiKahiFlg, keiyakuDataHenkoKahiFlg |
| **Action type** |  |  | |
| **Event Type** | | | | 