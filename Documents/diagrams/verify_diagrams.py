"""Verify diagram definitions against ORM metadata and route source evidence.

Run after build_diagrams.py. Importing models inspects metadata only: this script
never connects to MySQL or writes application records.
"""
from pathlib import Path
import ast, hashlib, json, re, sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'backend'))
from app.db.models import Base

schema=json.loads((OUT/'schema.json').read_text())
assert schema['sha256']==hashlib.sha256((ROOT/schema['source']).read_bytes()).hexdigest(), 'Schema source changed; rebuild first'
expected={e['table']:e for e in schema['entities']}
assert set(expected)==set(Base.metadata.tables)
fks=[]
for table,entity in expected.items():
    mapped=Base.metadata.tables[table]
    assert set(mapped.columns.keys())=={c['name'] for c in entity['columns']},table
    for c in entity['columns']:
        actual=mapped.columns[c['name']]
        assert actual.nullable==c['nullable'],(table,c['name'],'nullability')
        assert actual.primary_key==c['pk'],(table,c['name'],'PK')
        assert bool(actual.unique)==c['unique'],(table,c['name'],'unique')
        assert bool(actual.index)==c['indexed'],(table,c['name'],'index')
        assert type(actual.type).__name__==c['type'].split('(')[0],(table,c['name'],'type')
        if '(' in c['type']:
            assert actual.type.length==int(c['type'].split('(')[1].rstrip(')')),(table,c['name'],'length')
        for fk in actual.foreign_keys:
            assert fk.target_fullname==c['fk'] and fk.ondelete==c['ondelete']
            fks.append((fk.target_fullname.split('.')[0],table,c['name'],'0..1' if actual.nullable else '1','0..1' if actual.unique else '0..*'))
assert len(fks)==16
for filename in ['er-overview.mmd','er-full.mmd']:
    source=(OUT/'sources'/filename).read_text()
    lines=[l.strip() for l in source.splitlines() if '..' in l and ' : ' in l]
    expected_links=[]
    for parent,child,field,parent_end,child_end in fks:
        left='|o' if parent_end=='0..1' else '||';right='o|' if child_end=='0..1' else 'o{'
        expected_links.append(f'{parent} {left}..{right} {child} : "{field}"')
    assert sorted(lines)==sorted(expected_links),filename
rendered=ET.parse(OUT/'svg/er-full.svg').getroot()
rendered_nodes=[n for n in rendered.iter() if n.tag.endswith('g') and '-entity-' in n.attrib.get('id','') and n.attrib.get('data-complete')=='true']
assert len(rendered_nodes)==12
for e in schema['entities']:
    node=next(n for n in rendered_nodes if '-entity-'+e['table']+'-' in n.attrib['id'])
    tokens={x.strip() for x in node.itertext() if x.strip()}
    assert e['table'] in tokens,e['table']
    for c in e['columns']:assert c['name'] in tokens,(e['table'],c['name'],'rendered field')
# Check the rendered topology and orthogonal layout independently of the formatter.
layouts=json.loads((OUT/'layout.json').read_text())
for kind,panels in layouts.items():
    principal=[n['table'] for panel in panels for n in panel['nodes'] if not n['ref']]
    assert sorted(principal)==sorted(expected),kind
    actual_links=[(r['parent'],r['child'],r['field'],r['parent_end'],r['child_end']) for panel in panels for r in panel['edges']]
    assert sorted(actual_links)==sorted(fks),(kind,'layout relationships')
    svg_root=ET.parse(OUT/'svg'/(kind+'.svg')).getroot()
    svg_links=[n for n in svg_root.iter() if n.attrib.get('class')=='relation']
    assert len(svg_links)==16
    for r in schema['relationships']:
        n=next(n for n in svg_links if n.attrib['data-key']==r['child']+'.'+r['field'])
        assert n.attrib['data-parent']==r['parent'] and n.attrib['data-child']==r['child']
        assert n.attrib['data-parent-end']==r['parent_end'] and n.attrib['data-child-end']==r['child_end']
    for panel in panels:
        nodes=panel['nodes']
        for i,n in enumerate(nodes):
            for m in nodes[i+1:]:
                assert not(max(n['x'],m['x'])<min(n['x']+n['w'],m['x']+m['w']) and max(n['y'],m['y'])<min(n['y']+n['h'],m['y']+m['h'])),(kind,'overlapping cards')
        for edge in panel['edges']:
            for a,b in zip(edge['points'],edge['points'][1:]):
                assert a[0]==b[0] or a[1]==b[1],(kind,'non-orthogonal connector')
                for n in nodes:
                    x,y,w,h=n['x'],n['y'],n['w'],n['h']
                    crosses=(x<a[0]<x+w and max(min(a[1],b[1]),y)<min(max(a[1],b[1]),y+h)) if a[0]==b[0] else (y<a[1]<y+h and max(min(a[0],b[0]),x)<min(max(a[0],b[0]),x+w))
                    assert not crosses,(kind,edge['child'],edge['field'],'connector passes through '+n['table'])
        if len(panels)==1:continue
        crop=ET.parse(OUT/'svg'/(kind+'-domain-'+str(panel['id']+1)+'.svg')).getroot()
        assert crop.attrib['viewBox']==f"0 {panel['y']} {panel['width']} {panel['height']}"

# Chen uses entity-side participation, the opposite endpoint mapping from Crow's Foot.
chen_root=ET.parse(OUT/'svg/er-chen.svg').getroot()
chen_nodes=[n for n in chen_root.iter() if n.attrib.get('class')=='entity']
assert len([n for n in chen_nodes if n.attrib['data-complete']=='true'])==12
assert len([n for n in chen_root.iter() if n.attrib.get('class')=='relationship-diamond'])==16
for panel in layouts['er-chen']:
    for edge in panel['edges']:
        actual=Base.metadata.tables[edge['child']].columns[edge['field']]
        parent_part='(0,1)' if actual.unique else '(0,N)'
        child_part='(0,1)' if actual.nullable else '(1,1)'
        assert [p['value'] for p in edge['participation']]==[parent_part,child_part]
    for n in panel['nodes']:
        for c in n['columns']:
            assert c['name'] in Base.metadata.tables[n['table']].columns
            assert not c['fk'],'FKs are relationships in the Chen projection'
        assert any(c['pk'] for c in n['columns'])
for panel in layouts['er-chen']:
    diamonds=[e['diamond'] for e in panel['edges']]
    for i,d in enumerate(diamonds):
        assert d['x']-d['width']/2>=40 and d['x']+d['width']/2<=panel['width']-40
        assert d['y']-d['height']/2>=0 and d['y']+d['height']/2<=panel['height']
        for m in diamonds[i+1:]:
            assert abs(d['x']-m['x'])>=(d['width']+m['width'])/2 or abs(d['y']-m['y'])>=(d['height']+m['height'])/2
for node in chen_nodes:
    attrs=[n for n in node if n.attrib.get('class')=='attribute']
    for i,a in enumerate(attrs):
        for b in attrs[i+1:]:
            assert abs(float(a.attrib['cx'])-float(b.attrib['cx']))>=float(a.attrib['rx'])+float(b.attrib['rx']) or abs(float(a.attrib['cy'])-float(b.attrib['cy']))>=float(a.attrib['ry'])+float(b.attrib['ry'])
    tokens={t.strip() for t in node.itertext() if t.strip()}
    assert 'id' in tokens
assert len([n for n in chen_root.iter() if n.attrib.get('data-key-attribute')=='true'])==12

# Check whole-diagram connectivity, route crossings and the reserved header.
for kind,panels in layouts.items():
    assert len(panels)==1 and len(panels[0]['nodes'])==12,kind
    panel=panels[0];edges=panel['edges'];seen={panel['nodes'][0]['table']}
    while True:
        expanded=seen|{r['child'] for r in edges if r['parent'] in seen}|{r['parent'] for r in edges if r['child'] in seen}
        if expanded==seen:break
        seen=expanded
    assert seen==set(expected),(kind,'disconnected entity graph')
    def segments_cross(a,b,c,d):
        if a[0]==b[0] and c[1]==d[1]:return min(c[0],d[0])<a[0]<max(c[0],d[0]) and min(a[1],b[1])<c[1]<max(a[1],b[1])
        if a[1]==b[1] and c[0]==d[0]:return segments_cross(c,d,a,b)
        if a[0]==b[0]==c[0]==d[0]:return max(min(a[1],b[1]),min(c[1],d[1]))<min(max(a[1],b[1]),max(c[1],d[1]))
        if a[1]==b[1]==c[1]==d[1]:return max(min(a[0],b[0]),min(c[0],d[0]))<min(max(a[0],b[0]),max(c[0],d[0]))
        return False
    for i,e in enumerate(edges):
        assert all(p[1]>=190 for p in e['points']),(kind,'route enters header')
        for f in edges[i+1:]:
            assert not any(segments_cross(a,b,c,d) for a,b in zip(e['points'],e['points'][1:]) for c,d in zip(f['points'],f['points'][1:])),(kind,'crossing or shared connectors',e['field'],f['field'])

full=(OUT/'sources/er-full.mmd').read_text()
for e in schema['entities']:
    block=re.search(r'\b'+e['table']+r' \{(.*?)\n    \}',full,re.S).group(1)
    assert len([l for l in block.splitlines() if l.strip()])==len(e['columns'])
    for c in e['columns']:assert re.search(r'\b'+c['name']+r'\b',block)
class_source=(OUT/'sources/uml-class.mmd').read_text()
assert class_source.count('    class ')==12
assert len([l for l in class_source.splitlines() if re.search(r'" (--) "',l)])==16
for r in schema['relationships']:
    parent=expected[r['parent']]['class_name'];child=expected[r['child']]['class_name']
    assert f'{parent} "{r["parent_end"]}" -- "{r["child_end"]}" {child} : {r["field"].removesuffix("_id")}' in class_source
assert not any(x in class_source for x in ['<|','*--','o--']), 'No inheritance/composition is implemented in these domain classes'
for role,cases in json.loads((OUT/'sources/uml-use-case.json').read_text()):
    for label,source,name in cases:
        funcs={n.name for n in ast.parse((ROOT/source).read_text()).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
        assert name in funcs,(role,label,name)
activity=json.loads((OUT/'sources/uml-activity.json').read_text())
node_ids={n[0] for n in activity['nodes']}
for a,b,guard,points in activity['edges']:assert a in node_ids and b in node_ids
for key,kind,*_ in activity['nodes']:
    edges=[e for e in activity['edges'] if e[0]==key]
    if kind=='decision':assert len(edges)==2 and all(e[2] for e in edges),key
    if kind=='final':assert not edges,key
    if kind=='initial':assert len(edges)==1,key

def function_tree(path,name):
    return next(n for n in ast.parse((ROOT/path).read_text()).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name)
def commits(fn):
    return sorted(n.lineno for n in ast.walk(fn) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and ast.unparse(n.func)=='db.commit')
apply=function_tree('backend/app/routers/applications.py','submit_application')
schedule=function_tree('backend/app/routers/recruiter.py','schedule_interview')
assert len(commits(apply))==2 and len(commits(schedule))==2
assert ast.unparse(apply).index('db.commit()')<ast.unparse(apply).index('db.add(Notification(')
assert ast.unparse(schedule).index('db.commit()')<ast.unparse(schedule).index("app.status = 'Interview Scheduled'")
for source in ['uml-sequence-apply.mmd','uml-sequence-interview.mmd']:
    text=(OUT/'sources'/source).read_text();assert text.index('COMMIT 1')<text.index('COMMIT 2')
assert 'break Abort request if size exceeds 8 MiB' in (OUT/'sources/uml-sequence-apply.mmd').read_text()
packaged_pngs={'er-full.png','er-chen.png','uml-class.png'}
assert {p.name for p in (OUT/'png').iterdir()}==packaged_pngs,'Keep exactly the two ER images and one UML image'
manifest=[]
for d in json.loads((OUT/'catalog.json').read_text()):
    svg=OUT/'svg'/(d['id']+'.svg');root=ET.parse(svg).getroot()
    assert root.tag.endswith('svg') and 'viewBox' in root.attrib
    assert 'foreignObject' not in svg.read_text(), 'Portable text-only SVG required'
    manifest.append({'id':d['id'],'svg':'svg/'+svg.name,'png':('png/'+d['id']+'.png') if d['id']+'.png' in packaged_pngs else None,'source':'sources/'+d['source'],'svg_sha256':hashlib.sha256(svg.read_bytes()).hexdigest()})
source_paths=sorted({s for d in json.loads((OUT/'catalog.json').read_text()) for s in d['sources']})
report={'verification':'passed','scope':'Declared ORM metadata, diagram definitions, route evidence and SVG structure. No live MySQL or end-to-end application execution.','tables':len(expected),'columns':sum(len(e['columns']) for e in schema['entities']),'foreign_keys':len(fks),'packaged_pngs':sorted(packaged_pngs),'diagram_count':len(manifest),'diagrams':manifest,'implementation_hashes':[{'source':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in source_paths],'checks':['exactly two ER PNGs and one UML PNG packaged','single connected graph with no repeated entity cards','no connector crossings or shared connector segments','all mapped tables and fields','declared nullability, types, PK, UK, index and delete rules','all 16 ER links and their endpoint multiplicities','all 114 fields present in the rendered full ER SVG','12 UML entity classes and 16 exact associations','all use-case endpoint evidence','activity guard completeness and endpoints','two-commit order in both sequence workflows','valid text-only SVG exports','12 principal entities and 16 exact rendered relations per structural view','no overlapping structural cards or connectors through cards','three connected final diagrams with each of 12 entities appearing once','Chen entity rectangles, 16 relationship diamonds and underlined keys','same-side Chen min/max participation against ORM nullability and uniqueness']}
(OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS:',len(expected),'tables;',report['columns'],'fields;',len(fks),'foreign keys;',len(manifest),'diagram definitions.')
