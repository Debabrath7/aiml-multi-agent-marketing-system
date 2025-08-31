AIML Multi-Agent Marketing System

A production-ready multi-agent system for marketing lead triage, engagement, and campaign optimization.
This project was built as part of the AI/ML Assessment and demonstrates the use of agentic AI + memory fabric + orchestration in a real-world deployment.

🔹 Features

Triage Agent → Classifies leads as “Campaign Qualified” or not, with confidence scoring.

Engage Agent → Creates personalized engagement plans and simulates execution results.

Campaign Agent → Provides recommendations to optimize campaigns based on outcomes.

Memory Fabric → Stores short-term, long-term, and episodic memory of interactions.

AgentBus Orchestration → Event-driven communication between agents.

Control Plane API → FastAPI service to expose endpoints for lead ingestion, engagement, and recommendations.

Deployment → Fully deployed on Render with live API access.

🔹 Live Demo

Base URL: https://aiml-multi-agent-marketing-system.onrender.com

API Docs (Swagger): https://aiml-multi-agent-marketing-system.onrender.com/docs

🔹 Endpoints
Health Check
GET /

Returns service status.

Ingest Lead
POST /leads

Body:

{
  "score": 0.8,
  "recency": 0.9
}

Response:

{
  "lead_id": "84ea8330-74ef-4c29-8543-6ffd674ce261",
  "triage": {
    "label": "Campaign Qualified",
    "confidence": 0.51
  }
}

Engage Lead
POST /leads/{lead_id}/engage

Get Recommendations
GET /leads/{lead_id}/recommend

Inspect Memory/Profile
GET /leads/{lead_id}

🔹 Tech Stack

Python 3.10+

FastAPI (for control plane API)

Uvicorn (ASGI server)

scikit-learn, numpy (for ML + triage scoring)

Render (cloud deployment)

🔹 How to Run Locally
# 1. Clone the repo
git clone https://github.com/<your-username>/aiml-multi-agent-marketing-system.git
cd aiml-multi-agent-marketing-system

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the API
uvicorn control_plane:app --host 0.0.0.0 --port 8000


Visit http://localhost:8000/docs

🔹 Demo Script (for Evaluation)

Go to Swagger UI

POST /leads → Ingest a lead → copy the lead_id.

POST /leads/{lead_id}/engage → Trigger engagement → see execution results.

GET /leads/{lead_id}/recommend → Get optimization recommendations.

GET /leads/{lead_id} → Inspect memory/profile for stored episodes.


             ┌───────────────┐
             │   Control Plane│   (FastAPI + Endpoints)
             │   (API Layer)  │
             └───────┬───────┘
                     │ calls
         ┌───────────▼───────────┐
         │       AgentBus        │   (event-driven orchestration)
         └───────────┬───────────┘
   ┌─────────────────┼───────────────────┐
   │                 │                   │
   ▼                 ▼                   ▼
Triage Agent     Engage Agent       Campaign Agent
(classifies)     (plans/executes)   (optimizes)
   │                 │                   │
   └───────► Memory Fabric ◄─────────────┘
              (profile, short-term,
               episodic storage)
