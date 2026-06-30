class SecurityLayer: 
    def check(self, user):
        return {
            "user": user,
            "authenticated": True,
            "authorized": True
        }
