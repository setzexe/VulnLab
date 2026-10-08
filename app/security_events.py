import json
import logging
import sys
from datetime import datetime, timezone

logger = logging.getLogger("vulnlab.security")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

def log_login_failure():
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "auth.login_failed",
        "outcome": "failure",
    }
    logger.warning(json.dumps(event, separators=(",", ":")))