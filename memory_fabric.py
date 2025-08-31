import os, json, sqlite3, uuid, datetime
from typing import Dict, Any, Optional

BASE = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE, 'memory_longterm.sqlite')
EPISODIC_LOG = os.path.join(BASE, 'episodic_log.jsonl')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS profiles
                 (lead_id TEXT PRIMARY KEY, data TEXT, created_at TEXT, updated_at TEXT)''')
    conn.commit()
    conn.close()

def upsert_profile(lead_id: str, data: Dict[str, Any]):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.datetime.utcnow().isoformat()
    c.execute('SELECT 1 FROM profiles WHERE lead_id=?', (lead_id,))
    if c.fetchone():
        c.execute('UPDATE profiles SET data=?, updated_at=? WHERE lead_id=?',
                  (json.dumps(data), now, lead_id))
    else:
        c.execute('INSERT INTO profiles (lead_id, data, created_at, updated_at) VALUES (?,?,?,?)',
                  (lead_id, json.dumps(data), now, now))
    conn.commit()
    conn.close()

def get_profile(lead_id: str) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT data FROM profiles WHERE lead_id=?', (lead_id,))
    r = c.fetchone()
    conn.close()
    return json.loads(r[0]) if r else None

SHORT_TERM = {}

def add_short_term(lead_id: str, item: Dict[str, Any]):
    SHORT_TERM.setdefault(lead_id, []).append(item)
    SHORT_TERM[lead_id] = SHORT_TERM[lead_id][-20:]

def get_short_term(lead_id: str):
    return SHORT_TERM.get(lead_id, [])

def record_episode(lead_id: str, episode: Dict[str, Any]):
    entry = {
        'episode_id': str(uuid.uuid4()),
        'lead_id': lead_id,
        'ts': datetime.datetime.utcnow().isoformat(),
        'episode': episode
    }
    with open(EPISODIC_LOG, 'a') as f:
        f.write(json.dumps(entry) + '\n')

def query_episodes(lead_id: str, limit=10):
    out = []
    if not os.path.exists(EPISODIC_LOG):
        return out
    with open(EPISODIC_LOG, 'r') as f:
        for line in reversed(f.readlines()):
            obj = json.loads(line)
            if obj.get('lead_id') == lead_id:
                out.append(obj)
                if len(out) >= limit:
                    break
    return out

def consolidate_into_profile(lead_id: str):
    profile = get_profile(lead_id) or {}
    short = get_short_term(lead_id)
    if short:
        profile.setdefault('consolidated', {})
        profile['consolidated']['last_event'] = short[-1]
        profile['consolidated']['recent_events_count'] = len(short)
        upsert_profile(lead_id, profile)
    return profile

init_db()
