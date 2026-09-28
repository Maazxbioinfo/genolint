import json, subprocess, hashlib, base64, csv, collections, pathlib, re, sys, time

TOOLS = ["samtools", "bcftools", "gatk", "snpEff"]
EXTS = ["sh", "bash", "sbatch", "slurm", "pbs"]
PER_REPO_CAP = 3
EXCLUDE = {"Maazxbioinfo/genolint"}
CALL = re.compile(r"^\s*[^#\s].*\b(samtools|bcftools|gatk|snpEff)\b")
out = pathlib.Path("validation/corpus"); out.mkdir(exist_ok=True)

def gh(*a):
    return subprocess.run(["gh", *a], capture_output=True, text=True, check=True).stdout

def in_scope(text):
    return any(CALL.match(l) for l in text.decode("utf-8", "ignore").splitlines())

hits = []
for t in TOOLS:
    for e in EXTS:
        try:
            hits += json.loads(gh("search", "code", t, "--extension", e, "--limit", "100",
                                  "--json", "repository,path,sha"))
        except subprocess.CalledProcessError as ex:
            print("search failed", t, e, ex.stderr[:100], file=sys.stderr)
        time.sleep(8)   # code search is ~10 requests/min

seen_hash, per_repo, rows = set(), collections.Counter(), []
for h in hits:
    repo = h["repository"]["nameWithOwner"]
    if repo in EXCLUDE or per_repo[repo] >= PER_REPO_CAP: continue
    try:
        meta = json.loads(gh("api", f"repos/{repo}"))
        if meta["fork"]: continue
        f = json.loads(gh("api", f"repos/{repo}/contents/{h['path']}"))
        text = base64.b64decode(f["content"])
    except Exception:
        continue
    if not in_scope(text): continue
    digest = hashlib.sha256(text).hexdigest()
    if digest in seen_hash: continue
    seen_hash.add(digest); per_repo[repo] += 1
    local = out / f"{len(rows):04d}_{pathlib.Path(h['path']).name}"
    local.write_bytes(text)
    rows.append([local.name, repo, h["path"], f["sha"], (meta.get("license") or {}).get("spdx_id"),
                 meta["pushed_at"][:10], digest])

with open("validation/manifest.tsv", "w", newline="") as fh:
    w = csv.writer(fh, delimiter="\t")
    w.writerow(["file", "repo", "path", "blob_sha", "license", "last_push", "sha256"])
    w.writerows(rows)
print(len(rows), "files")
