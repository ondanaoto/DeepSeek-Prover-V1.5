import re

import torch
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams
from fastapi import FastAPI
from pydantic import BaseModel

from prover.lean.verifier import Lean4ServerScheduler

app = FastAPI()

class Question(BaseModel):
    code: str

model_name = "deepseek-ai/DeepSeek-Prover-V1.5-RL"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = LLM(model=model_name, max_num_batched_tokens=8192, seed=1, trust_remote_code=True)

lean4_scheduler = Lean4ServerScheduler(max_concurrent_requests=1, timeout=300, memory_limit=10, name='verifier')

prompt = r'''Complete the following Lean 4 code:

```lean4
'''

sampling_params = SamplingParams(
    temperature=1.0,
    max_tokens=2048,
    top_p=0.95,
    n=1,
)

@app.post("/prove/")
async def prove(question: Question):
    model_inputs = [prompt + question.code]
    model_outputs = model.generate(
        model_inputs,
        sampling_params,
        use_tqdm=False,
    )
    result = prompt + question.code + model_outputs[0].outputs[0].text

    request_id_list = lean4_scheduler.submit_all_request([re.search(r'```lean4\n(.*?)\n```', result, re.DOTALL).group(1)])
    outputs_list = lean4_scheduler.get_all_request_outputs(request_id_list)
    lean4_scheduler.close()

    return (outputs_list[0])
