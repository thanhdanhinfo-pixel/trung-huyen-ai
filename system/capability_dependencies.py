class CapabilityDependencies:
    def resolve(self, capability, depends_on=None):
        return {
            'capability': capability,
            'depends_on': depends_on or [],
            'required_by': []
        }

capability_dependencies = CapabilityDependencies()
