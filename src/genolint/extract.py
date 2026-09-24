import re
import shlex
from typing import List, Optional

from genolint.model import Command

# List of genomic tools we want to track in v1
SUPPORTED_TOOLS = {"bcftools", "samtools", "gatk", "snpEff", "SnpSift", "tabix", "bgzip"}

# Leading VAR=value assignments and wrappers such as `time` are skipped
_PREFIX = re.compile(
    r"^\s*(?:(?:[A-Za-z_][A-Za-z0-9_]*=\S*|time|sudo|nohup|env|command|exec|nice)\s+)*"
)


def _logical_lines(text: str):
    """Yield (starting line number, text), joining backslash continuations."""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        start = i + 1
        cur = lines[i]
        while cur.rstrip().endswith("\\") and i + 1 < len(lines):
            cur = cur.rstrip()[:-1] + " " + lines[i + 1]
            i += 1
        yield start, cur
        i += 1


def _split_commands(line: str) -> List[str]:
    """Split one logical line on | || && ; & ( ) and backticks (outside quotes),
    keeping the original text of each piece. Redirects like 2>&1 stay intact."""
    parts: List[str] = []
    buf: List[str] = []
    quote = None
    i, n = 0, len(line)

    def flush():
        s = "".join(buf).strip()
        if s:
            parts.append(s)
        buf.clear()

    while i < n:
        c = line[i]
        if quote:
            buf.append(c)
            if c == "\\" and quote == '"' and i + 1 < n:
                buf.append(line[i + 1])
                i += 2
                continue
            if c == quote:
                quote = None
            i += 1
            continue
        if c == "\\" and i + 1 < n:
            buf.append(c)
            buf.append(line[i + 1])
            i += 2
            continue
        if c in "'\"":
            quote = c
            buf.append(c)
        elif c == "#" and (i == 0 or line[i - 1].isspace()):
            break
        elif c in ";()`":
            flush()
        elif c == "|":
            flush()
            if i + 1 < n and line[i + 1] in "|&":
                i += 1
        elif c == "&":
            prev = line[i - 1] if i else ""
            nxt = line[i + 1] if i + 1 < n else ""
            if (prev and prev in "<>") or nxt == ">":
                buf.append(c)  # part of a redirect such as 2>&1
            else:
                flush()
                if nxt == "&":
                    i += 1
        else:
            buf.append(c)
        i += 1
    flush()
    return parts


def _make_command(segment: str, line_no: int) -> Optional[Command]:
    seg = _PREFIX.sub("", segment, count=1).strip()
    if not seg:
        return None
    try:
        tokens = shlex.split(seg)
    except ValueError:
        tokens = seg.split()
    if not tokens:
        return None

    tool = tokens[0]
    # Handle paths like /usr/bin/bcftools -> bcftools
    if "/" in tool:
        tool = tool.split("/")[-1]
    if tool not in SUPPORTED_TOOLS:
        return None

    subcommand = tokens[1] if len(tokens) > 1 else ""
    flags = {t for t in tokens[2:] if t.startswith("-")}
    return Command(tool=tool, subcommand=subcommand, flags=flags,
                   line_no=line_no, raw_line=seg)


def extract_commands_from_text(text: str) -> List[Command]:
    commands: List[Command] = []
    for line_no, raw_line in _logical_lines(text):
        stripped = raw_line.strip()
        # Skip empty lines and comments
        if not stripped or stripped.startswith("#"):
            continue
        for segment in _split_commands(stripped):
            cmd = _make_command(segment, line_no)
            if cmd:
                commands.append(cmd)
    return commands
