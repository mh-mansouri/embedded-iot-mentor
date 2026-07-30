#!/usr/bin/env python3
"""Build, verify, and install the `.skill` bundle for this repository.

A `.skill` file is a zip archive holding the skill folder. Per the Agent Skills
spec, SKILL.md may sit at the archive root or inside one top-level directory;
this packer uses the directory form so the bundle unzips straight into
`.claude/skills/<name>/`.

The skill source lives in its own folder next to this script, so the repository
can be cloned or downloaded under any name without breaking the spec's rule
that a skill's `name` match its folder.

Usage:
  python package_skill.py                 # -> ./embedded-iot-mentor.skill
  python package_skill.py --check         # validate source + committed bundle
  python package_skill.py --out-dir dist  # write somewhere else
  python package_skill.py --install       # build, then unpack into ~/.claude/skills/

Installing an existing bundle needs nothing else from this repository:
  python package_skill.py --install-from path/to/embedded-iot-mentor.skill
"""

import argparse
import hashlib
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Paths SKILL.md points Claude at, e.g. `references/power-and-battery-notes.md`.
REF_RE = re.compile(r"(?:references|scripts|examples|assets)/[A-Za-z0-9._/-]+")

# Build outputs and editor/interpreter droppings, never skill content.
EXCLUDE_DIRS = {"__pycache__", ".git", ".claude"}

# Files stored with LF regardless of how they sit in the working tree, so the
# bundle is byte-identical whoever builds it. Without this a Windows checkout
# produces a CRLF bundle, a Linux one produces LF, and --check reports drift
# that is really just line endings.
TEXT_SUFFIXES = {".md", ".py", ".txt", ".yml", ".yaml", ".json", ".toml", ".cfg"}

# Zip entries carry mtimes. Pinning them keeps a rebuild byte-identical instead
# of churning the committed binary on every run. 1980-01-01 is the zip epoch.
ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)


def normalize(path: Path) -> bytes:
    """File contents as they belong in the bundle: text always LF."""
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        data = data.replace(b"\r\n", b"\n")
    return data


def find_skill_dir(root: Path) -> Path:
    """Locate the one directory holding SKILL.md."""
    candidates = [
        d
        for d in sorted(root.iterdir())
        if d.is_dir() and d.name not in EXCLUDE_DIRS and (d / "SKILL.md").is_file()
    ]
    if not candidates:
        raise ValueError(f"no skill folder (a directory containing SKILL.md) under {root}")
    if len(candidates) > 1:
        names = ", ".join(d.name for d in candidates)
        raise ValueError(f"expected one skill folder, found several: {names}")
    return candidates[0]


def read_frontmatter(skill_md: Path) -> dict:
    """Minimal top-level `key: value` parse. Avoids a PyYAML dependency."""
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError("SKILL.md must start with a '---' frontmatter block")
    end = text.find("\n---", 3)
    if end == -1:
        raise ValueError("SKILL.md frontmatter block is not closed with '---'")
    fields = {}
    for line in text[3:end].splitlines():
        if not line.strip() or line.startswith((" ", "\t", "#")):
            continue
        key, sep, value = line.partition(":")
        if sep:
            fields[key.strip()] = value.strip()
    return fields


def validate(skill_dir: Path) -> str:
    """Check the spec's constraints and that referenced files exist."""
    skill_md = skill_dir / "SKILL.md"
    fields = read_frontmatter(skill_md)
    name = fields.get("name", "")
    description = fields.get("description", "")

    problems = []
    if not name:
        problems.append("frontmatter 'name' is required")
    elif not NAME_RE.match(name):
        problems.append(
            f"name '{name}' must be lowercase a-z, 0-9 and single hyphens, "
            "not leading/trailing/doubled"
        )
    elif len(name) > 64:
        problems.append(f"name is {len(name)} chars, max is 64")
    elif name != skill_dir.name:
        problems.append(f"name '{name}' must match its folder name '{skill_dir.name}'")

    if not description:
        problems.append("frontmatter 'description' is required")
    elif len(description) > 1024:
        problems.append(f"description is {len(description)} chars, max is 1024")

    # A reference SKILL.md names but the bundle lacks is a skill that tells
    # Claude to read a file that is not there. Catch renames at build time.
    for ref in sorted(set(REF_RE.findall(skill_md.read_text(encoding="utf-8")))):
        if not (skill_dir / ref).is_file():
            problems.append(f"SKILL.md references '{ref}', which does not exist")

    if problems:
        raise ValueError("; ".join(problems))
    return name


def collect(skill_dir: Path) -> list[Path]:
    """Every file in the skill folder, minus build and editor droppings."""
    return sorted(
        p
        for p in skill_dir.rglob("*")
        if p.is_file()
        and p.suffix != ".pyc"
        and not any(part in EXCLUDE_DIRS or part.startswith(".") for part in p.parts)
    )


def arcname(path: Path, skill_dir: Path) -> str:
    return f"{skill_dir.name}/{path.relative_to(skill_dir).as_posix()}"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build(skill_dir: Path, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    files = collect(skill_dir)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in files:
            info = zipfile.ZipInfo(arcname(path, skill_dir), date_time=ZIP_EPOCH)
            info.compress_type = zipfile.ZIP_DEFLATED
            # Keep helper scripts executable; everything else plain rw-r--r--.
            mode = 0o755 if path.suffix == ".py" else 0o644
            info.external_attr = mode << 16
            bundle.writestr(info, normalize(path))

    size_kb = out_path.stat().st_size / 1024
    print(f"built {out_path} ({size_kb:.1f} KB, {len(files)} files)")
    for path in files:
        print(f"  {arcname(path, skill_dir)}")


def verify(skill_dir: Path, bundle_path: Path) -> list[str]:
    """Compare a committed bundle against the source folder, file by file."""
    expected = {arcname(p, skill_dir): digest(normalize(p)) for p in collect(skill_dir)}
    with zipfile.ZipFile(bundle_path) as bundle:
        actual = {n: digest(bundle.read(n)) for n in bundle.namelist()}

    problems = []
    for name in sorted(set(expected) - set(actual)):
        problems.append(f"missing from bundle: {name}")
    for name in sorted(set(actual) - set(expected)):
        problems.append(f"stale file in bundle: {name}")
    for name in sorted(set(expected) & set(actual)):
        if expected[name] != actual[name]:
            problems.append(f"out of date in bundle: {name}")
    return problems


def install(bundle: Path, skills_dir: Path) -> int:
    """Unpack a .skill into a skills directory, replacing any previous copy."""
    if not bundle.is_file():
        print(f"error: no such bundle: {bundle}", file=sys.stderr)
        return 1

    with zipfile.ZipFile(bundle) as archive:
        names = archive.namelist()
        roots = {n.split("/", 1)[0] for n in names if "/" in n}
        if len(roots) != 1 or not any(n.endswith("/SKILL.md") for n in names):
            print(
                f"error: {bundle.name} is not a single-skill bundle "
                "(expected one top-level folder containing SKILL.md)",
                file=sys.stderr,
            )
            return 1
        skill_name = roots.pop()

        target = skills_dir / skill_name
        if target.exists():
            # Replace rather than merge, so files dropped from the bundle
            # do not linger from an older install.
            shutil.rmtree(target)
        skills_dir.mkdir(parents=True, exist_ok=True)
        archive.extractall(skills_dir)

    print(f"installed '{skill_name}' to {target}")
    print("Start a new Claude Code session, then run /skills to confirm it loaded.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out-dir",
        default=".",
        help="output directory, relative to the repository root (default: the root)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate the source and confirm the committed bundle matches it; build nothing",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="after building, unpack into the skills directory",
    )
    parser.add_argument(
        "--install-from",
        metavar="BUNDLE",
        help="install an existing .skill file instead of building one",
    )
    parser.add_argument(
        "--skills-dir",
        default=str(Path.home() / ".claude" / "skills"),
        help="where to install (default: ~/.claude/skills; use <repo>/.claude/skills for a project install)",
    )
    args = parser.parse_args()

    if args.install_from:
        return install(Path(args.install_from).expanduser(), Path(args.skills_dir).expanduser())

    try:
        skill_dir = find_skill_dir(ROOT)
        name = validate(skill_dir)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_path = out_dir / f"{name}.skill"

    if args.check:
        files = collect(skill_dir)
        print(f"ok: '{name}' is valid; {len(files)} files in {skill_dir.name}/")
        if not out_path.exists():
            print(f"ok: no bundle at {out_path.name} yet; nothing to compare")
            return 0
        problems = verify(skill_dir, out_path)
        if problems:
            print(f"error: {out_path.name} is out of sync with {skill_dir.name}/", file=sys.stderr)
            for problem in problems:
                print(f"  {problem}", file=sys.stderr)
            print("  fix: python package_skill.py, then commit the rebuilt bundle", file=sys.stderr)
            return 1
        print(f"ok: {out_path.name} matches {skill_dir.name}/")
        return 0

    build(skill_dir, out_path)

    if args.install:
        return install(out_path, Path(args.skills_dir).expanduser())
    return 0


if __name__ == "__main__":
    sys.exit(main())
