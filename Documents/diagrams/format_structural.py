"""Deterministic, domain-based SVG layouts for the ER and domain class views.

Relationship paths are orthogonal and use separate attachment ports. The same
schema generates compact key views, full fields and UML associations. Context
cards repeat an existing entity; they are explicitly marked as references.
"""
from pathlib import Path
import html,json,math

def esc(x):return html.escape(str(x),quote=True)
def text(x,y,s,size=22,anchor='start',fill='#21344E',weight='normal'):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{fill}" font-weight="{weight}">{esc(s)}</text>'
def segment(a,b,dash=False,width=2):return f'<path d="M{a[0]} {a[1]} L{b[0]} {b[1]}" fill="none" stroke="#4D6382" stroke-width="{width}"'+(' stroke-dasharray="7 6"' if dash else '')+'/>'
def markers(point,inside,mult):
    x,y=point;dx,dy=inside;norm=math.hypot(dx,dy);dx/=norm;dy/=norm;px,py=-dy,dx
    def at(d,p=0):return (x+d*dx+p*px,y+d*dy+p*py)
    def bar(d):return segment(at(d,-9),at(d,9),False,2.2)
    def circle(d):
        a,b=at(d);return f'<circle cx="{a}" cy="{b}" r="6" fill="white" stroke="#4D6382" stroke-width="2"/>'
    if mult=='1':return bar(11)+bar(20)
    if mult=='0..1':return bar(10)+circle(26)
    return segment(at(0,-10),at(17),False,2.2)+segment(at(0,10),at(17),False,2.2)+segment(at(0),at(17),False,2.2)+circle(32)

def format_structural(out,schema,selected):
    entities={e['table']:e for e in schema['entities']};rels=schema['relationships']
    layouts={};panel_titles=['Identity & communication','Student data','Recruitment']
    primary=[['users','students','recruiter_profiles','notifications','messages'],['skills','student_skills','documents'],['internships','applications','saved_internships','interviews']]
    for diagram,mode in [('er-overview','keys'),('er-full','full'),('uml-class','class'),('er-chen','chen')]:
        structural=[];all_panels=[];offset=0;fullwidth=2700
        for domain,title in enumerate(panel_titles):
            refs=[] if domain==0 else ['students'] if domain==1 else ['students','recruiter_profiles']
            nodes={}
            for table in primary[domain]+refs:
                entity=entities[table];ref=table in refs
                cols=[c for c in entity['columns'] if (c['pk'] or c['fk'])] if ref or mode=='keys' else entity['columns'] if mode=='full' else [c for c in entity['columns'] if c['name'] in selected[table]]
                if mode=='chen':
                    from format_chen import ATTRIBUTES
                    cols=[c for c in entity['columns'] if c['name'] in (['id'] if ref else ATTRIBUTES[table])]
                nodes[table]={'table':table,'columns':cols,'ref':ref,'w':700,'h':270 if mode=='chen' else 62+len(cols)*36,'x':0,'y':0}
            def pos(t,x,y):nodes[t].update(x=x,y=y)
            def pt(t,side,part=.5):
                n=nodes[t];x,y,w,h=n['x'],n['y'],n['w'],120 if mode=='chen' else n['h']
                return {'L':(x,y+h*part),'R':(x+w,y+h*part),'T':(x+w*part,y),'B':(x+w*part,y+h)}[side]
            edges=[]
            def edge(parent,child,field,points,label):
                r=next(r for r in rels if r['parent']==parent and r['child']==child and r['field']==field)
                edges.append(dict(**r,points=points,label=label))
            if domain==0:
                pos('students',60,180);pos('recruiter_profiles',1720,180);pos('users',890,320)
                notif_y=max(760,nodes['users']['y']+nodes['users']['h']+210)
                message_y=max(notif_y,nodes['recruiter_profiles']['y']+nodes['recruiter_profiles']['h']+180)
                pos('notifications',890,notif_y);pos('messages',1720,message_y)
                a,b=pt('users','L',.30),pt('students','R',.30)
                edge('users','students','user_id',[a,(825,a[1]),(825,b[1]),b],(825,(a[1]+b[1])/2-18))
                a,b=pt('users','R',.30),pt('recruiter_profiles','L',.30)
                edge('users','recruiter_profiles','user_id',[a,(1655,a[1]),(1655,b[1]),b],(1655,(a[1]+b[1])/2-18))
                a,b=pt('users','B'),pt('notifications','T')
                edge('users','notifications','user_id',[a,b],(a[0]+65,(a[1]+b[1])/2))
                for field,f,gutter in [('sender_id',.66,1630),('receiver_id',.86,1670)]:
                    a,b=pt('users','R',f),pt('messages','L',f)
                    edge('users','messages',field,[a,(gutter,a[1]),(gutter,b[1]),b],(gutter,(a[1]+b[1])/2))
            elif domain==1:
                pos('skills',60,180);pos('students',60,max(560,nodes['skills']['h']+360));pos('student_skills',1000,180)
                pos('documents',1000,max(650,nodes['student_skills']['h']+420))
                a,b=pt('skills','R',.35),pt('student_skills','L',.35)
                edge('skills','student_skills','skill_id',[a,(880,a[1]),(880,b[1]),b],(880,min(a[1],b[1])-24))
                a,b=pt('students','R',.35),pt('student_skills','L',.8)
                edge('students','student_skills','student_id',[a,(830,a[1]),(830,b[1]),b],(890,(a[1]+b[1])/2))
                a,b=pt('students','R',.8),pt('documents','L',.35)
                edge('students','documents','student_id',[a,(900,a[1]),(900,b[1]),b],(900,max(a[1],b[1])+38))
            else:
                pos('students',60,200);pos('saved_internships',1000,200)
                saved_bottom=nodes['saved_internships']['y']+nodes['saved_internships']['h']
                app_y=max(660,saved_bottom+240)+(180 if mode=='chen' else 0);pos('applications',1000,app_y)
                int_y=max(550,nodes['students']['y']+nodes['students']['h']+240);pos('internships',60,int_y)
                app_bottom=app_y+nodes['applications']['h'];int_bottom=int_y+nodes['internships']['h']
                interview_y=max(1040,app_bottom+170);pos('interviews',1900,interview_y)
                iv_bottom=interview_y+nodes['interviews']['h'];rec_y=max(int_bottom+180,iv_bottom+180);pos('recruiter_profiles',60,rec_y)
                a,b=pt('students','R',.25),pt('saved_internships','L',.25)
                edge('students','saved_internships','student_id',[a,(880,a[1]),(880,b[1]),b],(880,min(a[1],b[1])-22))
                a,b=pt('students','T',.5),pt('applications','T',.5)
                edge('students','applications','student_id',[a,(a[0],115),(1800,115),(1800,app_y-100),(b[0],app_y-100),b],(1260,95))
                a,b=pt('internships','R',.12),pt('saved_internships','L',.8)
                edge('internships','saved_internships','internship_id',[a,(910,a[1]),(910,b[1]),b],(910,(a[1]+b[1])/2))
                a,b=pt('internships','R',.45),pt('applications','L',.45)
                edge('internships','applications','internship_id',[a,(850,a[1]),(850,b[1]),b],(890,(a[1]+b[1])/2+35))
                a,b=pt('applications','R',.65),pt('interviews','L',.22)
                edge('applications','interviews','application_id',[a,(1810,a[1]),(1810,b[1]),b],(1810,(a[1]+b[1])/2-18))
                a,b=pt('internships','R',.90),pt('interviews','L',.8)
                bus=max(app_bottom+85,a[1],b[1])+70
                edge('internships','interviews','internship_id',[a,(820,a[1]),(820,bus),(1800,bus),(1800,b[1]),b],(1360,bus-20))
                a,b=pt('recruiter_profiles','T'),pt('internships','B')
                edge('recruiter_profiles','internships','recruiter_id',[a,b],(a[0]+80,(a[1]+b[1])/2))
                a,b=pt('recruiter_profiles','R',.65),pt('interviews','B')
                bus=rec_y+nodes['recruiter_profiles']['h']+110
                edge('recruiter_profiles','interviews','recruiter_id',[a,(820,a[1]),(820,bus),(b[0],bus),b],(1500,bus-20))
            if mode=='chen':
                # Bottom ports would pass through attributes; route these links around the clusters.
                for e in edges:
                    if (e['parent'],e['child'])==('users','notifications'):
                        a,b=pt('users','L',.7),pt('notifications','L',.35)
                        e['points']=[a,(810,a[1]),(810,b[1]),b]
                    if (e['parent'],e['child'])==('recruiter_profiles','internships'):
                        a,b=pt('recruiter_profiles','L',.3),pt('internships','L',.7)
                        e['points']=[a,(-60,a[1]),(-60,b[1]),b]
                    if (e['parent'],e['child'])==('recruiter_profiles','interviews'):
                        a,b=pt('recruiter_profiles','R',.65),pt('interviews','R',.6)
                        bus=nodes['recruiter_profiles']['y']+nodes['recruiter_profiles']['h']+110
                        e['points']=[a,(820,a[1]),(820,bus),(2700,bus),(2700,b[1]),b]
                from format_chen import transform
                chen_width=transform(nodes,edges,domain)
            height=max(max(n['y']+n['h'] for n in nodes.values()),max(p[1] for e in edges for p in e['points']))+100
            width=2500 if domain==0 else 1800 if domain==1 else 2700
            g=f'<g id="domain-{domain}" transform="translate(0,{offset})">'+text(60,48,f'{domain+1:02d}  {title} — '+('UML classes' if mode=='class' else 'Crow’s Foot ER'),30,weight='bold')+text(60,83,'Reference cards repeat an entity from another view; they do not introduce new tables.',18,fill='#63748C')
            g+=text(60,116,'UML multiplicities: 1 = exactly one · 0..1 = optional one · 0..* = optional many' if mode=='class' else 'PK = primary key · FK = foreign key · UK = unique · NN = not null · NULL = nullable',18,fill='#63748C')
            for e in edges:
                points=e['points'];rkey=e['child']+'.'+e['field'];dash=mode!='class'
                g+=f'<g class="relation" data-key="{rkey}" data-parent="{e["parent"]}" data-child="{e["child"]}" data-parent-end="{e["parent_end"]}" data-child-end="{e["child_end"]}">'
                for a,b in zip(points,points[1:]):g+=segment(a,b,dash)
                if mode!='class':
                    g+=markers(points[0],(points[1][0]-points[0][0],points[1][1]-points[0][1]),e['parent_end'])
                    g+=markers(points[-1],(points[-2][0]-points[-1][0],points[-2][1]-points[-1][1]),e['child_end'])
                else:
                    for endpoint,neighbor,mult in [(points[0],points[1],e['parent_end']),(points[-1],points[-2],e['child_end'])]:
                        dx,dy=neighbor[0]-endpoint[0],neighbor[1]-endpoint[1];norm=math.hypot(dx,dy);dx/=norm;dy/=norm
                        tx=endpoint[0]+dx*34 if dx else endpoint[0]+22
                        ty=endpoint[1]+26 if dx else endpoint[1]+dy*34
                        g+=text(tx,ty,mult,19,anchor='middle')
                label=e['field'].removesuffix('_id') if mode=='class' else e['field'];lx,ly=e['label'];lw=len(label)*12+20
                g+=f'<rect x="{lx-lw/2}" y="{ly-23}" width="{lw}" height="31" fill="white"/>'+text(lx,ly,label,20,anchor='middle')+'</g>'
            for table,n in nodes.items():
                x,y,w,h=n['x'],n['y'],n['w'],n['h'];ident=f'render_{diagram.replace("-","_")}-entity-{table}-'+('ref'+str(domain) if n['ref'] else 'main')
                g+=f'<g id="{ident}" class="entity" data-table="{table}" data-complete="{str(not n["ref"]).lower()}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="white" stroke="#3C5578" stroke-width="2"'+(' stroke-dasharray="7 5"' if n['ref'] else '')+'/>'
                g+=f'<path d="M{x} {y+54} H{x+w}" stroke="#3C5578" fill="none"/>'
                name=entities[table]['class_name'] if mode=='class' else table
                g+=text(x+20,y+35,name,25,weight='bold')
                if n['ref']:g+=text(x+w-18,y+34,'REFERENCE',16,anchor='end',fill='#63748C')
                for i,c in enumerate(n['columns']):
                    yy=y+82+i*36
                    if mode=='class':g+=text(x+20,yy,c['name']+' : '+c['type'].split('(')[0],22)
                    else:
                        typ={'Integer':'INT','String':'VARCHAR','Text':'TEXT','Boolean':'BOOL','Float':'FLOAT','DateTime':'DATETIME'}.get(c['type'].split('(')[0],c['type'])
                        if '(' in c['type']:typ+='('+c['type'].split('(',1)[1]
                        flags=','.join(a for a,b in [('PK',c['pk']),('FK',bool(c['fk'])),('UK',c['unique'])] if b)
                        g+=text(x+18,yy,c['name'],22)+text(x+335,yy,typ,20,fill='#63748C')+text(x+505,yy,flags,18,fill='#5145CD')+text(x+w-18,yy,'NULL' if c['nullable'] else 'NN',18,anchor='end',fill='#63748C')
                    if i<len(n['columns'])-1:g+=f'<path d="M{x+12} {yy+11} H{x+w-12}" stroke="#E1E6EF" fill="none"/>'
                g+='</g>'
            g+='</g>'
            if mode=='chen':
                from format_chen import render_panel
                g=render_panel(nodes,edges,entities,domain,title,offset,height)
                width=chen_width
            structural.append(g)
            all_panels.append({'id':domain,'title':title,'x':0,'y':offset,'width':width,'height':height,'nodes':list(nodes.values()),'edges':edges})
            offset+=height+95
        fullwidth=max(p['width'] for p in all_panels)
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{fullwidth}" height="{offset-95}" viewBox="0 0 {fullwidth} {offset-95}" role="img"><title>{esc(diagram)}: domain-organized structure</title><rect width="100%" height="100%" fill="white"/><g font-family="Arial, sans-serif" stroke-linejoin="round">'+''.join(structural)+'</g></svg>'
        (out/'svg'/(diagram+'.svg')).write_text(svg)
        for panel,g in zip(all_panels,structural):
            crop=f'<svg xmlns="http://www.w3.org/2000/svg" width="{panel["width"]}" height="{panel["height"]}" viewBox="0 {panel["y"]} {panel["width"]} {panel["height"]}" role="img"><title>{esc(panel["title"])}</title><rect x="0" y="{panel["y"]}" width="100%" height="100%" fill="white"/><g font-family="Arial, sans-serif" stroke-linejoin="round">'+g+'</g></svg>'
            (out/'svg'/(diagram+'-domain-'+str(panel['id']+1)+'.svg')).write_text(crop)
        layouts[diagram]=all_panels
    (out/'layout.json').write_text(json.dumps(layouts,indent=2)+'\n')
    return layouts
