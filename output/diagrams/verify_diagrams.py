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
rendered_nodes=[n for n in rendered.iter() if n.tag.endswith('g') and '-entity-' in n.attrib.get('id','')]
assert len(rendered_nodes)==12
for e in schema['entities']:
    node=next(n for n in rendered_nodes if '-entity-'+e['table']+'-' in n.attrib['id'])
    tokens={x.strip() for x in node.itertext() if x.strip()}
    assert e['table'] in tokens,e['table']
    for c in e['columns']:assert c['name'] in tokens,(e['table'],c['name'],'rendered field')
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
manifest=[]
for d in json.loads((OUT/'catalog.json').read_text()):
    svg=OUT/'svg'/(d['id']+'.svg');root=ET.parse(svg).getroot()
    assert root.tag.endswith('svg') and 'viewBox' in root.attrib
    assert 'foreignObject' not in svg.read_text(), 'Portable text-only SVG required'
    manifest.append({'id':d['id'],'svg':'svg/'+svg.name,'png':'png/'+d['id']+'.png','source':'sources/'+d['source'],'svg_sha256':hashlib.sha256(svg.read_bytes()).hexdigest()})
source_paths=sorted({s for d in json.loads((OUT/'catalog.json').read_text()) for s in d['sources']})
report={'verification':'passed','scope':'Declared ORM metadata, diagram definitions, route evidence and SVG structure. No live MySQL or end-to-end application execution.','tables':len(expected),'columns':sum(len(e['columns']) for e in schema['entities']),'foreign_keys':len(fks),'use_cases':18,'diagrams':manifest,'implementation_hashes':[{'source':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in source_paths],'checks':['all mapped tables and fields','declared nullability, types, PK, UK, index and delete rules','all 16 ER links and their endpoint multiplicities','all 114 fields present in the rendered full ER SVG','12 UML entity classes and 16 exact associations','all use-case endpoint evidence','activity guard completeness and endpoints','two-commit order in both sequence workflows','valid text-only SVG exports']}
(OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS:',len(expected),'tables;',report['columns'],'fields;',len(fks),'foreign keys; 7 diagram definitions.')
