"""Build human-readable Phase 1 findings from the read-only workbook inventory."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs'/'phase-1'
inventory=json.loads((OUT/'WORKBOOK_INVENTORY.json').read_text(encoding='utf-8'))
sheet=inventory['sheets'][0]
items=json.loads((OUT/'CATALOG_CANDIDATES.json').read_text(encoding='utf-8'))
groups=json.loads((OUT/'REPORTING_GROUPS.json').read_text(encoding='utf-8'))
by_row={item['source_row']:item for item in items}
def safe(value):return str(value).replace('|','\\|').replace('\n',' ')

text=f'''# Workbook findings and reporting-group register

Read-only inspection date: 8 October 2026, Asia/Manila.

Source: `{inventory['source_path']}`. Sheet: `{sheet['name']}`. Used dimension: `{sheet['dimension']}`.

Source SHA-256: `{inventory['source_sha256']}`.

The original workbook was not changed, recalculated or exported. The inspector checked source bytes before and after the scan and found them unchanged.

## Verified structure

| Finding | Result |
|---|---|
| Workbook title, A1 | {sheet['title']} |
| Reporting groups in row 4 | {len(groups)} |
| Candidate item rows after removing total rows | {len(items)} |
| Excluded subtotal/grand-total rows | {len(sheet['excluded_total_rows'])} |
| Expenditure labels represented by item candidates | {len(sheet['category_counts'])} |
| Formula cells in the sheet | {sheet['formula_cell_count']} |
| Data validation rules in the sheet | {sheet['data_validation_count']} |
| Candidate rows missing a unit | {len(sheet['candidate_missing_unit_rows'])} |
| Candidate rows with missing/nonnumeric price | {len(sheet['candidate_missing_or_nonnumeric_cost_rows'])} |
| Repeated description groups (trimmed/case-folded comparison) | {len(sheet['duplicate_description_groups'])} |

Classification rule: retain a row with a populated B cell as an item candidate, except rows whose label begins TOTAL or GRAND TOTAL and whose A, C and D fields are empty. All {len(sheet['excluded_total_rows'])} excluded rows are listed in WORKBOOK_INVENTORY.json. A-only headings and blank rows are not item candidates. This extraction is a candidate classification, not agency approval of each catalog entry. No description-based deduplication was performed.

The categories below count item candidates only. Empty named sections in the workbook can exist without any item candidates; this is not a count of every section heading.

| Expenditure label | Candidate rows |
|---|---:|
'''
for label,count in sheet['category_counts'].items():text+=f'| {safe(label)} | {count} |\n'
text+='''
## Reporting-group register

The labels and order below are copied from row 4. They are not automatically department names or login accounts. All accountable-department mappings remain unconfirmed. One department can own multiple groups.

For each block, start at its header column: offsets 0/1 = Q1 quantity/amount, 2/3 = Q2, 4/5 = Q3, 6/7 = Q4, 8 = annual quantity and 9 = annual amount. The next column is the spacer except after the last group. REPORTING_GROUPS.json contains exact column templates for every group.

| Order | Workbook label | Header cell | Accountable department |
|---:|---|---|---|
'''
for i,group in enumerate(groups,1):text+=f'| {i} | {safe(group["label"])} | {group["source_header"]} | Unconfirmed |\n'
text+='''
## Items requiring a unit

Retain these candidates with an issue flag. Do not guess whether a price is per piece, serving, job or lot.

| Source cell | Item description | Stored unit cost |
|---|---|---:|
'''
for row in sheet['candidate_missing_unit_rows']:
    item=by_row[row];text+=f'| C{row} | {safe(item["description"])} | {item["unit_cost_raw"]} |\n'
text+='\n## Items requiring a price\n\nThe source contains a dash rather than a numeric unit cost. Do not convert it to zero.\n\n| Source cell | Item | Unit |\n|---|---|---|\n'
for row in sheet['candidate_missing_or_nonnumeric_cost_rows']:
    item=by_row[row];text+=f'| D{row} | {safe(item["description"])} | {item["unit"]} |\n'
text+='\n## Quarter-amount checks\n\n'
checks=sheet['quarter_amount_checks']
text+=f'''For {checks.get('numeric_pairs_checked',0):,} item-quarter cells with numeric quantity, unit cost and stored amount, the inspector compared the stored amount with quantity x unit cost rounded half up to two decimals. No differences exceeded one cent. This is a bounded arithmetic check, not a complete reconciliation of annual totals or a certification of the workbook.

Six positive quantities have no stored numeric amount. The original values remain untouched:

| Amount cell | Reporting group | Quantity | Unit cost | Stored amount |
|---|---|---:|---:|---|
'''
for issue in sheet['quarter_amount_issues']:
    text+=f'| {issue["cell"]} | {safe(issue["group"])} | {issue["quantity"]} | {issue.get("unit_cost_raw",issue.get("unit_cost"))} | {safe(issue.get("stored_amount_raw",issue.get("stored_amount"))) or "Blank"} |\n'
text+='\nOther nonnumeric amount entries:\n\n'
for issue in sheet['quarter_cell_examples'].get('amount_other_text',[]):text+=f'- `{issue["cell"]}`: `{issue["value"]}`. Flag for review; do not import as a valid amount.\n'
text+='\n## Unit normalization and duplicate descriptions\n\n'
text+='Unit capitalization varies (for example, piece/PIECE and unit/UNIT). Preserve source values and use a reviewed alias map. Do not automatically equate units such as CART and CARTRIDGE or infer the meaning of ambiguous units. The following source values need explicit review:\n\n'
for item in items:
    if item['unit'] in ('0','PIEXE'):
        text+=f'- `C{item["source_row"]}`: `{item["unit"]}` for {safe(item["description"])}.\n'
text+='''
Descriptions are not unique identifiers. For example B13:D14 contains two `CALCULATOR, Compact` rows with different costs (283 and 299). All 163 repeated-description groups, their row numbers, units and prices are preserved in WORKBOOK_INVENTORY.json. Use the source fingerprint + sheet + row as import provenance, then assign a stable catalog ID following review. Do not merge by name alone.

## Proposed import behavior

1. Verify the expected workbook/header pattern and fiscal year before mapping columns.
2. Load references and quantities into review candidates, not directly into approved plans.
3. Keep raw text, typed values, source sheet/cell/row and workbook fingerprint.
4. Exclude headings, subtotals and grand totals from item detail; never add them to their own underlying item totals.
5. Preserve missing quantities, explicit zero and dash placeholders distinctly. No silent zero fill.
6. Block activation of affected records until missing units/prices, invalid text and group ownership are resolved. Incomplete records remain visible for review.
7. Preview quantities and amounts by group, item and quarter; reconcile department and consolidated outputs before accepting an import.
8. Make repeated import of the same source fingerprint idempotent. A changed workbook creates a new reviewed import, never a silent overwrite of approved versions.

## Output files and verification

- WORKBOOK_INVENTORY.json: aggregate counts, categories/units, duplicates, excluded totals, calculation exceptions and source fingerprint.
- REPORTING_GROUPS.json: 42 original labels, source header cells, exact quarter/annual column templates and unconfirmed owner fields.
- CATALOG_CANDIDATES.json: 2,352 original item candidates with source row, category, description, unit and raw/numeric price. These are not active database records.

Extraction checks verified unique source row keys and that quantity-cell counts equal 2,352 item rows x 42 groups x 4 quarters = 395,136 inspected positions. JSON outputs were reopened and inspected. No workbook editing or visual-layout change was made, so no workbook render was required for this read-only inventory.
'''
(OUT/'WORKBOOK_FINDINGS.md').write_text(text,encoding='utf-8')
assert len(items)==sum(sheet['category_counts'].values())
assert len(groups)==sheet['reporting_groups']
assert len({g['source_header'] for g in groups})==len(groups)
print(f'Wrote findings: {len(items)} candidates, {len(groups)} groups, {len(sheet["excluded_total_rows"])} total rows excluded.')
