# Validation protocol (written before harvesting)

Date: 2026-09-28
genolint version: see RESULTS_VERSION.txt

## Corpus selection
- Source: GitHub code search for samtools, bcftools, gatk, snpEff in
  .sh/.bash/.sbatch/.slurm/.pbs files.
- Exclusions: forks, this repo, exact-duplicate files (sha256), max 3 files per repo.
- Corpus is frozen after harvest. No files added or removed after results are seen.

## In-scope scripts
A script is in scope if a non-comment line invokes samtools, bcftools, gatk or snpEff.
In-scope count is reported separately from total scanned.

## Labels
TP = code really has the bug. FP = rule fired but code is fine (reason recorded).
Unclear = needs pipeline context (reported separately, excluded from precision).

## Misses
About 30 random zero-finding in-scope scripts read by hand for any of the 6 bug categories.

## Second labeler
Random ~25% of findings labeled independently; report Cohen's kappa.

## Fixes
Any rule change after seeing FPs is logged; pre-fix and post-fix numbers are both reported.
