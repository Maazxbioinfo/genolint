import sys

from genolint.extract import extract_commands_from_text
from genolint.rules.gl001 import check_gl001
from genolint.rules.gl002 import check_gl002
from genolint.rules.gl003 import check_gl003
from genolint.rules.gl004 import check_gl004
from genolint.rules.gl005 import check_gl005
from genolint.rules.gl006 import check_gl006

RULES = [
    check_gl001,
    check_gl002,
    check_gl003,
    check_gl004,
    check_gl005,
    check_gl006,
]

USAGE = "Usage: genolint <script.sh> [more_scripts ...]"

# Exit codes: 0 = clean, 1 = findings, 2 = usage / file error
EXIT_CLEAN = 0
EXIT_FINDINGS = 1
EXIT_ERROR = 2


def lint_text(content):
    commands = extract_commands_from_text(content)
    findings = []
    for rule in RULES:
        findings.extend(rule(commands))
    return findings


def lint_file(filepath):
    print(f"Linting {filepath}...")

    try:
        with open(filepath, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.", file=sys.stderr)
        return EXIT_ERROR
    except (OSError, UnicodeDecodeError) as e:
        print(f"Error: cannot read '{filepath}': {e}", file=sys.stderr)
        return EXIT_ERROR

    findings = lint_text(content)

    if findings:
        print(f"\n[!] Found {len(findings)} issue(s):")
        for finding in findings:
            print(f"  - [{finding.rule_id}] {finding.message}")
        print()
        return EXIT_FINDINGS

    print("\n[+] No issues found! Clean bill of health.\n")
    return EXIT_CLEAN


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv

    if not args:
        print(USAGE, file=sys.stderr)
        return EXIT_ERROR

    if args[0] in ("-h", "--help"):
        print(USAGE)
        print("Exit codes: 0 = clean, 1 = issues found, 2 = usage or file error")
        return EXIT_CLEAN

    # Lint every file; report the worst result (2 > 1 > 0)
    return max(lint_file(path) for path in args)


if __name__ == "__main__":
    sys.exit(main())
