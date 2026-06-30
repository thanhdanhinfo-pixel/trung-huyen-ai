class DependencyRisk:
    def score(
        self,
        dependency_count: int,
        has_cycle: bool = False
    ) -> dict:

        dependency_count = max(0, dependency_count)

        base = min(dependency_count * 10, 80)

        if has_cycle:
            base = 100

        level = (
            "high" if base >= 80
            else "medium" if base >= 40
            else "low"
        )

        return {
            "risk_score": base,
            "level": level,
        }


dependency_risk = DependencyRisk()
