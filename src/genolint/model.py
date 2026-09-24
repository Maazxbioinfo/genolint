from dataclasses import dataclass, field
from typing import List, Set

@dataclass
class Command:
    tool: str
    subcommand: str
    flags: Set[str] = field(default_factory=set)
    line_no: int = 0
    raw_line: str = ""

@dataclass
class Finding:
    rule_id: str
    message: str
    line_no: int
    severity: str = "error"
