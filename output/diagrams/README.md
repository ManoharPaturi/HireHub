# HireHub ER and UML diagrams

Open **[index.html](index.html)** in a browser. It is a standalone offline viewer with seven embedded SVG diagrams, diagram selection, zoom, SVG/PNG/source download buttons, and a print view. No server, CDN, or application login is required. Fit shows the whole diagram; zoom in to inspect labels.

| Diagram | Vector image | PNG image | Editable definition |
| --- | --- | --- | --- |
| ER overview | [SVG](svg/er-overview.svg) | [PNG](png/er-overview.png) | [Mermaid](sources/er-overview.mmd) |
| Full physical schema | [SVG](svg/er-full.svg) | [PNG](png/er-full.png) | [Mermaid](sources/er-full.mmd) |
| UML domain class associations | [SVG](svg/uml-class.svg) | [PNG](png/uml-class.png) | [Mermaid](sources/uml-class.mmd) |
| UML use cases | [SVG](svg/uml-use-case.svg) | [PNG](png/uml-use-case.png) | [Layout/evidence](sources/uml-use-case.json) |
| UML application sequence | [SVG](svg/uml-sequence-apply.svg) | [PNG](png/uml-sequence-apply.png) | [Mermaid](sources/uml-sequence-apply.mmd) |
| UML interview sequence | [SVG](svg/uml-sequence-interview.svg) | [PNG](png/uml-sequence-interview.png) | [Mermaid](sources/uml-sequence-interview.mmd) |
| UML application activity | [SVG](svg/uml-activity.svg) | [PNG](png/uml-activity.png) | [Nodes and edges](sources/uml-activity.json) |

## Sources and notation

The schema source of truth is [the SQLAlchemy models](../../backend/app/db/models.py), not the earlier SQL snapshot. There are 12 mapped tables, 114 fields and 16 foreign keys. [schema.json](schema.json) preserves extracted field types, primary/unique keys, nullability, explicit indexes, defaults and foreign-key deletion rules.

ER diagrams use crow's-foot notation. Dashed links are non-identifying because these tables use separate surrogate primary keys. Profile foreign keys are unique, giving zero-or-one profiles per account. The two nullable foreign keys are `internships.recruiter_id` and `interviews.internship_id`. A default value does not imply a NOT NULL constraint.

UML class views show ordinary associations and selected declared attributes. They do not invent domain methods, role inheritance or composition. Use-case actors remain outside the system boundary; authenticated access is a precondition for protected goals rather than an include arrow to login. The activity diagram uses an initial node, activity finals, actions, guarded decisions and a merge. Sequence diagrams use dashed lifelines, call/return arrows and UML combined fragments.

Behavioral diagrams follow the current routes and UI call paths. Application persistence and alerts use two commits. Interview insertion and the related status/alert update also use two commits. The interview route checks the recruiter role but currently does not check ownership of the submitted application. Diagram notes preserve these implementation boundaries.

Notation references: [OMG UML 2.5.1](https://www.omg.org/spec/UML/2.5.1), [Mermaid ER syntax](https://mermaid.js.org/syntax/entityRelationshipDiagram.html), [class diagrams](https://mermaid.js.org/syntax/classDiagram.html), and [sequence diagrams](https://mermaid.js.org/syntax/sequenceDiagram.html).

## Verification and updates

[verification.json](verification.json) records metadata/source checks, diagram hashes and browser/export checks. Verification compares extracted definitions with SQLAlchemy's own metadata without connecting to MySQL. All seven PNGs were visually inspected. These checks establish correspondence with declared implementation; they do not prove live database migration state or end-to-end runtime behavior.

With backend dependencies installed, run:

```bash
python output/diagrams/verify_diagrams.py
```

`build_diagrams.py` extracts schema definitions and generates the native use-case/activity SVGs. Mermaid definitions in `sources/` must be rendered into the matching files in `svg/` after changes. Then run `python output/diagrams/build_diagrams.py --gallery` to embed those SVGs into the offline viewer, refresh PNG exports, and rerun verification. The current viewer and images are already rendered.
