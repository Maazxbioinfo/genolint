import csv, pathlib, random, re, subprocess, collections

CORPUS = pathlib.Path("validation/corpus")
RES = pathlib.Path("validation/results"); RES.mkdir(exist_ok=True)
FIND = re.compile(r"\[(GL\d{3})\]\s+Line\s+(\d+):\s*(.*)")
CALL = re.compile(r"^\s*[^#\s].*\b(samtools|bcftools|gatk|snpEff)\b")
random.seed(20260928)

files = sorted(p for p in CORPUS.iterdir() if p.is_file())
findings, zero, errors = [], [], []
per_rule = collections.Counter()

for p in files:
    try:
        r = subprocess.run(["genolint", str(p)], capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        errors.append((p.name, "timeout")); continue
    (RES / (p.name + ".txt")).write_text(r.stdout + r.stderr)
    if r.returncode == 2:
        errors.append((p.name, "exit 2")); continue
    lines = p.read_text(errors="replace").splitlines()
    hits = FIND.findall(r.stdout)
    if not hits:
        if any(CALL.match(l) for l in lines): zero.append(p.name)
        continue
    for rule, ln, msg in hits:
        ln = int(ln)
        ctx = lines[max(0, ln - 4): ln + 3]
        findings.append(dict(rule=rule, file=p.name, line=ln,
                             snippet="\n".join(ctx), message=msg))
        per_rule[rule] += 1

random.shuffle(findings)
cols = ["id", "rule", "file", "line", "snippet", "label", "notes", "message"]
def write(path, rows):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader()
        for f in rows:
            w.writerow({**f, "label": "", "notes": ""})

for i, f in enumerate(findings, 1): f["id"] = i
write("validation/labels/labels.csv", findings)
sub = random.sample(findings, max(1, round(0.25 * len(findings)))) if findings else []
write("validation/labels/labels_rater2.csv", sub)

sample = random.sample(zero, min(30, len(zero)))
pathlib.Path("validation/labels/misses_to_review.txt").write_text("\n".join(sorted(sample)) + "\n")

flagged = len({f["file"] for f in findings})
print(f"scanned: {len(files)}   genolint errors: {len(errors)}")
print(f"in-scope with 0 findings: {len(zero)}   flagged scripts: {flagged}")
print(f"total findings: {len(findings)}   per rule: {dict(per_rule)}")
print(f"rater2 subset: {len(sub)}   miss-review sample: {len(sample)}")
for e in errors: print("ERR", *e)
