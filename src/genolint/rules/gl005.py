from typing import List
from genolint.model import Command, Finding

def check_gl005(commands: List[Command]) -> List[Finding]:
    findings = []
    has_chr_prefix = False
    has_naked_prefix = False
    chr_line = 0
    naked_line = 0
    
    # Common chromosome identifiers to scan for
    chromosomes = {str(i) for i in range(1, 23)} | {"X", "Y", "MT"}
    
    for cmd in commands:
        for flag in cmd.flags:
            # Check for chr-prefixed chromosomes (e.g., chr20)
            if any(flag.endswith(f"chr{c}") or f"chr{c}" in flag for c in chromosomes):
                has_chr_prefix = True
                chr_line = cmd.line_no
            # Check for naked chromosome numbers (e.g., 20 without chr)
            elif any(flag == c or flag.endswith(f":{c}") for c in chromosomes):
                has_naked_prefix = True
                naked_line = cmd.line_no
                
        # Also check raw line text for positional parameters
        for token in cmd.raw_line.split():
            if any(token == f"chr{c}" for c in chromosomes):
                has_chr_prefix = True
                if not chr_line: chr_line = cmd.line_no
            elif any(token == c for c in chromosomes):
                has_naked_prefix = True
                if not naked_line: naked_line = cmd.line_no

    if has_chr_prefix and has_naked_prefix:
        findings.append(Finding(
            rule_id="GL005",
            message=f"Contig-naming mismatch detected across script (mixing `chr`-prefixed and naked chromosome names around lines {chr_line}/{naked_line}). This causes silent empty intersections.",
            line_no=chr_line,
            severity="error"
        ))
        
    return findings
