# genolint

A static linter for genomics command-line scripts. It reads shell scripts and
finds command-line mistakes in samtools, bcftools, GATK and SnpEff/SnpSift
calls that tend to fail late or silently, before you spend hours on a run.

genolint never executes your script. It parses the commands and checks them
against a small set of rules.

## Install

```bash
git clone <repository-url>
cd genolint
pip install -e .
```

## Usage

```bash
genolint script.sh
genolint pipeline/*.sh
python src/genolint/cli.py script.sh   # without installing
```

Exit codes: `0` clean, `1` issues found, `2` usage or file error, so it can be
used in CI.

## Rules

| ID | What it checks |
|---|---|
| GL001 | `bcftools view` output filename ends in `.vcf.gz` but no compressed output type (`-Oz`) is set |
| GL002 | `bcftools concat` without `-a` when the inputs could overlap (per-chromosome inputs are not flagged) |
| GL003 | `bcftools view` given both `-r` and `-R` |
| GL004 | SnpSift `has` used with a substring where a full term is needed |
| GL005 | Inconsistent contig naming (`chr20` vs `20`) within one script |
| GL006 | Region options (`-r`/`-R`) on a VCF/BCF with no prior index step (`bcftools index`, `tabix`, `--write-index`) |

Some rules report warnings rather than errors because the pattern is risky, not
always wrong. For example, GL006 cannot know that an index already exists on disk.

## Tests

```bash
pip install pytest
python -m pytest -v
```

Each rule has a failing fixture in `tests/fixtures/bad/` and clean fixtures in
`tests/fixtures/good/`.

## Scope

Version 1 covers shell scripts and the `shell:` blocks of Snakefiles for
samtools, bcftools, GATK and SnpEff/SnpSift. Nextflow and other tools are not
supported yet.

## License

MIT. See `LICENSE`.
