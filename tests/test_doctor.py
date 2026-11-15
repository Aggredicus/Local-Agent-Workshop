from workshop.doctor import has_failures, run_doctor


def test_doctor_reports_missing_repo_files(tmp_path):
    checks = run_doctor(tmp_path)
    assert has_failures(checks)
    assert any(check.name == "repo" and check.level == "FAIL" for check in checks)


def test_doctor_does_not_accept_equal_counts_with_invalid_generated_skill(tmp_path):
    from workshop.skills import sync_skills
    source = tmp_path / 'skills' / 'demo' / 'SKILL.md'
    source.parent.mkdir(parents=True)
    source.write_text('---\nname: demo\ndescription: Demonstration\n---\n')
    target = tmp_path / '.agents' / 'skills'
    sync_skills(tmp_path / 'skills', target)
    checks = run_doctor(tmp_path)
    assert next(c for c in checks if c.name == 'skill-discovery').level == 'PASS'
    (target / 'demo' / 'SKILL.md').write_text('---\nname: wrong\ndescription: Stale\n---\n')
    checks = run_doctor(tmp_path)
    assert next(c for c in checks if c.name == 'skill-discovery').level == 'WARN'
