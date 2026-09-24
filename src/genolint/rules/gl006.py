import shlex
from typing import List

from genolint.model import Command, Finding

# Flags that consume the next token as their value (so it is not an input file)
VIEW_VALUE_FLAGS = {
    "-o", "--output", "-O", "--output-type", "-r", "--regions", "-R",
    "--regions-file", "-t", "--targets", "-T", "--targets-file", "-i",
    "--include", "-e", "--exclude", "-f", "--apply-filters", "-s",
    "--samples", "-S", "--samples-file", "-c", "--min-ac", "-C", "--max-ac",
    "-g", "--genotype", "-m", "--min-alleles", "-M", "--max-alleles",
    "-v", "--types", "-V", "--exclude-types", "-q", "--min-af", "-Q",
    "--max-af", "--threads", "--regions-overlap", "--targets-overlap",
    ">", ">>", "2>",
}
INDEX_VALUE_FLAGS = {"-o", "--output", "--output-file", "-m", "--min-shift",
                     "--threads", ">", ">>", "2>"}
TABIX_VALUE_FLAGS = {"-p", "--preset", "-s", "-b", "-e", "-c", "-m", "-0"}

VCF_EXTS = (".vcf", ".vcf.gz", ".bcf")


def _tokens(raw_line: str) -> List[str]:
    try:
        return shlex.split(raw_line)
    except ValueError:
        return raw_line.split()


def _positionals(tokens: List[str], value_flags) -> List[str]:
    """Non-flag tokens, skipping the values that belong to value-taking flags."""
    out, i = [], 0
    while i < len(tokens):
        t = tokens[i]
        if t in value_flags:
            i += 2
            continue
        if t.startswith("-") and t != "-":
            i += 1
            continue
        out.append(t)
        i += 1
    return out


def _option_value(tokens: List[str], names) -> str:
    for i, t in enumerate(tokens):
        if t in names and i + 1 < len(tokens):
            return tokens[i + 1]
        for n in names:
            if n.startswith("--") and t.startswith(n + "="):
                return t.split("=", 1)[1]
    return ""


def _writes_index(tokens: List[str]) -> bool:
    return any(t == "-W" or t == "--write-index" or t.startswith("--write-index=")
               or (t.startswith("-W") and not t.startswith("--"))
               for t in tokens)


def _uses_region(tokens: List[str]) -> bool:
    for t in tokens:
        if t in ("-r", "-R", "--regions", "--regions-file"):
            return True
        if t.startswith(("--regions=", "--regions-file=")):
            return True
        if len(t) > 2 and t[:2] in ("-r", "-R") and not t.startswith("--"):
            return True
    return False


def check_gl006(commands: List[Command]) -> List[Finding]:
    findings = []
    indexed_files = set()

    for cmd in commands:
        tokens = _tokens(cmd.raw_line)
        if not tokens:
            continue
        tool = tokens[0]

        # --- Things that create an index -------------------------------------
        if tool == "bcftools" and len(tokens) > 1 and tokens[1] == "index":
            for f in _positionals(tokens[2:], INDEX_VALUE_FLAGS):
                indexed_files.add(f)

        if tool == "tabix":
            for f in _positionals(tokens[1:], TABIX_VALUE_FLAGS):
                indexed_files.add(f)

        if tool == "bcftools" and _writes_index(tokens):
            out = _option_value(tokens, ("-o", "--output"))
            if out:
                indexed_files.add(out)

        # --- Region options that need an index -------------------------------
        if tool == "bcftools" and len(tokens) > 1 and tokens[1] == "view":
            args = tokens[2:]
            if not _uses_region(args):
                continue
            inputs = [p for p in _positionals(args, VIEW_VALUE_FLAGS)
                      if p.endswith(VCF_EXTS)]
            for input_file in inputs:
                if input_file not in indexed_files:
                    findings.append(Finding(
                        rule_id="GL006",
                        message=(f"Line {cmd.line_no}: `bcftools view` uses region "
                                 f"options on `{input_file}` but no prior index step "
                                 f"was found in this script. This is likely to fail "
                                 f"at runtime unless the index already exists."),
                        line_no=cmd.line_no,
                        severity="warning",
                    ))
    return findings
