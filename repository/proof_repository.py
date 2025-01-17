import os
import json

def save(result: str, output: dict) -> None:
    # make json
    with open('/data/proofs.jsonl', 'a') as f:
        f.write(json.dumps({
            'result': result,
            'output': output,
        }) + '\n')

def write_new_theorems(id_theorems: list[tuple[str, str]]) -> None:
    for conjecture_id, theorem in id_theorems:
        parent_dir = '/LeanLib/LeanLib/A' + conjecture_id.split('_')[0]
        file_name = 'A' + '_'.join(conjecture_id.split('_')[1:]) + '.lean'

        os.makedirs(parent_dir, exist_ok=True)
        with open(os.path.join(parent_dir, file_name), 'w') as f:
            f.write(theorem)