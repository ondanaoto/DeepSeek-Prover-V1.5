import os
import argparse

import torch

from domain.model.config_model import ConfigV2
from prover.workers import DataLoader, Scheduler, ProcessScheduler, GeneratorProcess, SearchProcess
from prover.lean.verifier import Lean4ServerScheduler
from prover.utils import get_datetime

class Prover:
    def prove(
            self,
            cfg: ConfigV2,
            node_rank: int,
            world_size: int,
            log_dir: str,
        ):
        os.makedirs(log_dir, exist_ok=True)

        ngpus = torch.cuda.device_count()
        assert ngpus >= 1
        
        print("dataloader")
        # create data loader
        data_loader = DataLoader(
            data_path=cfg.data_path,
            data_split=cfg.data_split,
            data_repeat=cfg.data_repeat,
            node_rank=node_rank,
            world_size=world_size,
            log_dir=log_dir,
        )

        print("lean4serverscheduler")
        # build Lean verifier
        verifier_scheduler = Lean4ServerScheduler(
            max_concurrent_requests=cfg.lean_max_concurrent_requests,
            memory_limit=cfg.lean_memory_limit,
            timeout=cfg.lean_timeout,
            name='verifier',
        )

        print("processscheduler")
        # load LLM models on gpus
        generator_scheduler = ProcessScheduler(batch_size=cfg.batch_size, name='generator')
        llm_processes = [
            GeneratorProcess(
                local_rank=local_rank,
                node_rank=node_rank,
                model_path=cfg.model_path,
                task_queue=generator_scheduler.task_queue,
                request_statuses=generator_scheduler.request_statuses,
                lock=generator_scheduler.lock,
                args=cfg.model_args,
            )
            for local_rank in range(ngpus)
        ]

        print("scheduler")
        # create a unified scheduler interface
        scheduler = Scheduler(dict(
            verifier=verifier_scheduler,
            generator=generator_scheduler,
        ))

        # launch search processes
        search_processes = [
            SearchProcess(
                idx=i + node_rank * cfg.n_search_procs,
                log_dir=log_dir,
                tokenizer_path=cfg.model_path,
                scheduler=scheduler,
                data_loader=data_loader,
                cfg=cfg,
            )
            for i in range(min(cfg.n_search_procs, data_loader.size()))
        ]
        for p in search_processes:
            p.start()
        print(f'Complete launching {len(search_processes)} SearchProcesses')

        for p in llm_processes:
            p.start()
        print(f'Complete launching {len(llm_processes)} LLMProcesses')

        for p in search_processes:
            p.join()
        print(f'All {len(search_processes)} SearchProcesses stopped')

        scheduler.close()

        for p in llm_processes:
            p.join()
        print(f'All {len(llm_processes)} LLMProcesses stopped')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_dir", type=str, default=f'/data/logs/{get_datetime()}')
    parser.add_argument("--node_rank", type=int, default=0)
    parser.add_argument("--world_size", type=int, default=1)
    args = parser.parse_args()

    cfg = ConfigV2(data_path='datasets/minif2f.jsonl')
    log_dir = args.log_dir
    node_rank = args.node_rank
    world_size = args.world_size
    prover_service = Prover()
    prover_service.prove(
        cfg=cfg,
        log_dir=log_dir, 
        node_rank=node_rank,
        world_size=world_size
        )
