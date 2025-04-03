
from enum import Enum
from prover.algorithms import Sampling, RMaxTS
from prover.utils import AttrDict


class AlgorithmKind(Enum):
    SAMPLING = 'Sampling'
    RMAX_TS = 'RMaxTS'


class ConfigV2:
    def __init__(
        self,
        data_path,
        data_split=None,
        data_repeat=1,
        # verifier
        lean_max_concurrent_requests=64,
        lean_memory_limit=10,
        lean_timeout=300,
        # model
        batch_size=32,
        model_path='deepseek-ai/DeepSeek-Prover-V1.5-RL',
        mode='cot',  # `cot` or `non-cot`
        temperature=1,
        max_tokens=2048,
        top_p=0.95,
        # algorithm
        n_search_procs=64,
        algorithm_kind=AlgorithmKind.SAMPLING,
        sample_num=128,
        log_interval=32
    ):
        # dataset
        self.data_path = data_path
        self.data_split = data_split
        self.data_repeat = data_repeat
        # verifier
        self.lean_max_concurrent_requests = lean_max_concurrent_requests
        self.lean_memory_limit = lean_memory_limit
        self.lean_timeout = lean_timeout
        # model
        self.batch_size = batch_size
        self.model_path = model_path
        self.mode = mode
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        # algorithm
        self.n_search_procs = n_search_procs
        self._sampler = None
        self.algorithm_kind = algorithm_kind.value
        self.sample_num = sample_num
        self.log_interval = log_interval
        self.sampler = dict(
            algorithm=self.algorithm,
            sample_num=self.sample_num,
            log_interval=self.log_interval,
        )

    @property
    def algorithm(self):
        registry = {
            "Sampling": Sampling,
            "RMaxTS": RMaxTS,
        }
        return registry[self.algorithm_kind]
    
    @property
    def model_args(self):
        return AttrDict(
            mode=self.mode,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p
        )
