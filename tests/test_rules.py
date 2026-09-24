import pathlib, subprocess, sys, pytest

FIX = pathlib.Path(__file__).parent / "fixtures"
CLI = pathlib.Path(__file__).parent.parent / "src" / "genolint" / "cli.py"

def run(f):
    return subprocess.run([sys.executable, str(CLI), str(f)],
                          capture_output=True, text=True).stdout

@pytest.mark.parametrize("rule", ["GL001","GL002","GL003","GL004","GL005","GL006"])
def test_bad_fixture_triggers_rule(rule):
    assert rule in run(FIX / "bad" / f"{rule.lower()}.sh")

@pytest.mark.parametrize("f", sorted((FIX / "good").glob("*.sh")), ids=lambda p: p.name)
def test_good_fixture_is_clean(f):
    assert "Found" not in run(f)
