from datetime import date
class CapabilityLineage:
    def __init__(self):
        self._history=[]
    def record_promotion(self,name,frm,to):
        self._history.append({'type':'promotion','capability':name,'from':frm,'to':to,'date':str(date.today())})
    def snapshot(self):
        return {'history_count':len(self._history),'history':self._history[-20:],'status':'tracking'}
capability_lineage=CapabilityLineage()
