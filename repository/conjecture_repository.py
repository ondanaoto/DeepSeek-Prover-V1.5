import json
import datetime

def fetch_conjecture_datas(
        nontrivial_only: bool = False,
        start_date: str = None,
) -> list[str, str, str]:
    '''
    return a list of tuples (conjecture_id, input_seed, conjecture).
    '''
    with open('/data/eval_conjecture_result.jsonl', 'r') as f:
        conjectures = [json.loads(line) for line in f]

    conjectures = [c for c in conjectures if c["grammatical"]]
    if nontrivial_only:
        conjectures = [c for c in conjectures if not c["already_exists"]]

    def is_new_date(conjecture_id: str, start_date: datetime) -> bool:
        target_date_str = '_'.join(conjecture_id.split('_')[:2])
        target_date = datetime.datetime.strptime(target_date_str, "%Y%m%d_%H%M%S")
        return target_date >= start_date

    if start_date:
        start_date = datetime.datetime.strptime(start_date, "%Y%m%d_%H%M%S")
        conjectures = [c for c in conjectures if is_new_date(c["conjecture_id"], start_date)]

    return [(c["conjecture_id"], c["input"], c["conjecture"]) for c in conjectures]

