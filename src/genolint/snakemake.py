"""Turn a Snakefile into plain shell text so the normal extractor can lint it.

Only `shell:` directives are handled. Every other line is blanked, and the
command text is placed starting at the line of the `shell:` keyword, so
reported line numbers point at the right place (approximately, for
multi-line commands).
"""
import ast
import os
import re
import textwrap
from typing import List

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


def _block_to_commands(block_lines: List[str]) -> List[str]:
    src = "(" + "\n".join(block_lines) + "\n)"
    try:
        value = ast.literal_eval(src)
        if isinstance(value, str):
            value = textwrap.dedent(value)
            return [l.strip() for l in value.splitlines() if l.strip()]
    except (ValueError, SyntaxError):
        pass
    # Fallback for f-strings, .format() calls, etc.: strip quotes line by line
    out = []
    for l in block_lines:
        if l.strip() and not l.strip().startswith("#"):
            s = _strip_quotes(l)
            if s:
                out.append(s)
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
        for k, cmd in enumerate(_block_to_commands(block)):
            if i + k < len(out):
                out[i + k] = cmd
        i = j
    return "\n".join(out) + "\n"
