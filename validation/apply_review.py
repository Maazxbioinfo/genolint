import csv, re, pathlib

text = pathlib.Path("validation/labels/review.txt").read_text()
blocks = text.split("===== Finding ")[1:]

answers = {}
for b in blocks:
    fid = int(b.split("|")[0].strip())
    label = re.search(r"LABEL:\s*(\S*)", b)
    notes = re.search(r"NOTES:\s*(.*)", b)
    answers[fid] = (
        (label.group(1).strip().upper() if label else ""),
        (notes.group(1).strip() if notes else ""),
    )

with open("validation/labels/labels.csv") as fh:
    cols = next(csv.reader(fh))
with open("validation/labels/labels.csv") as fh:
    rows = list(csv.DictReader(fh))

for r in rows:
    lab, note = answers.get(int(r["id"]), ("", ""))
    r["label"] = lab
    r["notes"] = note

with open("validation/labels/labels.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)

filled = sum(1 for r in rows if r["label"] in ("TP", "FP", "UNCLEAR"))
print(f"{filled}/{len(rows)} labeled")
