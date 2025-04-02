from pydantic import BaseModel, Field
from typing import Literal

# Request models
class ProveRequest(BaseModel):
    data_path: str = 'datasets/minif2f.jsonl'
    data_split: list[str] = Field(default=[])
    data_repeat: int = 1
    lean_max_concurrent_requests: int = 64
    lean_memory_limit: int = 10
    lean_timeout: int = 300
    batch_size: int = 32
    model_path: str = 'deepseek-ai/DeepSeek-Prover-V1.5-RL'
    mode: Literal['cot', 'non-cot'] = 'cot'
    temperature: float = 1.0
    max_tokens: int = 2048
    top_p: float = 0.95
    n_search_procs: int = 64
    algorithm_kind: Literal['Sampling', 'RMaxTS'] = 'Sampling'
    sample_num: int = 128
    log_interval: int = 32
    node_rank: int = 0
    world_size: int = 1

class ReadProofRequest(BaseModel):
    log_dir: str

# Response models
class ResultModel(BaseModel):
    passed: bool
    complete: bool
    verify_time: float
    sorries: list[str] = Field(default_factory=list)
    tactics: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    infos: list[str] = Field(default_factory=list)
    system_messages: str = ''
    system_errors: str | None = None
    verified_code: str | None = None

class ProofLogModel(BaseModel):
    problem_name: str
    sample_info: dict[str, str | int]
    formal_statement: str
    proof_code: str
    result: ResultModel

class ProofReadResponse(BaseModel):
    data: dict[str, tuple[list[ProofLogModel], list[ProofLogModel]]]

class ProveResponse(BaseModel):
    status: str
    log_dir: str
    task_id: str
