from workshop.doctor import has_failures, run_doctor


def test_doctor_reports_missing_repo_files(tmp_path):
    checks = run_doctor(tmp_path)
    assert has_failures(checks)
    assert any(check.name == "repo" and check.level == "FAIL" for check in checks)
