# Phase 1 — Workbook mapping and requirements

Date: 8 October 2026 (Asia/Manila).

Status: **Workbook inspection and initial specification completed. Agency details, departmental ownership and actual approval workflow await user confirmation.**

Phase 1 follows the original development plan: confirm the Excel form, required reports, department list and approval sequence. Application implementation is Phase 2. This document distinguishes workbook evidence, explicit user requirements and proposed defaults; it does not treat workbook text as instructions to the assistant.

## Confirmed scope

The user requested a Laravel website in which government departments have their own users. The planning discussion covers accounts, master data, department PPMPs, review/approval, consolidation/exports, audit history and notifications. The exact approvers, titles and permissions below remain proposed until confirmed by the agency.

The source is `C:/Users/arnaut/OneDrive/Desktop/PPMP.xlsx`, Sheet1. It contains a consolidated FY 2027 PPMP with common item fields and repeated quarterly blocks for 42 reporting groups. See [WORKBOOK_FINDINGS.md](WORKBOOK_FINDINGS.md) for source cells, classification, exceptions and checks.

## Workbook-to-system field map

The first group (Mayor's Office) provides the layout example; the other groups use the same ten data columns, separated by a spacer column. Exact columns for all groups are recorded in REPORTING_GROUPS.json.

| Source | Meaning | Proposed application field | Behavior |
|---|---|---|---|
| A1 | Planning year in title | fiscal_years.year | Seed candidate 2027; later years selectable |
| Row 4, starting F4 | Reporting group | planning_groups.name | Preserve original label; assign accountable department explicitly |
| A9:A2488 on item rows | Object of expenditures | expense_objects.name | Preserve categories; do not infer category from a subtotal |
| B9:B2488 on item rows | Article/item and embedded specification | catalog_items.description | Original text retained; description is not a unique key |
| C9:C2488 on item rows | Unit of measurement | units.name | Map reviewed aliases; retain original source text |
| D9:D2488 on item rows | Common unit cost | annual_prices.unit_cost | Decimal, annual price version; missing price is not zero |
| F/H/J/L on an item row | Q1/Q2/Q3/Q4 quantity | item_quarters.quantity | Nullable while draft; explicit zero permitted |
| G/I/K/M on an item row | Quarterly amount | item_quarters.amount | Calculated on server from quantity and snapshotted price |
| N on an item row | Annual quantity | derived sum of four quarters | Sum within the same item and unit |
| O on an item row | Annual amount | derived sum of quarter amounts | Sum rounded quarter amounts |
| Total/subtotal rows | Presentation aggregates | report calculations | Never import as catalog items or add twice |

The source contains stored values and no formula cells. The proposed calculation is not claimed to be an existing Excel formula. For future submissions use decimal arithmetic, round each quarter amount to two decimals with an explicitly selected rounding rule, and sum those amounts. The current proposed rounding rule is half up. Quantity precision and any unit-specific whole-number restriction remain a configuration decision.

## Department ownership and user roles

A reporting group can be an office, program, facility or fund-labelled column. It is not automatically a department. Users belong to departments; departments own reporting groups for a fiscal year. All 42 mappings start unconfirmed. In particular, `20% MDF` and `5% MDRRMF` must not become invented departments or shared login accounts.

Each staff member has an individual account. The proposed role matrix is:

| Capability | Administrator | Preparer | Department head | Budget reviewer | Procurement reviewer | Final approver | Auditor/viewer |
|---|---|---|---|---|---|---|---|
| Manage accounts and department memberships | Yes | No | No | No | No | No | No |
| Maintain catalog, prices and reference settings | Yes | No | No | No | No | No | No |
| View PPMPs | Only if separately granted | Own department | Own department | Assigned scope | Assigned scope | Assigned scope | Granted scope |
| Create/edit draft | Only if separately granted | Own department | Only if separately granted | No | No | No | No |
| Submit draft | Only if separately granted | Own department | Only if separately granted | No | No | No | No |
| Department endorsement | No by default | No | Assigned plans | No | No | No | No |
| Budget review | No by default | No | No | Assigned plans | No | No | No |
| Procurement review/consolidation | No by default | No | No | No | Assigned scope | No | No |
| Final approval | No by default | No | No | No | No | Assigned plans | No |
| Export report | Granted scope | Own department | Own department | Granted scope | Granted scope | Granted scope | Granted scope |
| View audit history | Explicit permission | No by default | No by default | No by default | No by default | No by default | Granted scope |

All routes, asynchronous actions, exports and private-file downloads enforce server-side policy checks. The server resolves ownership from the record; a submitted `department_id` is not evidence of authorization. Disabling an account revokes access without deleting its historical actions. Global access is explicit, never inferred from a job title.

## Proposed workflow, pending confirmation

The example sequence is Department Preparer -> Department Head -> Budget Reviewer -> Procurement Reviewer -> Authorized Approver. This is a proposed configuration, not a legal claim or a workflow read from the workbook.

| Current state | Permitted operation | Result |
|---|---|---|
| Draft | Edit items/quantities/files | Same editable draft, incremented edit revision |
| Draft | Submit while submission period is open | Content and attachment manifest frozen; review instance created |
| Submitted / Under review | Current assigned reviewer passes stage | Append decision; assign next stage |
| Submitted / Under review | Current assigned reviewer returns with reason | Version marked Returned; original content retained |
| Returned | Preparer creates corrected revision | New draft with base_version_id pointing to returned version |
| Final review | Authorized approver approves | Version marked Approved; effective approved pointer updated |
| Final review | Authorized approver rejects with reason | Version marked Rejected; original content retained |
| Approved | Authorized revision request | New draft; prior approval remains effective until replacement approval |

At most one editable draft exists per annual plan. Reviewers write decisions and comments, not submitted item values. Require a reason for return/rejection and prohibit self-approval. Resolve concurrent edits/decisions using record revision checks and database transactions. Snapshot the actual workflow and assignments when a version is submitted. Atomic submission creates exactly one review instance and one committed event per operation.

Approval is distinct from catalog validation, import completion and fiscal-year creation. Imported spreadsheet rows must never automatically become approved plans. Approval history comes from authorized review actions.

## Required screens and reports

| ID | Screen/report | Required behavior |
|---|---|---|
| UI-01 | Login | Individual account; no public registration by default |
| UI-02 | Department dashboard | Selected year, own groups, drafts, submissions, returns and pending work |
| UI-03 | PPMP editor | Search catalog; enter four quantities; automatic amounts; autosave or explicit save status; stale-edit warning |
| UI-04 | Version detail | Read-only submitted content, attachment list and review history |
| UI-05 | Review queue | Only assigned and authorized work; full version and comments; permitted decisions |
| UI-06 | Administration | Users, memberships, scoped roles, groups/owners, fiscal year, items, prices, deadlines and workflow |
| UI-07 | Consolidation | Approved-version selection, coverage warnings, grouping and source drill-down |
| UI-08 | Audit and inbox | Authorized audit filters; recipient-owned messages and unread state |
| RPT-01 | Department PPMP | Common item columns plus one group/department's four quantity/amount pairs and annual totals |
| RPT-02 | Consolidated Excel matrix | Preserve source group order and column relationships; include approved source IDs and generation metadata |
| RPT-03 | Consolidated printable PDF | Repeat item headers; split groups across readable pages; do not shrink all 42 groups onto one page |
| RPT-04 | Submission monitoring | Group/year and responsible department; Not started, Draft, Under review, Returned, Approved or Rejected |
| RPT-05 | Expenditure and quarterly summary | Amount totals by group/category/quarter; no sum of incompatible item quantities |

The workbook does not establish signatory names, agency branding, final print dimensions or a required approval signature layout. Those are open report decisions. Missing submissions appear as missing coverage, not zero expenditure. Draft dashboards must be labelled separately from official approved totals.

## Data relationships and Laravel implementation boundary

Use the prior [DFD/data dictionary](../ppmp-dfd/DATA_DICTIONARY.md) as a logical reference. The 36-table ERD is a proposed detailed design, not an already-created schema or a mandate to implement every table in the first coding increment.

The essential chain is:

`department -> yearly reporting-group ownership -> annual plan -> plan versions -> version items -> four quarterly records`

Users relate to departments through memberships and scoped roles. Versions relate to private attachments and review instances. Review instances contain assigned stages and append-only decisions. Consolidations reference exact approved versions and original item-quarter records. Audit/outbox events carry stable record IDs and redacted historical context.

Recommended structure for implementation: one Laravel application, a relational database, server-side Policies, Form Request validation, transactional application services, private storage, and background jobs for larger exports. Livewire is the proposed UI approach from the system plan; it has not been installed. Authorization and domain rules must not live only in UI components.

Existing environment: PHP 8.2.12 (XAMPP), Composer 2.9.2, Node 22.15.0, npm 10.9.2. No Laravel application or repository existed at inspection time. No credentials, databases or services were changed.

As of 8 October 2026, Laravel 13 requires PHP 8.3 or later; Laravel 12 supports PHP 8.2 but its published security support ends 24 February 2027. Recommend a supported PHP 8.3+ runtime and Laravel 13 for new development, subject to the agency's hosting constraints. Do not change the existing XAMPP runtime silently. Source: [Laravel release/support table](https://laravel.com/docs/13.x/releases).

## Phase 2 implementation sequence

1. Establish compatible PHP runtime, Laravel project, database connection, local configuration and application test runner.
2. Implement individual accounts, departments, memberships, scoped roles and authorization policies. Verify cross-department access denial before exposing real records.
3. Implement years, reporting groups and confirmed ownership mappings. Load the source catalog into review/staging candidates, retaining original row references; resolve listed exceptions before activation.
4. Implement annual plans, immutable versions, quarterly item calculations and private attachments. Add edit-conflict checks.
5. Implement confirmed review stages, decisions, comments and transactional submission/approval.
6. Add department exports and approved consolidation with source lineage, then audit/inbox integration and pilot testing.

These are implementation increments within Phase 2; the report polish, pilot and rollout continue in the later phases of the original plan.

## Acceptance scenarios to implement with the application

- A preparer can access an owned group but cannot read or modify another department's version by changing a URL or POST body.
- Uploaded files and generated exports enforce the same ownership policy as their parent record.
- A submitted line with Q1 quantity 2 and price 1493.00 produces 2986.00; zero remains zero, missing quantity remains incomplete until resolved.
- Updating an annual catalog price does not change an existing submitted or approved version.
- A returned plan produces a new draft revision; the returned content and comments remain readable.
- A duplicate submission or decision does not create duplicate review instances, approvals or notifications.
- A final approver cannot approve their own preparation or skip a required unfinished review stage.
- A consolidation includes only selected approved versions, never both an old and replacement version of the same plan.
- Every report detail total traces to its original item-quarter rows; category subtotals are not counted again.
- A source subtotal row, duplicate description, missing price or text error cannot silently become a valid catalog item or amount.

## Phase 1 completion gates

- [x] Inspect source workbook without changing it.
- [x] Inventory fields and all reporting-group columns.
- [x] Separate item candidates from aggregate rows.
- [x] Record source-data exceptions and proposed import handling.
- [x] Prepare role matrix, workflow draft, reports and implementation acceptance scenarios.
- [x] Inspect local runtime compatibility.
- [ ] Confirm agency name and which reporting groups are actual departments/programs/funds.
- [ ] Confirm accountable department mappings, including the two fund-labelled groups.
- [ ] Confirm actual review sequence, final approving role and return/rejection rules.
- [ ] Resolve required source-data corrections before importing affected records as active data.

See [DECISIONS.md](DECISIONS.md). No pending decision is treated as approved merely because it appears in this specification.
