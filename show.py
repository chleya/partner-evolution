import json
with open(r'F:\ai_partner_evolution\data\storage\beliefs.json', 'r', encoding='utf-8') as f:
    beliefs = json.load(f)
print(f"Total: {len(beliefs)}")
for b in beliefs:
    print(f"- {b.get('content')[:50]}... (conf:{b.get('confidence')})")
