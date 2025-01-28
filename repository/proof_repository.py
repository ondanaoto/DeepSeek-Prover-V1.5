import os
import json

def save(result: str, output: dict) -> None:
    # make json
    with open('/data/proofs.jsonl', 'a') as f:
        f.write(json.dumps({
            'result': result,
            'output': output,
        }) + '\n')

def write_new_theorems(id_theorems: list[tuple[str, str, str]]) -> None:
    for _, input_seed, theorem in id_theorems:
        parent_dir = _get_save_dir(input_seed)

        os.makedirs(parent_dir, exist_ok=True)
        with open(parent_dir, 'w') as f:
            f.write(theorem)

def _get_save_dir(input_seed: str) -> str:
    input_seed = input_seed.replace('.', '/')
    if not input_seed.startswith('Mathlib/A'):
        return 'mathlib4/Mathlib/A0' + input_seed[len('Mathlib'):] + '.lean'
    else:
        return 'mathlib4/Mathlib/A' + str(int(input_seed.split('/')[-1][1]) + 1) + '.lean'
