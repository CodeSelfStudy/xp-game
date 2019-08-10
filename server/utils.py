import json
from typing import Dict
from server.logger import create_logger

log = create_logger(__name__)


def to_dict(obj) -> Dict:
    return json.loads(json.dumps(obj, default=lambda o: o.__dict__))


def from_dict(data: Dict, to_type):
    """
    Parses a dictionary to a given type.  Doesn't parse recursively; nested
    structures need to be parsed manually
    TODO: make it parse recursively
    """
    try:
        parsed = to_type(**data)
        return parsed
    except Exception:
        log.exception("Unable to parse client event")
    return None
