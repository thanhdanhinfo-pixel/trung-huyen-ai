from pathlib import Path 
import yaml
BASE=Path(__file__).parent
class KnowledgeGraph:
    def _load(self,n):
        return yaml.safe_load((BASE/n).read_text(encoding='utf-8')) or {}
    def snapshot(self):
        ls=self._load('lessons.yaml').get('lessons',[])
        ps=self._load('patterns.yaml').get('patterns',[])
        ds=self._load('decisions.yaml').get('decisions',[])
        return {'lesson_count':len(ls),'pattern_count':len(ps),'decision_count':len(ds),'links':[{'lesson':l.get('id'),'pattern':p.get('id'),'decision':ds[min(i,len(ds)-1)].get('id') if ds else None} for i,(l,p) in enumerate(zip(ls,ps))]}
knowledge_graph=KnowledgeGraph()
