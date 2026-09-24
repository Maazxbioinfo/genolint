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
