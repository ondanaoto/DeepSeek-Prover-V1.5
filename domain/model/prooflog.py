from dataclasses import dataclass, field

@dataclass
class Result:
    passed: bool
    complete: bool
    verify_time: float
    sorries: list[str] = field(default_factory=list)
    tactics: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    infos: list[str] = field(default_factory=list)
    system_messages: str = ''
    system_errors: str | None = None
    verified_code: str | None = None

@dataclass
class ProofLog:
    problem_name: str
    sample_info: dict
    formal_statement: str
    proof_code: str
    result: Result
