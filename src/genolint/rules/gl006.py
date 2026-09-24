from typing import List
from genolint.model import Command, Finding

def check_gl006(commands: List[Command]) -> List[Finding]:
    findings = []
    indexed_files = set()
    
    for cmd in commands:
        # Track files that get indexed
        if cmd.tool == "bcftools" and cmd.subcommand == "index":
            for flag_or_arg in cmd.flags:
                if not flag_or_arg.startswith("-"):
                    indexed_files.add(flag_or_arg)
            # Also check raw line tokens for filename arguments
            tokens = cmd.raw_line.split()
            if len(tokens) > 2:
                for t in tokens[2:]:
                    if not t.startswith("-"):
                        indexed_files.add(t)
                        
        # Check if an operation needing an index uses a file
        if cmd.tool == "bcftools" and cmd.subcommand == "view":
            has_region = "-r" in cmd.flags or "-R" in cmd.flags
            if has_region:
                # Find input files in flags or raw line tokens
                tokens = cmd.raw_line.split()
                input_file = None
                for t in tokens[2:]:
                    if not t.startswith("-") and (t.endswith(".vcf") or t.endswith(".vcf.gz") or t.endswith(".bcf")):
                        input_file = t
                        break
                
                if input_file and input_file not in indexed_files:
                    findings.append(Finding(
                        rule_id="GL006",
                        message=f"Line {cmd.line_no}: `bcftools view` uses region options on `{input_file}` without a prior `bcftools index` call. This will fail at runtime.",
                        line_no=cmd.line_no,
                        severity="error"
                    ))
                    
    return findings
