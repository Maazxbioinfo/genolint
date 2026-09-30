import re
import shlex
from typing import List
from genolint.model import Command, Finding

CHROMS = {str(i) for i in range(1, 23)} | {"X", "Y", "MT"}

# Options whose value can name a contig/region. Bare integers anywhere else
# (thread counts, quality cutoffs) are not contig names.
REGION_OPTS = {
    "bcftools": {"-r", "--regions", "-t", "--targets"},
    "gatk": {"-L", "--intervals", "-XL", "--exclude-intervals"},
}
# Positional region such as 20:1000-2000
REGION_TOKEN = re.compile(r"^\^?(?:chr)?(?:\d+|X|Y|MT):\d")


def _tokens(raw_line: str) -> List[str]:
    raw_line = re.sub(r"\\\r?\n", " ", raw_line)
    try:
        return shlex.split(raw_line)
    except ValueError:
        return raw_line.split()


def _has_naked_contig(cmd: Command) -> bool:
    opts = REGION_OPTS.get(cmd.tool.lower(), set())
    tokens = _tokens(cmd.raw_line)
    for i, tok in enumerate(tokens):
        value = None
        if tok in opts and i + 1 < len(tokens):
            value = tokens[i + 1]
        elif "=" in tok and tok.split("=", 1)[0] in opts:
            value = tok.split("=", 1)[1]
        elif REGION_TOKEN.match(tok):
            value = tok
        if value is None:
            continue
        for part in value.split(","):
            if part.lstrip("^").split(":", 1)[0] in CHROMS:
                return True
    return False


def check_gl005(commands: List[Command]) -> List[Finding]:
    findings = []
    has_chr_prefix = False
    has_naked_prefix = False
    chr_line = 0
    naked_line = 0

    for cmd in commands:
        # chr-prefixed names (e.g. chr20) are unambiguous
        for flag in cmd.flags:
            if any(flag.endswith(f"chr{c}") or f"chr{c}" in flag for c in CHROMS):
                has_chr_prefix = True
                chr_line = cmd.line_no

        for token in cmd.raw_line.split():
            if any(token == f"chr{c}" for c in CHROMS):
                has_chr_prefix = True
                if not chr_line:
                    chr_line = cmd.line_no

        # bare names only count where a contig can actually appear
        if _has_naked_contig(cmd):
            has_naked_prefix = True
            if not naked_line:
                naked_line = cmd.line_no

    if has_chr_prefix and has_naked_prefix:
        findings.append(Finding(
            rule_id="GL005",
            message=f"Contig-naming mismatch detected across script (mixing `chr`-prefixed and naked chromosome names around lines {chr_line}/{naked_line}). This causes silent empty intersections.",
            line_no=chr_line,
            severity="error"
        ))

    return findings
