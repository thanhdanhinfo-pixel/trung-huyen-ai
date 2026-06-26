class DependencyRisk:
    def score(self,dependency_count:int,has_cycle:bool=False):
        base=min(dependency_count*10,80)
        if has_cycle:
            base=100
        return {'risk_score':base,'level':'high' if base>=80 else 'medium' if base>=40 else 'low'}
dependency_risk=DependencyRisk()
