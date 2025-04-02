import os
import asyncio
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

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
    allow_origins=[f"http://app:{AIMATH_PORT}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store running prove tasks
running_tasks: Dict[str, str] = {}

def convert_algorithm_kind(algorithm_kind_str: str) -> AlgorithmKind:
    """Convert string to AlgorithmKind enum"""
    # With Pydantic Literal validation, we should only receive valid values
    # But we'll still handle the conversion explicitly for robustness
    if algorithm_kind_str == 'Sampling':
        return AlgorithmKind.SAMPLING
    elif algorithm_kind_str == 'RMaxTS':
        return AlgorithmKind.RMAX_TS
    else:
        # This should never happen due to Pydantic validation
        # but we'll default to Sampling if it somehow does
        return AlgorithmKind.SAMPLING

async def run_prove_task(
    config: ConfigV2,
    log_dir: str,
    node_rank: int,
    world_size: int,
    task_id: str
):
    """Background task to run the prove process"""
    try:
        # Create the log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Run the prove process in a separate thread to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: _run_prove_process(
            config=config,
            log_dir=log_dir,
            node_rank=node_rank,
            world_size=world_size,
            task_id=task_id
        ))
    except Exception as e:
        running_tasks[task_id] = f"failed: {str(e)}"

def _run_prove_process(
    config: ConfigV2,
    log_dir: str,
    node_rank: int,
    world_size: int,
    task_id: str
):
    """Execute the prove process in a separate thread"""
    try:
        prover = Prover()
        prover.prove(
            cfg=config,
            log_dir=log_dir,
            node_rank=node_rank,
            world_size=world_size
        )
        running_tasks[task_id] = "completed"
    except Exception as e:
        running_tasks[task_id] = f"failed: {str(e)}"

@app.post("/api/prove", response_model=ProveResponse)
async def prove(request: ProveRequest, background_tasks: BackgroundTasks):
    """
    Start a proof generation task
    """
    # Create log directory if not exists
    log_dir = '/data/logs'
    
    # os.makedirs(log_dir, exist_ok=True)
    
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
    
    # Start background task
    background_tasks.add_task(
        run_prove_task,
        config=config,
        log_dir=log_dir,
        node_rank=request.node_rank,
        world_size=request.world_size,
        task_id=task_id
    )
    
    # Store task status
    running_tasks[task_id] = "running"
    
    return ProveResponse(
        status="started",
        log_dir=log_dir,
        task_id=task_id
    )

@app.get("/api/prove/status/{task_id}")
async def get_prove_status(task_id: str):
    """
    Get the status of a running prove task
    """
    if task_id not in running_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"status": running_tasks[task_id]}

@app.post("/api/read_proof", response_model=ProofReadResponse)
async def read_proof(request: ReadProofRequest):
    """
    Read proof logs from a directory
    """
    try:
        proof_reader = ProofReader()
        data = proof_reader.read(request.log_dir)
        
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
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}
