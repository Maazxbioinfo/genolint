# Validation

## Public workflow corpus

Cloned three public Snakemake workflows (shallow clone) and ran genolint over
every `.sh`, `.smk`, and `Snakefile` found:

- `snakemake-workflows/dna-seq-gatk-variant-calling`
- `snakemake-workflows/dna-seq-varlociraptor`
- `snakemake-workflows/rna-seq-star-deseq2`

41 files scanned, 0 findings. Manual review of the relevant tool calls (about
10 `bcftools view` calls, plus assorted `samtools`/`SnpSift` calls not covered
by any rule) confirmed none matched a rule's trigger condition, so this is a
true-negative result: the workflows are correct on the patterns genolint
checks, but the corpus contains few opportunities to fire any rule.

## Own coursework scripts

20 scripts scanned from prior coursework projects; only 5 contained
bcftools/samtools/gatk calls (all in a variant-calling project on
NA12878 chr20). 0 findings. The relevant script (`04_filtering.sh`) had
already been fixed before it was committed, so no buggy historical version
exists in git to test against directly.

## Reintroduced real bugs (before/after test)

Two bugs that were actually made and fixed during that project were manually
reintroduced into a scratch copy of `04_filtering.sh`, to get a genuine
before/after comparison:

1. Removed `-Oz` from a `bcftools view -f PASS ...` call writing a `.vcf.gz`
   file (originally caused uncompressed output despite the `.gz` name).
2. Removed `-a` from a `bcftools concat` call merging SNP and indel VCFs from
   the same chromosome (can cause wrong ordering/results on overlapping
   positions).

```
$ diff /tmp/04_filtering_buggy.sh scripts/04_filtering.sh
25c25
< bcftools view -f PASS -o pass_snps.vcf.gz    filtered_snps.vcf.gz
---
> bcftools view -f PASS -Oz -o pass_snps.vcf.gz    filtered_snps.vcf.gz
32c32
< bcftools concat pass_snps.vcf.gz pass_indels.vcf.gz  |  \
---
> bcftools concat -a pass_snps.vcf.gz pass_indels.vcf.gz  |  \

$ genolint /tmp/04_filtering_buggy.sh
Linting /tmp/04_filtering_buggy.sh...

[!] Found 2 issue(s):
  - [GL001] Line 25: `bcftools view` writes `pass_snps.vcf.gz` without an output type. Some bcftools versions then write uncompressed VCF; add -Oz (or -Ob for .bcf) to be explicit.
  - [GL002] Line 32: `bcftools concat` without `-a` (--allow-overlaps). Plain concat expects ordered, non-overlapping inputs, so if these files can overlap (shards, windows, multiple callers) the result may be wrong or the command may fail. Use `-a` for overlapping inputs (requires indexed files), or ignore this if they are one file per chromosome.

$ genolint scripts/04_filtering.sh
Linting scripts/04_filtering.sh...

[+] No issues found! Clean bill of health.
```

Both reintroduced bugs were caught (GL001, GL002), on the correct lines, and
the real fixed script reported clean.

## Summary

| Corpus | Files | Relevant calls | Findings | True positives confirmed |
|---|---|---|---|---|
| Public Snakemake workflows | 41 | ~30 (~10 testable) | 0 | n/a (true negative) |
| Own coursework scripts | 20 (5 relevant) | ~34 lines | 0 | n/a (already fixed) |
| Reintroduced bugs | 1 script, 2 bugs | 2 | 2 | 2/2 |
