# Builds the earlier 24-slide PowerPoint presentation using python-pptx.
# Coordinates, colors and helper functions below control native slide objects.
# The eight-slide Beamer review is maintained separately in output/beamer.

"""Generate HireHub Internship Portal project presentation (PPTX).

Run:  python make_presentation.py
Out:  <project root>/HireHub_Internship_Portal_Presentation.pptx
"""

import os
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR

# ---------------------------------------------------------------- palette ---
INK        = RGBColor(0x0F, 0x17, 0x2A)   # slate-900
INK_SOFT   = RGBColor(0x1E, 0x29, 0x3B)   # slate-800
PAPER      = RGBColor(0xFF, 0xFF, 0xFF)
MUTED      = RGBColor(0x47, 0x55, 0x69)   # slate-600
FAINT      = RGBColor(0x94, 0xA3, 0xB8)   # slate-400
ACCENT     = RGBColor(0x4F, 0x46, 0xE5)   # indigo-600
ACCENT_DK  = RGBColor(0x37, 0x30, 0xA3)   # indigo-700
ACCENT_BG  = RGBColor(0xEE, 0xF2, 0xFF)   # indigo-50
TEAL       = RGBColor(0x0D, 0x94, 0x88)   # teal-600
TEAL_BG    = RGBColor(0xCC, 0xFB, 0xF1)   # teal-100
GOLD       = RGBColor(0xB4, 0x53, 0x09)   # amber-700
GOLD_BG    = RGBColor(0xFE, 0xF3, 0xC7)   # amber-100
CARD       = RGBColor(0xF8, 0xFA, 0xFC)   # slate-50
BORDER     = RGBColor(0xE2, 0xE8, 0xF0)   # slate-200
GREEN      = RGBColor(0x15, 0x80, 0x3D)
GREEN_BG   = RGBColor(0xDC, 0xFC, 0xE7)
ROSE       = RGBColor(0xBE, 0x12, 0x3C)
ROSE_BG    = RGBColor(0xFF, 0xE4, 0xE6)

BODY = "Segoe UI"
MONO = "Consolas"
MATH = "Cambria Math"

SW, SH = Inches(13.333), Inches(7.5)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ER_PNG = os.path.join(ROOT, "docs", "er-diagram-preview.png")
OUT = os.path.join(ROOT, "HireHub_Internship_Portal_Presentation.pptx")

prs = Presentation()
prs.slide_width, prs.slide_height = SW, SH
BLANK = prs.slide_layouts[6]

TOTAL = 24
_page = {"n": 0}


# ---------------------------------------------------------------- helpers ---
def slide_new(bg=PAPER):
    s = prs.slides.add_slide(BLANK)
    _page["n"] += 1
    r = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SW, SH)
    r.fill.solid(); r.fill.fore_color.rgb = bg
    r.line.fill.background(); r.shadow.inherit = False
    return s


def shape(s, kind, x, y, w, h, fill=None, line=None, line_w=1.0, radius=None):
    sp = s.shapes.add_shape(kind, x, y, w, h)
    sp.shadow.inherit = False
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid(); sp.fill.fore_color.rgb = fill
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line; sp.line.width = Pt(line_w)
    if radius is not None and kind == MSO_SHAPE.ROUNDED_RECTANGLE:
        try: sp.adjustments[0] = radius
        except Exception: pass
    return sp


def tb(s, x, y, w, h, anchor=MSO_ANCHOR.TOP):
    box = s.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return tf


def para(tf, text=None, runs=None, size=14, bold=False, color=INK, font=BODY,
         align=PP_ALIGN.LEFT, sb=0, sa=6, first=False, line_spacing=1.0):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_before, p.space_after = Pt(sb), Pt(sa)
    p.line_spacing = line_spacing
    items = runs if runs is not None else [(text, size, bold, color, font)]
    for it in items:
        t, sz, bd, cl, fnt = (it + (None,) * 5)[:5]
        sz = sz or size; bd = bold if bd is None else bd
        cl = cl or color; fnt = fnt or font
        r = p.add_run(); r.text = t
        r.font.size = Pt(sz); r.font.bold = bd
        r.font.color.rgb = cl; r.font.name = fnt
    return p


def bullets(tf, items, size=14, gap=8, color=INK, first=True, bullet_color=ACCENT):
    """items: list of (level, text) or (level, lead, text) where lead is bold."""
    for i, item in enumerate(items):
        lvl, a, b = (item + (None,))[:3] if len(item) == 2 else item
        mark = "•  " if lvl == 0 else "–  "
        indent = "" if lvl == 0 else "      "
        runs = [(indent + mark, size, True, bullet_color, BODY)]
        if b is not None:
            runs += [(a, size, True, color, BODY), (b, size, False, color, BODY)]
        else:
            runs += [(a, size, False, color, BODY)]
        para(tf, runs=runs, size=size, sa=gap, first=(first and i == 0))


def content_slide(kicker, title, sa_title=True):
    s = slide_new()
    shape(s, MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.14), SH, fill=ACCENT)
    tf = tb(s, Inches(0.62), Inches(0.34), Inches(11.6), Inches(0.32))
    para(tf, runs=[(kicker.upper(), 12, True, ACCENT, BODY)], first=True, sa=2)
    tf2 = tb(s, Inches(0.6), Inches(0.66), Inches(12.1), Inches(0.62))
    para(tf2, text=title, size=30, bold=True, color=INK, first=True, sa=0)
    shape(s, MSO_SHAPE.RECTANGLE, Inches(0.62), Inches(1.42), Inches(0.85), Inches(0.05), fill=TEAL)
    ft = tb(s, Inches(0.62), Inches(7.08), Inches(9), Inches(0.3))
    para(ft, runs=[("HireHub — Internship Portal", 10, False, FAINT, BODY)], first=True)
    pn = tb(s, Inches(12.1), Inches(7.08), Inches(0.85), Inches(0.3))
    para(pn, runs=[(f"{_page['n']:02d} / {TOTAL}", 10, False, FAINT, BODY)],
         align=PP_ALIGN.RIGHT, first=True)
    return s


def card(s, x, y, w, h, fill=CARD, line=BORDER, radius=0.06):
    return shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h,
                 fill=fill, line=line, line_w=1.0, radius=radius)


def chip(s, x, y, w, text, fill=ACCENT_BG, fg=ACCENT_DK, size=11.5, h=Inches(0.34)):
    c = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=fill, radius=0.5)
    tf = c.text_frame; tf.word_wrap = False
    tf.margin_left = tf.margin_right = Inches(0.06)
    tf.margin_top = tf.margin_bottom = 0
    para(tf, text=text, size=size, bold=True, color=fg,
         align=PP_ALIGN.CENTER, first=True, sa=0)
    return c


def heading(s, x, y, text, color=INK, size=15, w=Inches(5.5)):
    tf = tb(s, x, y, w, Inches(0.35))
    para(tf, text=text, size=size, bold=True, color=color, first=True, sa=0)
    return tf


def code_block(s, x, y, w, h, lines, size=10.5, fill=CARD, title=None,
               border=BORDER, line_sp=1.06):
    card(s, x, y, w, h, fill=fill, line=border)
    tf = tb(s, x + Inches(0.18), y + Inches(0.12), w - Inches(0.36), h - Inches(0.24))
    start = 0
    if title:
        para(tf, text=title, size=size - 0.5, bold=True, color=ACCENT_DK,
             font=BODY, first=True, sa=3)
        start = 1
    for i, ln in enumerate(lines):
        clr = MUTED if ln.strip().startswith("--") or ln.strip().startswith("#") else INK
        para(tf, text=ln if ln else " ", size=size, color=clr, font=MONO,
             first=(i == 0 and start == 0), sa=1.5, line_spacing=line_sp)


def arrow_down(s, x, y, w, h, fill=TEAL):
    return shape(s, MSO_SHAPE.DOWN_ARROW, x, y, w, h, fill=fill)


# ================================================================ SLIDE 1 ===
s = slide_new(bg=INK)
shape(s, MSO_SHAPE.OVAL, Inches(9.1), Inches(-2.1), Inches(7.2), Inches(7.2), fill=INK_SOFT)
shape(s, MSO_SHAPE.OVAL, Inches(10.4), Inches(-0.9), Inches(5.0), Inches(5.0), fill=ACCENT_DK)
shape(s, MSO_SHAPE.OVAL, Inches(-1.6), Inches(5.6), Inches(4.6), Inches(4.6), fill=INK_SOFT)
shape(s, MSO_SHAPE.OVAL, Inches(-0.5), Inches(6.6), Inches(2.3), Inches(2.3), fill=TEAL)

tf = tb(s, Inches(0.9), Inches(1.28), Inches(11.5), Inches(0.4))
para(tf, runs=[("FULL-STACK WEB APPLICATION  •  DBMS PROJECT  •  AUGUST 2026",
               13, True, RGBColor(0xA5, 0xB4, 0xFC), BODY)], first=True)

tf = tb(s, Inches(0.85), Inches(1.75), Inches(11.6), Inches(1.9))
para(tf, text="HireHub", size=76, bold=True, color=PAPER, first=True, sa=2)
para(tf, text="Internship Portal — Connecting Students with Recruiters",
     size=24, bold=False, color=RGBColor(0xC7, 0xD2, 0xFE), sa=0)

shape(s, MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(3.86), Inches(2.6), Inches(0.05), fill=TEAL)

tf = tb(s, Inches(0.9), Inches(4.12), Inches(11.4), Inches(0.75))
para(tf, text="A three-tier system built on a normalized relational schema — covering internship "
              "discovery, applications, screening, interview scheduling and outcomes.",
     size=15, color=RGBColor(0xCB, 0xD5, 0xE1), first=True, sa=0, line_spacing=1.15)

labels = ["FastAPI", "React 19", "TypeScript", "MySQL 8", "SQLAlchemy", "JWT Auth", "Tailwind CSS"]
cx = Inches(0.9)
for lb in labels:
    w = Inches(0.34 + 0.115 * len(lb))
    chip(s, cx, Inches(5.15), w, lb, fill=RGBColor(0x1E, 0x29, 0x3B),
         fg=RGBColor(0xA5, 0xB4, 0xFC), size=12, h=Inches(0.42))
    cx = Emu(int(cx) + int(w) + int(Inches(0.18)))

shape(s, MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(6.15), Inches(11.5), Inches(0.022),
      fill=RGBColor(0x33, 0x41, 0x55))
tf = tb(s, Inches(0.9), Inches(6.38), Inches(11.5), Inches(0.6))
para(tf, runs=[("Presented by:  ", 14, False, FAINT, BODY),
               ("Pushpak", 16, True, PAPER, BODY)], first=True, sa=2)
para(tf, runs=[("Database Management Systems  •  Project Review", 12, False, FAINT, BODY)], sa=0)

# ================================================================ SLIDE 2 ===
s = content_slide("Agenda", "Table of Contents")
toc_left = [
    ("01", "Introduction"), ("02", "Motivation"), ("03", "Problem Statement"),
    ("04", "Objectives"), ("05", "Tech Stack"), ("06", "System Architecture"),
    ("07", "File Structure"), ("08", "ER Diagram"), ("09", "UML Use-Case Diagram"),
    ("10", "Normalization Used"), ("11", "DDL Used"),
]
toc_right = [
    ("12", "DML Used"), ("13", "Relational Algebra Expressions"),
    ("14", "CRUD Operations"), ("15", "Autonomous Triggers"),
    ("16", "Atomicity & ACID"), ("17", "Key Features"),
    ("18", "Application Lifecycle"), ("19", "Security & Validation"),
    ("20", "Future Enhancements"), ("21", "Conclusion"),
]
for col, (items, x) in enumerate([(toc_left, Inches(0.62)), (toc_right, Inches(6.85))]):
    y = Inches(1.75)
    for num, name in items:
        card(s, x, y, Inches(5.85), Inches(0.42), fill=CARD)
        n = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.07), y + Inches(0.06),
                  Inches(0.52), Inches(0.30), fill=ACCENT, radius=0.25)
        tfn = n.text_frame; tfn.margin_left = tfn.margin_right = 0
        tfn.margin_top = tfn.margin_bottom = 0
        para(tfn, text=num, size=12, bold=True, color=PAPER,
             align=PP_ALIGN.CENTER, first=True, sa=0)
        tf = tb(s, x + Inches(0.75), y + Inches(0.07), Inches(4.9), Inches(0.3))
        para(tf, text=name, size=14, bold=True, color=INK, first=True, sa=0)
        y = Emu(int(y) + int(Inches(0.5)))

# ================================================================ SLIDE 3 ===
s = content_slide("Section 01", "Introduction")
tf = tb(s, Inches(0.62), Inches(1.72), Inches(7.1), Inches(3.2))
para(tf, text="HireHub is a full-stack internship portal — a web application backed by a "
              "normalized relational database that connects students seeking internships "
              "with recruiters offering them.", size=15, color=MUTED, first=True,
     sa=10, line_spacing=1.18)
para(tf, text="Every action in the UI maps to a REST call, and every REST call maps to "
              "SQL against a 12-table MySQL schema — making it a complete, working "
              "demonstration of DBMS concepts in a real product.", size=15, color=MUTED,
     sa=12, line_spacing=1.18)
heading(s, Inches(0.62), Inches(4.05), "What the system does")
tf = tb(s, Inches(0.62), Inches(4.42), Inches(7.15), Inches(2.3))
bullets(tf, [
    (0, "Student module — ", "discover, filter, apply, upload documents and track application status"),
    (0, "Recruiter module — ", "post internships, screen applicants, update statuses, schedule interviews"),
    (0, "Communication — ", "automatic notifications keep both sides informed of every event"),
    (0, "Discovery engine — ", "keyword search, multi-filter queries, sorting, pagination, skill-based recommendations"),
], size=13.5, gap=7)

stats = [("12", "Relational Tables", TEAL, TEAL_BG),
         ("25+", "REST Endpoints", ACCENT, ACCENT_BG),
         ("2", "User Roles", GOLD, GOLD_BG),
         ("6", "API Routers", GREEN, GREEN_BG)]
y = Inches(1.72)
for num, lab, c, cbg in stats:
    card(s, Inches(8.1), y, Inches(4.6), Inches(1.06), fill=PAPER)
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.26), y + Inches(0.19),
          Inches(1.15), Inches(0.68), fill=cbg, radius=0.18)
    tfn = tb(s, Inches(8.26), y + Inches(0.19), Inches(1.15), Inches(0.68),
             anchor=MSO_ANCHOR.MIDDLE)
    para(tfn, text=num, size=22, bold=True, color=c, align=PP_ALIGN.CENTER, first=True, sa=0)
    tf = tb(s, Inches(9.6), y + Inches(0.33), Inches(3.0), Inches(0.4))
    para(tf, text=lab, size=15, bold=True, color=INK, first=True, sa=0)
    y = Emu(int(y) + int(Inches(1.22)))

# ================================================================ SLIDE 4 ===
s = content_slide("Section 02", "Motivation")
mot = [
    ("For Students", TEAL, TEAL_BG,
     ["Internship postings are scattered across portals, LinkedIn groups and word-of-mouth",
      "No single view of applied roles — statuses live in inboxes and spreadsheets",
      "Repeatedly re-entering the same profile & resume data on every portal"]),
    ("For Recruiters", ACCENT, ACCENT_BG,
     ["Screening happens over email threads with no structured applicant data",
      "Scheduling interviews and informing candidates is fully manual",
      "No lightweight tool that covers posting → screening → scheduling in one place"]),
    ("Academic Purpose", GOLD, GOLD_BG,
     ["Apply DBMS theory to a real system: normalization, keys, constraints, transactions",
      "Demonstrate SQL, relational algebra and CRUD through visible product features",
      "Build end-to-end engineering skill: database → API → user interface"]),
]
x = Inches(0.62)
for title, c, cbg, pts in mot:
    card(s, x, Inches(1.75), Inches(3.95), Inches(4.75), fill=CARD)
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.22), Inches(2.0),
          Inches(3.5), Inches(0.5), fill=cbg, radius=0.25)
    tfh = tb(s, x + Inches(0.22), Inches(2.0), Inches(3.5), Inches(0.5),
             anchor=MSO_ANCHOR.MIDDLE)
    para(tfh, text=title, size=15, bold=True, color=c, align=PP_ALIGN.CENTER,
         first=True, sa=0)
    tf = tb(s, x + Inches(0.28), Inches(2.75), Inches(3.42), Inches(3.6))
    bullets(tf, [(0, p) for p in pts], size=12.5, gap=10, bullet_color=c)
    x = Emu(int(x) + int(Inches(4.16)))

tf = tb(s, Inches(0.62), Inches(6.68), Inches(12.1), Inches(0.5))
para(tf, runs=[("The gap:  ", 14, True, ACCENT, BODY),
               ("no single end-to-end system that takes both sides from discovery to a final "
                "decision — with guaranteed data integrity underneath.", 14, False, MUTED, BODY)],
     first=True, sa=0)

# ================================================================ SLIDE 5 ===
s = content_slide("Section 03", "Problem Statement")
card(s, Inches(0.62), Inches(1.72), Inches(12.1), Inches(1.55), fill=ACCENT_BG,
     line=RGBColor(0xC7, 0xD2, 0xFE))
tf = tb(s, Inches(0.95), Inches(1.92), Inches(11.45), Inches(1.2), anchor=MSO_ANCHOR.MIDDLE)
para(tf, runs=[("“ ", 18, True, ACCENT, BODY),
               ("Students and recruiters need one reliable platform where internship discovery, "
                "application, screening, interview scheduling and outcomes are managed "
                "consistently — backed by a normalized relational database that eliminates "
                "redundancy, enforces integrity through constraints, and supports efficient "
                "multi-criteria queries.", 15.5, False, INK, BODY),
               (" ”", 18, True, ACCENT, BODY)], first=True, sa=0, line_spacing=1.2)

heading(s, Inches(0.62), Inches(3.62), "Pain points of the current manual process")
pains = [
    ("Fragmented discovery", "Roles spread across many portals; students miss deadlines and opportunities"),
    ("Zero status visibility", "Applicants learn outcomes late, or never — no tracking, no notifications"),
    ("Manual screening", "Recruiters compare candidates from email threads and unstructured resumes"),
    ("Data redundancy", "The same student, company and role data re-typed into every tool — inconsistencies creep in"),
    ("No integrity rules", "Spreadsheets allow orphaned records, duplicates and invalid statuses"),
]
y = Inches(4.05)
for i, (t, d) in enumerate(pains):
    x = Inches(0.62) if i % 2 == 0 else Inches(6.78)
    if i == 4:
        card(s, Inches(0.62), y, Inches(12.1), Inches(0.62), fill=CARD)
        tf = tb(s, Inches(0.85), y + Inches(0.15), Inches(11.7), Inches(0.35))
        para(tf, runs=[(t + " — ", 13, True, ROSE, BODY), (d, 13, False, MUTED, BODY)],
             first=True, sa=0)
        break
    card(s, x, y, Inches(5.94), Inches(1.14), fill=CARD)
    shape(s, MSO_SHAPE.RECTANGLE, x + Inches(0.02), y + Inches(0.14), Inches(0.05),
          Inches(0.86), fill=ROSE)
    tf = tb(s, x + Inches(0.22), y + Inches(0.12), Inches(5.55), Inches(0.95))
    para(tf, text=t, size=13.5, bold=True, color=INK, first=True, sa=2)
    para(tf, text=d, size=11.5, color=MUTED, sa=0, line_spacing=1.05)
    if i % 2 == 1:
        y = Emu(int(y) + int(Inches(1.3)))

# ================================================================ SLIDE 6 ===
s = content_slide("Section 04", "Objectives")
objectives = [
    ("Design a normalized schema", "Model the internship domain in 12 relational tables, normalized up to BCNF, with surrogate keys and no redundancy"),
    ("Expose secure REST APIs", "Role-based endpoints for students and recruiters, protected by JWT authentication and Pydantic validation"),
    ("Implement complete CRUD", "Every resource supports Create, Read, Update and Delete — mapped cleanly to SQL statements"),
    ("Enforce integrity in the DBMS", "Primary/foreign keys, UNIQUE constraints, ON DELETE CASCADE / SET NULL referential actions"),
    ("Automate workflows", "Event-driven triggers: notifications on apply & status change, auto status advance on interview scheduling"),
    ("Guarantee ACID transactions", "Atomic multi-table writes (application + notification commit together or not at all)"),
    ("Rich discovery experience", "Keyword search, filters, sorting, pagination and skill-based recommendations over indexed columns"),
    ("Deliver a usable product", "A responsive React SPA with dedicated dashboards for both roles"),
]
y = Inches(1.72)
for i, (t, d) in enumerate(objectives):
    x = Inches(0.62) if i % 2 == 0 else Inches(6.78)
    card(s, x, y, Inches(5.94), Inches(1.2), fill=CARD)
    n = shape(s, MSO_SHAPE.OVAL, x + Inches(0.16), y + Inches(0.33), Inches(0.52), Inches(0.52),
              fill=ACCENT)
    tfn = n.text_frame; tfn.margin_left = tfn.margin_right = 0
    tfn.margin_top = tfn.margin_bottom = 0
    para(tfn, text=str(i + 1), size=16, bold=True, color=PAPER,
         align=PP_ALIGN.CENTER, first=True, sa=0)
    tf = tb(s, x + Inches(0.85), y + Inches(0.14), Inches(4.95), Inches(1.0))
    para(tf, text=t, size=13.5, bold=True, color=INK, first=True, sa=2)
    para(tf, text=d, size=10.8, color=MUTED, sa=0, line_spacing=1.04)
    if i % 2 == 1:
        y = Emu(int(y) + int(Inches(1.34)))

# ================================================================ SLIDE 7 ===
s = content_slide("Section 05", "Tech Stack")
stack = [
    ("Frontend", TEAL, [
        ("React 19 + TypeScript", "component-based SPA, static typing"),
        ("Vite 8", "dev server & production bundler"),
        ("Tailwind CSS 4", "utility-first responsive styling"),
        ("Axios", "HTTP client with JWT request interceptor"),
        ("React Router 7, Context API", "navigation, auth & notification state"),
    ]),
    ("Backend", ACCENT, [
        ("Python FastAPI", "high-performance async REST framework"),
        ("Uvicorn", "ASGI server running the API"),
        ("SQLAlchemy 2.0 ORM", "models → tables, session transactions"),
        ("Pydantic v2", "request/response validation & schemas"),
        ("python-jose (JWT)", "token signing & verification"),
    ]),
    ("Database", GOLD, [
        ("MySQL 8.0", "relational store, InnoDB engine"),
        ("utf8mb4 charset", "full Unicode, including ₹ symbol"),
        ("12 tables", "normalized up to BCNF"),
        ("Indexes", "on email, titles, locations & all FKs"),
        ("PyMySQL driver", "SQLAlchemy ↔ MySQL connector"),
    ]),
    ("Tools & Practices", GREEN, [
        ("Swagger / OpenAPI", "auto-generated interactive docs at /docs"),
        ("Git", "version control across the stack"),
        ("oxlint + TypeScript", "static analysis, fewer runtime bugs"),
        ("Demo seeding", "auto-created demo data on first startup"),
        ("Base64 document storage", "resumes stored in MEDIUMTEXT columns"),
    ]),
]
x = Inches(0.62)
for name, c, rows in stack:
    card(s, x, Inches(1.72), Inches(2.98), Inches(4.95), fill=CARD)
    shape(s, MSO_SHAPE.RECTANGLE, x, Inches(1.72), Inches(2.98), Inches(0.06), fill=c)
    tf = tb(s, x + Inches(0.2), Inches(1.92), Inches(2.6), Inches(0.35))
    para(tf, text=name, size=15.5, bold=True, color=c, first=True, sa=0)
    tf = tb(s, x + Inches(0.2), Inches(2.38), Inches(2.62), Inches(4.1))
    for j, (tool, why) in enumerate(rows):
        para(tf, runs=[(tool, 11.5, True, INK, BODY)], first=(j == 0), sa=1)
        para(tf, runs=[(why, 9.8, False, MUTED, BODY)], sa=8, line_spacing=1.0)
    x = Emu(int(x) + int(Inches(3.14)))

# ================================================================ SLIDE 8 ===
s = content_slide("Section 06", "System Architecture — Three-Tier")
tiers = [
    ("PRESENTATION TIER", "React 19 + TypeScript SPA", TEAL, TEAL_BG,
     ["Component-based UI: listings, dashboards, tracker, calendar",
      "Axios client with JWT Bearer-token interceptor",
      "Context API for auth, notifications & theme state",
      "Tailwind CSS — responsive layouts for both roles"]),
    ("APPLICATION TIER", "FastAPI REST API (Uvicorn, port 8000)", ACCENT, ACCENT_BG,
     ["6 routers: auth, students, internships, applications, notifications, recruiter",
      "Pydantic schemas validate every request & response",
      "JWT authentication + role-based dependency guards",
      "Business logic: triggers, lifecycle rules, recommendations"]),
    ("DATA TIER", "MySQL 8.0 — internship_portal (12 tables)", GOLD, GOLD_BG,
     ["InnoDB engine: transactions, row-level locking, MVCC",
      "PK / FK constraints with CASCADE / SET NULL rules",
      "Indexes on searchable columns and all foreign keys",
      "SQLAlchemy 2.0 ORM maps Python models ↔ tables"]),
]
y = Inches(1.7)
for title, sub, c, cbg, pts in tiers:
    card(s, Inches(1.3), y, Inches(8.2), Inches(1.42), fill=PAPER)
    shape(s, MSO_SHAPE.RECTANGLE, Inches(1.3), y, Inches(0.09), Inches(1.42), fill=c)
    tf = tb(s, Inches(1.62), y + Inches(0.12), Inches(7.7), Inches(1.2))
    para(tf, runs=[(title + "   ", 13.5, True, c, BODY),
                   (sub, 12, False, MUTED, BODY)], first=True, sa=4)
    para(tf, text="  •  ".join(pts[:2]), size=10.3, color=MUTED, sa=1, line_spacing=1.05)
    para(tf, text="  •  ".join(pts[2:]), size=10.3, color=MUTED, sa=0, line_spacing=1.05)
    if title != "DATA TIER":
        a = arrow_down(s, Inches(5.18), y + Inches(1.44), Inches(0.42), Inches(0.34))
    y = Emu(int(y) + int(Inches(1.8)))

card(s, Inches(9.85), Inches(1.7), Inches(2.88), Inches(5.0), fill=ACCENT_BG,
     line=RGBColor(0xC7, 0xD2, 0xFE))
tf = tb(s, Inches(10.05), Inches(1.9), Inches(2.5), Inches(4.7))
para(tf, text="Request Flow", size=14, bold=True, color=ACCENT_DK, first=True, sa=8)
bullets(tf, [
    (0, "Browser renders the SPA and calls https//…/api endpoints"),
    (0, "Axios attaches Authorization: Bearer <JWT> to every call"),
    (0, "FastAPI validates the token, resolves the user & role"),
    (0, "Router applies filters / business rules via SQLAlchemy"),
    (0, "MySQL returns rows; the ORM maps them to objects"),
    (0, "JSON response drives the React UI — notifications update live"),
], size=10.8, gap=8, bullet_color=ACCENT_DK)
tf = tb(s, Inches(1.3), Inches(6.78), Inches(8.2), Inches(0.35))
para(tf, runs=[("Stateless API  •  ", 11.5, True, MUTED, BODY),
               ("every request is self-describing; horizontal scale-ready. Interactive docs "
                "auto-served at /docs (Swagger).", 11.5, False, MUTED, BODY)], first=True, sa=0)

# ================================================================ SLIDE 9 ===
s = content_slide("Section 07", "File Structure")
code_block(s, Inches(0.62), Inches(1.72), Inches(7.3), Inches(5.0), [
    "internship-portal/",
    "├─ backend/                  # FastAPI + SQLAlchemy",
    "│  ├─ app/",
    "│  │  ├─ core/               # config · security (JWT, hashing)",
    "│  │  ├─ db/                 # database · models (12 ORM classes)",
    "│  │  │                      # · init_db (demo seed)",
    "│  │  ├─ routers/            # auth · students · internships",
    "│  │  │                      # · applications · notifications",
    "│  │  │                      # · recruiter",
    "│  │  ├─ schemas/            # Pydantic request/response models",
    "│  │  └─ main.py             # FastAPI app · CORS · lifespan",
    "│  ├─ schema.sql             # MySQL 8 DDL (12 tables)",
    "│  └─ requirements.txt",
    "├─ frontend/                 # React 19 + TypeScript SPA",
    "│  ├─ src/",
    "│  │  ├─ components/         # Auth · Dashboard · Internships",
    "│  │  │                      # · Tracker · Recruiter · Profile",
    "│  │  ├─ context/            # Auth · Notification · Theme",
    "│  │  ├─ services/api.ts     # Axios client + JWT interceptor",
    "│  │  └─ types/              # shared TypeScript types",
    "│  └─ package.json",
    "└─ docs/                     # ER diagram (mmd · html · png)",
], size=10.2)

notes = [
    ("Separation of concerns", "routers (HTTP) are isolated from db models (schema) and core (cross-cutting security & config)"),
    ("Schema as code", "models.py is the single source of truth — tables auto-create on startup; schema.sql is the equivalent DDL"),
    ("Component-driven UI", "each screen is a self-contained component tree; contexts hold global auth & notification state"),
    ("Docs included", "ER diagram ships with the repo in Mermaid, HTML and PNG forms"),
]
y = Inches(1.72)
for t, d in notes:
    card(s, Inches(8.2), y, Inches(4.5), Inches(1.14), fill=CARD)
    tf = tb(s, Inches(8.42), y + Inches(0.13), Inches(4.1), Inches(0.95))
    para(tf, text=t, size=13, bold=True, color=ACCENT_DK, first=True, sa=2)
    para(tf, text=d, size=10.5, color=MUTED, sa=0, line_spacing=1.05)
    y = Emu(int(y) + int(Inches(1.3)))

# =============================================================== SLIDE 10 ===
s = content_slide("Section 08", "Entity-Relationship (ER) Diagram")
img = Image.open(ER_PNG)
iw, ih = img.size
max_w, max_h = Inches(8.5), Inches(5.2)
scale = min(max_w / iw, max_h / ih)
w, h = int(iw * scale), int(ih * scale)
card(s, Inches(0.55), Inches(1.68), Inches(8.85), Inches(5.25), fill=PAPER)
s.shapes.add_picture(ER_PNG, Inches(0.55) + (Inches(8.85) - w) // 2,
                     Inches(1.68) + (Inches(5.25) - h) // 2, w, h)

heading(s, Inches(9.62), Inches(1.72), "Relationships at a glance", size=14, w=Inches(3.3))
rels = [
    ("USERS  1:1  STUDENTS / RECRUITER_PROFILES", "one account extends into exactly one role profile (UNIQUE user_id enforces it)"),
    ("RECRUITER  1:N  INTERNSHIPS", "a recruiter posts many internships"),
    ("STUDENT  M:N  SKILLS", "via join table student_skills, with proficiency_level attribute"),
    ("STUDENT  M:N  INTERNSHIPS", "via applications (with status) and saved_internships (bookmarks)"),
    ("APPLICATION  1:N  INTERVIEWS", "each application can lead to scheduled interviews"),
    ("USERS  1:N  NOTIFICATIONS / MESSAGES", "per-user alerts and peer-to-peer messaging"),
]
y = Inches(2.14)
for t, d in rels:
    shape(s, MSO_SHAPE.RECTANGLE, Inches(9.62), y + Inches(0.03), Inches(0.05),
          Inches(0.72), fill=ACCENT)
    tf = tb(s, Inches(9.82), y, Inches(3.15), Inches(0.85))
    para(tf, text=t, size=10.5, bold=True, color=INK, first=True, sa=1, line_spacing=1.0)
    para(tf, text=d, size=9.5, color=MUTED, sa=0, line_spacing=1.0)
    y = Emu(int(y) + int(Inches(0.8)))

# =============================================================== SLIDE 11 ===
s = content_slide("Section 09", "UML Use-Case Diagram")
# system boundary
shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.1), Inches(1.66), Inches(7.15), Inches(5.3),
      fill=CARD, line=BORDER, radius=0.03)
tf = tb(s, Inches(3.3), Inches(1.74), Inches(6.8), Inches(0.3))
para(tf, text="HireHub — Internship Portal System", size=13, bold=True, color=MUTED,
     align=PP_ALIGN.CENTER, first=True, sa=0)

def use_case(s, cx, cy, w, h, label, fill=PAPER):
    uc = shape(s, MSO_SHAPE.OVAL, cx, cy, w, h, fill=fill, line=ACCENT, line_w=1.2)
    tf = uc.text_frame; tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.04)
    tf.margin_top = tf.margin_bottom = 0
    para(tf, text=label, size=9.8, bold=True, color=INK, align=PP_ALIGN.CENTER,
         first=True, sa=0, line_spacing=0.95)
    return uc

def actor(s, cx, cy, name, color):
    shape(s, MSO_SHAPE.OVAL, cx - Inches(0.14), cy, Inches(0.28), Inches(0.28),
          fill=PAPER, line=color, line_w=1.5)
    shape(s, MSO_SHAPE.RECTANGLE, cx - Inches(0.025), cy + Inches(0.30),
          Inches(0.05), Inches(0.42), fill=color)
    shape(s, MSO_SHAPE.RECTANGLE, cx - Inches(0.22), cy + Inches(0.40),
          Inches(0.44), Inches(0.045), fill=color)
    ln = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, cx - Inches(0.2),
                                cy + Inches(0.73), cx - Inches(0.08), cy + Inches(1.02))
    ln.line.color.rgb = color; ln.line.width = Pt(1.5); ln.shadow.inherit = False
    ln = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, cx + Inches(0.2),
                                cy + Inches(0.73), cx + Inches(0.08), cy + Inches(1.02))
    ln.line.color.rgb = color; ln.line.width = Pt(1.5); ln.shadow.inherit = False
    tf = tb(s, cx - Inches(0.75), cy + Inches(1.1), Inches(1.5), Inches(0.3))
    para(tf, text=name, size=12.5, bold=True, color=color,
         align=PP_ALIGN.CENTER, first=True, sa=0)

def link(s, x1, y1, x2, y2, color=FAINT):
    ln = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, x1, y1, x2, y2)
    ln.line.color.rgb = color; ln.line.width = Pt(1.1); ln.shadow.inherit = False

W, H = Inches(2.35), Inches(0.62)
left_uc = [
    ("Register / Login (JWT)", Inches(3.45), Inches(2.2)),
    ("Browse & Search Internships", Inches(3.45), Inches(3.05)),
    ("Filter · Sort · Save Roles", Inches(3.45), Inches(3.9)),
    ("Apply with Cover Letter & Resume", Inches(3.45), Inches(4.75)),
    ("Track Application Status", Inches(3.45), Inches(5.6)),
]
right_uc = [
    ("Post / Edit Internships", Inches(7.4), Inches(2.2)),
    ("Screen Applicants (joined view)", Inches(7.4), Inches(3.05)),
    ("Update Application Status", Inches(7.4), Inches(3.9)),
    ("Schedule Interviews", Inches(7.4), Inches(4.75)),
    ("View Dashboard Stats", Inches(7.4), Inches(5.6)),
]
for label, x, y in left_uc:  use_case(s, x, y, W, H, label)
for label, x, y in right_uc: use_case(s, x, y, W, H, label)
uc = use_case(s, Inches(5.42), Inches(6.28), Inches(2.35), Inches(0.55),
              "Receive Notifications", fill=TEAL_BG)

actor(s, Inches(1.55), Inches(3.0), "Student", ACCENT)
actor(s, Inches(11.75), Inches(3.0), "Recruiter", GOLD)
link(s, Inches(1.9), Inches(3.95), Inches(3.45), Inches(2.5))
link(s, Inches(1.9), Inches(4.05), Inches(3.45), Inches(3.35))
link(s, Inches(1.9), Inches(4.15), Inches(3.45), Inches(5.05))
link(s, Inches(1.9), Inches(4.25), Inches(3.45), Inches(5.9))
link(s, Inches(1.9), Inches(4.35), Inches(5.42), Inches(6.5))
link(s, Inches(11.4), Inches(3.95), Inches(9.75), Inches(2.5))
link(s, Inches(11.4), Inches(4.05), Inches(9.75), Inches(3.35))
link(s, Inches(11.4), Inches(4.15), Inches(9.75), Inches(4.2))
link(s, Inches(11.4), Inches(4.25), Inches(9.75), Inches(5.05))
link(s, Inches(11.4), Inches(4.35), Inches(7.77), Inches(6.5))

tf = tb(s, Inches(0.62), Inches(6.35), Inches(2.6), Inches(0.7))
para(tf, runs=[("«include»", 10, True, MUTED, MONO)], first=True, sa=2)
para(tf, runs=[("Every protected use case includes authentication.", 9.5, False, MUTED, BODY)],
     sa=0, line_spacing=1.0)

# =============================================================== SLIDE 12 ===
s = content_slide("Section 10", "Normalization Used")
rows = [
    ("1NF", "Atomic values; no repeating groups",
     "Every column holds a single value; each table has a PK (surrogate AUTO_INCREMENT id). "
     "Multi-valued facts became separate rows — e.g. a student's skills live in the "
     "student_skills join table, not a comma list on students."),
    ("2NF", "No partial dependency on part of a key",
     "All tables use single-column surrogate PKs, so partial dependencies cannot exist. "
     "Bridge tables (student_skills, saved_internships) carry only attributes that depend "
     "on the whole pair — proficiency_level, saved_at."),
    ("3NF", "No transitive (non-key → non-key) dependency",
     "Auth data (email, hash, role) lives only in users; student & company details live in "
     "their own profiles. Application status depends only on the application key — "
     "company or student details are referenced by FK, never copied into it."),
    ("BCNF", "Every determinant is a candidate key",
     "users.email and skills.name are UNIQUE alternate keys; all other determinism flows "
     "from the surrogate PKs — no non-key column determines another non-key column."),
]
y = Inches(1.72)
for tag, rule, how in rows:
    card(s, Inches(0.62), y, Inches(12.1), Inches(1.06), fill=CARD)
    n = shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y + Inches(0.26),
              Inches(0.85), Inches(0.52), fill=ACCENT, radius=0.2)
    tfn = n.text_frame; tfn.margin_left = tfn.margin_right = 0
    tfn.margin_top = tfn.margin_bottom = 0
    para(tfn, text=tag, size=15, bold=True, color=PAPER, align=PP_ALIGN.CENTER,
         first=True, sa=0)
    tf = tb(s, Inches(1.85), y + Inches(0.12), Inches(10.7), Inches(0.9))
    para(tf, runs=[(rule, 13, True, INK, BODY)], first=True, sa=2)
    para(tf, runs=[(how, 10.6, False, MUTED, BODY)], sa=0, line_spacing=1.05)
    y = Emu(int(y) + int(Inches(1.2)))

card(s, Inches(0.62), y + Inches(0.04), Inches(12.1), Inches(0.78), fill=GOLD_BG,
     line=RGBColor(0xFD, 0xE6, 0x8A))
tf = tb(s, Inches(0.85), y + Inches(0.16), Inches(11.7), Inches(0.6))
para(tf, runs=[("Deliberate, documented exception:  ", 12, True, GOLD, BODY),
               ("internships.skills_required keeps a free-text skill string to power fast "
                "LIKE-search on listings — while skill tagging stays fully normalized in the "
                "skills / student_skills tables. Search convenience without losing integrity.",
                12, False, MUTED, BODY)], first=True, sa=0, line_spacing=1.1)

# =============================================================== SLIDE 13 ===
s = content_slide("Section 11", "DDL Used — Data Definition")
code_block(s, Inches(0.62), Inches(1.72), Inches(7.15), Inches(5.0), [
    "CREATE DATABASE IF NOT EXISTS internship_portal;",
    "USE internship_portal;",
    "",
    "CREATE TABLE users (",
    "  id            INT AUTO_INCREMENT PRIMARY KEY,",
    "  email         VARCHAR(255) NOT NULL UNIQUE,",
    "  password_hash VARCHAR(255) NOT NULL,",
    "  role          VARCHAR(50) DEFAULT 'student',",
    "  is_active     BOOLEAN     DEFAULT TRUE,",
    "  created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,",
    "  INDEX idx_users_email (email)",
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;",
    "",
    "CREATE TABLE applications (",
    "  id            INT AUTO_INCREMENT PRIMARY KEY,",
    "  student_id    INT NOT NULL,",
    "  internship_id INT NOT NULL,",
    "  status        VARCHAR(50) DEFAULT 'Applied',",
    "  applied_at    DATETIME DEFAULT CURRENT_TIMESTAMP,",
    "  FOREIGN KEY (student_id)",
    "      REFERENCES students(id) ON DELETE CASCADE,",
    "  FOREIGN KEY (internship_id)",
    "      REFERENCES internships(id) ON DELETE CASCADE",
    ") ENGINE=InnoDB;",
], size=10.6)

heading(s, Inches(8.05), Inches(1.72), "Constructs used across the 12 tables", size=14, w=Inches(4.6))
items = [
    ("CREATE DATABASE / TABLE", "database + 12 tables defined once, idempotent IF NOT EXISTS"),
    ("PRIMARY KEY", "surrogate AUTO_INCREMENT id in every table"),
    ("UNIQUE", "users.email, skills.name, and user_id in students / recruiter_profiles (enforces 1:1)"),
    ("NOT NULL + DEFAULT", "mandatory fields; sensible defaults ('Applied', TRUE, ₹, CURRENT_TIMESTAMP)"),
    ("FOREIGN KEY … ON DELETE", "CASCADE cleanup of dependent rows; SET NULL for interviews.internship_id"),
    ("INDEX", "secondary indexes on email, names, title/company/location and every FK"),
    ("ENGINE=InnoDB + utf8mb4", "transactional storage; full Unicode"),
    ("ON UPDATE CURRENT_TIMESTAMP", "updated_at audit column refreshes automatically"),
]
y = Inches(2.14)
for t, d in items:
    shape(s, MSO_SHAPE.RECTANGLE, Inches(8.05), y + Inches(0.03), Inches(0.05),
          Inches(0.5), fill=TEAL)
    tf = tb(s, Inches(8.25), y, Inches(4.45), Inches(0.62))
    para(tf, runs=[(t, 11, True, INK, MONO)], first=True, sa=1)
    para(tf, runs=[(d, 9.8, False, MUTED, BODY)], sa=0, line_spacing=1.0)
    y = Emu(int(y) + int(Inches(0.585)))

# =============================================================== SLIDE 14 ===
s = content_slide("Section 12", "DML Used — Data Manipulation")
blocks = [
    ("INSERT — Create", TEAL, TEAL_BG, Inches(0.62), Inches(1.72),
     ["-- POST /api/auth/register",
      "INSERT INTO users (email, password_hash, role)",
      "VALUES ('ravi@demo.com', 'sha256$ab12…', 'student');",
      "",
      "INSERT INTO applications (student_id,",
      "    internship_id, cover_letter)",
      "VALUES (7, 3, 'I am passionate about…');"]),
    ("SELECT — Read", ACCENT, ACCENT_BG, Inches(6.9), Inches(1.72),
     ["-- GET /api/internships?mode=Remote&min_stipend=20000",
      "SELECT title, company_name, stipend_amount, deadline",
      "FROM internships",
      "WHERE is_active = TRUE AND mode = 'Remote'",
      "  AND stipend_amount >= 20000",
      "  AND (title LIKE '%data%' OR skills_required",
      "       LIKE '%data%')",
      "ORDER BY created_at DESC LIMIT 20 OFFSET 0;"]),
    ("UPDATE — Modify", GOLD, GOLD_BG, Inches(0.62), Inches(4.28),
     ["-- PUT /api/recruiter/applications/42/status",
      "UPDATE applications SET status = 'Shortlisted'",
      "WHERE id = 42;",
      "",
      "-- PUT /api/students/profile",
      "UPDATE students SET cgpa = 8.9, location = 'Bengaluru'",
      "WHERE user_id = 15;"]),
    ("DELETE — Remove", ROSE, ROSE_BG, Inches(6.9), Inches(4.28),
     ["-- DELETE /api/applications/42  (student withdraws)",
      "DELETE FROM applications WHERE id = 42;",
      "",
      "-- DELETE /api/recruiter/internships/5",
      "DELETE FROM internships WHERE id = 5;",
      "-- FKs auto-clean applications, saved rows &",
      "-- interviews (CASCADE / SET NULL)"]),
]
for title, c, cbg, x, y, lines in blocks:
    card(s, x, y, Inches(5.8), Inches(2.4), fill=CARD)
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.18), y + Inches(0.14),
          Inches(2.6), Inches(0.36), fill=cbg, radius=0.3)
    tfh = tb(s, x + Inches(0.18), y + Inches(0.14), Inches(2.6), Inches(0.36),
             anchor=MSO_ANCHOR.MIDDLE)
    para(tfh, text=title, size=11.5, bold=True, color=c, align=PP_ALIGN.CENTER,
         first=True, sa=0)
    code_block(s, x + Inches(0.14), y + Inches(0.6), Inches(5.52), Inches(1.68),
               lines, size=9.6, fill=PAPER)

# =============================================================== SLIDE 15 ===
s = content_slide("Section 13", "Relational Algebra Expressions Used")
ops = "σ  selection      π  projection      ⋈  join      −  difference      ∪  union      G  grouping / aggregation"
tf = tb(s, Inches(0.62), Inches(1.62), Inches(12.1), Inches(0.3))
para(tf, text=ops, size=12.5, bold=True, color=TEAL, font=MATH, first=True, sa=0)

exprs = [
    ("Selection σ — filtered listings",
     "σ mode='Remote' ∧ stipend_amount ≥ 20000 ∧ is_active ( INTERNSHIPS )",
     "GET /api/internships?mode=Remote&min_stipend=20000 — filters compose with AND at query time"),
    ("Projection π — listing columns",
     "π title, company_name, stipend_amount, deadline ( INTERNSHIPS )",
     "Only the needed attributes are returned — mirrors the API response schema"),
    ("Join ⋈ — recruiter applicant view",
     "π full_name, title, company_name, status ( STUDENTS ⋈ APPLICATIONS ⋈ INTERNSHIPS )",
     "GET /api/recruiter/applicants — three-table natural join over the FKs"),
    ("Difference − — saved but not applied",
     "π internship_id (σ student_id=s (SAVED_INTERNSHIPS))  −  π internship_id (σ student_id=s (APPLICATIONS))",
     "Powers the 'Saved' tab minus already-applied roles for student s"),
    ("Aggregation G — dashboard stats",
     "internship_id  G  count(*) ( APPLICATIONS )        ℱ  AVG stipend_amount ( INTERNSHIPS )",
     "GET /api/recruiter/stats — applicants per role; average stipend across listings"),
]
y = Inches(2.06)
for title, expr, note in exprs:
    card(s, Inches(0.62), y, Inches(12.1), Inches(0.86), fill=CARD)
    shape(s, MSO_SHAPE.RECTANGLE, Inches(0.62), y, Inches(0.06), Inches(0.86), fill=ACCENT)
    tf = tb(s, Inches(0.88), y + Inches(0.1), Inches(11.6), Inches(0.7))
    para(tf, runs=[(title, 11.5, True, INK, BODY)], first=True, sa=2)
    para(tf, runs=[(expr, 12, True, ACCENT_DK, MATH)], sa=2)
    para(tf, runs=[(note, 10, False, MUTED, BODY)], sa=0)
    y = Emu(int(y) + int(Inches(1.0)))

# =============================================================== SLIDE 16 ===
s = content_slide("Section 14", "CRUD Operations Used")
tbl_shape = s.shapes.add_table(10, 4, Inches(0.62), Inches(1.72), Inches(12.1), Inches(5.0))
tbl = tbl_shape.table
tbl.columns[0].width = Inches(1.3)
tbl.columns[1].width = Inches(4.5)
tbl.columns[2].width = Inches(3.6)
tbl.columns[3].width = Inches(2.7)
head = ["Operation", "REST Endpoint", "SQL Statement", "Where in the UI"]
crud_rows = [
    ("CREATE", "POST /api/auth/register", "INSERT INTO users + students", "Sign-up modal", TEAL),
    ("CREATE", "POST /api/applications", "INSERT INTO applications", "Apply on internship card", TEAL),
    ("CREATE", "POST /api/recruiter/internships", "INSERT INTO internships", "Recruiter 'Post Internship'", TEAL),
    ("READ", "GET /api/internships?search&mode&min_stipend…", "SELECT … WHERE/LIKE/ORDER/LIMIT", "Browse & search page", ACCENT),
    ("READ", "GET /api/recruiter/applicants", "SELECT over 3-table JOIN", "Applicants view", ACCENT),
    ("READ", "GET /api/recruiter/stats", "SELECT COUNT(*) … GROUP BY", "Recruiter dashboard", ACCENT),
    ("UPDATE", "PUT /api/recruiter/applications/{id}/status", "UPDATE applications SET status …", "Applicant status buttons", GOLD),
    ("UPDATE", "PUT /api/recruiter/internships/{id}/toggle", "UPDATE internships SET is_active", "Manage listings", GOLD),
    ("DELETE", "DELETE /api/applications/{id}", "DELETE FROM applications", "Withdraw application", ROSE),
]
for j, h in enumerate(head):
    cell = tbl.cell(0, j)
    cell.fill.solid(); cell.fill.fore_color.rgb = INK
    cell.margin_left = Inches(0.1); cell.margin_top = Inches(0.03); cell.margin_bottom = Inches(0.03)
    tf = cell.text_frame; tf.word_wrap = True
    para(tf, text=h, size=12.5, bold=True, color=PAPER, first=True, sa=0)
for i, (op, ep, sql, ui, c) in enumerate(crud_rows, start=1):
    tbl.rows[i].height = Inches(0.5)
    vals = [op, ep, sql, ui]
    for j, v in enumerate(vals):
        cell = tbl.cell(i, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = PAPER if i % 2 else CARD
        cell.margin_left = Inches(0.1); cell.margin_top = Inches(0.02)
        cell.margin_bottom = Inches(0.02); cell.margin_right = Inches(0.06)
        tf = cell.text_frame; tf.word_wrap = True
        if j == 0:
            para(tf, text=v, size=11, bold=True, color=c, first=True, sa=0)
        elif j == 1:
            para(tf, text=v, size=10.3, bold=False, color=INK, font=MONO, first=True, sa=0)
        else:
            para(tf, text=v, size=10.3, color=MUTED,
                 font=MONO if j == 2 else BODY, first=True, sa=0)
tbl.rows[0].height = Inches(0.42)

# =============================================================== SLIDE 17 ===
s = content_slide("Section 15", "Autonomous Triggers — Automated System Actions")
trigs = [
    ("TRIGGER 1", "Student submits an application", TEAL,
     ["INSERT INTO applications …", "→  system instantly INSERTs a notification row:",
      "“Application Submitted — your application for '{title}' at {company} was successful.”",
      "Both rows commit in one transaction (atomic)."]),
    ("TRIGGER 2", "Recruiter changes application status", ACCENT,
     ["UPDATE applications SET status = 'Shortlisted' …", "→  student is automatically notified:",
      "“Application Status Updated: Shortlisted” — no manual email needed"]),
    ("TRIGGER 3", "Interview is scheduled", GOLD,
     ["INSERT INTO interviews …", "→  application status auto-advances:",
      "UPDATE applications SET status = 'Interview Scheduled'",
      "→  + notification with date, time & meeting link"]),
    ("TRIGGER 4", "Row deleted (DB-level, declarative)", ROSE,
     ["DELETE FROM internships / users …", "→  ON DELETE CASCADE wipes dependent applications,",
      "saved rows & child interviews automatically;",
      "interviews.internship_id uses ON DELETE SET NULL"]),
    ("TRIGGER 5", "Any profile row updated (DB-level)", GREEN,
     ["UPDATE students / recruiter_profiles …", "→  ON UPDATE CURRENT_TIMESTAMP refreshes updated_at",
      "— an automatic audit trail with zero application code"]),
]
y = Inches(1.72)
for tag, event, c, effects in trigs:
    card(s, Inches(0.62), y, Inches(12.1), Inches(0.94), fill=CARD)
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.78), y + Inches(0.24),
          Inches(1.05), Inches(0.44), fill=c, radius=0.25)
    tfh = tb(s, Inches(0.78), y + Inches(0.24), Inches(1.05), Inches(0.44),
             anchor=MSO_ANCHOR.MIDDLE)
    para(tfh, text=tag, size=10.5, bold=True, color=PAPER, align=PP_ALIGN.CENTER,
         first=True, sa=0)
    tf = tb(s, Inches(2.0), y + Inches(0.1), Inches(5.0), Inches(0.8),
            anchor=MSO_ANCHOR.MIDDLE)
    para(tf, text="EVENT", size=9, bold=True, color=FAINT, first=True, sa=1)
    para(tf, text=event, size=12, bold=True, color=INK, sa=0, line_spacing=1.0)
    tf = tb(s, Inches(7.15), y + Inches(0.08), Inches(5.4), Inches(0.82))
    para(tf, text="AUTOMATED ACTION", size=9, bold=True, color=FAINT, first=True, sa=1)
    line = effects[0] + "   " + " ".join(effects[1:]) if len(effects) > 1 else effects[0]
    for k, eff in enumerate(effects):
        para(tf, text=eff, size=8.9, color=MUTED, font=MONO if k == 0 else BODY,
             sa=0.5, line_spacing=1.0)
    y = Emu(int(y) + int(Inches(1.06)))

# =============================================================== SLIDE 18 ===
s = content_slide("Section 16", "Atomicity & ACID Transactions")
card(s, Inches(0.62), Inches(1.72), Inches(7.2), Inches(2.6), fill=ACCENT_BG,
     line=RGBColor(0xC7, 0xD2, 0xFE))
tf = tb(s, Inches(0.88), Inches(1.9), Inches(6.7), Inches(2.3))
para(tf, text="What atomicity guarantees here", size=15, bold=True, color=ACCENT_DK,
     first=True, sa=6)
para(tf, runs=[("When a student applies, ", 13, False, INK, BODY),
               ("two tables must change", 13, True, INK, BODY),
               (" — a row in applications AND a confirmation row in notifications. "
                "They are staged in one SQLAlchemy session and committed with a single "
                "db.commit(). If any part fails, the session rolls back and ", 13, False, INK, BODY),
               ("neither row is written", 13, True, INK, BODY),
               (" — the database never shows an application without its notification, "
                "or vice-versa.", 13, False, INK, BODY)], sa=0, line_spacing=1.2)

code_block(s, Inches(0.62), Inches(4.5), Inches(7.2), Inches(2.25), [
    "# applications.py — one atomic transaction",
    "db.add(new_app)            # stage INSERT into applications",
    "db.add(Notification(       # stage INSERT into notifications",
    "    user_id=current_user.id,",
    "    title=\"Application Submitted\",",
    "    message=f\"… '{internship.title}' at {internship.company_name} …\"))",
    "db.commit()                # BOTH rows persist — or NEITHER does",
], size=10.8)

acid = [
    ("A — Atomicity", "All-or-nothing commits; failed multi-table writes roll back entirely", TEAL),
    ("C — Consistency", "PK/FK/UNIQUE constraints + Pydantic validation keep data valid in every state", ACCENT),
    ("I — Isolation", "InnoDB MVCC & row locks — concurrent students can apply simultaneously without conflicts", GOLD),
    ("D — Durability", "Once commit() returns, InnoDB redo logging survives crashes — no accepted application is lost", GREEN),
]
y = Inches(1.72)
for t, d, c in acid:
    card(s, Inches(8.1), y, Inches(4.6), Inches(1.16), fill=CARD)
    shape(s, MSO_SHAPE.RECTANGLE, Inches(8.1), y, Inches(0.07), Inches(1.16), fill=c)
    tf = tb(s, Inches(8.38), y + Inches(0.14), Inches(4.15), Inches(0.95))
    para(tf, text=t, size=13.5, bold=True, color=c, first=True, sa=3)
    para(tf, text=d, size=10.8, color=MUTED, sa=0, line_spacing=1.08)
    y = Emu(int(y) + int(Inches(1.32)))

# =============================================================== SLIDE 19 ===
s = content_slide("Section 17", "Key Features")
feat = [
    ("Student Module", TEAL, TEAL_BG, [
        "Keyword search across title, company, description & skills",
        "Filters: location, mode, min stipend, duration, skills",
        "Sorting (newest / stipend / deadline) + pagination",
        "One-click apply with cover letter & attached resume",
        "Saved-internships bookmarking with a dedicated tab",
        "Live application tracker with status timeline",
        "Profile: university, CGPA, portfolio, GitHub, LinkedIn",
        "Document vault — resumes stored & served from the DB",
    ]),
    ("Recruiter Module", ACCENT, ACCENT_BG, [
        "Post, edit, pause/unpause and delete internships",
        "Consolidated applicant list via 3-table join",
        "Status pipeline: Under Review → Shortlisted → Accepted/Rejected",
        "Interview scheduler with type, duration & meeting link",
        "Dashboard stats: posts, applications, interviews, offers",
        "Company profile: logo, industry, size, website, LinkedIn",
    ]),
    ("System-Wide", GOLD, GOLD_BG, [
        "Skill-based internship recommendations for students",
        "Automatic notifications on every lifecycle event",
        "JWT auth with role-based access on protected routes",
        "Splash → role-aware dashboards (student / recruiter)",
        "Dark / light theme via ThemeContext",
        "Demo data seeded on first startup for instant walkthrough",
    ]),
]
x = Inches(0.62)
for title, c, cbg, pts in feat:
    card(s, x, Inches(1.72), Inches(3.98), Inches(5.0), fill=CARD)
    shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.2), Inches(1.94),
          Inches(3.58), Inches(0.46), fill=cbg, radius=0.25)
    tfh = tb(s, x + Inches(0.2), Inches(1.94), Inches(3.58), Inches(0.46),
             anchor=MSO_ANCHOR.MIDDLE)
    para(tfh, text=title, size=14, bold=True, color=c, align=PP_ALIGN.CENTER,
         first=True, sa=0)
    tf = tb(s, x + Inches(0.24), Inches(2.56), Inches(3.5), Inches(4.0))
    bullets(tf, [(0, p) for p in pts], size=11, gap=7, bullet_color=c)
    x = Emu(int(x) + int(Inches(4.08)))

# =============================================================== SLIDE 20 ===
s = content_slide("Section 18", "Application Lifecycle — Status State Machine")
stages = [
    ("Applied", "student submits application + resume", TEAL),
    ("Under Review", "recruiter opens the applicant view", RGBColor(0x03, 0x69, 0x9E)),
    ("Shortlisted", "recruiter marks candidate as promising", GOLD),
    ("Interview Scheduled", "interview booked — status auto-updates", ACCENT),
    ("Accepted / Rejected", "final decision; student notified", ROSE),
]
x = Inches(0.62)
for i, (name, desc, c) in enumerate(stages):
    ch = shape(s, MSO_SHAPE.CHEVRON, x, Inches(2.35), Inches(2.62), Inches(1.05), fill=c)
    tf = ch.text_frame; tf.word_wrap = True
    tf.margin_left = Inches(0.18); tf.margin_right = Inches(0.05)
    para(tf, text=name, size=12.5, bold=True, color=PAPER, align=PP_ALIGN.CENTER,
         first=True, sa=0, line_spacing=0.95)
    tfd = tb(s, x + Inches(0.18), Inches(3.55), Inches(2.45), Inches(0.75))
    para(tfd, text=desc, size=10.5, color=MUTED, align=PP_ALIGN.CENTER, first=True,
         sa=0, line_spacing=1.05)
    x = Emu(int(x) + int(Inches(2.52)))

card(s, Inches(0.62), Inches(4.55), Inches(12.1), Inches(1.0), fill=TEAL_BG,
     line=RGBColor(0x99, 0xF6, 0xE4))
tf = tb(s, Inches(0.88), Inches(4.7), Inches(11.6), Inches(0.75))
para(tf, runs=[("Every transition is event-driven:  ", 13, True, TEAL, BODY),
               ("each status change fires an automatic notification to the student, and "
                "scheduling an interview advances the state machine by itself — the recruiter "
                "never updates two places.", 13, False, MUTED, BODY)],
     first=True, sa=0, line_spacing=1.15)

tf = tb(s, Inches(0.62), Inches(5.85), Inches(12.1), Inches(1.0))
bullets(tf, [
    (0, "Guarded transitions — ", "status changes are only accepted from the recruiter who owns the posting"),
    (0, "Auditable history — ", "applied_at, updated_at and notification rows timestamp every step"),
    (0, "No dead ends — ", "students withdraw cleanly (DELETE), which cascades away pending interviews"),
], size=12.5, gap=7)

# =============================================================== SLIDE 21 ===
s = content_slide("Section 19", "Security & Validation")
sec = [
    ("Authentication", ACCENT, [
        "JWT bearer tokens signed with a server secret (python-jose)",
        "Token expiry built into every issued credential",
        "Passwords stored only as salted-format SHA-256 hashes",
        "Login / register return short-lived access tokens",
    ]),
    ("Authorization", TEAL, [
        "Role field on every user: student | recruiter",
        "FastAPI dependency guards protect each router",
        "Students reach student endpoints only; recruiters theirs",
        "Ownership checks — recruiters edit only their own posts & applicants",
    ]),
    ("Validation", GOLD, [
        "Pydantic schemas validate shape & types of every request",
        "email-validator rejects malformed addresses at signup",
        "Multipart uploads capped (8 MB) & stored as base64 in MEDIUMTEXT",
        "Invalid payloads fail fast with 422 — never reach SQL",
    ]),
    ("Transport & Config", GREEN, [
        "CORS middleware controls browser access to the API",
        "Credentials & secrets via environment settings",
        "Parameterized ORM queries — no string-built SQL, no injection",
        "Inactive accounts can be disabled via is_active flag",
    ]),
]
x = Inches(0.62)
for title, c, pts in sec:
    card(s, x, Inches(1.72), Inches(2.98), Inches(4.6), fill=CARD)
    shape(s, MSO_SHAPE.RECTANGLE, x, Inches(1.72), Inches(2.98), Inches(0.06), fill=c)
    tf = tb(s, x + Inches(0.2), Inches(1.94), Inches(2.6), Inches(0.35))
    para(tf, text=title, size=14.5, bold=True, color=c, first=True, sa=0)
    tf = tb(s, x + Inches(0.2), Inches(2.42), Inches(2.62), Inches(3.8))
    bullets(tf, [(0, p) for p in pts], size=10.6, gap=9, bullet_color=c)
    x = Emu(int(x) + int(Inches(3.14)))

tf = tb(s, Inches(0.62), Inches(6.5), Inches(12.1), Inches(0.5))
para(tf, runs=[("Defense in depth:  ", 12.5, True, INK, BODY),
               ("UI guards  →  JWT verification  →  role & ownership checks  →  schema "
                "validation  →  parameterized SQL  →  DB constraints.", 12.5, False, MUTED, BODY)],
     first=True, sa=0)

# =============================================================== SLIDE 22 ===
s = content_slide("Section 20", "Future Enhancements")
future = [
    ("Resume parsing & auto-tagging", "Extract skills from uploaded resumes to auto-fill student_skills — making the M:N skill graph zero-effort", "1"),
    ("Matching & ranking engine", "Score students against postings using skill overlap, stipend & mode preferences (a real σ/⋈ workload)", "2"),
    ("Real-time in-app messaging", "The messages table is already modeled with sender/receiver FKs — surface it with WebSocket chat", "3"),
    ("Email & SMS delivery", "Mirror in-app notifications to email/SMS for deadlines and interview reminders", "4"),
    ("Company verification badges", "Verified-employer workflow to build student trust in postings", "5"),
    ("Analytics dashboards", "Funnel metrics per posting: views → applies → interviews → offers, over time", "6"),
    ("Containerized deployment", "Docker Compose for one-command spin-up of MySQL + API + frontend", "7"),
    ("Accessibility & i18n", "WCAG-audited flows and multi-language UI for wider reach", "8"),
]
y = Inches(1.72)
for i, (t, d, n) in enumerate(future):
    x = Inches(0.62) if i % 2 == 0 else Inches(6.78)
    card(s, x, y, Inches(5.94), Inches(1.2), fill=CARD)
    nn = shape(s, MSO_SHAPE.OVAL, x + Inches(0.16), y + Inches(0.33), Inches(0.52), Inches(0.52),
               fill=TEAL)
    tfn = nn.text_frame; tfn.margin_left = tfn.margin_right = 0
    tfn.margin_top = tfn.margin_bottom = 0
    para(tfn, text=n, size=15, bold=True, color=PAPER, align=PP_ALIGN.CENTER,
         first=True, sa=0)
    tf = tb(s, x + Inches(0.85), y + Inches(0.14), Inches(4.95), Inches(1.0))
    para(tf, text=t, size=13, bold=True, color=INK, first=True, sa=2)
    para(tf, text=d, size=10.5, color=MUTED, sa=0, line_spacing=1.05)
    if i % 2 == 1:
        y = Emu(int(y) + int(Inches(1.34)))

# =============================================================== SLIDE 23 ===
s = content_slide("Section 21", "Conclusion")
concl_left = [
    ("A complete, working system", "Discovery → application → screening → interview → decision, running end-to-end on one normalized MySQL schema with 12 tables"),
    ("DBMS theory made tangible", "Normalization to BCNF, keys & constraints, DDL/DML, relational algebra, triggers and ACID transactions are all visible product features"),
    ("Production-grade practices", "Layered architecture, ORM-based parameterized SQL, JWT security, auto-generated API docs, seeded demo data"),
]
y = Inches(1.72)
for t, d in concl_left:
    card(s, Inches(0.62), y, Inches(7.2), Inches(1.5), fill=CARD)
    shape(s, MSO_SHAPE.RECTANGLE, Inches(0.62), y, Inches(0.07), Inches(1.5), fill=ACCENT)
    tf = tb(s, Inches(0.95), y + Inches(0.16), Inches(6.7), Inches(1.25))
    para(tf, text=t, size=14.5, bold=True, color=INK, first=True, sa=3)
    para(tf, text=d, size=12, color=MUTED, sa=0, line_spacing=1.15)
    y = Emu(int(y) + int(Inches(1.66)))

card(s, Inches(8.1), Inches(1.72), Inches(4.6), Inches(4.98), fill=INK, line=INK)
tf = tb(s, Inches(8.4), Inches(1.95), Inches(4.0), Inches(4.6))
para(tf, text="By the numbers", size=14.5, bold=True, color=PAPER, first=True, sa=10)
metrics = [
    ("12", "normalized tables (BCNF)"),
    ("25+", "REST endpoints across 6 routers"),
    ("15", "foreign-key relationships"),
    ("5", "autonomous triggers / automations"),
    ("20+", "secondary indexes for fast queries"),
    ("2", "roles with dedicated dashboards"),
]
for num, lab in metrics:
    para(tf, runs=[(num + "   ", 17, True, RGBColor(0xA5, 0xB4, 0xFC), BODY),
                   (lab, 12, False, RGBColor(0xCB, 0xD5, 0xE1), BODY)], sa=9)

tf = tb(s, Inches(0.62), Inches(6.85), Inches(12.1), Inches(0.4))
para(tf, runs=[("Learning outcome:  ", 12.5, True, TEAL, BODY),
               ("designing schema first — keys, constraints and normal forms — made every "
                "layer above it (API, triggers, UI) simpler, safer and faster to build.",
                12.5, False, MUTED, BODY)], first=True, sa=0)

# =============================================================== SLIDE 24 ===
s = slide_new(bg=INK)
shape(s, MSO_SHAPE.OVAL, Inches(9.6), Inches(-2.3), Inches(7.0), Inches(7.0), fill=INK_SOFT)
shape(s, MSO_SHAPE.OVAL, Inches(10.8), Inches(-1.1), Inches(4.7), Inches(4.7), fill=ACCENT_DK)
shape(s, MSO_SHAPE.OVAL, Inches(-1.8), Inches(5.4), Inches(4.8), Inches(4.8), fill=INK_SOFT)
shape(s, MSO_SHAPE.OVAL, Inches(-0.7), Inches(6.5), Inches(2.4), Inches(2.4), fill=TEAL)

tf = tb(s, Inches(0.9), Inches(2.3), Inches(11.5), Inches(1.6))
para(tf, text="Thank You", size=60, bold=True, color=PAPER, first=True, sa=4)
para(tf, text="Questions & Discussion", size=22, color=RGBColor(0xC7, 0xD2, 0xFE), sa=0)

shape(s, MSO_SHAPE.RECTANGLE, Inches(0.95), Inches(4.35), Inches(2.6), Inches(0.05), fill=TEAL)

tf = tb(s, Inches(0.9), Inches(4.7), Inches(11.5), Inches(0.8))
para(tf, runs=[("HireHub — Internship Portal", 15, True, PAPER, BODY),
               ("   •   FastAPI + React + MySQL", 13, False, FAINT, BODY)], first=True, sa=4)
para(tf, runs=[("Presented by Pushpak  •  August 2026", 12, False, FAINT, BODY)], sa=0)

# ------------------------------------------------------------------- save ---
prs.save(OUT)
print(f"Saved {len(prs.slides.__iter__.__self__._sldIdLst)} slides -> {OUT}")
