"""Offline guardrails for Debian LAW provisioning. This does NOT test real hosts."""
from __future__ import annotations

from pathlib import Path
import re
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: str):
    return yaml.safe_load((ROOT / path).read_text(encoding="utf-8"))


class DebianDeployContractTests(unittest.TestCase):
    def test_all_playbooks_target_two_node_group(self):
        for name in ("preflight.yml", "site.yml", "verify.yml", "rust-swarm.yml"):
            with self.subTest(name=name):
                plays = load_yaml(name)
                self.assertTrue(plays)
                self.assertEqual(plays[0]["hosts"], "law_nodes")

    def test_preflight_requires_debian_13_x86_64(self):
        text = (ROOT / "preflight.yml").read_text()
        self.assertIn("Debian", text)
        self.assertIn("'13'", text)
        self.assertIn("x86_64", text)

    def test_compose_is_loopback_and_no_host_engine_access(self):
        compose = load_yaml("files/compose.yaml")
        self.assertEqual(compose["name"], "law-smoke")
        self.assertEqual(set(compose["services"]), {"sentinel"})
        service = compose["services"]["sentinel"]
        self.assertEqual(service["ports"], ["127.0.0.1:8088:8080"])
        self.assertEqual(service["cap_drop"], ["ALL"])
        self.assertTrue(service["read_only"])
        self.assertIn("no-new-privileges:true", service["security_opt"])
        self.assertNotIn("privileged", service)
        self.assertNotIn("network_mode", service)
        self.assertNotIn("pid", service)
        self.assertNotIn("devices", service)
        self.assertNotIn("docker.sock", str(service))
        self.assertNotIn("/var/run", str(service))

    def test_docker_apt_uses_signed_official_repository(self):
        text = (ROOT / "site.yml").read_text()
        self.assertIn("https://download.docker.com/linux/debian/gpg", text)
        self.assertIn("Signed-By: /etc/apt/keyrings/docker.asc", text)
        self.assertIn("docker-compose-plugin", text)
        self.assertIn("community.docker.docker_compose_v2", text)

    def test_rust_prototype_has_review_gate_and_pinned_sha(self):
        text = (ROOT / "rust-swarm.yml").read_text()
        self.assertIn("rust_prototype_review_approved", text)
        self.assertRegex(text, r"138700f11185a8aff3cabc77f1fd1f105bd2506f")
        self.assertNotIn("StrictHostKeyChecking=no", text)

    def test_private_workflow_template_is_not_an_active_public_workflow(self):
        template = ROOT / "github-actions/PRIVATE_DEPLOY_TEMPLATE.yml"
        self.assertTrue(template.is_file())
        content = template.read_text()
        self.assertIn("workflow_dispatch", content)
        self.assertIn("law_commit", content)
        self.assertIn("law-controller", content)
        self.assertIn("environment: law-production", content)
        self.assertNotIn("pull_request:", content)
        self.assertFalse((ROOT.parent.parent / ".github/workflows/deploy.yml").exists())

    def test_html_guide_is_standalone_and_has_twelve_steps(self):
        html = (ROOT / "INSTALL_GUIDE.html").read_text()
        self.assertTrue(html.lstrip().lower().startswith("<!doctype html>"))
        self.assertEqual(len(re.findall(r'data-step="\d+"', html)), 12)
        self.assertNotIn("<script src=", html)
        self.assertNotIn("<link rel=\"stylesheet\"", html)
        self.assertIn("Debian 13", html)
        self.assertIn("Windows 11", html)


if __name__ == "__main__":
    unittest.main()
