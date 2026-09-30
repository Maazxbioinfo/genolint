# Changelog

## Unreleased

### Fixed
- GL005: bare integers are now treated as contig names only where a contig can
  appear (region options such as `-r`, `-L`, `--regions`, `--intervals`, or a
  positional `chrom:start-end` region). Previously any token equal to 1-22, X, Y
  or MT counted, so a thread count such as `--native-pair-hmm-threads 4` next to
  `-L chr20` raised a false positive. Found during corpus review (2 false
  positives, both GATK HaplotypeCaller scripts); fixtures added.
