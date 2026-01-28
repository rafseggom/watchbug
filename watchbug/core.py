import os
from dotenv import load_dotenv

class Watchbug:
    def __init__(self):
        load_dotenv()
        self.enabled = os.getenv("WATCHBUG_ENABLED") == "True"
        self.sentry_dsn = os.getenv("SENTRY_DSN")
        self.logrocket_id = os.getenv("LOGROCKET_ID")
        
    def get_script_tag(self):
        if not self.enabled:
            return ""
        # Aquí irá el código JS que inyectaremos en el frontend
        return ""