#!/usr/bin/env python3
"""Build and verify the ChatGPT bundle: instructions plus knowledge files.

A Custom GPT is configured by hand in the browser, so there is nothing to
install — but two of its limits bite silently. Instructions are capped at 8000
characters, and knowledge is capped at 20 files. Both are easy to blow past
while editing the mentor, and ChatGPT only tells you at paste time.

This script assembles the upload set from the skill folder, checks it against
those limits, and confirms every knowledge file the instructions name actually
exists — the same gate `package_skill.py --check` applies to the Claude skill.

Usage:
  python build_chatgpt_bundle.py          # -> dist/embedded-iot-mentor-gpt.zip
  python build_chatgpt_bundle.py --check  # validate only, build nothing
"""

import argparse
import re
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent / "embedded-iot-mentor"
INSTRUCTIONS = HERE / "custom-gpt" / "instructions.md"
CONFIG = HERE / "custom-gpt" / "gpt-config.json"

# ChatGPT's Custom GPT builder, as of writing.
MAX_INSTRUCTION_CHARS = 8000
MAX_KNOWLEDGE_FILES = 20

# Knowledge files are uploaded flat, so the instructions name them without a
# folder: `power-and-battery-notes.md`, not `references/power-and-battery-notes.md`.
KNOWLEDGE_RE = re.compile(r"`([A-Za-z0-9._-]+\.(?:md|py))`")

# Text goes into the zip with LF and pinned timestamps, so a rebuild on Windows
# and one on Linux produce the same archive.
ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)


def knowledge_files() -> list[Path]:
    """Everything the GPT gets uploaded: reference docs, worked examples, scripts.

    Scripts are included because a GPT with Code Interpreter can run an uploaded
    .py, which is how a battery runtime here stays a calculation rather than a
    guess.
    """
    files = []
    for folder, pattern in (("references", "*.md"), ("examples", "*.md"), ("scripts", "*.py")):
        files += sorted((SKILL_DIR / folder).glob(pattern))
    return files


def validate(files: list[Path]) -> list[str]:
    problems = []

    if not INSTRUCTIONS.is_file():
        return [f"missing {INSTRUCTIONS.relative_to(HERE)}"]

    text = INSTRUCTIONS.read_text(encoding="utf-8").replace("\r\n", "\n")
    if len(text) > MAX_INSTRUCTION_CHARS:
        problems.append(
            f"instructions.md is {len(text)} characters; ChatGPT accepts "
            f"{MAX_INSTRUCTION_CHARS}. Cut {len(text) - MAX_INSTRUCTION_CHARS}."
        )

    if len(files) > MAX_KNOWLEDGE_FILES:
        problems.append(
            f"{len(files)} knowledge files; a GPT accepts {MAX_KNOWLEDGE_FILES}. "
            "Merge some references before adding more."
        )

    # An instruction that points at a file nobody uploaded is an instruction the
    # GPT cannot follow. Catch a rename here rather than in a bad answer.
    available = {path.name for path in files}
    for name in sorted(set(KNOWLEDGE_RE.findall(text))):
        if name not in available:
            problems.append(f"instructions.md names '{name}', which is not in the bundle")

    return problems


def build(files: list[Path], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as bundle:
        for source, arcname in _entries(files):
            info = zipfile.ZipInfo(arcname, date_time=ZIP_EPOCH)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            bundle.writestr(info, source.read_bytes().replace(b"\r\n", b"\n"))

    size_kb = out_path.stat().st_size / 1024
    print(f"built {out_path} ({size_kb:.1f} KB)")
    print(f"  instructions.md   {len(INSTRUCTIONS.read_text(encoding='utf-8'))} chars")
    print(f"  knowledge/        {len(files)} files")


def _entries(files: list[Path]) -> list[tuple[Path, str]]:
    entries = [(INSTRUCTIONS, "instructions.md")]
    if CONFIG.is_file():
        entries.append((CONFIG, "gpt-config.json"))
    entries += [(path, f"knowledge/{path.name}") for path in files]
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate only, build nothing")
    parser.add_argument("--out-dir", default="dist", help="where to write the zip (default: dist)")
    args = parser.parse_args()

    if not SKILL_DIR.is_dir():
        print(f"error: no skill folder at {SKILL_DIR}", file=sys.stderr)
        return 1

    files = knowledge_files()
    problems = validate(files)
    if problems:
        print("error: the ChatGPT bundle does not fit ChatGPT's limits", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1

    chars = len(INSTRUCTIONS.read_text(encoding="utf-8").replace("\r\n", "\n"))
    print(
        f"ok: instructions {chars}/{MAX_INSTRUCTION_CHARS} chars, "
        f"{len(files)}/{MAX_KNOWLEDGE_FILES} knowledge files"
    )
    if args.check:
        return 0

    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = HERE / out_dir
    build(files, out_dir / "embedded-iot-mentor-gpt.zip")
    return 0


if __name__ == "__main__":
    sys.exit(main())
