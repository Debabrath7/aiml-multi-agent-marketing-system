import uuid, json
from typing import Dict, Any
from sklearn.linear_model import LogisticRegression
import numpy as np
from agent_bus import BUS
from memory_fabric import add_short_term, get_profile, upsert_profile

LABELS = ['Campaign Qualified', 'Cold Lead', 'General Inquiry']

class TriageAgent:
    def __init__(self):
        X = np.array([[0.9, 1.0], [0.2, 0.1], [0.5, 0.4], [0.7, 0.6]])
        y = np.array([0,2,1,0])
        self.model = LogisticRegression(multi_class='auto', solver='liblinear')
        self.model.fit(X,y)

    def classify(self, params: Dict[str, Any]):
        lead_id = params.get('lead_id') or str(uuid.uuid4())
        features = params.get('features', {})
        score = float(features.get('score', 0.5))
        recency = float(features.get('recency', 0.5))
        x = np.array([[score, recency]])
        pred = int(self.model.predict(x)[0])
        prob = float(self.model.predict_proba(x)[0][pred])
        label = LABELS[pred]
        rationale = {'score': score, 'recency': recency}
        add_short_term(lead_id, {'event': 'triage.classify', 'label': label})
        profile = get_profile(lead_id) or {}
        profile['last_triage'] = {'label': label, 'prob': prob}
        upsert_profile(lead_id, profile)
        return {'lead_id': lead_id, 'label': label, 'confidence': prob, 'rationale': rationale}

agent = TriageAgent()
BUS.register('triage.classify', agent.classify)
