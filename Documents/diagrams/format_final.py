"""Build the three final, connected diagrams without repeated entity cards.

All positions, routes and labels are explicit SVG geometry. Source schema values
remain unchanged; the layout places each of the twelve entities once.
"""
import math,json
from format_structural import text,segment,markers,esc
from format_chen import ATTRIBUTES,NAMES

ROWS=[['notifications','users','messages','recruiter_profiles'],['documents','students','interviews','internships'],['skills','student_skills','applications','saved_internships']]

def overlap(a,b,pad=0):
 return max(a[0],b[0])-pad<min(a[0]+a[2],b[0]+b[2]) and max(a[1],b[1])-pad<min(a[1]+a[3],b[1]+b[3])
def hits(a,b,r):
 x,y,w,h=r
 return (x<a[0]<x+w and max(min(a[1],b[1]),y)<min(max(a[1],b[1]),y+h)) if a[0]==b[0] else (y<a[1]<y+h and max(min(a[0],b[0]),x)<min(max(a[0],b[0]),x+w))
def simplify(points):
 result=[]
 for p in points:
  p=list(p)
  if result and p==result[-1]:continue
  if len(result)>1 and ((result[-2][0]==result[-1][0]==p[0]) or (result[-2][1]==result[-1][1]==p[1])):result[-1]=p
  else:result.append(p)
 return result

def make_layout(schema,selected,mode):
 entities={e['table']:e for e in schema['entities']};nodes={}
 width=460 if mode=='chen' else 440 if mode=='class' else 600
 gap=350 if mode=='chen' else 250
 for row,tables in enumerate(ROWS):
  for col,table in enumerate(tables):
   cols=[c for c in entities[table]['columns'] if mode=='full' or c['name'] in (ATTRIBUTES[table] if mode=='chen' else selected[table])]
   h=315 if mode=='chen' else 62+len(cols)*32
   nodes[table]={'table':table,'x':100+col*(width+gap),'y':0,'w':width,'h':h,'columns':cols,'ref':False,'row':row,'col':col}
 ys=[340]
 for tables in ROWS[:-1]:ys.append(ys[-1]+max(nodes[t]['h'] for t in tables)+300)
 for n in nodes.values():n['y']=ys[n['row']]
 def pt(t,side,f=.5):
  n=nodes[t];x,y,w,h=n['x'],n['y'],n['w'],100 if mode=='chen' else n['h']
  return {'L':(x,y+h*f),'R':(x+w,y+h*f),'T':(x+w*f,y),'B':(x+w if mode=='chen' else x+w*f,y+h)}[side]
 def gutter(col,f=.5):return nodes[ROWS[0][col]]['x']+width+gap*f
 edges=[]
 def edge(parent,child,field,points):
  r=next(r for r in schema['relationships'] if (r['parent'],r['child'],r['field'])==(parent,child,field))
  edges.append(dict(**r,points=simplify(points)))
 a,b=pt('users','L',.3),pt('notifications','R',.3)
 edge('users','notifications','user_id',[a,(gutter(0),a[1]),(gutter(0),b[1]),b])
 a,b=pt('users','T',.65),pt('recruiter_profiles','T',.35)
 edge('users','recruiter_profiles','user_id',[a,(a[0],240),(b[0],240),b])
 a,b=pt('users','B',.4),pt('students','T',.5)
 edge('users','students','user_id',[a,(a[0],ys[1]-150),(b[0],ys[1]-150),b])
 a,b=pt('users','R',.12 if mode=='chen' else .25),pt('messages','L',.12 if mode=='chen' else .25)
 edge('users','messages','sender_id',[a,b])
 a,b=pt('users','R',.7),pt('messages','B',.75)
 edge('users','messages','receiver_id',[a,(gutter(1,.3),a[1]),(gutter(1,.3),ys[1]-230),(b[0],ys[1]-230),b])
 a,b=pt('students','L',.3),pt('documents','R',.4)
 edge('students','documents','student_id',[a,(gutter(0),a[1]),(gutter(0),b[1]),b])
 a,b=pt('students','B',.25),pt('student_skills','T',.5)
 edge('students','student_skills','student_id',[a,(a[0],ys[2]-130),(b[0],ys[2]-130),b])
 a,b=pt('skills','R',.4),pt('student_skills','L',.4)
 edge('skills','student_skills','skill_id',[a,(gutter(0),a[1]),(gutter(0),b[1]),b])
 a,b=pt('students','R',.55),pt('applications','T',.3)
 edge('students','applications','student_id',[a,(gutter(1,.7),a[1]),(gutter(1,.7),ys[2]-190),(b[0],ys[2]-190),b])
 a,b=pt('internships','L',.8),pt('applications','T',.8)
 edge('internships','applications','internship_id',[a,(gutter(2,.7),a[1]),(gutter(2,.7),ys[2]-90),(b[0],ys[2]-90),b])
 # A different top attachment separates the student link from the interview link.
 a,b=pt('applications','T',.55),pt('interviews','B',.5)
 edge('applications','interviews','application_id',[a,(a[0],ys[2]-240),(b[0],ys[2]-240),b])
 a,b=pt('internships','L',.12 if mode=='chen' else .25),pt('interviews','R',.12 if mode=='chen' else .5)
 edge('internships','interviews','internship_id',[a,(gutter(2,.35),a[1]),(gutter(2,.35),b[1]),b])
 a,b=pt('recruiter_profiles','B',.6),pt('internships','T',.6)
 edge('recruiter_profiles','internships','recruiter_id',[a,(a[0],ys[1]-160),(b[0],ys[1]-160),b])
 a,b=pt('recruiter_profiles','L',.8),pt('interviews','T',.8)
 edge('recruiter_profiles','interviews','recruiter_id',[a,(gutter(2,.8),a[1]),(gutter(2,.8),ys[1]-80),(b[0],ys[1]-80),b])
 a,b=pt('internships','B',.6),pt('saved_internships','T',.5)
 edge('internships','saved_internships','internship_id',[a,(a[0],ys[2]-150),(b[0],ys[2]-150),b])
 a,b=pt('students','R',.85),pt('saved_internships','B',.65)
 bottom=ys[2]+max(nodes[t]['h'] for t in ROWS[2])+130
 edge('students','saved_internships','student_id',[a,(gutter(1,.25),a[1]),(gutter(1,.25),bottom),(b[0],bottom),b])
 total_w=4*width+3*gap+(280 if mode=='chen' else 200);total_h=bottom+(140 if mode=='chen' else 100)
 return nodes,edges,total_w,total_h

def annotations(nodes,edges,mode):
 occupied=[(n['x'],n['y'],n['w'],n['h']) for n in nodes.values()]
 pairs={'1':'(1,1)','0..1':'(0,1)','0..*':'(0,N)'}
 for e in edges:
  p=e['points'];e['participation']=[]
  for a,b,m in [(p[0],p[1],e['child_end'] if mode=='chen' else e['parent_end']),(p[-1],p[-2],e['parent_end'] if mode=='chen' else e['child_end'])]:
   dx,dy=b[0]-a[0],b[1]-a[1];norm=math.hypot(dx,dy);dx/=norm;dy/=norm
   x=a[0]+dx*48 if dx else a[0]+38;y=a[1]-18 if dx else a[1]+dy*42
   if mode in ['chen','class']:
    value=pairs[m] if mode=='chen' else m;e['participation'].append({'x':x,'y':y,'value':value});occupied.append((x-30,y-21,60,27))
   else:occupied.append((a[0]+dx*20-26,a[1]+dy*20-19,52,38))
 for e in edges:
  name=NAMES[e['child']+'.'+e['field']] if mode=='chen' else e['field'].removesuffix('_id') if mode=='class' else e['field']
  w,h=(170,96) if mode=='chen' else (len(name)*10.5+18,30)
  candidates=[]
  points=e['points']
  for i,(a,b) in enumerate(zip(points,points[1:])):
   length=math.dist(a,b)
   for fraction in [.5,.35,.65,.2,.8,0,1]:
    x=a[0]+(b[0]-a[0])*fraction;y=a[1]+(b[1]-a[1])*fraction
    if mode!='chen':y-=(66 if mode=='class' else 46) if a[1]==b[1] else 0
    box=(x-w/2,y-h/2,w,h)
    if y-h/2<190:continue
    if any(overlap(box,r,10) for r in occupied):continue
    if any(hits(c,d,box) for other in edges if other is not e for c,d in zip(other['points'],other['points'][1:])):continue
    candidates.append((length-abs(.5-fraction)*120,x,y,box))
  assert candidates,('No clear label position',mode,e['child'],e['field'])
  _,x,y,box=max(candidates);occupied.append(box)
  e['label']={'x':x,'y':y,'width':w,'height':h,'name':name}
  if mode=='chen':e['diamond']=dict(e['label'])

def draw(nodes,edges,w,h,mode,diagram):
 title={'full':'HireHub — Crow’s Foot ER diagram','chen':'HireHub — Chen ER diagram','class':'HireHub — UML class diagram'}[mode]
 note={'full':'All 12 mapped tables · 114 fields · 16 foreign keys','chen':'All 12 entities · 16 relationships · Selected non-FK attributes','class':'All 12 mapped classes · 16 associations · Selected declared attributes'}[mode]
 legend={'full':'PK = primary key · FK = foreign key · UK = unique · NN = not null · NULL = nullable. Dashed links are non-identifying.', 'chen':'Rectangle = entity · Diamond = relationship · Oval = attribute · Underlined attribute = primary key.', 'class':'Multiplicity: 1 = exactly one · 0..1 = optional one · 0..* = optional many. Solid lines are associations.'}[mode]
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{esc(title)}</title><rect width="100%" height="100%" fill="white"/><g font-family="Arial, sans-serif" stroke-linejoin="round">'+text(80,60,title,36,weight='bold')+text(80,104,note,22,fill='#63748C')+text(80,145,legend,19)
 for e in edges:
  key=e['child']+'.'+e['field'];p=e['points'];svg+=f'<g class="relation" data-key="{key}" data-parent="{e["parent"]}" data-child="{e["child"]}" data-parent-end="{e["parent_end"]}" data-child-end="{e["child_end"]}">'
  for a,b in zip(p,p[1:]):svg+=segment(a,b,mode=='full',2.1)
  if mode=='full':
   svg+=markers(p[0],(p[1][0]-p[0][0],p[1][1]-p[0][1]),e['parent_end'])+markers(p[-1],(p[-2][0]-p[-1][0],p[-2][1]-p[-1][1]),e['child_end'])
  for a in e['participation']:svg+=text(a['x'],a['y'],a['value'],19,anchor='middle')
  l=e['label'];x,y=l['x'],l['y']
  if mode=='chen':
   svg+=f'<path class="relationship-diamond" d="M{x-85} {y} L{x} {y-48} L{x+85} {y} L{x} {y+48} Z" fill="#EEF1FE" stroke="#4D6382" stroke-width="2"/>'
   words=l['name'].split();lines=[l['name']] if len(l['name'])<=13 else [' '.join(words[:-1]),words[-1]]
   for i,line in enumerate(lines):svg+=text(x,y+(6 if len(lines)==1 else -4)+i*22,line,17,anchor='middle')
  else:svg+=f'<rect x="{x-l["width"]/2}" y="{y-15}" width="{l["width"]}" height="30" fill="white"/>'+text(x,y+7,l['name'],20,anchor='middle')
  svg+='</g>'
 for table,n in nodes.items():
  x,y,cw,ch=n['x'],n['y'],n['w'],n['h'];coreh=100 if mode=='chen' else ch
  svg+=f'<g id="final-entity-{table}-main" class="entity" data-table="{table}" data-complete="true"><rect x="{x}" y="{y}" width="{cw}" height="{coreh}" fill="white" stroke="#334C70" stroke-width="2"/>'
  name=table.upper() if mode=='chen' else table if mode=='full' else n['class_name']
  svg+=text(x+cw/2 if mode=='chen' else x+15,y+60 if mode=='chen' else y+36,name,24 if mode!='chen' else 26,anchor='middle' if mode=='chen' else 'start',weight='bold')
  if mode!='chen':svg+=f'<path d="M{x} {y+54} H{x+cw}" stroke="#334C70" fill="none"/>'
  for i,c in enumerate(n['columns']):
   if mode=='chen':
    dx,dy=[(110,180),(350,180),(230,270)][i];cx,cy=x+dx,y+dy
    svg+=segment((cx,y+100),(cx,cy-30))+f'<ellipse class="attribute" cx="{cx}" cy="{cy}" rx="100" ry="30" fill="white" stroke="#4D6382" stroke-width="1.8"/>'
    label=text(cx,cy+7,c['name'],20,anchor='middle')
    if c['pk']:label=label.replace('<text ','<text data-key-attribute="true" text-decoration="underline" ',1)
    svg+=label
   else:
    yy=y+80+i*32
    if mode=='class':svg+=text(x+15,yy,c['name']+' : '+c['type'].split('(')[0],21)
    else:
     typ={'Integer':'INT','String':'VARCHAR','Text':'TEXT','Boolean':'BOOL','Float':'FLOAT','DateTime':'DATETIME'}.get(c['type'].split('(')[0],c['type'])
     if '(' in c['type']:typ+='('+c['type'].split('(',1)[1]
     flags=','.join(a for a,b in [('PK',c['pk']),('FK',bool(c['fk'])),('UK',c['unique'])] if b)
     svg+=text(x+14,yy,c['name'],21)+text(x+280,yy,typ,18,fill='#63748C')+text(x+430,yy,flags,17,fill='#5145CD')+text(x+cw-14,yy,'NULL' if c['nullable'] else 'NN',17,anchor='end',fill='#63748C')
    if i<len(n['columns'])-1:svg+=f'<path d="M{x+10} {yy+10} H{x+cw-10}" stroke="#E1E6EF"/>'
  svg+='</g>'
 if mode=='chen':svg+=text(80,h-30,'(min,max) counts participation of the adjacent entity: (0,N) optional many · (1,1) exactly one · (0,1) optional one.',19,fill='#63748C')
 return svg+'</g></svg>'

def format_final(out,schema,selected):
 layouts={};entities={e['table']:e for e in schema['entities']}
 for diagram,mode in [('er-full','full'),('er-chen','chen'),('uml-class','class')]:
  nodes,edges,w,h=make_layout(schema,selected,mode)
  for table,n in nodes.items():n['class_name']=entities[table]['class_name']
  annotations(nodes,edges,mode)
  svg=draw(nodes,edges,w,h,mode,diagram)
  (out/'svg'/(diagram+'.svg')).write_text(svg)
  # Old domain crops are no longer the final diagrams.
  for f in (out/'svg').glob(diagram+'-domain-*.svg'):f.unlink()
  layouts[diagram]=[{'id':0,'title':'Complete connected diagram','x':0,'y':0,'width':w,'height':h,'nodes':list(nodes.values()),'edges':edges}]
 return layouts
