from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uuid, asyncio

from agent_bus import BUS
from memory_fabric import get_profile, get_short_term, consolidate_into_profile, query_episodes

# ✅ Import all agents so they self-register with BUS
import triage_agent
import engage_agent
import campaign_agent

app = FastAPI(title="AIML Multi-Agent Control Plane - Prototype")

# ✅ Root landing page (HTML instead of plain JSON)
@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html>
      <head><title>AIML Multi-Agent System</title></head>
      <body style="font-family: sans-serif; text-align: center; margin-top: 50px;">
        <h1>AIML Multi-Agent Marketing System</h1>
        <p>Status: <strong style="color:green;">Running ✅</strong></p>
        <p>This service powers a modular multi-agent system with:</p>
        <ul style="list-style:none;">
          <li>🤖 Triage Agent – Lead classification</li>
          <li>📩 Engage Agent – Strategy planning & execution</li>
          <li>📊 Campaign Agent – Optimization recommendations</li>
          <li>🧠 Memory Fabric – Profiles + Episodes</li>
        </ul>
        <p>➡️ Explore the <a href="/docs">Interactive API Documentation</a></p>
        <p>➡️ Base Endpoint: <code>/leads</code> (Ingest new leads)</p>
      </body>
    </html>
    """

# --------- MODELS ---------
class LeadIn(BaseModel):
    score: float
    recency: float

# --------- ROUTES ---------

@app.post("/leads")
def ingest_lead(lead: LeadIn):
    lead_id = str(uuid.uuid4())
    triage_res = asyncio.run(BUS.call("triage.classify", {
        "lead_id": lead_id,
        "features": lead.dict()
    }))
    return {"lead_id": lead_id, "triage": triage_res}

@app.get("/leads/{lead_id}")
def get_lead(lead_id: str):
    return {
        "profile": get_profile(lead_id),
        "short_term": get_short_term(lead_id),
        "episodes": query_episodes(lead_id)
    }

@app.post("/leads/{lead_id}/engage")
def engage_lead(lead_id: str):
    plan = asyncio.run(BUS.call("engage.plan", {"lead_id": lead_id}))
    exec_res = asyncio.run(BUS.call("engage.execute", plan))
    return {"plan": plan, "result": exec_res}

@app.get("/leads/{lead_id}/recommend")
def recommend_for_lead(lead_id: str):
    return asyncio.run(BUS.call("campaign.recommend", {"lead_id": lead_id}))

@app.post("/consolidate/{lead_id}")
def consolidate_lead(lead_id: str):
    return consolidate_into_profile(lead_id)
