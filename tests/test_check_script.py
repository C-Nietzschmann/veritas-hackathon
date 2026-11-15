"""Test for scripts/check.sh, the check that runs before every share. It runs in a throwaway git repo."""

import shutil
import subprocess
from pathlib import Path

import pytest

CHECK = Path(__file__).resolve().parents[1] / "scripts" / "check.sh"


def run_check(repo):
    return subprocess.run(["sh", "scripts/check.sh"], cwd=repo, capture_output=True, text=True, encoding="utf-8")


# The check is a shell script: where plain Python can't start `sh` (Windows outside Git Bash), skip.
@pytest.mark.skipif(shutil.which("sh") is None or shutil.which("git") is None, reason="needs sh and git")
def test_a_file_with_an_accent_in_its_name_is_checked_too(tmp_path):
    # git lists such a file as "Caf\303\251.md". Read that way it is no file, so it used to be skipped.
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "scripts").mkdir()
    shutil.copy(CHECK, tmp_path / "scripts" / "check.sh")
    assert run_check(tmp_path).returncode == 0   # the control: nothing to find yet

    (tmp_path / "Café.md").write_text("<<<<<<< HEAD\nmine\n=======\ntheirs\n>>>>>>> main\n", encoding="utf-8")
    result = run_check(tmp_path)
    assert result.returncode == 1
    assert "unresolved merge conflict in: Café.md" in result.stdout
