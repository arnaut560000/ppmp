# Government PPMP: PlantUML design package

Start with **01_level1.puml** for the system-wide data-flow diagram. Read each Level 2 file separately for detail; do not combine them into one oversized page.

| File | Purpose |
|---|---|
| 00_context.puml | Whole-system boundary and external users |
| 01_level1.puml | Six processes, eight stores, 64 named flows |
| 02_level2_p1.puml | Authentication, department membership and scoped roles |
| 03_level2_p2.puml | Item catalog, annual prices, reporting-group ownership and workflow setup |
| 04_level2_p3.puml | Department drafts, quarterly calculations, files, revisions and submission |
| 05_level2_p4.puml | Review assignment, decisions, comments, approval and returns |
| 06_level2_p5.puml | Version selection, consolidation, source lineage and exports |
| 07_level2_p6.puml | Transactional events, audit records and in-app notifications |
| 08_database_relationships.puml | Companion ERD: 36 tables and 55 foreign keys |
| FLOW_REGISTER.md | Every named flow, its endpoints and payload fields |
| DATA_DICTIONARY.md | Workbook mapping, key constraints and business rules |

Open a `.puml` file in a PlantUML editor, or paste its entire contents from `@startuml` to `@enduml`. No third-party includes or remote macros are required. Each file is standalone. The notation uses PlantUML rectangle/usecase/database shapes to express a logical DFD. The ERD uses PlantUML information-engineering relationships.

The workbook was successfully read on the second conversation turn. The quarterly fields and reporting-group structure reflect that inspection; the approval route and operational controls are proposed. See DATA_DICTIONARY.md for exact evidence and assumptions.

Structural checks passed for node references and DFD boundary balancing. A local PlantUML rendering check was not completed: no renderer JAR was available, and downloading it failed because the shell could not resolve github.com. The diagrams have not been visually validated.

Sources for syntax:
- https://plantuml.com/deployment-diagram
- https://plantuml.com/ie-diagram
