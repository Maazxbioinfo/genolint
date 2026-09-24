import shlex
from typing import List, Optional, Tuple

from genolint.model import Command, Finding

# bcftools subcommands that write VCF/BCF and accept -O/-o
OUTPUT_COMMANDS = {"view", "concat", "merge", "norm", "annotate", "sort",
                   "filter", "call", "mpileup"}


def _tokens(raw_line: str) -> List[str]:
    try:
        return shlex.split(raw_line)
    except ValueError:
        return raw_line.split()


def _output_target(tokens: List[str]) -> Tuple[Optional[str], str]:
    """Return (target file, 'option' | 'redirect') or (None, '')."""
    for i, t in enumerate(tokens):
        if t in ("-o", "--output") and i + 1 < len(tokens):
            return tokens[i + 1], "option"
        if t.startswith("--output="):
            return t.split("=", 1)[1], "option"
        if t.startswith("-o") and len(t) > 2 and not t.startswith("--"):
            return t[2:], "option"
    for i, t in enumerate(tokens):
        if t in (">", ">>") and i + 1 < len(tokens):
            return tokens[i + 1], "redirect"
        if t.startswith(">") and not t.startswith(">&") and len(t.lstrip(">")) > 0:
            return t.lstrip(">"), "redirect"
    return None, ""


def _output_type(tokens: List[str]) -> Optional[str]:
    """First letter of the -O/--output-type value (z, b, u, v), or None."""
    for i, t in enumerate(tokens):
        if t in ("-O", "--output-type") and i + 1 < len(tokens):
            return tokens[i + 1][:1].lower()
        if t.startswith("--output-type="):
            return t.split("=", 1)[1][:1].lower()
        if t.startswith("-O") and len(t) > 2 and not t.startswith("--"):
            return t[2:3].lower()
    return None


def _expected_type(name: str) -> Optional[str]:
    n = name.lower()
    if n.endswith((".vcf.gz", ".vcf.bgz")):
        return "z"
    if n.endswith((".bcf", ".bcf.gz")):
        return "b"
    if n.endswith(".vcf"):
        return "v"
    return None


def _mismatch(expected: str, otype: str) -> bool:
    if expected == "z":
        return otype != "z"
    if expected == "b":
        return otype not in ("b", "u")
    return otype != "v"


def check_gl001(commands: List[Command]) -> List[Finding]:
    findings = []
    for cmd in commands:
        if cmd.tool != "bcftools" or cmd.subcommand not in OUTPUT_COMMANDS:
            continue

        tokens = _tokens(cmd.raw_line)
        target, kind = _output_target(tokens)
        if not target:
            continue
        expected = _expected_type(target)
        if expected is None:
            continue  # unknown extension or a {placeholder}: nothing to compare

        otype = _output_type(tokens)

        if otype is None:
            if expected == "v":
                continue  # plain VCF is the default
            if kind == "redirect":
                findings.append(Finding(
                    rule_id="GL001",
                    message=(f"Line {cmd.line_no}: `bcftools {cmd.subcommand}` "
                             f"redirects stdout to `{target}`, but with no output "
                             f"type stdout is uncompressed VCF, so the file will "
                             f"not match its extension. Add -Oz (or -Ob for .bcf)."),
                    line_no=cmd.line_no,
                    severity="error",
                ))
            else:
                findings.append(Finding(
                    rule_id="GL001",
                    message=(f"Line {cmd.line_no}: `bcftools {cmd.subcommand}` "
                             f"writes `{target}` without an output type. Some "
                             f"bcftools versions then write uncompressed VCF; "
                             f"add -Oz (or -Ob for .bcf) to be explicit."),
                    line_no=cmd.line_no,
                    severity="warning",
                ))
        elif _mismatch(expected, otype):
            findings.append(Finding(
                rule_id="GL001",
                message=(f"Line {cmd.line_no}: output type `-O{otype}` does not "
                         f"match the file name `{target}`."),
                line_no=cmd.line_no,
                severity="error",
            ))
    return findings
