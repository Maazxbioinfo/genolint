import pathlib
import subprocess
import sys

import pytest

FIX = pathlib.Path(__file__).parent / "fixtures"
CLI = pathlib.Path(__file__).parent.parent / "src" / "genolint" / "cli.py"


def run(*args):
    return subprocess.run(
        [sys.executable, str(CLI), *map(str, args)],
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize("rule", ["GL001", "GL002", "GL003", "GL004", "GL005", "GL006"])
def test_bad_fixture_triggers_rule(rule):
    assert rule in run(FIX / "bad" / f"{rule.lower()}.sh").stdout


@pytest.mark.parametrize(
    "f", sorted((FIX / "good").glob("*.sh")), ids=lambda p: p.name
)
def test_good_fixture_is_clean(f):
    assert "Found" not in run(f).stdout


def test_exit_codes():
    assert run(FIX / "bad" / "gl001.sh").returncode == 1
    assert run(FIX / "good" / "gl006_indexed.sh").returncode == 0
    assert run("does_not_exist.sh").returncode == 2
    assert run().returncode == 2


def test_multiple_files_returns_worst_code():
    good = FIX / "good" / "gl006_indexed.sh"
    bad = FIX / "bad" / "gl001.sh"
    assert run(good, bad).returncode == 1


def test_gl002_still_flags_shards():
    assert "GL002" in run(FIX / "bad" / "gl002_shards.sh").stdout


def test_snakemake_bad_flags_rules():
    out = run(FIX / "snakemake" / "bad.smk").stdout
    assert "GL006" in out and "GL002" in out


def test_snakemake_good_is_clean():
    assert run(FIX / "snakemake" / "good.smk").returncode == 0


@pytest.mark.parametrize(
    "f", sorted((FIX / "bad_extra").glob("*.sh")), ids=lambda p: p.name
)
def test_bad_extra_fixture_triggers_its_rule(f):
    assert f.name.split("_")[0].upper() in run(f).stdout

from genolint.snakemake import snakemake_to_shell


def _snakemake_rows(text):
    out = snakemake_to_shell(text).splitlines()
    return {i + 1: l for i, l in enumerate(out) if l.strip()}


def test_snakemake_line_numbers_bad_fixture():
    rows = _snakemake_rows(open("tests/fixtures/snakemake/bad.smk").read())
    assert set(rows) == {5, 10}
    assert rows[5].startswith("bcftools view")
    assert rows[10].startswith("bcftools concat")


def test_snakemake_line_numbers_with_continuations():
    text = (
        "rule a:\n"
        "    shell:\n"
        '        """\n'
        "        bcftools view \\\n"
        "            -r chr20 a.vcf.gz \\\n"
        "            -Oz -o out.vcf.gz\n"
        "        bcftools index out.vcf.gz\n"
        '        """\n'
    )
    assert set(_snakemake_rows(text)) == {4, 7}
