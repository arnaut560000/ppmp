# Government PPMP System

A Laravel application for department PPMP preparation. The first local test release is in `app/`.

**Current stage:** First testable implementation: login, two isolated demo departments, a searchable workbook-derived catalog, quarterly calculations and saved drafts. Approvals, attachments, official exports and account administration remain future work.

Open **http://127.0.0.1:8000** while the local server is running. See [Testing the application](TESTING.md) for accounts, restart instructions and test scenarios.

Start with [Phase 1 specification](docs/phase-1/README.md).

- [Workbook findings and reporting-group register](docs/phase-1/WORKBOOK_FINDINGS.md)
- [Open decisions](docs/phase-1/DECISIONS.md)
- [Existing DFD and relationship design](docs/ppmp-dfd/README.md)

The source workbook is read only. Extracted rows are candidates for review, not approved catalog records, approved PPMPs or real user accounts.
