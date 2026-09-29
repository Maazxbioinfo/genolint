"""Turn a Snakefile into plain shell text so the normal extractor can lint it.

Only `shell:` directives are handled. Every other line is blanked, and the
commands are placed on the line where they start in the Snakefile, so
reported line numbers match the source.
"""
import ast
import os
import re
import textwrap
from typing import List, Tuple

_RULE = re.compile(r"^\s*rule\s+\w*\s*:", re.M)
_SHELL = re.compile(r"^(\s*)shell\s*:\s*(.*)$")


def is_snakemake(filepath: str, content: str) -> bool:
    name = os.path.basename(filepath).lower()
    if name == "snakefile" or name.endswith((".smk", ".snakefile")):
        return True
    return bool(_RULE.search(content))


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def _strip_quotes(line: str) -> str:
    s = line.strip()
    s = re.sub(r"""^[rRfFbBuU]{0,2}(\"\"\"|'''|"|')""", "", s)
    s = re.sub(r"""(\"\"\"|'''|"|')$""", "", s)
    return s


def _line_starts(block_lines: List[str], node: ast.AST) -> List[int]:
    """block_lines index where each line of the evaluated string begins.

    Python joins a physical line ending in an odd number of backslashes to the
    next one, so that next line does not start a new line of the string.
    """
    starts, new_line = [], True
    for p in range(node.lineno - 1, node.end_lineno):
        if new_line:
            starts.append(p)
        line = block_lines[p]
        new_line = (len(line) - len(line.rstrip("\\"))) % 2 == 0
    return starts


def _block_to_commands(block_lines: List[str]) -> List[Tuple[int, str]]:
    """Return (offset, command) pairs; offset indexes into block_lines."""
    src = "(" + "\n".join(block_lines) + "\n)"
    try:
        node = ast.parse(src, mode="eval").body
    except (ValueError, SyntaxError):
        node = None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        starts = _line_starts(block_lines, node)
        value = textwrap.dedent(node.value)
        return [
            (starts[min(n, len(starts) - 1)], l.strip())
            for n, l in enumerate(value.splitlines())
            if l.strip()
        ]
    # Fallback for f-strings, .format() calls, etc.: strip quotes line by line
    out = []
    for idx, l in enumerate(block_lines):
        if l.strip() and not l.strip().startswith("#"):
            s = _strip_quotes(l)
            if s:
                out.append((idx, s))
    return out


def snakemake_to_shell(text: str) -> str:
    lines = text.splitlines()
    out = [""] * len(lines)
    i = 0
    while i < len(lines):
        m = _SHELL.match(lines[i])
        if not m:
            i += 1
            continue
        base = len(m.group(1))
        block = [m.group(2)]
        j = i + 1
        while j < len(lines) and (not lines[j].strip() or _indent(lines[j]) > base):
            block.append(lines[j])
            j += 1
        for offset, cmd in _block_to_commands(block):
            row = i + offset
            if row < len(out):
                out[row] = f"{out[row]} ; {cmd}" if out[row] else cmd
        i = j
    return "\n".join(out) + "\n"
