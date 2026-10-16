# HireHub ER and UML diagrams

The final deliverables are **two ER diagrams and one UML class diagram**. Each is a single connected diagram containing all 12 entities exactly once and all 16 mapped relationships. The PNG folder contains only these three images.

| Diagram | PNG image | Vector image | Editable definition |
| --- | --- | --- | --- |
| Crow’s Foot ER — full schema | [PNG](png/er-full.png) | [SVG](svg/er-full.svg) | [Mermaid](sources/er-full.mmd) |
| Chen ER — conceptual projection | [PNG](png/er-chen.png) | [SVG](svg/er-chen.svg) | [Layout and schema evidence](sources/er-chen.json) |
| UML class associations | [PNG](png/uml-class.png) | [SVG](svg/uml-class.svg) | [Mermaid](sources/uml-class.mmd) |

Open **[index.html](index.html)** for the offline viewer. Select one of the three diagrams, use Fit or zoom, and download SVG/PNG/source files. No server, CDN or application login is required. The full Crow’s Foot schema has 114 fields and needs zoom to inspect every field at ordinary screen sizes; SVG remains sharp when enlarged.

## Notation

The relational view uses **Crow’s Foot ER notation**. Entity rectangles contain all mapped fields, SQL types, keys and declared nullability. Crow’s-foot, circle and bar markers express cardinality. Dashed connectors are non-identifying because every child table has its own surrogate primary key. `PK` means primary key, `FK` foreign key, `UK` unique, `NN` not null and `NULL` nullable.

The conceptual view uses **Chen shapes with explicit (min,max) participation**. Rectangles are entities, diamonds are relationships, ovals are attributes and underlined labels are primary keys. Only selected non-FK attributes are shown; foreign keys are expressed as relationships. The full Crow’s Foot view preserves every mapped field.

Read Chen’s pair beside the entity it describes: `STUDENTS (0,N) — Submits — (1,1) APPLICATIONS` means a student can submit zero or many applications and each application belongs to exactly one student. These same-side participation pairs differ from the placement of Crow’s Foot endpoint markers. `N` means an unrestricted maximum. The pairs replace the single/double participation-line encoding in this view.

The UML view shows the 12 mapped classes, selected declared attributes and plain associations. Multiplicities are `1`, `0..1` and `0..*`. The view does not invent methods, inheritance or composition. Application routes are separate from the ORM entity classes.

Notation references: [Mermaid Crow’s Foot ER](https://mermaid.js.org/syntax/entityRelationshipDiagram.html), [Emory ER symbols](https://www.cs.emory.edu/~cheung/Courses/377/Syllabus/2-ER/ER-diagram.html), [Pittsburgh min/max participation](https://people.cs.pitt.edu/~chang/156/03ERmodel.html), and [OMG UML 2.5.1](https://www.omg.org/spec/UML/2.5.1).

## Implementation correspondence

[The SQLAlchemy models](../../backend/app/db/models.py) are the schema source of truth. [schema.json](schema.json) records all 12 mapped tables, 114 fields and 16 foreign keys, including types, keys, nullability, explicit indexes, defaults and deletion rules. The two nullable foreign keys are `internships.recruiter_id` and `interviews.internship_id`. Defaults do not imply NOT NULL.

Student and recruiter profiles have unique user foreign keys, allowing zero or one profile per account. StudentSkills, Application and SavedInternship have their own IDs; the models do not declare uniqueness on their student/skill or student/internship pairs. Documents belong to students; there is no document-to-application foreign key. No weak entities, identifying diamonds, derived or multivalued attributes are invented in the Chen projection.

## Build and verification

`build_diagrams.py` extracts the schema, saves editable definitions and builds the offline viewer. `format_final.py` creates the final three connected SVGs using explicit layout geometry. [layout.json](layout.json) records each node, relationship route and label. The earlier layout helpers remain source utilities; the final viewer uses the three connected layouts.

```bash
python output/diagrams/build_diagrams.py --gallery
python output/diagrams/verify_diagrams.py
```

Run verification with the backend dependencies installed. The verifier imports SQLAlchemy metadata without connecting to MySQL. It checks all fields, constraints, endpoint cardinalities, Chen participation, connectedness, exactly one card per entity, connector crossings and header clearance. [verification.json](verification.json) also records the final browser checks for text bounds, relationship-label overlaps, header collisions, viewer fit and SVG/PNG downloads.

PNG files are browser-rendered from the matching SVGs. Keep only `er-full.png`, `er-chen.png`, and `uml-class.png` in `png/`. These checks establish correspondence to declared models and rendered geometry; they do not establish the state of a live database or prove end-to-end application behavior.
