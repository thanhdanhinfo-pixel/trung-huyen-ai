import json
mapping={'planning':'application/planning','agent':'application/orchestration','workflow':'application/orchestration','knowledge':'knowledge/core','rule':'kernel/governance','scheduler':'worker/scheduler'}
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
result={}
for p in ROOT.glob('*.py'):
    target='root'
    for k,v in mapping.items():
        if k in p.stem:
            target=v
            break
    result[p.name]=target
out=ROOT/'artifacts';out.mkdir(exist_ok=True)
(out/'domain_classification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
