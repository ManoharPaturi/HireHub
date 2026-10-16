"""Build implementation-derived ER/UML sources and an offline HTML viewer.

Run from any directory with Python 3. Rendering Mermaid sources is a separate
browser step; the final HTML embeds the resulting SVGs and has no network needs.
"""
from pathlib import Path
import ast, hashlib, html, json, re

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
MODEL = ROOT / 'backend/app/db/models.py'

def val(node):
    try: return ast.literal_eval(node)
    except (ValueError,TypeError): return ast.unparse(node)

def extract():
    entities=[]
    for node in ast.parse(MODEL.read_text()).body:
        if not isinstance(node,ast.ClassDef): continue
        table=None; cols=[]
        for n in node.body:
            if not isinstance(n,ast.Assign) or not isinstance(n.targets[0],ast.Name):continue
            name=n.targets[0].id
            if name=='__tablename__': table=val(n.value)
            if not isinstance(n.value,ast.Call) or ast.unparse(n.value.func)!='Column':continue
            kws={k.arg:val(k.value) for k in n.value.keywords}
            typ=ast.unparse(n.value.args[0]).replace(' ','')
            fk=None;delete=None
            for a in n.value.args[1:]:
                if isinstance(a,ast.Call) and ast.unparse(a.func)=='ForeignKey':
                    fk=val(a.args[0]);delete=next((val(k.value) for k in a.keywords if k.arg=='ondelete'),None)
            cols.append(dict(name=name,type=typ,pk=kws.get('primary_key',False),unique=kws.get('unique',False),nullable=kws.get('nullable',not kws.get('primary_key',False)),indexed=kws.get('index',False),fk=fk,ondelete=delete,default=kws.get('default')))
        if table:entities.append(dict(class_name=node.name,table=table,columns=cols))
    return entities

entities=extract();bytable={e['table']:e for e in entities}
relations=[]
for e in entities:
    for c in e['columns']:
        if c['fk']:
            parent=c['fk'].split('.')[0]
            relations.append(dict(parent=parent,child=e['table'],field=c['name'],parent_end='0..1' if c['nullable'] else '1',child_end='0..1' if c['unique'] else '0..*',ondelete=c['ondelete'],identifying=c['pk']))
assert len(entities)==12 and len(relations)==16
schema={'source':'backend/app/db/models.py','sha256':hashlib.sha256(MODEL.read_bytes()).hexdigest(),'entities':entities,'relationships':relations}
(OUT/'schema.json').write_text(json.dumps(schema,indent=2)+'\n')

names={e['table']:e['class_name'] for e in entities}

def er(full):
    lines=['erDiagram','    direction LR']
    for e in entities:
        lines.append('    '+e['table']+' {')
        for c in e['columns']:
            if not full and not(c['pk'] or c['fk']):continue
            typ={'Integer':'INT','String':'VARCHAR','Text':'TEXT','Boolean':'BOOLEAN','Float':'FLOAT','DateTime':'DATETIME','MEDIUMTEXT':'MEDIUMTEXT'}.get(c['type'].split('(')[0],c['type'])
            if '(' in c['type']:typ+='('+c['type'].split('(',1)[1]
            flags=[x for x,b in [('PK',c['pk']),('FK',bool(c['fk'])),('UK',c['unique'])] if b]
            label='NULL allowed' if c['nullable'] else 'NOT NULL'
            lines.append(f'        {typ} {c["name"]}'+(' '+', '.join(flags) if flags else '')+f' "{label}"')
        lines.append('    }')
    for r in relations:
        left='|o' if r['parent_end']=='0..1' else '||'
        right='o|' if r['child_end']=='0..1' else 'o{'
        # Separate surrogate primary keys mean these are non-identifying FKs.
        lines.append(f'    {r["parent"]} {left}..{right} {r["child"]} : "{r["field"]}"')
    return '\n'.join(lines)

classlines=['classDiagram','    direction LR']
selected={'users':['id','email','role','is_active'],'students':['id','user_id','full_name','university'],'recruiter_profiles':['id','user_id','full_name','company_name'],'internships':['id','recruiter_id','title','skills_required'],'applications':['id','student_id','internship_id','status'],'interviews':['id','recruiter_id','application_id','internship_id','scheduled_at'],'documents':['id','student_id','file_name','file_data'],'skills':['id','name'],'student_skills':['id','student_id','skill_id','proficiency_level'],'saved_internships':['id','student_id','internship_id'],'notifications':['id','user_id','is_read'],'messages':['id','sender_id','receiver_id','content']}
for e in entities:
    classlines.append(f'    class {e["class_name"]} {{')
    for c in e['columns']:
        if c['name'] in selected[e['table']]:
            # Do not invent public methods; routes live in modules, not these classes.
            classlines.append('        '+c['name']+' : '+c['type'].split('(')[0])
    classlines.append('    }')
for r in relations:
    classlines.append(f'    {names[r["parent"]]} "{r["parent_end"]}" -- "{r["child_end"]}" {names[r["child"]]} : {r["field"].removesuffix("_id")}')

applyseq='''sequenceDiagram
    autonumber
    actor S as Student
    participant UI as React student UI
    participant API as FastAPI applications route
    participant DB as MySQL via SQLAlchemy
    S->>UI: Submit application with optional resume
    UI->>API: POST /api/applications (bearer token, multipart)
    API->>DB: Load account by token subject
    DB-->>API: Account identity
    API->>API: Check active-account flag
    API->>DB: Find student, internship, existing application
    DB-->>API: Related records and duplicate result
    alt Missing profile or internship
        API-->>UI: 404 response
    else Application already exists
        API-->>UI: 400 response
    else New application
        opt Resume supplied
            API->>API: Read resume bytes
            break Abort request if size exceeds 8 MiB
                API-->>UI: 413 response before writes
            end
            opt Non-empty file
                API->>API: Encode data URI and queue Document
            end
        end
        API->>DB: INSERT Application (+ optional Document); COMMIT 1
        DB-->>API: Application ID; refreshed record
        API->>DB: INSERT student alert (+ recruiter alert if linked); COMMIT 2
        DB-->>API: Alerts persisted
        API-->>UI: Application response with related internship
        UI-->>S: Confirmation; refresh listing/dashboard data
    end
    Note over API,DB: Application and alerts<br/>use separate commits.<br/>COMMIT 1 survives a later<br/>alert failure.<br/>Duplicate checks are not<br/>a UNIQUE constraint.
'''
interviewseq='''sequenceDiagram
    autonumber
    actor R as Recruiter
    participant UI as ApplicantsView
    participant API as FastAPI recruiter route
    participant DB as MySQL via SQLAlchemy
    R->>UI: Select candidate; enter interview details
    UI->>API: POST /api/recruiter/interviews
    API->>DB: Load active account and recruiter profile
    DB-->>API: Recruiter identity
    Note over API,DB: Recruiter role is checked.<br/>Candidate ownership<br/>is not checked here.
    API->>DB: INSERT Interview; COMMIT 1; refresh
    DB-->>API: Saved interview
    API->>DB: Find Application by submitted application_id
    DB-->>API: Application record
    opt Referenced application found
        API->>API: Set status to Interview Scheduled
        API->>API: Queue student notification if student is linked
        API->>DB: UPDATE Application (+ notification); COMMIT 2
        DB-->>API: Changes persisted
    end
    API-->>UI: Interview response with display names
    UI->>API: Reload recruiter workspace datasets
    API-->>UI: Updated applicants, interviews and totals
    UI-->>R: Updated applicant list and interview schedule
    Note over API,DB: Two separate commits.<br/>Foreign keys validate IDs,<br/>not recruiter ownership.
'''

# Mermaid treats semicolons as statement delimiters in sequence messages.
applyseq = applyseq.replace(";", ",")
interviewseq = interviewseq.replace(";", ",")

catalog=[
 dict(id='er-overview',kind='ER',title='Relational overview',subtitle='All 12 tables and all 16 foreign keys, with identity fields only.',source='er-overview.mmd',code=er(False),sources=['backend/app/db/models.py'],notes=['Crow\'s-foot markers show cardinalities at both ends. Dashed links are non-identifying: every child table has its own surrogate primary key.','A user may have zero or one student profile and zero or one recruiter profile. Role exclusivity is application logic, not a database inheritance relationship.','The two messages-to-users links are distinct: sender_id and receiver_id.']),
 dict(id='er-full',kind='ER',title='Full physical schema',subtitle='Every mapped field, SQL type, key and declared nullability.',source='er-full.mmd',code=er(True),sources=['backend/app/db/models.py'],notes=['NULL labels follow the ORM model literally. A default value does not imply NOT NULL.','Only recruiter_id on internships and internship_id on interviews are nullable foreign keys.','student_skills, applications and saved_internships have surrogate IDs but no composite pair-uniqueness constraints.','documents belongs to students; there is no documents-to-applications foreign key. Application resume content is stored separately in applications.resume_url.']),
 dict(id='uml-class',kind='UML class',title='Domain class associations',subtitle='The 12 ORM entities, selected declared attributes and exact association multiplicities.',source='uml-class.mmd',code='\n'.join(classlines),sources=['backend/app/db/models.py'],notes=['Solid lines are UML associations. No inheritance or composition is claimed.','Selected attributes are shown for readability. Endpoint functions are not invented as entity methods.','Student and RecruiterProfile associate with User. They do not inherit from User in the implementation.']),
 dict(id='uml-use-case',kind='UML use case',title='Actors and system responsibilities',subtitle='Student, recruiter and administrator goals inside the HireHub system boundary.',source='uml-use-case.json',code=None,sources=['backend/app/routers/auth.py','backend/app/routers/students.py','backend/app/routers/internships.py','backend/app/routers/applications.py','backend/app/routers/recruiter.py','backend/app/routers/admin.py','backend/app/routers/messages.py','backend/app/routers/notifications.py'],notes=['Actors remain outside the system boundary. Ellipses represent user goals; unarrowed solid lines show participation.','Authenticated access is a precondition for protected goals, not an include arrow to a login screen.','Messaging requires an existing application connection. Shared goal names appear for each participating role to keep the view readable.','Admin self-registration, email delivery, a calendar grid and machine-learned matching are not shown as implemented capabilities.']),
 dict(id='uml-sequence-apply',kind='UML sequence',title='Submit an application',subtitle='Internal application request, optional resume, rejection paths and both commits.',source='uml-sequence-apply.mmd',code=applyseq,sources=['frontend/src/components/Student/StudentApp.tsx','frontend/src/services/api.ts','backend/app/routers/auth.py','backend/app/routers/applications.py'],notes=['Solid arrows are requests/calls; dashed arrows are replies. opt and alt frames show conditional behavior.','Authentication/token rejection and database exceptions can terminate processing; the diagram details business validation branches after successful authentication.','COMMIT 1 saves the application and optional document. COMMIT 2 saves alerts. These boundaries intentionally match the current code.']),
 dict(id='uml-sequence-interview',kind='UML sequence',title='Schedule an interview',subtitle='Recruiter scheduling with the current authorization and transaction behavior.',source='uml-sequence-interview.mmd',code=interviewseq,sources=['frontend/src/components/Recruiter/ApplicantsView.tsx','frontend/src/components/Recruiter/RecruiterApp.tsx','backend/app/routers/recruiter.py'],notes=['Successful authentication and database writes are assumed; failures return before later steps.','The recruiter role dependency is implemented, but schedule_interview does not verify ownership of the submitted application. The diagram records this gap rather than inventing a check.','Interview persistence precedes the application status/notification commit. The meeting link is supplied data; there is no video-conferencing integration.']),
 dict(id='uml-activity',kind='UML activity',title='Application submission activity',subtitle='Guarded branches for internal/external roles and the internal API processing path.',source='uml-activity.json',code=None,sources=['frontend/src/components/Internships/InternshipDetailModal.tsx','backend/app/routers/applications.py'],notes=['Filled circle: initial node. Bullseye: activity final. Rounded rectangles: actions. Diamonds: decisions. Every outgoing decision edge has a guard.','External applications redirect to a supplied company link; this branch does not create a local application record.','The internal branch assumes a valid active-account token. A rejected request ends this attempt; a user may start another attempt.','Application validation does not currently enforce active-post or deadline eligibility; no such checks are invented here.'])]
for d in catalog:
    if d['code']:(OUT/'sources'/d['source']).write_text(d['code'].rstrip()+'\n')

# Native SVG generators below use explicit UML symbols instead of flowchart stand-ins.
def escape(x):return html.escape(str(x),quote=True)
def text(x,y,label,size=20,anchor='middle',fill='#182A42',weight='normal'):
    ls=label.split('\n');return ''.join(f'<text x="{x}" y="{y+i*(size+6)}" font-size="{size}" text-anchor="{anchor}" fill="{fill}" font-weight="{weight}">{escape(l)}</text>' for i,l in enumerate(ls))
def svg_start(w,h,title):return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img"><title>{escape(title)}</title><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M1 1 L9 5 L1 9" fill="none" stroke="#526882" stroke-width="1.8"/></marker></defs><rect width="100%" height="100%" fill="white"/><g font-family="Arial, sans-serif" stroke-linecap="round" stroke-linejoin="round">'
def line(points,arrow=False):return f'<polyline points="{points}" fill="none" stroke="#526882" stroke-width="2"'+(' marker-end="url(#arrow)"' if arrow else '')+'/>'
def action(cx,cy,label,w=480,h=70):return f'<rect x="{cx-w/2}" y="{cy-h/2}" width="{w}" height="{h}" rx="15" fill="#F2F5FC" stroke="#334C70" stroke-width="2"/>'+text(cx,cy-(10 if '\n' in label else -7),label,20)
def diamond(cx,cy,label):return f'<path d="M {cx} {cy-55} L {cx+155} {cy} L {cx} {cy+55} L {cx-155} {cy} Z" fill="#F2F5FC" stroke="#334C70" stroke-width="2"/>'+text(cx,cy+6,label,19)

roles=[('Student',[
('Register / sign in','backend/app/routers/auth.py','register'),
('Maintain profile and skills','backend/app/routers/students.py','update_student_profile'),
('Upload / remove documents','backend/app/routers/students.py','upload_document'),
('Discover / save opportunities','backend/app/routers/internships.py','list_internships'),
('Submit / withdraw applications','backend/app/routers/applications.py','submit_application'),
('Track application status','backend/app/routers/applications.py','list_student_applications'),
('Message recruiters / read alerts','backend/app/routers/messages.py','send_message')]),
('Recruiter',[
('Register / sign in','backend/app/routers/auth.py','login'),
('Maintain company profile','backend/app/routers/recruiter.py','update_profile'),
('Manage internship postings','backend/app/routers/recruiter.py','post_internship'),
('Review candidates / resumes','backend/app/routers/recruiter.py','list_applicants'),
('Update candidate status','backend/app/routers/recruiter.py','update_app_status'),
('Schedule / view interviews','backend/app/routers/recruiter.py','schedule_interview'),
('Message applicants / read alerts','backend/app/routers/messages.py','send_message')]),
('Administrator',[
('Sign in to admin console','backend/app/routers/admin.py','admin_login'),
('Manage user accounts','backend/app/routers/admin.py','toggle_user'),
('Manage postings / inspect applications','backend/app/routers/admin.py','list_all_applications'),
('View reports and recent activity','backend/app/routers/admin.py','chart_data')])]
(OUT/'sources/uml-use-case.json').write_text(json.dumps(roles,indent=2)+'\n')
s=svg_start(2520,1050,'HireHub UML use-case diagram: three role views')
for column,(role,cases) in enumerate(roles):
    origin=column*840;ax=origin+90;mid=530
    s+=text(origin+420,48,role+' view',28,weight='bold')
    s+=f'<rect x="{origin+230}" y="90" width="580" height="900" fill="none" stroke="#182A42" stroke-width="2"/>'+text(origin+520,133,'HireHub',24,weight='bold')
    s+=f'<circle cx="{ax}" cy="{mid-52}" r="21" fill="white" stroke="#182A42" stroke-width="2.5"/>'
    s+=line(f'{ax},{mid-31} {ax},{mid+24}')+line(f'{ax-40},{mid-8} {ax+40},{mid-8}')+line(f'{ax},{mid+24} {ax-32},{mid+65}')+line(f'{ax},{mid+24} {ax+32},{mid+65}')+text(ax,mid+100,role,19,weight='bold')
    ys=[210+i*115 for i in range(len(cases))] if len(cases)==7 else [300+i*155 for i in range(len(cases))]
    for cy,(label,_,_) in zip(ys,cases):
        s+=line(f'{ax+40},{mid-8} {origin+270},{cy}')
        if len(label)>34:
            words=label.split();cut=min(range(1,len(words)),key=lambda i:abs(len(' '.join(words[:i]))-len(' '.join(words[i:]))));label=' '.join(words[:cut])+'\n'+' '.join(words[cut:])
        s+=f'<ellipse cx="{origin+520}" cy="{cy}" rx="250" ry="44" fill="#F2F5FC" stroke="#334C70" stroke-width="2"/>'+text(origin+520,cy-8 if '\n' in label else cy+7,label,20)
s+='</g></svg>'
(OUT/'svg/uml-use-case.svg').write_text(s)

# Activity nodes and edge data are kept separately so guard completeness can be audited.
nodes=[('start','initial',650,65,''),('choose','action',650,160,'Open internship details'),('external','decision',650,300,'External role?'),('redirect','action',1250,300,'Confirm redirect; open company link'),('final_external','final',1250,430,''),('form','action',650,450,'Enter cover letter; select optional file'),('submit','action',650,570,'Send internal multipart application'),('exists','decision',650,710,'Records found?'),('duplicate','decision',650,880,'Already applied?'),('file','decision',650,1050,'Resume supplied?'),('size','decision',1250,1050,'Within 8 MiB?'),('encode','action',1250,1220,'Encode non-empty file; queue Document'),('merge','merge',650,1370,''),('commit1','action',650,1500,'Insert Application (+ Document)\nCOMMIT 1'),('commit2','action',650,1630,'Insert participant notifications\nCOMMIT 2'),('response','action',650,1760,'Return saved application; show confirmation'),('final_ok','final',650,1870,''),('error404','action',1250,710,'Return 404: missing student or posting'),('final404','final',1580,710,''),('error400','action',1250,880,'Return 400: duplicate application'),('final400','final',1580,880,''),('error413','action',1740,1050,'Return 413: oversized file'),('final413','final',1740,1220,'')]
edges=[('start','choose',None,'650,78 650,125'),('choose','external',None,'650,195 650,245'),('external','redirect','external','805,300 1010,300'),('redirect','final_external',None,'1250,335 1250,416'),('external','form','internal','650,355 650,415'),('form','submit',None,'650,485 650,535'),('submit','exists',None,'650,605 650,655'),('exists','error404','missing','805,710 1010,710'),('error404','final404',None,'1490,710 1566,710'),('exists','duplicate','found','650,765 650,825'),('duplicate','error400','yes','805,880 1010,880'),('error400','final400',None,'1490,880 1566,880'),('duplicate','file','no','650,935 650,995'),('file','size','yes','805,1050 1095,1050'),('size','error413','no','1405,1050 1500,1050'),('error413','final413',None,'1740,1085 1740,1206'),('size','encode','yes','1250,1105 1250,1185'),('encode','merge',None,'1250,1255 1250,1370 675,1370'),('file','merge','no','650,1105 650,1345'),('merge','commit1',None,'650,1395 650,1465'),('commit1','commit2',None,'650,1535 650,1595'),('commit2','response',None,'650,1665 650,1725'),('response','final_ok',None,'650,1795 650,1856')]
(OUT/'sources/uml-activity.json').write_text(json.dumps({'nodes':nodes,'edges':edges},indent=2)+'\n')
s=svg_start(2040,1950,'HireHub application submission UML activity')
for a,b,guard,points in edges:
    s+=line(points,True)
    if guard:
        coords=points.split();x0,y0=map(float,coords[0].split(','));x1,y1=map(float,coords[1].split(','))
        s+=text((x0+x1)/2+15,(y0+y1)/2-12,'['+guard+']',18,anchor='start')
for key,kind,x,y,label in nodes:
    if kind=='initial':s+=f'<circle cx="{x}" cy="{y}" r="13" fill="#182A42"/>'
    elif kind=='final':s+=f'<circle cx="{x}" cy="{y}" r="15" fill="white" stroke="#182A42" stroke-width="2"/><circle cx="{x}" cy="{y}" r="9" fill="#182A42"/>'
    elif kind=='decision':s+=diamond(x,y,label)
    elif kind=='merge':s+=f'<path d="M{x} {y-25} L{x+25} {y} L{x} {y+25} L{x-25} {y} Z" fill="white" stroke="#334C70" stroke-width="2"/>'
    else:s+=action(x,y,label)
s+=text(90,70,'Application submission',30,anchor='start',weight='bold')+text(90,105,'Active-account authentication assumed',18,anchor='start',fill='#526882')
s+='</g></svg>'
(OUT/'svg/uml-activity.svg').write_text(s)

from format_structural import format_structural
layouts=format_structural(OUT,schema,selected)
for d in catalog:
    if d['id'] in layouts:
        d['domains']=[{k:p[k] for k in ['id','title','x','y','width','height']} for p in layouts[d['id']]]
        d['notes'].insert(0,'Use the Domain selector to view one area at a time. Dashed reference cards repeat an existing entity; all relationships appear once across the three views.')
    if d['id']=='uml-use-case':d['notes'].insert(0,'The three role views are projections of the same HireHub system, not separate systems.')

(OUT/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
print('Built',len(catalog),'diagram definitions;',sum(len(e['columns']) for e in entities),'columns;',len(relations),'relationships.')

# Once SVGs are rendered, --gallery creates a single portable, offline HTML file.
if '--gallery' in __import__('sys').argv:
    items=[]
    for i,d in enumerate(catalog):
        svg=(OUT/'svg'/(d['id']+'.svg')).read_text()
        svg=re.sub(r'<\?xml.*?\?>','',svg,flags=re.S)
        svg=re.sub(r'<!DOCTYPE.*?>','',svg,flags=re.S)
        notes=''.join('<li>'+escape(n)+'</li>' for n in d['notes'])
        sources=''.join('<li><code>'+escape(n)+'</code></li>' for n in d['sources'])
        code=d['code'] if d['code'] else (OUT/'sources'/d['source']).read_text()
        domain_control=('<label>Domain <select class="domain-select">'+''.join(f'<option value="{p["id"]}">{escape(p["title"])}</option>' for p in d['domains'])+'<option value="all">All domains</option></select></label>') if d.get('domains') else ''
        items.append(f'''<section class="diagram" id="{d['id']}" {'hidden' if i else ''}>
<div class="eyebrow">{escape(d['kind'])}</div><h2>{escape(d['title'])}</h2><p class="subtitle">{escape(d['subtitle'])}</p>
<div class="toolbar">{domain_control}<button data-action="fit">Fit</button><button data-action="minus" aria-label="Zoom out">−</button><output>100%</output><button data-action="plus" aria-label="Zoom in">+</button><button data-action="svg">Save SVG</button><button data-action="png">Save PNG</button><button data-action="source">Save source</button><button data-action="print">Print diagram</button></div>
<div class="viewport" tabindex="0" aria-label="Scrollable diagram. Use zoom controls for details."><div class="canvas">{svg}</div></div>
<div class="below"><article><h3>Reading this diagram</h3><ul>{notes}</ul></article><details><summary>Source traceability and editable definition</summary><ul>{sources}</ul><pre>{escape(code)}</pre></details></div></section>''')
    options=''.join(f'<option value="{d["id"]}">{i+1:02d} / {escape(d["title"])}</option>' for i,d in enumerate(catalog))
    data=json.dumps({d['id']:{'source':d['source'],'domains':d.get('domains',[]),'code':d['code'] if d['code'] else (OUT/'sources'/d['source']).read_text()} for d in catalog}).replace('</','<\\/')
    css='''*{box-sizing:border-box}body{margin:0;color:#182a42;background:#f5f7fb;font:16px/1.55 Arial,sans-serif}header{padding:28px 4vw 22px;background:#17243a;color:#fff}header h1{font-size:30px;letter-spacing:-.6px;margin:0}header p{margin:6px 0;color:#c5d0e0}.topbar{display:flex;align-items:center;gap:22px;flex-wrap:wrap;padding:18px 4vw;border-bottom:1px solid #dbe2eb;background:white}.topbar label{font-weight:bold}select{min-width:360px;max-width:90vw;padding:11px;border:1px solid #adbdd1;border-radius:5px;background:white;color:#182a42;font:inherit}main{padding:26px 4vw}h2{font-size:29px;line-height:1.2;margin:8px 0}.eyebrow{font-size:13px;text-transform:uppercase;letter-spacing:1.5px;color:#5145cd;font-weight:bold}.subtitle{color:#526176;margin:8px 0 20px}.domain-select{min-width:240px;padding:8px;font-size:15px}.toolbar label{font-size:14px;font-weight:bold}.toolbar{display:flex;gap:9px;align-items:center;flex-wrap:wrap;margin-bottom:12px}button{padding:8px 13px;border:1px solid #bdc9d8;border-radius:5px;background:white;color:#182a42;font:inherit;cursor:pointer}button:hover,button:focus-visible{border-color:#5145cd;background:#efedff}output{min-width:52px;text-align:center}.viewport{height:70vh;min-height:470px;overflow:auto;background:white;border:1px solid #cad3e0;border-radius:6px;padding:24px;overscroll-behavior:contain}.canvas svg{display:block;max-width:none!important;background:white}.below{display:grid;grid-template-columns:1fr 1fr;gap:34px;margin-top:22px}h3{margin:0 0 9px}li{margin-bottom:9px}summary{cursor:pointer;font-weight:bold}pre{white-space:pre-wrap;word-break:break-word;background:#fff;padding:18px;border:1px solid #dbe2eb;font:13px/1.5 monospace;max-height:460px;overflow:auto}.legend{font-size:14px;color:#526176;max-width:850px}.status{margin-left:auto;font-size:14px;color:#526176}footer{margin:20px 4vw 35px;color:#526176;font-size:13px}footer a{color:#5145cd}[hidden]{display:none!important}@media(max-width:800px){.below{grid-template-columns:1fr}.viewport{padding:10px}}@media print{header,.topbar,.toolbar,.below,footer,.eyebrow,.subtitle{display:none!important}main{padding:0}.diagram:not([hidden]){display:block}.viewport{height:auto;overflow:visible;border:0;padding:0}.canvas svg{width:100%!important;height:auto!important}}'''
    js='''const definitions=DEFINITIONS;const selector=document.querySelector('#diagram-select');let current,scale=1,natural={w:1,h:1};function active(){return document.querySelector('.diagram:not([hidden])')}function sizing(){const s=active(),svg=s.querySelector('svg');const v=svg.viewBox.baseVal;natural={w:v.width||Number(svg.getAttribute('width'))||1200,h:v.height||Number(svg.getAttribute('height'))||800};}function zoom(value){scale=Math.max(.08,Math.min(4,value));const s=active();s.querySelector('svg').style.width=natural.w*scale+'px';s.querySelector('svg').style.height=natural.h*scale+'px';s.querySelector('output').textContent=Math.round(scale*100)+'%';}function fit(){sizing();const v=active().querySelector('.viewport');zoom(Math.min((v.clientWidth-52)/natural.w,(v.clientHeight-52)/natural.h))}function domain(value){const svg=active().querySelector('svg');if(!svg.dataset.fullView)svg.dataset.fullView=svg.getAttribute('viewBox');const p=definitions[current].domains.find(p=>String(p.id)===value);svg.setAttribute('viewBox',p?[p.x,p.y,p.width,p.height].join(' '):svg.dataset.fullView);fit();active().querySelector('.viewport').scrollTo(0,0)}function exportName(){const select=active().querySelector('.domain-select');return current+(select&&select.value!=='all'?'-domain-'+(Number(select.value)+1):'')}function choose(id){document.querySelectorAll('.diagram').forEach(s=>s.hidden=s.id!==id);current=id;selector.value=id;const ds=active().querySelector('.domain-select');if(ds)domain(ds.value);else fit();history.replaceState(null,'','#'+id);window.scrollTo(0,0);active().querySelector('.viewport').scrollTo(0,0)}function download(blob,name){const a=document.createElement('a'),url=URL.createObjectURL(blob);a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}function svgString(){const svg=active().querySelector('svg').cloneNode(true);svg.style.width='';svg.style.height='';svg.setAttribute('xmlns','http://www.w3.org/2000/svg');svg.setAttribute('width',natural.w);svg.setAttribute('height',natural.h);return new XMLSerializer().serializeToString(svg)}document.querySelectorAll('.toolbar').forEach(t=>t.addEventListener('click',async e=>{const a=e.target.dataset.action;if(!a)return;if(a==='fit')fit();if(a==='plus')zoom(scale*1.25);if(a==='minus')zoom(scale/1.25);if(a==='source')download(new Blob([definitions[current].code],{type:'text/plain'}),definitions[current].source);if(a==='svg')download(new Blob([svgString()],{type:'image/svg+xml'}),exportName()+'.svg');if(a==='print')window.print();if(a==='png'){const blob=new Blob([svgString()],{type:'image/svg+xml'}),url=URL.createObjectURL(blob),im=new Image();im.onload=()=>{const ratio=Math.min(2,10000/Math.max(natural.w,natural.h));const c=document.createElement('canvas');c.width=natural.w*ratio;c.height=natural.h*ratio;const ctx=c.getContext('2d');ctx.fillStyle='white';ctx.fillRect(0,0,c.width,c.height);ctx.drawImage(im,0,0,c.width,c.height);c.toBlob(b=>download(b,exportName()+'.png'),'image/png');URL.revokeObjectURL(url)};im.onerror=()=>{URL.revokeObjectURL(url);alert('PNG export failed. Use Save SVG for the original vector diagram.')};im.src=url}}));document.querySelectorAll('.domain-select').forEach(s=>s.addEventListener('change',()=>domain(s.value)));selector.addEventListener('change',e=>choose(e.target.value));choose(definitions[location.hash.slice(1)]?location.hash.slice(1):selector.value);window.diagramViewerReady=true;'''.replace('DEFINITIONS',data)
    page='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>HireHub / ER and UML diagrams</title><style>'+css+'</style></head><body><header><h1>HireHub / ER &amp; UML diagrams</h1><p>Database structure and implemented recruitment workflows</p></header><div class="topbar"><label for="diagram-select">Diagram</label><select id="diagram-select">'+options+'</select><span class="status">7 diagrams · Offline SVG · Editable sources</span><div class="legend">ER: PK = primary key, FK = foreign key, UK = unique. One = ||, zero or one = circle + bar, zero or many = circle + crow\'s foot. UML multiplicities: 1, 0..1 and 0..*.</div></div><main>'+''.join(items)+'</main><footer>Notation references: <a href="https://www.omg.org/spec/UML/2.5.1">OMG UML 2.5.1</a> and <a href="https://mermaid.js.org/syntax/entityRelationshipDiagram.html">Mermaid crow\'s-foot ER notation</a>. Structural views follow declared SQLAlchemy models; behavioral views document current implementation. No live-database verification is implied.</footer><script>'+js+'</script></body></html>'
    (OUT/'index.html').write_text(page)
    print('Wrote standalone offline index.html')
