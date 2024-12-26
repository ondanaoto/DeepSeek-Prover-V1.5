import json

def fetch_conjectures(
        nontrivial_only: bool = False,
) -> list[str]:
    with open('/data/eval_conjecture_result.jsonl', 'r') as f:
        conjectures = [json.loads(line) for line in f]
        
    conjectures = [c for c in conjectures if c["grammatical"]]
    if nontrivial_only:
        conjectures = [c for c in conjectures if not (c["already_exists"] or c["aesop_provable"]) ]
    
    return [c["conjecture"] for c in conjectures]
