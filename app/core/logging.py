import json
import logging
import sys
from datetime import datetime, timezone

from app.config import settings

# Basic logging setup so we can see important events in console.
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger("patient_registration")


# This writes a clean JSON log for key app actions like create/update/delete.
def log_event(event_type: str, payload: dict) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event_type,
        "payload": payload,
    }
    logger.info(json.dumps(entry))