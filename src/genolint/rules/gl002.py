from typing import List
from genolint.model import Command, Finding

def check_gl002(commands: List[Command]) -> List[Finding]:
    findings = []
    for cmd in commands:
        if cmd.tool == "bcftools" and cmd.subcommand == "concat":
            # Check if the allow-overlaps flag '-a' is present
            has_allow_overlaps = "-a" in cmd.flags
            
            if not has_allow_overlaps:
                findings.append(Finding(
                    rule_id="GL002",
                    message=f"Line {cmd.line_no}: `bcftools concat` used without the `-a` (allow-overlaps) flag. This can cause silent failures on overlapping SNP/indel positions.",
                    line_no=cmd.line_no,
                    severity="error"
                ))
    return findings
