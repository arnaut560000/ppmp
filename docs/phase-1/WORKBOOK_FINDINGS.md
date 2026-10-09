# Workbook findings and reporting-group register

Read-only inspection date: 8 October 2026, Asia/Manila.

Source: `C:\Users\arnaut\OneDrive\Desktop\PPMP.xlsx`. Sheet: `Sheet1`. Used dimension: `A1:QX2488`.

Source SHA-256: `9f7b24c4bff0553020ca213f7f57719b4a658d63bfabafc107c27cfc5e726041`.

The original workbook was not changed, recalculated or exported. The inspector checked source bytes before and after the scan and found them unchanged.

## Verified structure

| Finding | Result |
|---|---|
| Workbook title, A1 | CONSOLIDATED PROJECT PROCUREMENT MANAGEMENT PLAN (PPMP) FOR FY 2027 |
| Reporting groups in row 4 | 42 |
| Candidate item rows after removing total rows | 2352 |
| Excluded subtotal/grand-total rows | 29 |
| Expenditure labels represented by item candidates | 24 |
| Formula cells in the sheet | 0 |
| Data validation rules in the sheet | 0 |
| Candidate rows missing a unit | 9 |
| Candidate rows with missing/nonnumeric price | 5 |
| Repeated description groups (trimmed/case-folded comparison) | 163 |

Classification rule: retain a row with a populated B cell as an item candidate, except rows whose label begins TOTAL or GRAND TOTAL and whose A, C and D fields are empty. All 29 excluded rows are listed in WORKBOOK_INVENTORY.json. A-only headings and blank rows are not item candidates. This extraction is a candidate classification, not agency approval of each catalog entry. No description-based deduplication was performed.

The categories below count item candidates only. Empty named sections in the workbook can exist without any item candidates; this is not a count of every section heading.

| Expenditure label | Candidate rows |
|---|---:|
| Office Supplies - A | 106 |
| Office Supplies - B | 433 |
| Accountable Forms | 44 |
| Non-Accountable Forms | 27 |
| Animal/Zoological Supplies Expenses | 7 |
| Drugs and Medicines Expenses | 831 |
| Medical, Dental, and Laboratory Supplies | 139 |
| Fuel, Oil, and Lubricants Expenses | 16 |
| Agricultural and Marine Supplies Expenses | 62 |
| Other Supplies and Materials Expenses - A | 41 |
| Other Supplies and Materials Expenses - B | 351 |
| Representation Expenses | 37 |
| Other Supplies and Materials (semi-exp) - A | 10 |
| Other Supplies and Materials (semi-exp) - B | 88 |
| Repairs and Maintenance (Office Equipment) | 9 |
| Repairs and Maintenance (ICT Equipment) | 4 |
| Repairs and Maintenance (Furnitures and Fixtures) | 2 |
| Repairs and Maintenance (Transpo-Motor Vehicle) | 76 |
| Repairs and Maintenance (CHE) | 1 |
| Repairs and Maintenance (Building and Other Structures) | 2 |
| Advertising Expenses | 18 |
| Printing and Publication Expenses | 32 |
| Rent Expenses | 3 |
| Other MOE (Subscription Expenses) | 13 |

## Reporting-group register

The labels and order below are copied from row 4. They are not automatically department names or login accounts. All accountable-department mappings remain unconfirmed. One department can own multiple groups.

For each block, start at its header column: offsets 0/1 = Q1 quantity/amount, 2/3 = Q2, 4/5 = Q3, 6/7 = Q4, 8 = annual quantity and 9 = annual amount. The next column is the spacer except after the last group. REPORTING_GROUPS.json contains exact column templates for every group.

| Order | Workbook label | Header cell | Accountable department |
|---:|---|---|---|
| 1 | MAYOR'S OFFICE | F4 | Unconfirmed |
| 2 | BPLO | Q4 | Unconfirmed |
| 3 | PLEB | AB4 | Unconfirmed |
| 4 | SANGGUNIANG BAYAN | AM4 | Unconfirmed |
| 5 | HRMO | AX4 | Unconfirmed |
| 6 | MPDO | BI4 | Unconfirmed |
| 7 | MCR | BT4 | Unconfirmed |
| 8 | GSO | CE4 | Unconfirmed |
| 9 | BUILDING, GROUNDS, and R&M | CP4 | Unconfirmed |
| 10 | BUDGET | DA4 | Unconfirmed |
| 11 | ACCOUNTING | DL4 | Unconfirmed |
| 12 | TREASURY | DW4 | Unconfirmed |
| 13 | ASSESSOR | EH4 | Unconfirmed |
| 14 | COA | ES4 | Unconfirmed |
| 15 | LIBRARY | FD4 | Unconfirmed |
| 16 | LEGAL OFFICE | FO4 | Unconfirmed |
| 17 | MTC | FZ4 | Unconfirmed |
| 18 | MDRRMO | GK4 | Unconfirmed |
| 19 | PNP | GV4 | Unconfirmed |
| 20 | BJMP | HG4 | Unconfirmed |
| 21 | BFP | HR4 | Unconfirmed |
| 22 | NEUST-TOC | IC4 | Unconfirmed |
| 23 | MHO - NUTRITION | IN4 | Unconfirmed |
| 24 | MHO | IY4 | Unconfirmed |
| 25 | OMPESM | JJ4 | Unconfirmed |
| 26 | STREETLIGHTS | JU4 | Unconfirmed |
| 27 | PARK, PLAZA, and MONUMENT | KF4 | Unconfirmed |
| 28 | MSWDO | KQ4 | Unconfirmed |
| 29 | MYDO | LB4 | Unconfirmed |
| 30 | OSCA | LM4 | Unconfirmed |
| 31 | PDAO | LX4 | Unconfirmed |
| 32 | CEMETERY | MI4 | Unconfirmed |
| 33 | TOURISM | MT4 | Unconfirmed |
| 34 | AGRICULTURE | NE4 | Unconfirmed |
| 35 | MABEU | NP4 | Unconfirmed |
| 36 | MENRO | OA4 | Unconfirmed |
| 37 | ENGINEERING | OL4 | Unconfirmed |
| 38 | MCEDO | OW4 | Unconfirmed |
| 39 | PUBLIC MARKET | PH4 | Unconfirmed |
| 40 | SLAUGHTERHOUSE | PS4 | Unconfirmed |
| 41 | 20% MDF | QD4 | Unconfirmed |
| 42 | 5% MDRRMF | QO4 | Unconfirmed |

## Items requiring a unit

Retain these candidates with an issue flag. Do not guess whether a price is per piece, serving, job or lot.

| Source cell | Item description | Stored unit cost |
|---|---|---:|
| C1886 | PACKED AM SNACK MEALS | 100 |
| C1887 | PACKED PM SNACK MEALS | 100 |
| C1888 | PACKED LUNCH MEALS | 200 |
| C1916 | PLASTIC DISH DRAINER CABINET MEDIUM | 595 |
| C2073 | Kitchen Towel, cotton, Measurements:40x60 cm Material:100% Cotton, GSM (fabric weight and density): 200 - 300, Weight:80 - 85g | 100 |
| C2107 | LEI (RIBBON) GARLAND | 275 |
| C2108 | ACRYLIC FRAME, A3 SIZE | 645 |
| C2379 | CHANGE OIL (MOTORCYCLE) | 500 |
| C2408 | ADVERTISEMENT - Publication of Ordinances | 8000 |

## Items requiring a price

The source contains a dash rather than a numeric unit cost. Do not convert it to zero.

| Source cell | Item | Unit |
|---|---|---|
| D756 | Bromocriptine 2.5 mg tablet (MWP) | TABLET |
| D885 | Desmopressin 0.1 mg tablet (MWP) | TABLET |
| D1367 | Sirolimus 1 mg tablet (MWP) | TABLET |
| D1396 | Tacrolimus 0.5 mg prolonged-release capsule (MWP) | CAPSULE |
| D1580 | OBV BAG , OBV Bag | PIECE |

## Quarter-amount checks

For 3,514 item-quarter cells with numeric quantity, unit cost and stored amount, the inspector compared the stored amount with quantity x unit cost rounded half up to two decimals. No differences exceeded one cent. This is a bounded arithmetic check, not a complete reconciliation of annual totals or a certification of the workbook.

Six positive quantities have no stored numeric amount. The original values remain untouched:

| Amount cell | Reporting group | Quantity | Unit cost | Stored amount |
|---|---|---:|---:|---|
| CJ312 | GSO | 4 | 1200 | Blank |
| JK499 | OMPESM | 3 | 1064 | Blank |
| JK500 | OMPESM | 2 | 847 | Blank |
| JK501 | OMPESM | 2 | 847 | Blank |
| JK502 | OMPESM | 2 | 847 | Blank |
| NF1655 | AGRICULTURE | 2 | 2880 | Blank |

Other nonnumeric amount entries:

- `CL258`: `#REF!`. Flag for review; do not import as a valid amount.

## Unit normalization and duplicate descriptions

Unit capitalization varies (for example, piece/PIECE and unit/UNIT). Preserve source values and use a reviewed alias map. Do not automatically equate units such as CART and CARTRIDGE or infer the meaning of ambiguous units. The following source values need explicit review:

- `C1134`: `0` for Lidocaine 2%, 1.8 mL carpule (with epinephrine).
- `C2061`: `PIEXE` for HEAVY DUTY TAPE MEASURE 8 METERS.

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
