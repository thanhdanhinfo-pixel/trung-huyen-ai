from datetime import datetime 

class AuditLog:
    def record(self, action):
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "status": "logged"
        }
