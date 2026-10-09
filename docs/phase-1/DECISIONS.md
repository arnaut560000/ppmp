# Decisions awaiting confirmation

These are business/setup decisions, not requests to approve document-writing operations. Phase 1 analysis can proceed while these remain open; dependent application behavior must not be represented as confirmed.

| ID | Decision | Current state / proposed default | Blocks |
|---|---|---|---|
| D-01 | Official agency/LGU name | Unspecified; do not infer from workbook acronyms | Branding and final report headers |
| D-02 | Actual departments versus reporting groups | 42 workbook group labels preserved; all owner mappings unconfirmed | Creating real scoped accounts and activating group ownership |
| D-03 | Owners of 20% MDF and 5% MDRRMF | Unspecified | Activating those groups |
| D-04 | Review stages, order and approvers | Proposed head -> budget -> procurement -> final approver | Live workflow configuration and assignment |
| D-05 | Price authority | Proposed centralized annual prices, no ordinary preparer override | Any later override feature; basic centralized-price implementation can proceed |
| D-06 | Blank quantities and dash amounts | Preserve missing, zero and dash separately during source import | Historical-data activation where meanings are unresolved |
| D-07 | Data correction ownership | Nine blank units, five missing prices, six missing computed amounts and text error recorded in findings | Activating affected source records |
| D-08 | Runtime and hosting constraints | Recommend PHP 8.3+ with Laravel 13; existing XAMPP is PHP 8.2.12 | Installing a compatible development/deployment runtime |
| D-09 | Signatories and PDF page layout | Not established by workbook; readable split-group PDF proposed | Final report sign-off |

The user has been asked for D-01, D-03 and D-04. All other entries remain documented assumptions or subsequent review items; no answer has been invented.
