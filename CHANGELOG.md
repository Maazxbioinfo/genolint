# Changelog

## Unreleased

## 0.1.0 - 2026-10-03

### Added
- First tagged release. Static linter for bcftools, samtools, GATK, SnpEff and SnpSift commands in shell scripts and Snakemake files, with six rules (GL001-GL006): output type vs file extension, `bcftools concat` without `-a`, `-r` together with `-R`, partial SnpSift consequence terms, mixed `chr`/bare contig names, and region queries without an index.
- Validation protocol, labels, per-script results and a reproducible comparison with ShellCheck and `snakemake --lint` (see `validation/` and `paper/comparison/`).

### Fixed
- Parser: commands after `do`/`then`/`else`/`if`/`while` on the same line (one-line loops) are now recognized.
- Parser: `java [opts] -jar SnpSift.jar|snpEff.jar <subcommand>` is treated as a direct SnpSift/snpEff call (GL004 could not see these before).
- Parser: tools called through a variable (`$BCFTOOLS view ...`) or a full path are recognized, and the command head is normalized so every rule sees the bare tool name.
- GL006: `--output-file` is now treated as a value-taking option of `bcftools view`.
- GL005: bare integers are now treated as contig names only where a contig can
  appear (region options such as `-r`, `-L`, `--regions`, `--intervals`, or a
  positional `chrom:start-end` region). Previously any token equal to 1-22, X, Y
  or MT counted, so a thread count such as `--native-pair-hmm-threads 4` next to
  `-L chr20` raised a false positive. Found during corpus review (2 false
  positives, both GATK HaplotypeCaller scripts); fixtures added.
