import json
import os
import subprocess
# ★ 非同期系のimportは削除
# import asyncio
# from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api.schema import (
    ProveRequest, 
    ReadProofRequest, 
    ProveResponse, 
    ProofReadResponse,
    ProofLogModel,
    ResultModel
)
from domain.model.config_model import ConfigV2, AlgorithmKind
from usecase.prove import Prover
from usecase.read_proof import ProofReader
from prover.utils import get_datetime

app = FastAPI(
    title="Mathematical Proof API",
    description="API for generating and reading mathematical proofs",
    version="1.0.0"
)

AIMATH_PORT = os.environ['AIMATH_PORT']
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", f"http://app:{AIMATH_PORT}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store running prove tasks
running_tasks = {}

def convert_algorithm_kind(algorithm_kind_str: str) -> AlgorithmKind:
    """Convert string to AlgorithmKind enum"""
    if algorithm_kind_str == 'Sampling':
        return AlgorithmKind.SAMPLING
    elif algorithm_kind_str == 'RMaxTS':
        return AlgorithmKind.RMAX_TS
    raise ValueError("unknown algorithm kind")

def _run_prove_process(
    config: ConfigV2,
    log_dir: str,
    node_rank: int,
    world_size: int,
    task_id: str
):
    """
    同期的にproveを実行する処理。
    以前は別スレッドで実行していたが、ここではシンプルに直列で処理する。
    """
    try:
        # 事前にディレクトリ作成
        os.makedirs(log_dir, exist_ok=True)
        
        # ConfigV2をJSON文字列に変換
        config_dict = {
            "data_path": config.data_path,
            "data_split": config.data_split,
            "data_repeat": config.data_repeat,
            "lean_max_concurrent_requests": config.lean_max_concurrent_requests,
            "lean_memory_limit": config.lean_memory_limit,
            "lean_timeout": config.lean_timeout,
            "batch_size": config.batch_size,
            "model_path": config.model_path,
            "mode": config.mode,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "top_p": config.top_p,
            "n_search_procs": config.n_search_procs,
            "algorithm_kind": config.algorithm_kind,  # enumの値を取得
            "sample_num": config.sample_num,
            "log_interval": config.log_interval
        }
        
        # 一時的なJSONファイルに設定を保存
        config_file = f"/tmp/config_{task_id}.json"
        with open(config_file, "w") as f:
            json.dump(config_dict, f)
        
        # 外部プロセスとしてprove_wrapper.pyを実行（同期的に待機）
        cmd = [
            "python", "usecase/prove_wrapper.py",  # prove_wrapper.pyへのパスを適切に設定
            "--config_file", config_file,
            "--log_dir", log_dir,
            "--node_rank", str(node_rank),
            "--world_size", str(world_size),
            "--task_id", task_id
        ]
        
        # 同期的に実行して完了を待つ
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        # 不要になった設定ファイルを削除
        os.remove(config_file)
        
        # エラーチェック
        if result.returncode != 0:
            error_message = result.stderr or "Unknown error occurred"
            running_tasks[task_id] = f"failed: {error_message}"
            raise RuntimeError(error_message)
            
        running_tasks[task_id] = "completed"
        return True

    except Exception as e:
        running_tasks[task_id] = f"failed: {str(e)}"
        raise

@app.post("/api/prove", response_model=ProveResponse)
def prove(request: ProveRequest):
    """
    Start a proof generation task (同期実行)
    重い処理は終わるまでHTTPレスポンスを返しません。
    """
    # Create log directory if not exists
    exp_datetime = get_datetime()
    log_dir = f'/data/logs/{exp_datetime}'
    
    # Create config
    config = ConfigV2(
        data_path=request.data_path,
        data_split=request.data_split,
        data_repeat=request.data_repeat,
        lean_max_concurrent_requests=request.lean_max_concurrent_requests,
        lean_memory_limit=request.lean_memory_limit,
        lean_timeout=request.lean_timeout,
        batch_size=request.batch_size,
        model_path=request.model_path,
        mode=request.mode,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
        top_p=request.top_p,
        n_search_procs=request.n_search_procs,
        algorithm_kind=convert_algorithm_kind(request.algorithm_kind),
        sample_num=request.sample_num,
        log_interval=request.log_interval
    )
    
    # Generate task ID
    task_id = f"prove_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # ステータスを "running" にしておく
    running_tasks[task_id] = "running"

    # ここで同期的に prove 処理を実行する
    try:
        _run_prove_process(
            config=config,
            log_dir=log_dir,
            node_rank=request.node_rank,
            world_size=request.world_size,
            task_id=task_id
        )
    except Exception as e:
        # 失敗時はHTTPExceptionに変換
        # running_tasksにはすでに "failed: ..." が入っている想定
        raise HTTPException(status_code=500, detail=str(e))
    
    # 成功したので "completed" がセットされている
    return ProveResponse(
        status="completed",
        exp_id=exp_datetime,
        task_id=task_id
    )

@app.get("/api/prove/status/{task_id}")
def get_prove_status(task_id: str):
    """
    Get the status of a prove task
    同期呼び出しのため、基本的にはリクエスト完了時点で終わっているはずだが
    状態管理のサンプルとして残している
    """
    if task_id not in running_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"status": running_tasks[task_id]}

@app.post("/api/read_proof", response_model=ProofReadResponse)
def read_proof(request: ReadProofRequest):
    """
    Read proof logs from a directory (同期)
    """
    try:
        proof_reader = ProofReader()
        data = proof_reader.read(request.exp_id)
        
        # Convert domain models to Pydantic models
        result_data = {}
        for key, (success_logs, failure_logs) in data.items():
            success_models = [
                ProofLogModel(
                    problem_name=log.problem_name,
                    sample_info=log.sample_info,
                    formal_statement=log.formal_statement,
                    proof_code=log.proof_code,
                    result=ResultModel(
                        passed=log.result.passed,
                        complete=log.result.complete,
                        verify_time=log.result.verify_time,
                        sorries=log.result.sorries,
                        tactics=log.result.tactics,
                        errors=log.result.errors,
                        warnings=log.result.warnings,
                        infos=log.result.infos,
                        system_messages=log.result.system_messages,
                        system_errors=log.result.system_errors,
                        verified_code=log.result.verified_code
                    )
                )
                for log in success_logs
            ]
            
            failure_models = [
                ProofLogModel(
                    problem_name=log.problem_name,
                    sample_info=log.sample_info,
                    formal_statement=log.formal_statement,
                    proof_code=log.proof_code,
                    result=ResultModel(
                        passed=log.result.passed,
                        complete=log.result.complete,
                        verify_time=log.result.verify_time,
                        sorries=log.result.sorries,
                        tactics=log.result.tactics,
                        errors=log.result.errors,
                        warnings=log.result.warnings,
                        infos=log.result.infos,
                        system_messages=log.result.system_messages,
                        system_errors=log.result.system_errors,
                        verified_code=log.result.verified_code
                    )
                )
                for log in failure_logs
            ]
            
            result_data[key] = (success_models, failure_models)
        
        return ProofReadResponse(data=result_data)
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health_check():
    """
    Health check endpoint (同期)
    """
    return {"status": "healthy"}
