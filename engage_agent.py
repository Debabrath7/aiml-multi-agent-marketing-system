import random
from typing import Dict, Any
from agent_bus import BUS
from memory_fabric import add_short_term, record_episode, get_profile, upsert_profile

TEMPLATES = [
    {'id': 'email_A', 'channel': 'email', 'text': 'Hi {name}, try our product A!'},
    {'id': 'email_B', 'channel': 'email', 'text': 'Hello {name}, special offer on B.'},
    {'id': 'sms_A', 'channel': 'sms', 'text': 'Hey {name}, quick deal: A.'},
]

class EngagementAgent:
    def __init__(self, epsilon=0.25):
        self.counts = {t['id']: 0 for t in TEMPLATES}
        self.successes = {t['id']: 0 for t in TEMPLATES}
        self.epsilon = epsilon

    def plan(self, params: Dict[str, Any]):
        lead_id = params.get('lead_id')
        if random.random() < self.epsilon:
            chosen = random.choice(TEMPLATES)
        else:
            rates = {tid: (self.successes[tid]/self.counts[tid]) if self.counts[tid]>0 else 0.0 for tid in self.counts}
            best = max(rates, key=lambda k: rates[k])
            chosen = next(t for t in TEMPLATES if t['id']==best)
        plan = {'lead_id': lead_id, 'template_id': chosen['id'], 'channel': chosen['channel'], 'body': chosen['text']}
        add_short_term(lead_id, {'event': 'engage.plan', 'plan': plan})
        return plan

    def execute(self, params: Dict[str, Any]):
        lead_id = params.get('lead_id')
        template_id = params.get('template_id')
        base = {'email_A':0.12, 'email_B':0.09, 'sms_A':0.07}
        p = base.get(template_id, 0.05)
        outcome = {'delivered': True, 'opened': random.random() < p, 'converted': random.random() < (p*0.3)}
        self.counts[template_id] += 1
        if outcome.get('opened') or outcome.get('converted'):
            self.successes[template_id] += 1
        record_episode(lead_id, {'action':'send','template':template_id,'outcome':outcome})
        add_short_term(lead_id, {'event': 'engage.execute', 'outcome': outcome})
        profile = get_profile(lead_id) or {}
        profile.setdefault('engagement', []).append({'template': template_id, 'outcome': outcome})
        upsert_profile(lead_id, profile)
        return {'lead_id': lead_id, 'outcome': outcome}

agent = EngagementAgent()
BUS.register('engage.plan', agent.plan)
BUS.register('engage.execute', agent.execute)
