class CapabilityDependencies:
    def resolve(self, capability, depends_on=None): 
        deps=depends_on or []
        return {'capability':capability,'depends_on':deps,'required_by':[],'has_cycle':capability in deps}
    def topological_order(self, graph):
        return list(graph.keys())
capability_dependencies=CapabilityDependencies()  
