from agent_bus import BUS
from memory_fabric import query_episodes
from typing import Dict, Any

class CampaignAgent:
    def monitor(self, params: Dict[str, Any]):
        lead_id = params.get('lead_id')
        episodes = query_episodes(lead_id) if lead_id else []
        sends, opens, conv = 0,0,0
        for e in episodes:
            out = e.get('episode',{})
            if out.get('action')=='send':
                sends+=1
                o = out.get('outcome',{})
                if o.get('opened'): opens+=1
                if o.get('converted'): conv+=1
        return {'lead_id': lead_id, 'sends': sends, 'opens': opens, 'conversions': conv}

    def recommend(self, params: Dict[str, Any]):
        agg = self.monitor(params)
        sends, opens, conv = agg['sends'], agg['opens'], agg['conversions']
        recs=[]
        if sends < 3 and (opens/(sends+0.001)) < 0.1:
            recs.append({'action':'try_alternate_channel','reason':'low_open_rate'})
        if conv==0 and sends>=3:
            recs.append({'action':'escalate_to_manager','reason':'no_conversions_after_3_sends'})
        if not recs:
            recs.append({'action':'no_change','reason':'metrics_ok'})
        return {'lead_id': params.get('lead_id'), 'recommendations': recs}

agent = CampaignAgent()
BUS.register('campaign.monitor', agent.monitor)
BUS.register('campaign.recommend', agent.recommend)
