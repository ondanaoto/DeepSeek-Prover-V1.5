import json

def fetch_conjecture_datas(
        nontrivial_only: bool = False,
) -> list[str, str, str]:
    '''
    return a list of tuples (conjecture_id, input_seed, conjecture).
    '''
    with open('/data/eval_conjecture_result.jsonl', 'r') as f:
        conjectures = [json.loads(line) for line in f]

    conjectures = [c for c in conjectures if c["grammatical"]]
    if nontrivial_only:
        conjectures = [c for c in conjectures if not c["already_exists"]]

    return [(c["conjecture_id"], c["input"], c["conjecture"]) for c in conjectures]
