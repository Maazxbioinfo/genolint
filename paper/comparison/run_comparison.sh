#!/usr/bin/env bash
# Regenerates every file in paper/comparison/ (run from anywhere).
set -u
cd "$(dirname "$0")/../.."
OUT=paper/comparison

shellcheck --version > $OUT/shellcheck_version.txt
snakemake --version > $OUT/snakemake_version.txt 2>&1

FIX=(tests/fixtures/bad/*.sh tests/fixtures/good/*.sh tests/fixtures/bad_extra/*.sh)
for f in "${FIX[@]}"; do
  echo "=== $f"; shellcheck -s bash -f gcc "$f"; echo "exit: $?"
done > $OUT/shellcheck_fixtures.txt 2>&1
genolint "${FIX[@]}" > $OUT/genolint_fixtures.txt 2>&1

for f in validation/corpus/*; do
  echo "=== $f"; shellcheck -s bash -f gcc "$f"; echo "exit: $?"
done > $OUT/shellcheck_corpus_all.txt 2>&1
genolint validation/corpus/* > $OUT/genolint_corpus_all.txt 2>&1

for f in tests/fixtures/snakemake/bad.smk tests/fixtures/snakemake/good.smk; do
  echo "=== $f"; snakemake --lint -s "$f" 2>&1
done > $OUT/snakemake_lint.txt
genolint tests/fixtures/snakemake/bad.smk tests/fixtures/snakemake/good.smk > $OUT/genolint_snakemake.txt 2>&1
