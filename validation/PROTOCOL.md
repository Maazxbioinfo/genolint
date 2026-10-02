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

## Fix log
- 2026-10-01 (commit 6e31afb): GL005 false positives found during corpus review.
  Both corpus GL005 findings (0583_3, 0585_1; GATK HaplotypeCaller) were labeled FP:
  the thread count in `--native-pair-hmm-threads 4` was parsed as contig "4".
  Rule narrowed so bare integers count as contigs only inside region arguments.
  The two findings were labeled after the main review round.
  Before fix: 27 findings in 20 scripts; 19 TP / 4 FP / 4 UNCLEAR (precision 19/23 = 82.6%, UNCLEAR excluded).
  After fix: 25 findings in 18 scripts; 19 TP / 2 FP / 4 UNCLEAR (precision 19/21 = 90.5%, UNCLEAR excluded).
  Snapshots: validation/findings_pre_gl005_fix.txt, validation/findings_post_gl005_fix.txt.

## Fix log (parser and GL006)
- 2026-10-02 (commits 4dced35 through 36748ec; code version in RESULTS_VERSION.txt):
  the hand review of 30 zero-finding scripts (labels/misses_verdicts.csv: 0 confirmed misses,
  1 UNCLEAR) exposed parser blind spots, each reproduced with a one-line example: tool calls on a
  one-line `for ... do ...; done` or `if ... then ...`; `java -jar SnpSift.jar` calls (GL004 could not
  see 9 of the 10 SnpSift-filter scripts); tools called via `$VARIABLE` or a full path. The parser was fixed.
  This made two commands visible to GL006 that it had never seen: 0450 (UNCLEAR) and 0413, where one
  finding was a false positive caused by `--output-file` missing from GL006's value-taking options (fixed)
  and one was UNCLEAR.
  Results by version (UNCLEAR excluded from precision):
  frozen rules (d0b197e): 27 findings in 20 scripts, 19 TP / 4 FP / 4 UNCLEAR, precision 19/23 = 82.6%.
  after the GL005 fix: 25 findings in 18 scripts, 19 TP / 2 FP / 4 UNCLEAR, precision 19/21 = 90.5%.
  after the parser changes and the GL006 fix: 27 findings in 20 scripts, 19 TP / 2 FP / 6 UNCLEAR, precision 19/21 = 90.5%.
  The labeled set also contains 3 findings that the fixes removed (2 GL005, 1 GL006). Precision after the
  fixes was measured on the corpus that motivated them (development corpus), not on held-out data.
