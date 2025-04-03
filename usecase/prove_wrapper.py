import argparse
import json
import sys

from domain.model.config_model import ConfigV2, AlgorithmKind
from usecase.prove import Prover

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_file", type=str, required=True, help="Path to JSON config file")
    parser.add_argument("--log_dir", type=str, required=True, help="Directory for logs")
    parser.add_argument("--node_rank", type=int, default=0, help="Node rank")
    parser.add_argument("--world_size", type=int, default=1, help="World size")
    parser.add_argument("--task_id", type=str, required=True, help="Task ID")
    args = parser.parse_args()

    # Load config from JSON file
    with open(args.config_file, "r") as f:
        config_dict = json.load(f)
    
    # Convert algorithm_kind from int to enum
    algorithm_kind_val = config_dict.pop("algorithm_kind")
    algorithm_kind = AlgorithmKind(algorithm_kind_val)
    
    # Create ConfigV2 instance
    config = ConfigV2(
        **config_dict,
        algorithm_kind=algorithm_kind
    )
    
    try:
        prover_service = Prover()
        prover_service.prove(
            cfg=config,
            log_dir=args.log_dir,
            node_rank=args.node_rank,
            world_size=args.world_size
        )
        # Success
        sys.exit(0)
    except Exception as e:
        print(f"Error in prove_wrapper: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()