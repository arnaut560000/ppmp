from pathlib import Path

OUT=Path(__file__).resolve().parent
# Table: store, non-key business fields. Every table has a surrogate primary key.
tables={
 'departments':('D1','code, name, active'),
 'users':('D1','name, login_identifier, password_hash, active'),
 'memberships':('D1','active, effective_from, effective_to'),
 'roles':('D1','name'),
 'permissions':('D1','name'),
 'role_permissions':('D1',''),
 'role_assignments':('D1','scope_type: department or global'),
 'sessions':('D1','expires_at, last_activity_at'),
 'fiscal_years':('D2','year, state'),
 'planning_groups':('D2','code, name, kind: office or program or fund'),
 'group_owners':('D2',''),
 'expense_objects':('D2','code, name'),
 'units':('D2','code, name'),
 'catalog_items':('D2','code, description, specifications, active'),
 'annual_prices':('D2','price_version, unit_cost_decimal, effective_at, active'),
 'funds':('D2','code, name'),
 'procurement_methods':('D2','code, name, active'),
 'allocations':('D2','allocated_amount_decimal'),
 'workflow_templates':('D2','name, template_version, stage_rules_json, active'),
 'planning_cycles':('D2','opens_at, closes_at, active'),
 'plans':('D3','reference_number'),
 'plan_versions':('D3','revision_no, state, lock_version, submitted_at, approved_at, content_hash'),
 'version_items':('D3','line_no, description_snapshot, specifications_snapshot, unit_snapshot, expense_snapshot, unit_cost_decimal, remarks'),
 'item_quarters':('D3','quarter_number, quantity_decimal, amount_decimal'),
 'attachments':('D4','storage_key, filename, mime_type, byte_size, checksum, uploaded_at'),
 'review_instances':('D5','state, started_at, completed_at'),
 'review_stages':('D5','stage_order, stage_type, state, lock_version'),
 'review_actions':('D5','decision, comment, actor_scope_snapshot, acted_at'),
 'report_runs':('D6','report_type, filters_json, grouping_json, as_of_at, coverage_json, created_at'),
 'report_sources':('D6',''),
 'report_lines':('D6','grouping_key, quarter_number, quantity_decimal, amount_decimal'),
 'report_line_sources':('D6','quantity_contribution_decimal, amount_contribution_decimal'),
 'exports':('D6','format, state, storage_key, checksum, created_at'),
 'audit_logs':('D7','event_uuid, actor_snapshot, resource_type, resource_id, action, redacted_changes_json, outcome, occurred_at, correlation_id'),
 'outbox_events':('D8','event_uuid, event_type, redacted_payload_json, state, attempts, occurred_at'),
 'notifications':('D8','safe_payload_json, read_at, created_at'),
}
# (child, foreign-key name, parent, nullable). Arrows are labelled with actual FK names.
rels=[
 ('memberships','user_id','users',False),('memberships','department_id','departments',False),
 ('role_permissions','role_id','roles',False),('role_permissions','permission_id','permissions',False),
 ('role_assignments','user_id','users',False),('role_assignments','role_id','roles',False),('role_assignments','department_id','departments',True),
 ('sessions','user_id','users',False),
 ('group_owners','planning_group_id','planning_groups',False),('group_owners','fiscal_year_id','fiscal_years',False),('group_owners','owner_department_id','departments',False),
 ('catalog_items','unit_id','units',False),('catalog_items','expense_object_id','expense_objects',False),
 ('annual_prices','item_id','catalog_items',False),('annual_prices','fiscal_year_id','fiscal_years',False),
 ('allocations','group_owner_id','group_owners',False),('allocations','fund_id','funds',False),
 ('planning_cycles','fiscal_year_id','fiscal_years',False),('planning_cycles','workflow_template_id','workflow_templates',False),
 ('plans','group_owner_id','group_owners',False),('plans','effective_approved_version_id','plan_versions',True),
 ('plan_versions','plan_id','plans',False),('plan_versions','base_version_id','plan_versions',True),('plan_versions','created_by','users',False),('plan_versions','submitted_by','users',True),('plan_versions','planning_cycle_id','planning_cycles',False),
 ('version_items','version_id','plan_versions',False),('version_items','item_id','catalog_items',False),('version_items','annual_price_id','annual_prices',False),('version_items','fund_id','funds',True),('version_items','procurement_method_id','procurement_methods',True),
 ('item_quarters','version_item_id','version_items',False),
 ('attachments','version_id','plan_versions',False),('attachments','uploaded_by','users',False),
 ('review_instances','version_id','plan_versions',False),('review_instances','workflow_template_id','workflow_templates',False),
 ('review_stages','review_instance_id','review_instances',False),('review_stages','assigned_user_id','users',False),
 ('review_actions','review_stage_id','review_stages',False),('review_actions','actor_id','users',False),('review_actions','version_item_id','version_items',True),
 ('report_runs','fiscal_year_id','fiscal_years',False),('report_runs','created_by','users',False),
 ('report_sources','report_run_id','report_runs',False),('report_sources','version_id','plan_versions',False),
 ('report_lines','report_run_id','report_runs',False),
 ('report_line_sources','report_line_id','report_lines',False),('report_line_sources','report_source_id','report_sources',False),('report_line_sources','item_quarter_id','item_quarters',False),
 ('exports','report_run_id','report_runs',False),('exports','requested_by','users',False),
 ('audit_logs','actor_id','users',True),('audit_logs','department_id','departments',True),
 ('notifications','recipient_user_id','users',False),('notifications','outbox_event_id','outbox_events',False),
]
unique={
 'departments':'code', 'users':'login_identifier', 'memberships':'(user_id, department_id)',
 'roles':'name', 'permissions':'name', 'role_permissions':'(role_id, permission_id)',
 'role_assignments':'(user_id, role_id, normalized scope key); enforce NULL/global uniqueness explicitly',
 'planning_groups':'code', 'fiscal_years':'year', 'group_owners':'(planning_group_id, fiscal_year_id)',
 'catalog_items':'code; descriptions are NOT unique', 'annual_prices':'(item_id, fiscal_year_id, price_version)',
 'allocations':'(group_owner_id, fund_id)', 'workflow_templates':'(name, template_version)',
 'plans':'group_owner_id; one annual plan per group/year in this proposed scope',
 'plan_versions':'(plan_id, revision_no)', 'version_items':'(version_id, line_no)',
 'item_quarters':'(version_item_id, quarter_number), quarter_number in 1..4',
 'review_instances':'version_id', 'review_stages':'(review_instance_id, stage_order)',
 'report_sources':'(report_run_id, version_id)',
 'report_line_sources':'(report_line_id, report_source_id, item_quarter_id)',
 'audit_logs':'event_uuid', 'outbox_events':'event_uuid',
 'notifications':'(outbox_event_id, recipient_user_id)',
}
lines=['@startuml ppmp_database_relationships','hide circle','skinparam linetype ortho','skinparam shadowing false','skinparam entityBackgroundColor #F8FAFC','title PPMP - Proposed Database Relationships (companion ERD)']
for table,(store,fields) in tables.items():
    lines += [f'entity "{table}" as {table} {{','  * id : bigint <<PK>>',f'  -- {store} --']
    for child,fk,parent,nullable in rels:
        if child==table:lines.append(f'  {" " if nullable else "*"} {fk} : bigint <<FK>>')
    for field in fields.split(', '):
        if field:lines.append('  '+field)
    lines.append('}')
for child,fk,parent,nullable in rels:
    # Parent-to-child multiplicity. A few foreign keys also have uniqueness.
    one_child=(child,fk) in {('plans','group_owner_id'),('review_instances','version_id'),('plans','effective_approved_version_id')}
    left='|o' if nullable else '||'
    right='o|' if one_child else 'o{'
    lines.append(f'{parent} {left}--{right} {child} : {fk}')
lines += ['note as Rules','Required FK: exactly one parent; nullable FK: zero or one parent.','Children default to zero or many unless the FK is unique.','Additional composite uniqueness and cross-table rules: DATA_DICTIONARY.md','Historical rows use RESTRICT/deactivation, not cascading deletion.','end note','@enduml']
(OUT/'08_database_relationships.puml').write_text('\n'.join(lines)+'\n',encoding='utf-8')

doc='''# PPMP data dictionary and relationship rules

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
'''
for table,(store,_) in tables.items():doc+=f'| {store} | `{table}` | {unique.get(table,"Primary key; additional indexes based on queries")} |\n'
doc+='\n## Foreign-key relationships\n\nEach required FK points to exactly one parent. Optional FKs point to zero or one. A parent may have zero or many child rows unless the uniqueness table limits it.\n\n| Child table | Foreign key | Parent table | Nullable |\n|---|---|---|---|\n'
for child,fk,parent,nullable in rels:doc+=f'| `{child}` | `{fk}` | `{parent}` | {"Yes" if nullable else "No"} |\n'
doc+='''
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
'''
(OUT/'DATA_DICTIONARY.md').write_text(doc,encoding='utf-8')
for child,fk,parent,nullable in rels:
    assert child in tables and parent in tables
assert len({(c,f) for c,f,_,_ in rels})==len(rels)
print(f'Created ERD and dictionary: {len(tables)} tables, {len(rels)} foreign keys.')
