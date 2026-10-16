"""Chen shapes with explicit same-side (min,max) participation constraints.

This is a conceptual projection of the mapped schema: relationships replace FK
attributes, and selected non-FK attributes keep the diagram readable. Each entity
has its own mapped ID, so no weak entities or identifying diamonds are invented.
"""
import math
from format_structural import esc,text,segment

ATTRIBUTES={
 'users':['id','email','role'],'students':['id','full_name','university'],
 'recruiter_profiles':['id','full_name','company_name'],
 'notifications':['id','message','is_read'],'messages':['id','content','sent_at'],
 'skills':['id','name','category'],'student_skills':['id','proficiency_level'],
 'documents':['id','file_name','document_type'],'internships':['id','title','company_name'],
 'applications':['id','status','applied_at'],'saved_internships':['id','saved_at'],
 'interviews':['id','scheduled_at','interview_type']}
NAMES={'students.user_id':'Student profile','recruiter_profiles.user_id':'Recruiter profile',
 'notifications.user_id':'Receives alert','messages.sender_id':'Sends message','messages.receiver_id':'Receives message',
 'documents.student_id':'Owns document','student_skills.student_id':'Lists skill','student_skills.skill_id':'Refers to skill',
 'internships.recruiter_id':'Publishes','applications.student_id':'Submits','applications.internship_id':'Targets posting',
 'interviews.recruiter_id':'Schedules','interviews.application_id':'For application','interviews.internship_id':'For posting',
 'saved_internships.student_id':'Saves','saved_internships.internship_id':'Saved posting'}

def intersects(a,b,pad=0):
 return max(a[0],b[0])-pad<min(a[0]+a[2],b[0]+b[2]) and max(a[1],b[1])-pad<min(a[1]+a[3],b[1]+b[3])
def transform(nodes,edges,domain):
 # Widen the existing connector corridors without stretching entity rectangles.
 knots=[(0,0),(760,760),(890,1200),(1590,1900),(1720,2340),(2500,3120)] if domain==0 else [(0,0),(760,760),(1000,1260),(1800,2060)] if domain==1 else [(0,0),(760,760),(1000,1260),(1700,1960),(1900,2460),(2700,3260)]
 def xx(x):
  for (a,c),(b,d) in zip(knots,knots[1:]):
   if x<=b:return round(c+(x-a)*(d-c)/(b-a),2)+220
  return x+knots[-1][1]-knots[-1][0]+220
 for n in nodes.values():n['x']=xx(n['x'])
 for e in edges:
  points=[]
  for x,y in e['points']:
   point=(xx(x),y)
   if points and point==points[-1]:continue
   if len(points)>1 and ((points[-2][0]==points[-1][0]==point[0]) or (points[-2][1]==points[-1][1]==point[1])):points[-1]=point
   else:points.append(point)
  e['points']=points
 return knots[-1][1]+440

def render_panel(nodes,edges,entities,domain,title,offset,height):
 boxes=[(n['x'],n['y'],n['w'],n['h']) for n in nodes.values()];diamonds=[]
 pairs={'1':'(1,1)','0..1':'(0,1)','0..*':'(0,N)'}
 for e in edges:
  p=e['points'];labels=[]
  # Same-side participation counts relationship instances for THIS entity.
  for endpoint,neighbor,mult in [(p[0],p[1],e['child_end']),(p[-1],p[-2],e['parent_end'])]:
   dx,dy=neighbor[0]-endpoint[0],neighbor[1]-endpoint[1];norm=math.hypot(dx,dy);dx/=norm;dy/=norm
   x=endpoint[0]+dx*62 if dx else endpoint[0]+45;y=endpoint[1]-16 if dx else endpoint[1]+dy*35
   labels.append({'x':x,'y':y,'value':pairs[mult]})
  e['participation']=labels
 # Keep diamonds clear of all entities, attributes and endpoint constraints.
 label_boxes=[(l['x']-40,l['y']-22,80,28) for e in edges for l in e['participation']]
 for e in edges:
  candidates=[]
  for a,b in zip(e['points'],e['points'][1:]):
   length=math.dist(a,b)
   for fraction in [.5,.35,.65,.2,.8]:
    x=a[0]+(b[0]-a[0])*fraction;y=a[1]+(b[1]-a[1])*fraction
    box=(x-95,y-50,190,100)
    if length<(130 if a[0]==b[0] else 220):continue
    if any(intersects(box,r,12) for r in boxes+label_boxes+diamonds):continue
    # A different relationship must not enter this diamond.
    cross=False
    for other in edges:
     if other is e:continue
     for c,d in zip(other['points'],other['points'][1:]):
      if c[0]==d[0]:hit=box[0]<c[0]<box[0]+box[2] and max(min(c[1],d[1]),box[1])<min(max(c[1],d[1]),box[1]+box[3])
      else:hit=box[1]<c[1]<box[1]+box[3] and max(min(c[0],d[0]),box[0])<min(max(c[0],d[0]),box[0]+box[2])
      cross|=hit
    if not cross:candidates.append((length-abs(.5-fraction)*1000,x,y,box))
  assert candidates,('No clear diamond position',domain,e['child'],e['field'])
  _,x,y,box=max(candidates);diamonds.append(box);e['diamond']={'x':x,'y':y,'width':190,'height':100,'name':NAMES[e['child']+'.'+e['field']]}
 g=f'<g id="chen-domain-{domain}" transform="translate(0,{offset})">'+text(60,48,f'{domain+1:02d}  {title} — Chen ER',30,weight='bold')+text(60,83,'Rectangle: entity · Diamond: relationship · Oval: attribute · Underline: primary key',20)
 for e in edges:
  key=e['child']+'.'+e['field'];g+=f'<g class="relation" data-key="{key}" data-parent="{e["parent"]}" data-child="{e["child"]}" data-parent-end="{e["parent_end"]}" data-child-end="{e["child_end"]}">'
  for a,b in zip(e['points'],e['points'][1:]):g+=segment(a,b)
  for l in e['participation']:g+=text(l['x'],l['y'],l['value'],19,anchor='middle')
  d=e['diamond'];x,y=d['x'],d['y'];g+=f'<path class="relationship-diamond" d="M{x-95} {y} L{x} {y-50} L{x+95} {y} L{x} {y+50} Z" fill="#EEF1FE" stroke="#4D6382" stroke-width="2"/>'
  words=d['name'].split();lines=[' '.join(words)] if len(d['name'])<=14 else [' '.join(words[:-1]),words[-1]]
  for i,label in enumerate(lines):g+=text(x,y+(7 if len(lines)==1 else -5)+i*23,label,18,anchor='middle')
  g+='</g>'
 for table,n in nodes.items():
  x,y,w=n['x'],n['y'],n['w'];attrs=n['columns'];g+=f'<g class="entity" data-table="{table}" data-complete="{str(not n["ref"]).lower()}"><rect x="{x}" y="{y}" width="{w}" height="120" fill="white" stroke="#334C70" stroke-width="2"/>'+text(x+w/2,y+64,table.upper(),26,anchor='middle',weight='bold')
  if n['ref']:g+=text(x+w/2,y+97,'REFERENCE — SAME ENTITY',15,anchor='middle',fill='#63748C')
  for i,c in enumerate(attrs):
   cx=x+([120,350,580][i] if len(attrs)==3 else [200,500][i] if len(attrs)==2 else 350);cy=y+210
   g+=segment((cx,y+120),(cx,cy-29))+f'<ellipse class="attribute" cx="{cx}" cy="{cy}" rx="108" ry="29" fill="white" stroke="#4D6382" stroke-width="1.8"/>'
   label=text(cx,cy+7,c['name'],19,anchor='middle')
   if c['pk']:label=label.replace('<text ','<text text-decoration="underline" data-key-attribute="true" ',1)
   g+=label
  g+='</g>'
 g+=text(60,height-30,'(min,max) describes the adjacent entity: (0,N) = optional many · (1,1) = exactly one · (0,1) = optional one',19,fill='#63748C')
 return g+'</g>'
