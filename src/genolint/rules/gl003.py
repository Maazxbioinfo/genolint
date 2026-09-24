from typing import List
from genolint.model import Command, Finding

def check_gl003(commands: List[Command]) -> List[Finding]:
    findings = []
    for cmd in commands:
        if cmd.tool == "bcftools" and cmd.subcommand == "view":
            # Check if both -r and -R flags are present
            has_r = "-r" in cmd.flags
            has_capital_r = "-R" in cmd.flags
            
            if has_r and has_capital_r:
                findings.append(Finding(
                    rule_id="GL003",
                    message=f"Line {cmd.line_no}: `bcftools view` uses both `-r` and `-R` flags. These are conflicting region options and should not be used together.",
                    line_no=cmd.line_no,
                    severity="error"
                ))
    return findings
