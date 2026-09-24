from typing import List
from genolint.model import Command, Finding

def check_gl004(commands: List[Command]) -> List[Finding]:
    findings = []
    # Truncated or problematic terms mapped to their full Sequence Ontology equivalents
    risky_terms = {"missense": "missense_variant", "synonymous": "synonymous_variant"}
    
    for cmd in commands:
        # Check for SnpSift filter commands
        if cmd.tool in ("SnpSift", "snpeff") and cmd.subcommand == "filter":
            # Check raw line content for risky terms
            for risky, correct in risky_terms.items():
                if risky in cmd.raw_line and correct not in cmd.raw_line:
                    findings.append(Finding(
                        rule_id="GL004",
                        message=f"Line {cmd.line_no}: `SnpSift filter` uses substring `{risky}` instead of full term `{correct}`. This can silently match zero records.",
                        line_no=cmd.line_no,
                        severity="error"
                    ))
    return findings
