import sys
from genolint.extract import extract_commands_from_text
from genolint.rules.gl001 import check_gl001
from genolint.rules.gl002 import check_gl002
from genolint.rules.gl003 import check_gl003
from genolint.rules.gl004 import check_gl004
from genolint.rules.gl005 import check_gl005
from genolint.rules.gl006 import check_gl006

def main():
    if len(sys.argv) < 2:
        print("Usage: genolint <script.sh>")
        sys.exit(1)
        
    filepath = sys.argv[1]
    print(f"Linting {filepath}...")
    
    try:
        with open(filepath, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)
        
    # 1. Extract commands
    commands = extract_commands_from_text(content)
    
    # 2. Run rules
    findings = []
    findings.extend(check_gl001(commands))
    findings.extend(check_gl002(commands))
    findings.extend(check_gl003(commands))
    findings.extend(check_gl004(commands))
    findings.extend(check_gl005(commands))
    findings.extend(check_gl006(commands))
    
    # 3. Report findings
    if findings:
        print(f"\n[!] Found {len(findings)} issue(s):")
        for finding in findings:
            print(f"  - [{finding.rule_id}] {finding.message}")
        sys.exit(1)
    else:
        print("\n[+] No issues found! Clean bill of health.")
        sys.exit(0)

if __name__ == "__main__":
    main()
