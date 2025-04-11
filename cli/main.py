import argparse
from datetime import datetime

from usecase.prove import Prover
from domain.model.config_model import ConfigV2, AlgorithmKind
from usecase.read_proof import ProofReader
from usecase.log_repository import LogRepository
def main(
    log_dir: str,
    node_rank: int,
    world_size: int,
    data_path: str,
    data_repeat: int,
    lean_max_concurrent_requests: int,
    lean_memory_limit: int,
    lean_timeout: int,
    batch_size: int,
    model_path: str,
    mode: str,
    temperature: float,
    max_tokens: int,
    top_p: float,
    n_search_procs: int,
    algorithm_kind: str,
    sample_num: int,
    log_interval: int,
    ):
    config_v2 = ConfigV2(
        data_path=data_path,
        data_split=None,
        data_repeat=data_repeat,
        lean_max_concurrent_requests=lean_max_concurrent_requests,
        lean_memory_limit=lean_memory_limit,
        lean_timeout=lean_timeout,
        batch_size=batch_size,
        model_path=model_path,
        mode=mode,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        n_search_procs=n_search_procs,
        algorithm_kind=AlgorithmKind.from_string(algorithm_kind),
        sample_num=sample_num,
        log_interval=log_interval
    )
    prover = Prover()

    print("Starting proving process...")
    prover.prove(
        cfg=config_v2,
        node_rank=node_rank,
        world_size=world_size,
        log_dir=log_dir)
    print("Proving process completed.")

    print("Reading proof logs...")
    proof_reader = ProofReader()
    d = proof_reader.read(
        log_dir=log_dir
    )
    print("Proof logs read successfully.")

    print("Saving logs...")
    log_repository = LogRepository(log_dir)
    log_repository.save(d)
    print("Proving completed and logs saved.")

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Prover CLI")
    argparser.add_argument("--log_dir", type=str, default=f"logs/{datetime.now()}", help="Directory to save logs")
    argparser.add_argument("--node_rank", type=int, default=0)
    argparser.add_argument("--world_size", type=int, default=1)
    argparser.add_argument("--data_path", type=str, default="/data/nontrivial_conjectures.jsonl", help="Path to the data file")
    argparser.add_argument("--data_repeat", type=int, default=1, help="Number of times to repeat the data")
    argparser.add_argument("--lean_max_concurrent_requests", type=int, default=64, help="Max concurrent requests for Lean")
    argparser.add_argument("--lean_memory_limit", type=int, default=10, help="Memory limit for Lean")
    argparser.add_argument("--lean_timeout", type=int, default=300, help="Timeout for Lean")
    argparser.add_argument("--batch_size", type=int, default=32, help="Batch size for the model")
    argparser.add_argument("--model_path", type=str, default='deepseek-ai/DeepSeek-Prover-V1.5-RL', help="Path to the model")
    argparser.add_argument("--mode", type=str, choices=["cot", "non-cot"], default="cot", help="Mode for the model")
    argparser.add_argument("--temperature", type=float, default=1.0, help="Temperature for the model")
    argparser.add_argument("--max_tokens", type=int, default=2048, help="Max tokens for the model")
    argparser.add_argument("--top_p", type=float, default=0.95, help="Top-p for the model")
    argparser.add_argument("--n_search_procs", type=int, default=64, help="Number of search processes")
    argparser.add_argument("--algorithm_kind", type=str, choices=["Sampling", "RMaxTS"], default="Sampling", help="Algorithm kind")
    argparser.add_argument("--sample_num", type=int, default=128, help="Number of samples")
    argparser.add_argument("--log_interval", type=int, default=32, help="Log interval")

    args = argparser.parse_args()
    main(
        log_dir=args.log_dir,
        node_rank=args.node_rank,
        world_size=args.world_size,
        data_path=args.data_path,
        data_repeat=args.data_repeat,
        lean_max_concurrent_requests=args.lean_max_concurrent_requests,
        lean_memory_limit=args.lean_memory_limit,
        lean_timeout=args.lean_timeout,
        batch_size=args.batch_size,
        model_path=args.model_path,
        mode=args.mode,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        top_p=args.top_p,
        n_search_procs=args.n_search_procs,
        algorithm_kind=args.algorithm_kind,
        sample_num=args.sample_num,
        log_interval=args.log_interval
    )
