from pathlib import Path

import pytest

from workshop.skills import discover_skills, select_skills, sync_skills, validate_skills


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


def test_select_skills_applies_merge_review_gate(tmp_path):
    root = tmp_path / "skills"
    write_skill(root, "merge-review", description="Review pull requests and merge readiness.")
    write_skill(root, "design-first", description="Design software before implementation.")

    report = select_skills(root, "Review this pull request before we merge it")

    assert report["selected_primary_skill"]["name"] == "merge-review"
    assert report["new_skill_needed"] is False
    assert any("must consider /merge-review" in reason for reason in report["selected_primary_skill"]["reasons"])


def test_select_skills_checks_named_skill_directly(tmp_path):
    root = tmp_path / "skills"
    write_skill(root, "design-first", description="Design software before implementation.")
    write_skill(root, "repo-cleanup", description="Clean repository state before and after work.")

    report = select_skills(root, "Do some general preparation", named_skill="/repo-cleanup")

    assert report["direct_lookup"]["found"] is True
    assert report["selected_primary_skill"]["name"] == "repo-cleanup"
    assert report["selected_primary_skill"]["score"] >= 100


def test_sync_rejects_destination_symlinks_without_writing(tmp_path):
    source, target, outside = tmp_path / 'source', tmp_path / 'target', tmp_path / 'outside'
    write_skill(source, 'demo')
    target.mkdir()
    outside.mkdir()
    (outside / 'canary').write_text('untouched')
    (target / 'demo').symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match='symlink'):
        sync_skills(source, target)
    assert sorted(p.name for p in outside.iterdir()) == ['canary']


def test_sync_rejects_source_symlinks_before_copying(tmp_path):
    source, target = tmp_path / 'source', tmp_path / 'target'
    write_skill(source, 'demo')
    outside = tmp_path / 'private'
    outside.write_text('synthetic canary')
    (source / 'demo' / 'secret.txt').symlink_to(outside)
    with pytest.raises(ValueError, match='symlink'):
        sync_skills(source, target)
    assert not target.exists()


@pytest.mark.parametrize('relation', ['same', 'child', 'parent'])
def test_sync_rejects_overlapping_trees(tmp_path, relation):
    source = tmp_path / 'source'
    write_skill(source, 'demo')
    target = {'same': source, 'child': source / 'cache', 'parent': tmp_path}[relation]
    with pytest.raises(ValueError, match='overlap'):
        sync_skills(source, target)


def test_sync_removes_only_obsolete_owned_files(tmp_path):
    source, target = tmp_path / 'source', tmp_path / 'target'
    write_skill(source, 'demo')
    old = source / 'demo' / 'old.py'
    old.write_text('# old helper')
    sync_skills(source, target)
    user_file = target / 'demo' / 'user-note.txt'
    user_file.write_text('preserve this')
    old.unlink()
    sync_skills(source, target)
    assert not (target / 'demo' / 'old.py').exists()
    assert user_file.read_text() == 'preserve this'


def test_sync_preserves_modified_owned_files_on_failure(tmp_path):
    source, target = tmp_path / 'source', tmp_path / 'target'
    write_skill(source, 'demo')
    sync_skills(source, target)
    generated = target / 'demo' / 'SKILL.md'
    generated.write_text('operator work')
    with pytest.raises(ValueError, match='modified'):
        sync_skills(source, target)
    assert generated.read_text() == 'operator work'


def test_sync_rolls_back_failed_generation_swap(tmp_path, monkeypatch):
    source, target = tmp_path / 'source', tmp_path / 'target'
    write_skill(source, 'demo')
    sync_skills(source, target)
    original = (target / 'demo' / 'SKILL.md').read_text()
    write = source / 'demo' / 'SKILL.md'
    write.write_text(write.read_text().replace('Use for tests.', 'New description.'))
    import os
    original_replace = os.replace
    def fail_stage(src, dst):
        if Path(src).name.startswith('.target.stage-'):
            raise OSError('injected storage failure')
        return original_replace(src, dst)
    monkeypatch.setattr(os, 'replace', fail_stage)
    with pytest.raises(OSError, match='injected'):
        sync_skills(source, target)
    assert (target / 'demo' / 'SKILL.md').read_text() == original


def test_sync_preserves_unrelated_empty_directory(tmp_path):
    source, target = tmp_path / 'source', tmp_path / 'target'
    write_skill(source, 'demo')
    unrelated = target / 'operator-empty-directory'
    unrelated.mkdir(parents=True)
    sync_skills(source, target)
    assert unrelated.is_dir()


def test_sync_rejects_forged_ownership_manifest(tmp_path):
    import json
    source, target = tmp_path / 'source', tmp_path / 'target'
    write_skill(source, 'demo')
    target.mkdir()
    (target / '.workshop-generated.json').write_text(json.dumps({'version': 1, 'files': {'../outside': '0' * 64}}))
    with pytest.raises(ValueError, match='ownership manifest'):
        sync_skills(source, target)
    assert not (target / 'demo').exists()


def test_sync_recovers_retained_previous_generation(tmp_path):
    import os
    source, target = tmp_path / 'source', tmp_path / 'target'
    write_skill(source, 'demo')
    sync_skills(source, target)
    os.replace(target, tmp_path / '.target.workshop-backup')
    sync_skills(source, target)
    assert (target / 'demo' / 'SKILL.md').is_file()
    assert not (tmp_path / '.target.workshop-backup').exists()


def test_sync_preserves_posix_executable_helpers(tmp_path):
    import os
    if os.name == 'nt':
        pytest.skip('POSIX executable mode semantics')
    from workshop.skills import cache_is_current
    source, target = tmp_path / 'source', tmp_path / 'target'
    write_skill(source, 'demo')
    helper = source / 'demo' / 'helper.sh'
    helper.write_text('#!/bin/sh\nexit 0\n')
    helper.chmod(0o755)
    sync_skills(source, target)
    assert (target / 'demo' / 'helper.sh').stat().st_mode & 0o111 == 0o111
    assert cache_is_current(source, target)
    (target / 'demo' / 'helper.sh').chmod(0o644)
    assert not cache_is_current(source, target)


def test_unknown_legacy_helpers_require_preserved_manual_migration(tmp_path):
    from workshop.skills import cache_is_current
    source, target = tmp_path / 'source', tmp_path / 'target'
    write_skill(source, 'demo')
    write_skill(target, 'demo')
    (target / '.workshop-generated').write_text('Legacy generated cache')
    obsolete = target / 'demo' / 'obsolete.sh'
    obsolete.write_text('operator or old generated content')
    with pytest.raises(ValueError, match='legacy'):
        sync_skills(source, target)
    assert obsolete.exists()
    assert not cache_is_current(source, target)


def test_windows_reparse_points_fail_closed_without_is_junction(tmp_path, monkeypatch):
    import stat
    from types import SimpleNamespace
    import workshop.skills as module
    original = Path.lstat
    def reparse(path, *args, **kwargs):
        if path == tmp_path:
            return SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, 'lstat', reparse)
    with pytest.raises(ValueError, match='symlink/junction'):
        module._safe_tree(tmp_path)
