from typing import List
from genolint.model import Command, Finding

def check_gl001(commands: List[Command]) -> List[Finding]:
    findings = []
    for cmd in commands:
        if cmd.tool == "bcftools" and cmd.subcommand == "view":
            # Check if it uses filter -f PASS (or similar)
            has_filter = any(f.startswith("-f") for f in cmd.flags)
            # Check if proper compression/output flags are missing
            has_output_flag = any(f in cmd.flags for f in ("-o", "-Oz", "-Ob", "-b"))
            
            # If it filters but lacks explicit output compression flags, flag it as a risk
            if has_filter and not has_output_flag:
                findings.append(Finding(
                    rule_id="GL001",
                    message=f"Line {cmd.line_no}: `bcftools view` with filter used without explicit output compression flag (-Oz/-b/-o). This can cause silent uncompressed output format issues.",
                    line_no=cmd.line_no,
                    severity="error"
                ))
    return findings
