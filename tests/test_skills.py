from pathlib import Path

import pytest

from workshop.skills import discover_skills, sync_skills, validate_skills


def write_skill(root: Path, name: str, *, description: str = "Use for tests.", frontmatter: bool = True) -> Path:
    path = root / name / "SKILL.md"
    path.parent.mkdir(parents=True)
    prefix = f"---\nname: {name}\ndescription: {description}\n---\n\n" if frontmatter else ""
    body = f"# {name}\n\nUse this skill for {name} test workflows.\n"
    path.write_text(prefix + body, encoding="utf-8")
    return path


def test_discover_and_validate_valid_skills(tmp_path):
    root = tmp_path / "skills"
    write_skill(root, "design-first")
    found = discover_skills(root)
    assert [item.name for item in found] == ["design-first"]
    assert validate_skills(root) == []


def test_legacy_skill_is_sync_compatible_but_fails_strict_validation(tmp_path):
    root = tmp_path / "skills"
    write_skill(root, "old-skill", frontmatter=False)
    found = discover_skills(root)
    assert found[0].legacy is True
    assert found[0].description.startswith("Use this skill")
    assert validate_skills(root) == []
    strict = validate_skills(root, strict=True)
    assert len(strict) == 1
    assert "missing YAML frontmatter" in strict[0].errors


def test_sync_normalizes_legacy_skills_and_preserves_unrelated_content(tmp_path):
    source = tmp_path / "skills"
    target = tmp_path / ".agents" / "skills"
    write_skill(source, "design-first", frontmatter=False)
    unrelated = target / "local-only"
    unrelated.mkdir(parents=True)
    (unrelated / "note.txt").write_text("keep", encoding="utf-8")

    copied = sync_skills(source, target)

    generated = (target / "design-first" / "SKILL.md").read_text(encoding="utf-8")
    assert copied == [target / "design-first"]
    assert generated.startswith("---\nname: design-first\n")
    assert validate_skills(target, strict=True) == []
    assert (target / ".workshop-generated").exists()
    assert (unrelated / "note.txt").read_text(encoding="utf-8") == "keep"


def test_sync_refuses_invalid_frontmatter(tmp_path):
    source = tmp_path / "skills"
    path = write_skill(source, "broken")
    path.write_text("---\nname: wrong-name\ndescription: nope\n---\n# broken\n", encoding="utf-8")
    with pytest.raises(ValueError, match="refusing to sync invalid skills"):
        sync_skills(source, tmp_path / ".agents" / "skills")
