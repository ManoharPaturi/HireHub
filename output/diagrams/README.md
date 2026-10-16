# HireHub ER and UML diagrams

Open **[index.html](index.html)** in a browser. It is a standalone offline viewer with eight embedded SVG diagrams, diagram selection, zoom, SVG/PNG/source download buttons, and a print view. No server, CDN, or application login is required. ER and class views open one domain at a time: Identity & communication, Student data, and Recruitment. Use the Domain selector to switch areas or choose All domains. Fit shows the selected area; zoom in to inspect labels. SVG and PNG downloads preserve the selected area.

| Diagram | Vector image | PNG image | Editable definition |
| --- | --- | --- | --- |
| Crow’s Foot ER overview | [SVG](svg/er-overview.svg) | [PNG](png/er-overview.png) | [Mermaid](sources/er-overview.mmd) |
| Crow’s Foot full physical schema | [SVG](svg/er-full.svg) | [PNG](png/er-full.png) | [Mermaid](sources/er-full.mmd) |
| Chen ER (entities, relationships, selected attributes) | [SVG](svg/er-chen.svg) | [PNG](png/er-chen.png) | [Layout/evidence](sources/er-chen.json) |
| UML domain class associations | [SVG](svg/uml-class.svg) | [PNG](png/uml-class.png) | [Mermaid](sources/uml-class.mmd) |
| UML use cases | [SVG](svg/uml-use-case.svg) | [PNG](png/uml-use-case.png) | [Layout/evidence](sources/uml-use-case.json) |
| UML application sequence | [SVG](svg/uml-sequence-apply.svg) | [PNG](png/uml-sequence-apply.png) | [Mermaid](sources/uml-sequence-apply.mmd) |
| UML interview sequence | [SVG](svg/uml-sequence-interview.svg) | [PNG](png/uml-sequence-interview.png) | [Mermaid](sources/uml-sequence-interview.mmd) |
| UML application activity | [SVG](svg/uml-activity.svg) | [PNG](png/uml-activity.png) | [Nodes and edges](sources/uml-activity.json) |

## Focused exports

Each structural view also has standalone domain images for use in reports and slides:

| Domain | Crow’s Foot ER overview | Full ER schema | UML classes |
| --- | --- | --- | --- |
| Identity & communication | [SVG](svg/er-overview-domain-1.svg) / [PNG](png/er-overview-domain-1.png) | [SVG](svg/er-full-domain-1.svg) / [PNG](png/er-full-domain-1.png) | [SVG](svg/uml-class-domain-1.svg) / [PNG](png/uml-class-domain-1.png) |
| Student data | [SVG](svg/er-overview-domain-2.svg) / [PNG](png/er-overview-domain-2.png) | [SVG](svg/er-full-domain-2.svg) / [PNG](png/er-full-domain-2.png) | [SVG](svg/uml-class-domain-2.svg) / [PNG](png/uml-class-domain-2.png) |
| Recruitment | [SVG](svg/er-overview-domain-3.svg) / [PNG](png/er-overview-domain-3.png) | [SVG](svg/er-full-domain-3.svg) / [PNG](png/er-full-domain-3.png) | [SVG](svg/uml-class-domain-3.svg) / [PNG](png/uml-class-domain-3.png) |

Chen focused views: [Identity & communication SVG](svg/er-chen-domain-1.svg) / [PNG](png/er-chen-domain-1.png), [Student data SVG](svg/er-chen-domain-2.svg) / [PNG](png/er-chen-domain-2.png), and [Recruitment SVG](svg/er-chen-domain-3.svg) / [PNG](png/er-chen-domain-3.png).

## ER notation guide

The original relational diagrams use **Crow’s Foot ER notation**. The additional conceptual view uses **Chen shapes with the (min,max) participation variant**.

| Feature | Crow’s Foot views | Chen view |
| --- | --- | --- |
| Entity | Table rectangle with field rows | Plain rectangle |
| Relationship | Named connector with endpoint markers | Named diamond joined to entities |
| Attribute | Field inside a table rectangle | Oval connected to an entity |
| Primary key | PK marker | Underlined attribute name |
| Optional / many | Circle, bar and crow’s-foot endpoint symbols | Explicit (0,1), (1,1), or (0,N) beside each participating entity |
| Detail | Keys-only overview or all 114 mapped fields | Selected non-FK attributes; FKs represented by relationships |

In Chen’s min/max variant, read the pair beside the entity it describes: `STUDENTS (0,N) — Submits — (1,1) APPLICATIONS` means a student can submit zero or many applications, and each application belongs to exactly one student. This is a different placement convention from Crow’s Foot endpoint markers. `N` means an unrestricted maximum; `min = 0` means optional participation. The explicit pairs replace single/double participation-line encoding in this view.

All 12 mapped tables have their own primary key. The Chen view therefore uses ordinary entity rectangles and relationship diamonds, without inventing weak entities, identifying relationships, derived attributes, or multivalued attributes. Associative records such as student_skills, applications and saved_internships remain entities because they have their own IDs and attributes; no unsupported pair-uniqueness rule is implied.

Chen symbol definitions follow [Emory CS457](https://www.cs.emory.edu/~cheung/Courses/377/Syllabus/2-ER/ER-diagram.html); same-side min/max participation follows the [University of Pittsburgh ER model notes](https://people.cs.pitt.edu/~chang/156/03ERmodel.html).

## Sources and notation

The schema source of truth is [the SQLAlchemy models](../../backend/app/db/models.py), not the earlier SQL snapshot. There are 12 mapped tables, 114 fields and 16 foreign keys. [schema.json](schema.json) preserves extracted field types, primary/unique keys, nullability, explicit indexes, defaults and foreign-key deletion rules.

The two relational ER diagrams use Crow’s Foot notation. Dashed links are non-identifying because these tables use separate surrogate primary keys. Profile foreign keys are unique, giving zero-or-one profiles per account. The two nullable foreign keys are `internships.recruiter_id` and `interviews.internship_id`. A default value does not imply a NOT NULL constraint.

UML class views show ordinary associations and selected declared attributes. They do not invent domain methods, role inheritance or composition. Use-case actors remain outside the system boundary; authenticated access is a precondition for protected goals rather than an include arrow to login. The activity diagram uses an initial node, activity finals, actions, guarded decisions and a merge. Sequence diagrams use dashed lifelines, call/return arrows and UML combined fragments.

Behavioral diagrams follow the current routes and UI call paths. Application persistence and alerts use two commits. Interview insertion and the related status/alert update also use two commits. The interview route checks the recruiter role but currently does not check ownership of the submitted application. Diagram notes preserve these implementation boundaries.

Notation references: [OMG UML 2.5.1](https://www.omg.org/spec/UML/2.5.1), [Mermaid ER syntax](https://mermaid.js.org/syntax/entityRelationshipDiagram.html), [class diagrams](https://mermaid.js.org/syntax/classDiagram.html), and [sequence diagrams](https://mermaid.js.org/syntax/sequenceDiagram.html).

## Verification and updates

[verification.json](verification.json) records metadata/source checks, diagram hashes and browser/export checks. Verification compares extracted definitions with SQLAlchemy's own metadata without connecting to MySQL. The reformatted structural panels, role views and sequence lanes were visually inspected; browser checks cover all eight diagrams and all twelve domain exports. These checks establish correspondence with declared implementation; they do not prove live database migration state or end-to-end runtime behavior.

With backend dependencies installed, run:

```bash
python output/diagrams/verify_diagrams.py
```

`build_diagrams.py` extracts schema definitions and generates the use-case/activity SVGs. `format_structural.py` creates orthogonal ER/class layouts; `format_chen.py` draws the Chen entity, relationship and attribute shapes. The formatter uses uniform spacing and emits `layout.json` plus twelve focused domain SVGs. Reference cards repeat existing entities for context; all 12 principal entities and all 16 relationships appear once across the three domains. Mermaid ER/class sources remain editable semantic definitions; rendering them directly will use Mermaid's own layout. Only the two sequence Mermaid definitions must be rendered into their matching files in `svg/` after changes. Then run `python output/diagrams/build_diagrams.py --gallery` to embed those SVGs into the offline viewer, refresh PNG exports, and rerun verification. The current viewer and images are already rendered.
