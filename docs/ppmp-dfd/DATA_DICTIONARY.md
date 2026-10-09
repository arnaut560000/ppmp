# PPMP data dictionary and relationship rules

This is a proposed Laravel design for one government agency/LGU. It is not a statement of legally required approval procedures. All departmental users have personal accounts. Central permissions are explicitly scoped.

## Workbook evidence and design assumptions

Read-only inspection of `C:/Users/arnaut/OneDrive/Desktop/PPMP.xlsx`, Sheet1, found:

- A1: consolidated PPMP for FY 2027.
- A5:D5: object of expenditures, article/item, unit of measurement, unit cost.
- F4:O7: first office block with four quarter quantity/amount pairs and annual quantity/amount totals. Further groups repeat this structure across row 4.
- QD4 and QO4: `20% MDF` and `5% MDRRMF`. These are fund-labelled reporting groups; their actual departmental owners are not established by the workbook. Do not create department accounts automatically from every group header.
- B13:D14: two `CALCULATOR, Compact` rows with different unit costs. Description alone is not an item identifier and is not safe for merging records.
- The sampled rows contain blank quantities and text dash amounts. Treat these as an import-mapping issue; do not silently assume every blank/dash is a confirmed zero.

The workbook structure establishes the quarterly reporting fields. Login, permissions, approvals, attachments, budget allocations, procurement methods, fund assignments, audit history and notification records are proposed system features from the earlier plan, not verified workbook columns. The workflow is configurable; a sequential Department Head -> Budget -> Procurement -> Authorized Approver route is an example only.

## How to read the diagrams

- `00_context.puml`: external roles and the system boundary. This document calls the single-process context view Level 0; some schools call the decomposed view Level 0 instead.
- `01_level1.puml`: six processes, eight logical stores, and all 64 boundary flows.
- `02_level2_p1.puml` through `07_level2_p6.puml`: decompositions of processes 1.0 through 6.0; parent boundary IDs and packets are preserved.
- `08_database_relationships.puml`: ERD with primary keys, foreign keys and cardinalities. An ERD describes database relationships; it is not itself a DFD.
- `FLOW_REGISTER.md`: every DFD arrow and the exact proposed fields in its payload.

Rectangles represent people/roles outside the application, ovals transform data, and cylinders are logical stores. The cylinder is a convenient PlantUML symbol; it is not strict Gane-Sarson store notation. `U` is a grouped alias for all seven roles when they use shared authentication, scoped reports, or their own inbox. It does not grant identical permissions. Arrow direction means data transfer, not execution order. Arrows labelled requests are also data: IDs, filters, quantities and decisions.

Laravel is the implementation boundary. Database writes, private file storage and background jobs are internal. There is no external email gateway in this scope; notifications are in-app. Supplier bidding, purchase orders, inventory and payment execution are outside this PPMP planning model. Imports use validated draft/reference writes; they do not have an independently persistent staging module in this version.

## Logical-store ownership

| Store | Writers | Readers |
|---|---|---|
| D1 identity/access | 1.0 | 1.0-6.0, only the fields required by each process |
| D2 reference/planning | 2.0 | 2.0-5.0 |
| D3 plans and versions | 3.0 content; 4.0 review state/effective version only | 3.0-5.0 |
| D4 private attachments | 3.0 | 3.0 and 4.0 |
| D5 review records | 4.0 | 3.0, 4.0 and 5.0 |
| D6 report/export snapshots | 5.0 | 5.0 |
| D7 audit log | 6.0 append only | 6.0 with audit permission |
| D8 event outbox/inbox | 6.0 logically; domain transaction invokes its recorder | 6.0 |

## Tables and uniqueness

Every table uses `id` as its primary key. Foreign keys are listed exhaustively in the next section. Fields named in the ERD are logical fields; decimal precision, indexes and framework session/token details must be finalized during implementation.

| Store | Table | Additional uniqueness / constraints |
|---|---|---|
| D1 | `departments` | code |
| D1 | `users` | login_identifier |
| D1 | `memberships` | (user_id, department_id) |
| D1 | `roles` | name |
| D1 | `permissions` | name |
| D1 | `role_permissions` | (role_id, permission_id) |
| D1 | `role_assignments` | (user_id, role_id, normalized scope key); enforce NULL/global uniqueness explicitly |
| D1 | `sessions` | Primary key; additional indexes based on queries |
| D2 | `fiscal_years` | year |
| D2 | `planning_groups` | code |
| D2 | `group_owners` | (planning_group_id, fiscal_year_id) |
| D2 | `expense_objects` | Primary key; additional indexes based on queries |
| D2 | `units` | Primary key; additional indexes based on queries |
| D2 | `catalog_items` | code; descriptions are NOT unique |
| D2 | `annual_prices` | (item_id, fiscal_year_id, price_version) |
| D2 | `funds` | Primary key; additional indexes based on queries |
| D2 | `procurement_methods` | Primary key; additional indexes based on queries |
| D2 | `allocations` | (group_owner_id, fund_id) |
| D2 | `workflow_templates` | (name, template_version) |
| D2 | `planning_cycles` | Primary key; additional indexes based on queries |
| D3 | `plans` | group_owner_id; one annual plan per group/year in this proposed scope |
| D3 | `plan_versions` | (plan_id, revision_no) |
| D3 | `version_items` | (version_id, line_no) |
| D3 | `item_quarters` | (version_item_id, quarter_number), quarter_number in 1..4 |
| D4 | `attachments` | Primary key; additional indexes based on queries |
| D5 | `review_instances` | version_id |
| D5 | `review_stages` | (review_instance_id, stage_order) |
| D5 | `review_actions` | Primary key; additional indexes based on queries |
| D6 | `report_runs` | Primary key; additional indexes based on queries |
| D6 | `report_sources` | (report_run_id, version_id) |
| D6 | `report_lines` | Primary key; additional indexes based on queries |
| D6 | `report_line_sources` | (report_line_id, report_source_id, item_quarter_id) |
| D6 | `exports` | Primary key; additional indexes based on queries |
| D7 | `audit_logs` | event_uuid |
| D8 | `outbox_events` | event_uuid |
| D8 | `notifications` | (outbox_event_id, recipient_user_id) |

## Foreign-key relationships

Each required FK points to exactly one parent. Optional FKs point to zero or one. A parent may have zero or many child rows unless the uniqueness table limits it.

| Child table | Foreign key | Parent table | Nullable |
|---|---|---|---|
| `memberships` | `user_id` | `users` | No |
| `memberships` | `department_id` | `departments` | No |
| `role_permissions` | `role_id` | `roles` | No |
| `role_permissions` | `permission_id` | `permissions` | No |
| `role_assignments` | `user_id` | `users` | No |
| `role_assignments` | `role_id` | `roles` | No |
| `role_assignments` | `department_id` | `departments` | Yes |
| `sessions` | `user_id` | `users` | No |
| `group_owners` | `planning_group_id` | `planning_groups` | No |
| `group_owners` | `fiscal_year_id` | `fiscal_years` | No |
| `group_owners` | `owner_department_id` | `departments` | No |
| `catalog_items` | `unit_id` | `units` | No |
| `catalog_items` | `expense_object_id` | `expense_objects` | No |
| `annual_prices` | `item_id` | `catalog_items` | No |
| `annual_prices` | `fiscal_year_id` | `fiscal_years` | No |
| `allocations` | `group_owner_id` | `group_owners` | No |
| `allocations` | `fund_id` | `funds` | No |
| `planning_cycles` | `fiscal_year_id` | `fiscal_years` | No |
| `planning_cycles` | `workflow_template_id` | `workflow_templates` | No |
| `plans` | `group_owner_id` | `group_owners` | No |
| `plans` | `effective_approved_version_id` | `plan_versions` | Yes |
| `plan_versions` | `plan_id` | `plans` | No |
| `plan_versions` | `base_version_id` | `plan_versions` | Yes |
| `plan_versions` | `created_by` | `users` | No |
| `plan_versions` | `submitted_by` | `users` | Yes |
| `plan_versions` | `planning_cycle_id` | `planning_cycles` | No |
| `version_items` | `version_id` | `plan_versions` | No |
| `version_items` | `item_id` | `catalog_items` | No |
| `version_items` | `annual_price_id` | `annual_prices` | No |
| `version_items` | `fund_id` | `funds` | Yes |
| `version_items` | `procurement_method_id` | `procurement_methods` | Yes |
| `item_quarters` | `version_item_id` | `version_items` | No |
| `attachments` | `version_id` | `plan_versions` | No |
| `attachments` | `uploaded_by` | `users` | No |
| `review_instances` | `version_id` | `plan_versions` | No |
| `review_instances` | `workflow_template_id` | `workflow_templates` | No |
| `review_stages` | `review_instance_id` | `review_instances` | No |
| `review_stages` | `assigned_user_id` | `users` | No |
| `review_actions` | `review_stage_id` | `review_stages` | No |
| `review_actions` | `actor_id` | `users` | No |
| `review_actions` | `version_item_id` | `version_items` | Yes |
| `report_runs` | `fiscal_year_id` | `fiscal_years` | No |
| `report_runs` | `created_by` | `users` | No |
| `report_sources` | `report_run_id` | `report_runs` | No |
| `report_sources` | `version_id` | `plan_versions` | No |
| `report_lines` | `report_run_id` | `report_runs` | No |
| `report_line_sources` | `report_line_id` | `report_lines` | No |
| `report_line_sources` | `report_source_id` | `report_sources` | No |
| `report_line_sources` | `item_quarter_id` | `item_quarters` | No |
| `exports` | `report_run_id` | `report_runs` | No |
| `exports` | `requested_by` | `users` | No |
| `audit_logs` | `actor_id` | `users` | Yes |
| `audit_logs` | `department_id` | `departments` | Yes |
| `notifications` | `recipient_user_id` | `users` | No |
| `notifications` | `outbox_event_id` | `outbox_events` | No |

## Rules spanning multiple tables

1. **Department isolation:** the server resolves the plan's group owner and fiscal year, then checks current user membership and scoped permission on every read/write/export/download. Never trust a client-provided department ID. A global role requires an explicit assignment. System-administrator permissions do not inherently include approval.
2. **Planning groups versus departments:** one department has many users and may own multiple reporting groups in a year. One group has exactly one accountable department per year in this proposed model. Freeze ownership once a plan is submitted; ownership changes require an explicit audited reassignment process. A group is not automatically a funding source: assign `fund_id` independently.
3. **Annual plan identity:** one `plans` record per `group_owners` record (hence group/year). It has many versions. At most one editable draft per plan. `effective_approved_version_id`, when present, must reference an approved version belonging to that same plan and be unique. The circular reference is resolved by creating the plan first with a NULL effective version, then versions.
4. **Version provenance:** `base_version_id` must belong to the same plan and point to an earlier immutable version. Returned/rejected/submitted/approved versions keep their original content. A correction creates a new draft version; approval of a later version updates the effective pointer while retaining the older approval history.
5. **Price policy:** draft lines select an annual catalog price; ordinary preparers cannot overwrite the shared price. Authorized administrators create a new price version. Existing submitted versions retain their description/unit/expense/price snapshots. The selected price must belong to the same item and fiscal year as the plan. Permit a departmental price override only if explicitly added to the future policy and audit model.
6. **Line identity:** retain stable catalog IDs and version line IDs. Do not merge solely by item name. `line_no` is unique within a version; the same item can appear in separate lines when funding or other distinctions require it.
7. **Quarter quantities:** exactly four `item_quarters` records per submitted item, quarters 1-4. Zero is a valid planned quantity; an omitted quantity remains missing until explicitly completed. Proposed formulas: quarter amount = round(quantity * snapshotted unit cost, 2); annual quantity = sum of four quarter quantities; annual amount = sum of four rounded quarter amounts. Sum amounts across items; do not sum quantities across incompatible units/items. Calculate with decimal arithmetic on the server. These are proposed calculation rules, not formulas verified in the workbook.
8. **Planning-cycle consistency:** a version's planning cycle, catalog price and plan group owner must all resolve to the same fiscal year. Submission requires an open period and valid mandatory fields. Validate any configured budget restriction using the matching group/fund/year allocation; a warning versus hard block is a policy setting.
9. **Atomic submission:** within one database transaction validate draft ownership and `lock_version`, freeze content and attachment manifest, set submitted state, create exactly one review instance with snapshotted stage assignments, and enqueue a unique committed event. A repeated submit request must not create duplicate review instances. Process boundaries in the DFD do not imply separate database transactions.
10. **Reviews:** the illustrative route is configurable but this initial model assumes sequential stages. Snapshot the route/template version at submission. Recheck current reviewer authority on every action. Do not allow the preparer to approve their own submission. A review action's optional `version_item_id` must belong to the reviewed version. One terminal decision per stage must be enforced with a transaction/lock; additional comments may coexist. Returning ends the current review run; resubmission uses a new version and review instance. Reassignment is explicit and audited, never a silent rewrite of who previously decided.
11. **Reviewer edits:** reviewers write decisions/comments and version state, not quantities or prices. Approve only when all required predecessor stages have passed. A returned/rejected replacement does not silently erase the last effective approved version.
12. **Attachments:** store files privately and authorize retrieval through the version's plan. Submitted file bytes, checksums and metadata are immutable. A new version receives a new version-linked attachment record, optionally referencing the same immutable object. Do not delete an object while another version references it. Exporting a PPMP does not automatically embed all attachments.
13. **Consolidation source selection:** official consolidations include approved versions only, normally one effective approved version per plan. A historical run retains its exact selected version IDs and as-of timestamp. Draft dashboards are explicitly labelled and cannot be mistaken for official approved reports.
14. **Consolidation lineage:** a `report_line_sources` row must reference a quarter belonging to the version listed by its `report_source_id`; the report source and report line must belong to the same report run. For an official run, enforce one version per source plan and exactly one inclusion of each selected item-quarter in the detail aggregation. Group only compatible item/specification/unit/price/fund combinations; differing prices remain separate when exporting a matrix with one unit-cost column.
15. **Report calculations:** quarter/category/department/grand totals derive from the same source-detail amounts. Subtotals must not be re-added as line items. Record missing departments/groups as incomplete coverage; missing submissions do not equal confirmed zero demand. Dashboard status counts and approved totals use distinct labelled filters.
16. **Exports:** store the report selection, lineage and file checksum together. Recheck authorization on download; possession of a file ID is insufficient. Generated exports are private. A later approval creates a new report run, not an unexplained mutation of an old export.
17. **Audit/outbox consistency:** domain changes and their outbox records commit together. Audit/notification workers deduplicate on event UUID; retries must not duplicate entries/messages. Audit logs also accept security failure/read events, which are explicitly marked as such. Exclude credentials, session tokens and private file bytes from event payloads. Resource type/ID is a deliberate polymorphic logical reference, not a database FK; keep a safe resource snapshot for historical readability.
18. **History retention:** disable accounts/catalog entries instead of deleting records referenced by history. Use restrictive foreign-key deletion behavior for plans, versions, reviews, source lines and reports. Audit rows are append-only. System/login events can have a NULL actor; failed login identifiers must be redacted appropriately.

## Verification performed

The DFD generator checks declared node IDs, labelled edge endpoints, context/Level 1 boundary matching, Level 1/Level 2 boundary flow-ID matching, and absence of store-to-store arrows. The companion relationship generator verifies all FK endpoints and field names. These are structural checks, not a PlantUML rendering or an application behavior test.
