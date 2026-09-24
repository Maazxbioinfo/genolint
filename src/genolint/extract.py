import re
from typing import List
from genolint.model import Command

# List of genomic tools we want to track in v1
SUPPORTED_TOOLS = {"bcftools", "samtools", "gatk", "snpEff", "SnpSift"}

def extract_commands_from_text(text: str) -> List[Command]:
    commands = []
    lines = text.splitlines()
    
    for line_no, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()
        
        # Skip empty lines and comments
        if not stripped or stripped.startswith("#"):
            continue
            
        # Tokenize the line by whitespace
        tokens = stripped.split()
        if not tokens:
            continue
            
        tool = tokens[0]
        # Handle paths like /usr/bin/bcftools -> bcftools
        if "/" in tool:
            tool = tool.split("/")[-1]
            
        if tool in SUPPORTED_TOOLS:
            subcommand = tokens[1] if len(tokens) > 1 else ""
            # Extract all flags (tokens starting with -)
            flags = {token for token in tokens[2:] if token.startswith("-")}
            
            commands.append(Command(
                tool=tool,
                subcommand=subcommand,
                flags=flags,
                line_no=line_no,
                raw_line=raw_line
            ))
            
    return commands
