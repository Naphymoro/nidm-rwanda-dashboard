"""Capture NDIM MCP tool schemas and real tool results for the local-model benchmark."""
import asyncio, json
from deerflow.mcp.tools import get_mcp_tools

WS = 'ndim-core'
A = ('[E2E TEST] Households in Niboye say the improved stoves save charcoal and they trust the health worker who showed '
     'them, but the price is too high and some neighbours heard a rumour that the smoke makes food taste bad.')
B = ('[E2E TEST] In Gatenga the cooperative leader explained the subsidy, yet families worry about repair costs and '
     'whether spare parts can be found nearby. Several said they would adopt if a neighbour they trust used one first.')

async def main():
    tools = {t.name: t for t in await get_mcp_tools() if t.name.startswith('ndim_')}
    schemas = []
    for t in tools.values():
        params = t.args_schema if isinstance(t.args_schema, dict) else t.args_schema.model_json_schema()
        schemas.append({'type': 'function', 'function': {'name': t.name, 'description': t.description, 'parameters': params}})
    async def call(name, **args):
        out = await tools[name].ainvoke(args)
        text = out if isinstance(out, str) else out[0]['text'] if isinstance(out, list) and isinstance(out[0], dict) else str(out)
        return json.loads(text)
    fx = {'guide': await call('ndim_journey_guide')}
    q = 'How might trusted messengers change clean cooking adoption?'
    fx['start'] = await call('ndim_journey_start', workspace_id=WS, question=q, question_confirmation='Yes, that is my question.')
    jid = fx['start']['journey_id']
    rec = lambda t, p: {'text': t, 'admin_unit': p, 'source_name': 'E2E synthetic', 'period': '2026-Q2', 'consent': 'synthetic'}
    fx['evidence'] = await call('ndim_journey_add_evidence', workspace_id=WS, journey_id=jid, records=[rec(A, 'Kicukiro / Niboye'), rec(B, 'Kicukiro / Gatenga')])
    await call('ndim_journey_record_decisions', workspace_id=WS, journey_id=jid, approval_statement='Accept both.',
               decisions=[{'record_id': r['record_id'], 'decision': 'accept'} for r in fx['evidence']['records']])
    for stage, extra in [('encoding', {}), ('compartmental', {}), ('agents', {}),
                         ('digital', {'observed_adoption': 0.2, 'trust_shift': 0.0, 'barrier_shift': 0.05, 'approval_statement': 'Our June survey: 20%.'}),
                         ('bayes', {}), ('rl', {}), ('graph', {}), ('inoculation', {})]:
        fx[stage] = await call('ndim_journey_run_stage', workspace_id=WS, journey_id=jid, stage=stage, **extra)
    json.dump({'question': q, 'tools': schemas, 'results': fx}, open('/tmp/fixtures.json', 'w'), ensure_ascii=False)
    print('tools', len(schemas), 'results', list(fx))
asyncio.run(main())
