CAPABILITY_STATES=['PROPOSED','EXPERIMENTAL','ACTIVE','DEPRECATED','REMOVED']
class CapabilityEvolution:
    def promote(self,name,current):  
        try:
            idx=CAPABILITY_STATES.index(current)
            return CAPABILITY_STATES[min(idx+1,len(CAPABILITY_STATES)-1)]
        except ValueError:
            return 'PROPOSED'
capability_evolution=CapabilityEvolution()  

