PROTECTED_AREAS={'identity','mission','core_architecture','constitution'}

class FounderControl:
    def can_modify(self, area:str)->bool:
        return area not in PROTECTED_AREAS

    def review_required(self, area:str):
        return area in PROTECTED_AREAS

founder_control=FounderControl()
