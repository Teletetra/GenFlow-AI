import hashlib
import json
from redis import Redis
from .config import settings

_client = Redis.from_url(settings.redis_url, decode_responses=True)


def _key(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True).encode()
    return "genflow:" + hashlib.sha256(raw).hexdigest()


def get(payload: dict):
    try:
        value = _client.get(_key(payload))
        return json.loads(value) if value else None
    except Exception:
        return None


def put(payload: dict, value: dict):
    try:
        _client.setex(_key(payload), settings.cache_ttl_seconds, json.dumps(value))
    except Exception:
        pass
