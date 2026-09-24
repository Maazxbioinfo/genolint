import os
import re
import shlex
from typing import List, Optional

from genolint.model import Command, Finding

# concat options that consume the next token as a value
CONCAT_VALUE_FLAGS = {
    "-d", "--rm-dups", "-f", "--file-list", "-L", "--ligate-max",
    "-o", "--output", "-O", "--output-type", "-q", "--min-PQ",
    "-r", "--regions", "-R", "--regions-file", "--threads",
    ">", ">>", "2>",
}
NO_OVERLAP_FLAGS = {"-a", "--allow-overlaps", "-n", "--naive", "--naive-force"}
FILE_LIST_FLAGS = {"-f", "--file-list"}
SHARD_WORDS = ("shard", "part", "chunk", "window", "scatter", "batch", "split")

CHR_LABEL = re.compile(r"(?:^|[._\-])chr(\d{1,2}|X|Y|M|MT)(?=$|[._\-])", re.I)
BARE_LABEL = re.compile(r"^(\d{1,2}|X|Y)$", re.I)
EXTS = (".vcf.gz", ".vcf", ".bcf", ".gz")


def _tokens(raw_line: str) -> List[str]:
    try:
        return shlex.split(raw_line)
    except ValueError:
        return raw_line.split()


def _input_files(args: List[str]) -> List[str]:
    out, i = [], 0
    while i < len(args):
        t = args[i]
        if t in CONCAT_VALUE_FLAGS:
            i += 2
            continue
        if t.startswith("-") and t != "-":
            i += 1
            continue
        out.append(t)
        i += 1
    return out


def _stem(path: str) -> str:
    name = os.path.basename(path)
    for ext in EXTS:
        if name.lower().endswith(ext):
            return name[: -len(ext)]
    return name


def _chrom_label(path: str) -> Optional[str]:
    stem = _stem(path)
    m = CHR_LABEL.search(stem)
    if m:
        return m.group(1).upper()
    m = BARE_LABEL.match(stem)
    if m:
        return m.group(1).upper()
    return None


def _looks_per_chromosome(files: List[str]) -> bool:
    """True only if every input has a chromosome label and all labels differ."""
    if len(files) < 2:
        return False
    if any(w in _stem(f).lower() for f in files for w in SHARD_WORDS):
        return False
    labels = [_chrom_label(f) for f in files]
    if any(label is None for label in labels):
        return False
    return len(set(labels)) == len(labels)


def check_gl002(commands: List[Command]) -> List[Finding]:
    findings = []

    for cmd in commands:
        if cmd.tool != "bcftools" or cmd.subcommand != "concat":
            continue

        tokens = _tokens(cmd.raw_line)
        if "concat" not in tokens:
            continue
        args = tokens[tokens.index("concat") + 1:]

        if any(t in NO_OVERLAP_FLAGS for t in args):
            continue
        # Inputs come from a list file we cannot see: stay quiet
        if any(t in FILE_LIST_FLAGS or t.startswith("--file-list=") for t in args):
            continue

        files = _input_files(args)
        if _looks_per_chromosome(files):
            continue

        findings.append(Finding(
            rule_id="GL002",
            message=(f"Line {cmd.line_no}: `bcftools concat` without `-a` "
                     f"(--allow-overlaps). Plain concat expects ordered, "
                     f"non-overlapping inputs, so if these files can overlap "
                     f"(shards, windows, multiple callers) the result may be "
                     f"wrong or the command may fail. Use `-a` for overlapping "
                     f"inputs (requires indexed files), or ignore this if they "
                     f"are one file per chromosome."),
            line_no=cmd.line_no,
            severity="warning",
        ))
    return findings
