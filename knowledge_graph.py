from collections import defaultdict
 
class KnowledgeGraph:
    def __init__(self):
        self.nodes={}
        self.edges=defaultdict(list)

    def add_document(self,doc_id,name,topics=None):
        self.nodes[doc_id]={
            "id":doc_id,
            "name":name,
            "topics":topics or []
        }

    def link(self,source,target,relation):
        self.edges[source].append({
            "target":target,
            "relation":relation
        })
