from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid, asyncio
from agent_bus import BUS
from memory_fabric import get_profile, get_short_term, consolidate_into_profile, query_episodes

app = FastAPI(title='AIML Multi-Agent Control Plane - Prototype')

class LeadIn(BaseModel):
    lead_id: str = None
    name: str = None
    email: str = None
    score: float = 0.5
    recency: float = 0.5

@app.post('/leads')
def ingest_lead(payload: LeadIn):
    lead_id = payload.lead_id or str(uuid.uuid4())
    try:
        triage_res = asyncio.run(BUS.call('triage.classify', {
            'lead_id': lead_id,
            'features': {'score': payload.score, 'recency': payload.recency}
        }))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {'lead_id': lead_id, 'triage': triage_res}

@app.get('/leads/{lead_id}')
def inspect_lead(lead_id: str):
    profile = get_profile(lead_id)
    short = get_short_term(lead_id)
    episodes = query_episodes(lead_id)
    return {'lead_id': lead_id, 'profile': profile, 'short_term': short, 'episodes_count': len(episodes)}

@app.post('/leads/{lead_id}/engage')
def trigger_engage(lead_id: str):
    plan = asyncio.run(BUS.call('engage.plan', {'lead_id': lead_id, 'triage_result': {}}))
    exec_res = asyncio.run(BUS.call('engage.execute', plan))
    return {'plan': plan, 'exec': exec_res}

@app.get('/leads/{lead_id}/recommend')
def recommend(lead_id: str):
    return asyncio.run(BUS.call('campaign.recommend', {'lead_id': lead_id}))

@app.post('/consolidate/{lead_id}')
def consolidate(lead_id: str):
    profile = consolidate_into_profile(lead_id)
    return {'lead_id': lead_id, 'profile': profile}
