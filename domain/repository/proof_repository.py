import json

def save(result: str, output: dict) -> None:
    # make json
    with open('/data/proofs.jsonl', 'a') as f:
        f.write(json.dumps({
            'result': result,
            'output': output,
        }) + '\n')
