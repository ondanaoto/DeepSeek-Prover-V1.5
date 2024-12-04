import json

def fetch_all() -> list[str]:
    with open('/data/conjectures.jsonl', 'r') as f:
        conjectures = [json.loads(line) for line in f]
        
    conjectures = [c['conjecture'] for c in conjectures]
    return conjectures

def fetch_by_datetime(datetime: str) -> list[str]:
    with open('/data/conjectures.jsonl', 'r') as f:
        conjectures = [json.loads(line) for line in f]
        
    conjectures = [c['conjecture'] for c in conjectures if c['experiment_date_time'] == datetime]
    return conjectures