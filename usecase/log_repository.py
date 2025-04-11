from dataclasses import dataclass
import json

from domain.model.prooflog import ProofLog

@dataclass
class LogRepository:
    dir_name: str
    def __post_init__(self):
        """
        Create directory if it does not exist.
        """
        import os
        os.makedirs(self.dir_name, exist_ok=True)

    def save(self, logs: dict[str, tuple[list[ProofLog], list[ProofLog]]]):
        """
        Save logs to a file.
        """
        success_lst, fail_lst = [], []
        for log in logs.values():
            success_lst.extend(log[0])
            fail_lst.extend(log[1])
        with open(f"{self.dir_name}/success.jsonl", "w") as f:
            for log in success_lst:
                f.write(f"{json.dumps(parse_prooflog(log))}\n")
        with open(f"{self.dir_name}/fail.jsonl", "w") as f:
            for log in fail_lst:
                f.write(f"{json.dumps(parse_prooflog(log))}\n")

def parse_prooflog(log: ProofLog) -> dict:
    """
    Parse a proof log into a dictionary.
    """
    return {
        "problem_name": log.problem_name,
        "sample_info": log.sample_info,
        "formal_statement": log.formal_statement,
        "proof_code": log.proof_code,
        "result": {
            "passed": log.result.passed,
            "complete": log.result.complete,
            "verify_time": log.result.verify_time,
            "sorries": log.result.sorries,
            "tactics": log.result.tactics,
            "errors": log.result.errors,
            "warnings": log.result.warnings,
            "infos": log.result.infos,
            "system_messages": log.result.system_messages,
            "system_errors": log.result.system_errors,
            "verified_code": log.result.verified_code
        }
    }
