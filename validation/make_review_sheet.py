import csv, pathlib

with open("validation/labels/labels.csv") as fh:
    rows = list(csv.DictReader(fh))

out = []
for r in rows:
    out.append(f"===== Finding {r['id']} | {r['rule']} | {r['file']} line {r['line']} =====")
    out.append("--- code ---")
    out.append(r["snippet"])
    out.append("--- genolint says ---")
    out.append(r["message"])
    out.append("")
    out.append("LABEL: ")       # type TP, FP, or Unclear after the colon
    out.append("NOTES: ")       # optional
    out.append("")
    out.append("")

pathlib.Path("validation/labels/review.txt").write_text("\n".join(out))
print(f"wrote {len(rows)} findings to validation/labels/review.txt")
