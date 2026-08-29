import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from workshop import cli


def test_cli_main_exists():
    assert callable(cli.main)


def test_cli_main_without_args_prints_help(capsys):
    assert cli.main([]) == 0
    captured = capsys.readouterr()
    assert "Local Agent Workshop CLI" in captured.out


def test_cli_skills_select_uses_local_gate(tmp_path, capsys):
    skills = tmp_path / "skills"
    skill = skills / "merge-review" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text(
        "---\nname: merge-review\ndescription: Review pull requests before merging.\n---\n\n# /merge-review\n",
        encoding="utf-8",
    )

    assert cli.main(["skills", "--root", str(skills), "select", "--task", "Review this PR before merge"]) == 0
    captured = capsys.readouterr()
    assert "/merge-review" in captured.out
    assert "must consider /merge-review" in captured.out
