class CapabilityRegistryV3:
    def metadata(self,name,version='1.0',lifecycle='ACTIVE',confidence=1.0):
        return {'name':name,'version':version,'lifecycle':lifecycle,'confidence':confidence,'dependencies':[],'experiments':[]}
capability_registry_v3=CapabilityRegistryV3()  
