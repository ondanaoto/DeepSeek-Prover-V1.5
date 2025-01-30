import os
import re
import json

def save(result: str, output: dict) -> None:
    # make json
    with open('/data/proofs.jsonl', 'a') as f:
        f.write(json.dumps({
            'result': result,
            'output': output,
        }) + '\n')

def write_new_theorems(id_theorems: list[tuple[str, str, str]]) -> None:
    for conjecture_id, input_seed, theorem in id_theorems:
        id_num = conjecture_id.split('_')[-1]
        filepath = _get_save_filepath(input_seed, id_num)
        
        dirname = os.path.dirname(filepath)

        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(filepath, 'w') as f:
            f.write(theorem)

def _get_save_filepath(input_seed: str, id_num: str) -> str:
    input_seed = input_seed.replace('.', '/')
    if not re.match(r'^Mathlib/A\d+', input_seed):
        return 'mathlib4/Mathlib/A0' + input_seed[len('Mathlib'):] + '.lean'
    else:
        num = int(re.search(r'A(\d+)', input_seed).group(1)) + 1
        num_str = str(num)
        return 'mathlib4/Mathlib/A' + num_str + input_seed[len('Mathlib/A' + num_str):] + id_num + '.lean'

