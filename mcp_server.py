
---

# 📝 `mcp_server.py`
```python
import time, uuid, json
from typing import Dict

TOKENS = {}

def issue_token(agent_id: str, scopes: Dict[str, bool], ttl_seconds: int = 600):
    token = str(uuid.uuid4())
    TOKENS[token] = {
        "agent_id": agent_id,
        "scopes": scopes,
        "issued_at": time.time(),
        "expiry": time.time() + ttl_seconds
    }
    return token

def validate_token(token: str):
    info = TOKENS.get(token)
    if not info:
        return False, "token_not_found"
    if time.time() > info['expiry']:
        return False, "token_expired"
    return True, info
