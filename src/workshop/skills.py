"""Agent Skill discovery, validation, selection, and project-local synchronization."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import re
import stat
import tempfile
import shutil

VALID_SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER = re.compile(r"\A---\s*\n(?P<body>.*?)\n---\s*(?:\n|$)", re.DOTALL)

MANDATORY_SKILL_RULES = (
    (
        "merge-review",
        ("merge", "merging", "pull request", "pr review", "approve", "approval", "stacked pr", "retarget"),
        "Merge or PR-review tasks must consider /merge-review.",
    ),
    (
        "skill-security-auditor",
        ("external skill", "skill import", "importing skills", "activate skill", "untrusted", "upstream skill", "script review"),
        "External skill import or activation must consider /skill-security-auditor.",
    ),
    (
        "dependency-auditor",
        ("dependency", "dependencies", "package.json", "requirements.txt", "license", "version pinning"),
        "Dependency review tasks should consider /dependency-auditor.",
    ),
    (
        "env-secrets-manager",
        (".env", "env file", "environment config", "secret", "secrets", "credential", "redaction"),
        "Env/config review tasks should consider /env-secrets-manager.",
    ),
)


@dataclass(frozen=True)
class SkillInfo:
    name: str
    description: str
    path: Path
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    legacy: bool = False


def _frontmatter_value(body: str, key: str) -> str:
    match = re.search(rf"(?m)^{re.escape(key)}\s*:\s*(.+?)\s*$", body)
    if not match:
        return ""
    value = match.group(1).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    return value


def _infer_legacy_description(text: str) -> str:
    paragraphs = re.split(r"\n\s*\n", text)
    for paragraph in paragraphs:
        candidate = " ".join(line.strip() for line in paragraph.splitlines()).strip()
        if not candidate or candidate.startswith("#") or candidate.startswith("```"):
            continue
        candidate = re.sub(r"\s+", " ", candidate)
        return candidate[:1024]
    return "Legacy Local Agent Workshop skill; use when its named workflow applies."


def inspect_skill(skill_md: Path, *, allow_legacy: bool = True) -> SkillInfo:
    expected_name = skill_md.parent.name
    try:
        if _is_link(skill_md) or _is_link(skill_md.parent) or not skill_md.is_file():
            return SkillInfo(expected_name, '', skill_md, ('SKILL.md must be a regular file inside an unlinked skill directory',))
        text = skill_md.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return SkillInfo(expected_name, '', skill_md, ('SKILL.md must be readable UTF-8',))
    errors: list[str] = []
    warnings: list[str] = []
    match = FRONTMATTER.match(text)
    if not match:
        if allow_legacy:
            description = _infer_legacy_description(text)
            warnings.append("legacy SKILL.md has no YAML frontmatter; sync will normalize the generated copy")
            return SkillInfo(expected_name, description, skill_md, (), tuple(warnings), True)
        return SkillInfo(expected_name, "", skill_md, ("missing YAML frontmatter",), (), True)

    body = match.group("body")
    name = _frontmatter_value(body, "name")
    description = _frontmatter_value(body, "description")

    if not name:
        errors.append("missing required 'name' frontmatter")
    elif not VALID_SKILL_NAME.fullmatch(name) or "--" in name:
        errors.append(f"invalid skill name: {name!r}")
    if name and name != expected_name:
        errors.append(f"frontmatter name {name!r} does not match directory {expected_name!r}")
    if not description:
        errors.append("missing required 'description' frontmatter")
    elif len(description) > 1024:
        errors.append("description exceeds 1024 characters")

    return SkillInfo(name or expected_name, description, skill_md, tuple(errors), tuple(warnings), False)


def discover_skills(skills_root: Path, *, allow_legacy: bool = True) -> list[SkillInfo]:
    try:
        if _is_link(skills_root) or (skills_root.exists() and not skills_root.is_dir()):
            return [SkillInfo(skills_root.name, '', skills_root, ('Skill library must be an unlinked directory',))]
        if not skills_root.exists():
            return []
        paths = sorted(skills_root.glob("*/SKILL.md"))
    except OSError:
        return [SkillInfo(skills_root.name, '', skills_root, ('Skill library is unreadable',))]
    return [inspect_skill(path, allow_legacy=allow_legacy) for path in paths]


def validate_skills(skills_root: Path, *, strict: bool = False) -> list[SkillInfo]:
    return [skill for skill in discover_skills(skills_root, allow_legacy=not strict) if skill.errors]


def _task_tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9_.*/-]+", text.lower())
        if len(token) >= 4
    }


def select_skills(skills_root: Path, task: str, named_skill: str | None = None) -> dict[str, object]:
    """Rank local skills for a task using deterministic, inspectable rules.

    This is the package-level counterpart to the repository's /skill-discovery
    helper scripts. It intentionally uses simple lexical rules rather than an LLM
    so cold-start behavior is reproducible and available offline.
    """
    inventory = discover_skills(skills_root)
    discovery_errors = [{'path': str(skill.path), 'errors': list(skill.errors)} for skill in inventory if skill.errors]
    by_name = {skill.name: skill for skill in inventory if not skill.errors}
    task_lower = re.sub(r"\s+", " ", task.lower()).strip()
    task_tokens = _task_tokens(task)
    candidates: dict[str, dict[str, object]] = {}

    def add(name: str, score: int, reason: str) -> None:
        skill = by_name.get(name)
        if skill is None:
            return
        candidate = candidates.setdefault(
            name,
            {"name": skill.name, "path": str(skill.path), "score": 0, "reasons": []},
        )
        candidate["score"] = int(candidate["score"]) + score
        reasons = candidate["reasons"]
        assert isinstance(reasons, list)
        reasons.append(reason)

    direct_lookup: dict[str, object] | None = None
    if named_skill:
        normalized_name = named_skill.strip().lstrip("/")
        direct = by_name.get(normalized_name)
        direct_lookup = {
            "name": normalized_name,
            "found": direct is not None,
            "path": str(direct.path) if direct else str(skills_root / normalized_name / "SKILL.md"),
        }
        if direct:
            add(normalized_name, 100, "User named this skill; direct path was checked before broad matching.")

    for name, terms, reason in MANDATORY_SKILL_RULES:
        if any(term in task_lower for term in terms):
            add(name, 80, reason)

    for skill in inventory:
        if skill.errors:
            continue
        candidate_text = f"{skill.name} {skill.description}".lower()
        overlap = sum(1 for token in task_tokens if token in candidate_text)
        if overlap:
            add(skill.name, overlap, "Task terms overlap this skill's name or description.")

    ranked = sorted(candidates.values(), key=lambda item: (-int(item["score"]), str(item["name"])))
    selected = ranked[0] if ranked else None

    return {
        "task_summary": task,
        "direct_lookup": direct_lookup,
        "selected_primary_skill": selected,
        "secondary_or_composed_skills": ranked[1:],
        "alternatives_considered": [
            {"name": skill.name, "path": str(skill.path)}
            for skill in inventory
            if not skill.errors and (selected is None or skill.name != selected["name"])
        ],
        "discovery_errors": discovery_errors,
        "new_skill_needed": selected is None and not discovery_errors,
        "recommended_next_action": (
            "Resolve skill discovery errors before choosing or creating a skill." if discovery_errors else
            "Read the selected SKILL.md and follow its workflow."
            if selected
            else "Create or improve a skill only after confirming no existing skill overlaps the task."
        ),
    }


def _normalized_skill_text(skill: SkillInfo) -> str:
    original = skill.path.read_text(encoding="utf-8")
    if not skill.legacy:
        return original
    description = skill.description.replace("\n", " ").replace('"', "\\\"")
    return (
        "---\n"
        f"name: {skill.name}\n"
        f'description: "{description}"\n'
        "metadata:\n"
        "  local-agent-workshop-source: legacy-normalized\n"
        "---\n\n"
        + original
    )


CACHE_MANIFEST = ".workshop-generated.json"


def _is_link(path: Path) -> bool:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    # Python 3.11 on Windows lacks Path.is_junction; all reparse points fail closed.
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _safe_tree(root: Path) -> None:
    """Reject symlinks, junctions and special files before reading/copying a tree.

    This is for a single-user cache, not a sandbox against another process with
    the same OS account. The cache parent must not be writable by untrusted users.
    """
    for path in (root, *root.parents):
        if _is_link(path):
            raise ValueError("refusing symlink/junction in skill tree")
    if not root.exists():
        return
    if not root.is_dir():
        raise ValueError("skill tree must be a directory")
    def unreadable(error: OSError) -> None:
        raise ValueError("unreadable directory in skill tree") from error
    for folder, dirs, files in os.walk(root, followlinks=False, onerror=unreadable):
        for name in dirs + files:
            path = Path(folder) / name
            if _is_link(path):
                raise ValueError("refusing symlink/junction in skill tree")
            mode = path.stat().st_mode
            if not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                raise ValueError("refusing special file in skill tree")


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _owned_files(target: Path) -> dict[str, str]:
    path = target / CACHE_MANIFEST
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        files = data["files"]
        if data["version"] != 1 or not isinstance(files, dict):
            raise ValueError
        for name, checksum in files.items():
            parts = PurePosixPath(name).parts
            if (not isinstance(name, str) or "\\" in name or len(parts) < 2
                    or PurePosixPath(name).as_posix() != name or PurePosixPath(name).is_absolute() or any(p in {".", ".."} for p in parts)
                    or not VALID_SKILL_NAME.fullmatch(parts[0])
                    or not isinstance(checksum, str) or not re.fullmatch(r"[a-f0-9]{64}", checksum)):
                raise ValueError
        modes = data.get("modes", {})
        if not isinstance(modes, dict) or any(name not in files or type(mode) is not int or not 0 <= mode <= 0o777 for name, mode in modes.items()):
            raise ValueError
        return files
    except (OSError, TypeError, KeyError, ValueError):
        raise ValueError("invalid generated skill ownership manifest") from None


def cache_is_current(skills_root: Path, target_root: Path) -> bool:
    """Compare the owned generation with normalized canonical contents."""
    try:
        _safe_tree(skills_root)
        _safe_tree(target_root)
        owned = _owned_files(target_root)
        expected = _skill_contents(skills_root)
        modes = {name: stat.S_IMODE((skills_root / name).stat().st_mode) & 0o777 for name in expected}
        saved_modes = json.loads((target_root / CACHE_MANIFEST).read_text())["modes"]
        if os.name != "nt" and modes != saved_modes:
            return False
        if _unknown_skill_content(target_root, expected):
            return False
        if set(owned) != set(expected):
            return False
        for name, content in expected.items():
            path = target_root / name
            checksum = hashlib.sha256(content).hexdigest()
            if (owned[name] != checksum or not path.is_file() or _hash(path) != checksum
                    or (os.name != "nt" and stat.S_IMODE(path.stat().st_mode) != modes[name])):
                return False
        return bool(expected)
    except (OSError, ValueError, KeyError):
        return False


def _skill_contents(source: Path) -> dict[str, bytes]:
    skills = discover_skills(source)
    if any(skill.errors for skill in skills):
        raise ValueError("refusing to sync invalid skills")
    if not skills:
        raise ValueError(f"no skills found under {source}")
    contents: dict[str, bytes] = {}
    for skill in skills:
        if not VALID_SKILL_NAME.fullmatch(skill.path.parent.name):
            raise ValueError("invalid skill directory name")
        for path in skill.path.parent.rglob("*"):
            if path.is_file():
                content = _normalized_skill_text(skill).encode("utf-8") if path == skill.path else path.read_bytes()
                contents[path.relative_to(source).as_posix()] = content
    return contents


def _unknown_skill_content(target: Path, expected: dict[str, bytes]) -> bool:
    names = {PurePosixPath(name).parts[0] for name in expected}
    for skill in target.glob("*/SKILL.md"):
        if skill.parent.name not in names:
            return True
    return any(path.is_file() and path.relative_to(target).as_posix() not in expected
               for name in names for path in (target / name).rglob("*"))


def sync_skills(skills_root: Path, target_root: Path) -> list[Path]:
    """Replace a staged, manifest-owned generation; preserve unrelated files.

    A failed swap restores the previous generation. If the process is interrupted
    between directory renames, a retained lock must first be reviewed/removed;
    the next unlocked invocation then restores the retained backup.
    Modified generated files are preserved and reported for operator resolution.
    """
    source = skills_root.absolute()
    target = target_root.absolute()
    _safe_tree(source)
    _safe_tree(target)
    if source.resolve() == target.resolve() or source.resolve() in target.resolve().parents or target.resolve() in source.resolve().parents:
        raise ValueError("source and target skill trees overlap")
    source, target = source.resolve(), target.resolve()
    contents = _skill_contents(source)
    modes = {name: stat.S_IMODE((source / name).stat().st_mode) & 0o777 for name in contents}
    target.parent.mkdir(parents=True, exist_ok=True)
    lock = target.with_name(f".{target.name}.workshop-lock")
    try:
        lock.mkdir()
    except FileExistsError:
        raise ValueError("skill sync already locked; verify no writer is active before removing its stale lock") from None
    stage = None
    backup = target.with_name(f".{target.name}.workshop-backup")
    try:
        _safe_tree(backup)
        if backup.exists():
            if target.exists():
                raise ValueError("retained skill backup needs review before another sync")
            os.replace(backup, target)
        _safe_tree(target)
        owned = _owned_files(target)
        if not owned and (target / ".workshop-generated").exists() and _unknown_skill_content(target, contents):
            raise ValueError("legacy cache contains unowned content; preserve and move it aside before regeneration")
        for name, checksum in owned.items():
            path = target / name
            if path.exists() and (not path.is_file() or _hash(path) != checksum):
                raise ValueError("modified generated file preserved; move it aside before syncing")
        for name, content in contents.items():
            path = target / name
            if path.exists() and name not in owned and (not path.is_file() or path.read_bytes() != content):
                raise ValueError("unowned or legacy file differs; move it aside before syncing")
        stage = Path(tempfile.mkdtemp(prefix=f".{target.name}.stage-", dir=target.parent))
        if target.exists():
            shutil.copytree(target, stage, dirs_exist_ok=True)
        for name in owned:
            path = stage / name
            if path.is_file():
                path.unlink()
        parents = {parent for name in owned for parent in (stage / name).parents if stage in parent.parents}
        for path in sorted(parents, key=lambda p: len(p.parts), reverse=True):
            if path.is_dir() and not any(path.iterdir()):
                path.rmdir()
        for name, content in contents.items():
            path = stage / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            if os.name != "nt":
                path.chmod(modes[name])
        (stage / CACHE_MANIFEST).write_text(json.dumps({"version": 1, "modes": modes, "files": {
            name: hashlib.sha256(content).hexdigest() for name, content in contents.items()
        }}, indent=2) + "\n", encoding="utf-8")
        (stage / ".workshop-generated").write_text(
            "Generated by workshop skills sync. Edit canonical skills/, not this cache.\n", encoding="utf-8")
        if target.exists():
            os.replace(target, backup)
        try:
            os.replace(stage, target)
        except OSError:
            if backup.exists() and not target.exists():
                os.replace(backup, target)
            raise
        if backup.exists():
            shutil.rmtree(backup)
        return [target_root / skill.path.parent.name for skill in discover_skills(source)]
    finally:
        if stage is not None and stage.exists():
            shutil.rmtree(stage)
        lock.rmdir()
