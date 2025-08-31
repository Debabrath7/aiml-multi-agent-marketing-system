import time, uuid, json, asyncio
from agent_bus import BUS
# Import modules to ensure they register on the BUS
import triage_agent, engage_agent, campaign_agent, memory_fabric

def simulate_lead_flow(lead_id=None, score=0.8, recency=0.9):
    lead_id = lead_id or f'lead_{uuid.uuid4().hex[:6]}'
    print("\n--- Simulating lead:", lead_id, "---")

    triage = asyncio.run(BUS.call('triage.classify', {
        'lead_id': lead_id,
        'features': {'score': score, 'recency': recency}
    }))
    print("Triage result:", triage)

    plan = asyncio.run(BUS.call('engage.plan', {
        'lead_id': lead_id,
        'triage_result': triage
    }))
    print("Plan chosen:", plan)

    exec_res = asyncio.run(BUS.call('engage.execute', plan))
    print("Execution outcome:", exec_res)

    rec = asyncio.run(BUS.call('campaign.recommend', {'lead_id': lead_id}))
    print("Campaign recommendations:", rec)

    # inspect episodic
    episodes = memory_fabric.query_episodes(lead_id)
    print("Episodes logged:", len(episodes))

    return {'lead_id': lead_id, 'triage': triage, 'plan': plan, 'exec': exec_res, 'rec': rec}


if __name__ == '__main__':
    # simulate multiple leads
    for i in range(3):
        simulate_lead_flow(score=0.6 + (i*0.15), recency=0.5 + (i*0.2))
        time.sleep(0.5)
    print("\nSimulation complete. Inspect profiles via control_plane endpoints if desired.")
