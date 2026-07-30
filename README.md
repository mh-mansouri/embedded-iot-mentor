# embedded-iot-mentor

A Claude Code Agent Skill that acts as an embedded-systems / IoT project mentor: MCU and tool selection, hardware/software recommendations with alternatives, time & cost estimates, and MVP-first build plans through to production PCB.

Claude loads `SKILL.md` automatically when a conversation mentions embedded/IoT topics (ESP32, STM32, Arduino, KiCad, PlatformIO, PCB, firmware, etc.) — see the `description` in its frontmatter for the full trigger list. This README is for humans browsing the repo; it isn't read by Claude at runtime.

## Layout

The skill itself lives in `embedded-iot-mentor/`. Everything at the repository root is
packaging and project metadata that the skill never reads.

| Path | What it is |
|---|---|
| `embedded-iot-mentor/SKILL.md` | The instructions Claude follows. Most changes go here. |
| `embedded-iot-mentor/references/` | Detail loaded on demand: MCU selection, cost estimation, PCB checklist, power/battery notes, learning resources. |
| `embedded-iot-mentor/scripts/` | Small deterministic helpers, run only when a concrete calculation is needed. |
| `embedded-iot-mentor.skill` | **Generated.** A zip of the folder above — don't edit by hand. |
| `package_skill.py` | Builds, verifies, and installs the bundle. |

Keeping the skill in its own folder matters: the spec requires a skill's `name` to match its
folder name, so building it straight from the repository root would break the moment someone
downloaded the repo as a ZIP and got `embedded-iot-mentor-main/`.

## Package

```bash
python package_skill.py          # -> ./embedded-iot-mentor.skill
python package_skill.py --check  # validate source + bundle, build nothing
```

A `.skill` file is a zip archive holding the skill folder — the format is defined by the
[Agent Skills specification](https://agentskills.io/specification). The packer bundles
everything under `embedded-iot-mentor/`, so a new reference file is picked up automatically
with no build-script edit.

`--check` is the gate. It fails if any of these is true, and CI runs it on every push and
pull request:

- the frontmatter breaks a spec constraint (`name` pattern/length, folder match, `description` length);
- `SKILL.md` points at a `references/…` or `scripts/…` file that doesn't exist;
- the committed `.skill` doesn't match the source folder byte for byte.

That last one matters because the bundle is committed: edit the skill, forget to rebuild, and
the one-click download would ship a different version than the source folder.

## Install

Installing means unpacking the bundle into a skills directory. The folder name must stay
`embedded-iot-mentor`, since the spec requires it to match the `name` in the frontmatter.

| Scope | Destination |
|-------|-------------|
| Personal (all projects) | `~/.claude/skills/` |
| Project (committed, shared with the repo) | `<repo>/.claude/skills/` |

The packer doubles as the installer and works the same on Windows, macOS, and Linux:

```bash
python package_skill.py --install                          # build + install for your user
python package_skill.py --install --skills-dir <repo>/.claude/skills   # install into a project
```

To install a bundle you already have, with no copy of this repo present:

```bash
python package_skill.py --install-from embedded-iot-mentor.skill
```

Or unpack it by hand — a `.skill` is just a zip:

```bash
mkdir -p ~/.claude/skills && unzip embedded-iot-mentor.skill -d ~/.claude/skills/
```

On Windows, `Expand-Archive` refuses any extension but `.zip`, so rename the copy first:

```powershell
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item embedded-iot-mentor.skill "$env:TEMP\embedded-iot-mentor.zip"
Expand-Archive "$env:TEMP\embedded-iot-mentor.zip" -DestinationPath "$HOME\.claude\skills" -Force
```

Claude Code picks the skill up on the next session — `/skills` lists it, and Claude also loads it
automatically when a conversation matches the `description`. For other Agent Skills-compatible
tools, or for uploading to claude.ai, check that client's own skills directory or upload page.

## Scripts

```bash
python embedded-iot-mentor/scripts/cost_estimator.py 1 4.50 "ESP32 DevKit" 10 0.12 "10k resistor"
python embedded-iot-mentor/scripts/footprint_hint.py 0603
```

## License

Released under the [MIT License](./LICENSE) — free to use, share, and build on.
