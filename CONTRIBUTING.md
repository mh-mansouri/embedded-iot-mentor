# Contributing

Thanks for helping make this skill better. You don't need to be a programmer to contribute —
bench experience is the most valuable thing here.

## Ways to help

- **Report a bad recommendation.** The mentor suggested a part that's unobtainable in your
  country, a toolchain that no longer builds, or a runtime estimate that was wildly off. Open
  an issue with the project details and what actually happened.
- **Correct or add hardware knowledge.** Regional suppliers and fabs, current part
  availability, a package that's harder to hand-solder than the notes claim, a dev board whose
  quiescent current ruins battery projects.
- **Improve the wording** of the instructions so Claude follows them more reliably.
- **Sharpen a trigger.** If a reference file is being read when it isn't needed, or ignored
  when it is, the trigger table in `SKILL.md` is the thing to fix.

## Where things live

| Path | What it is |
|---|---|
| `embedded-iot-mentor/SKILL.md` | The instructions Claude follows. Most changes go here. |
| `embedded-iot-mentor/references/` | Detail read on a trigger, one file per topic. |
| `embedded-iot-mentor/scripts/` | Deterministic helpers. Standard library only — no dependencies. |
| `embedded-iot-mentor/examples/` | Worked scenarios. A new one earns its place by showing a *reply shape* the existing three don't. |
| `embedded-iot-mentor.skill` | **Generated.** A zip of the folder above — don't edit by hand. |
| `package_skill.py` | Builds, verifies, and installs the bundle. |
| `vscode-copilot/` | Port to GitHub Copilot Chat — a paste-in prompt, no build step. A behaviour change to `SKILL.md` usually belongs in `vscode-copilot/copilot-custom-instruction.md` too — say in the pull request if you deliberately left it behind. |
| `api/` | The REST API. `api/main.py` reads `embedded-iot-mentor/references/` and shells out to its scripts; `api/instructions.md` is the mentor's rules condensed to a self-contained `/chat` system prompt — mirror a `SKILL.md` behaviour change there too. |
| `.github/workflows/release-reminder.yml` | Weekly check for shipped-surface changes since the last tag — see "Cutting a release" below. |
| `.github/workflows/reference-review.yml` | Weekly reminder issue to check the reference files for stale prices, stock, or toolchain claims — see "Keeping estimates honest" below. |
| `CHANGELOG.md` | Human-readable release history, [Keep a Changelog](https://keepachangelog.com/) format. Versions follow `embedded-iot-mentor/SKILL.md`'s `metadata.version`. |

`SKILL.md` points Claude at the reference files and scripts by relative path, so if you rename
or move one, update `SKILL.md` too — `--check` fails if you forget.

## How to propose a change

1. Fork the repository.
2. Make your edit (most changes live in `embedded-iot-mentor/SKILL.md`).
3. **If you changed anything inside `embedded-iot-mentor/`, rebuild the bundle:**
   ```bash
   python package_skill.py
   ```
   Commit the regenerated `embedded-iot-mentor.skill` alongside your edit — otherwise the
   one-file download and the source folder ship different versions of the skill.
4. Confirm the gate passes, and the API still works if you touched it:
   ```bash
   python package_skill.py --check
   python api/test_api.py
   ```
   The first is exactly what CI runs: checks the frontmatter against the
   [Agent Skills spec](https://agentskills.io/specification), confirms every file `SKILL.md`
   references exists, and confirms the committed bundle matches the source folder. The second
   confirms the API's routes, including `/chat`'s use of `api/instructions.md`.
5. Open a pull request with a short note on what you changed and why.

If you changed the skill's behaviour, please try it on a couple of real project briefs first
and say what you tested in the pull request.

## Adding a reference file

Keep each reference file focused on one topic and add a row to the trigger table in
`SKILL.md` saying **when** Claude should read it — not just what's in it. Claude loads these
on demand, so a file that's read when it isn't needed costs context on every answer.

Don't commit datasheets, catalogues, or vendor PDFs. Link to them instead. Bundle a file only
when its license clearly permits redistribution, and add the attribution to a `NOTICE.md` if
you do.

## Keeping estimates honest

Prices, stock, and toolchain details go stale. Prefer ranges over point figures, say what
drives the number, and name the date or source when you cite a concrete price.
`reference-review.yml` opens a weekly issue as a nudge to re-check this; close it once
reviewed, or open a PR first if something needs fixing.

## Cutting a release

`release-reminder.yml` runs weekly and opens an issue *only* when something in the
**shipped surface** — `embedded-iot-mentor/` (what `package_skill.py` bundles into the
`.skill`) or `universal-prompt.md` — has changed since the last tag. That's the actual
criterion: **does this change what a user installs or pastes?**

- **Triggers a reminder:** any edit to `SKILL.md`, `references/`, `scripts/`, `examples/`,
  `universal-prompt.md`, or `package_skill.py` itself.
- **Doesn't trigger one:** README/translation wording, `docs/index.html`, CI/workflow
  files, `vscode-copilot/`, or the API. None of that changes what a tagged release
  installs, so it doesn't need a version bump — see below for why the API is different.

When a reminder fires, classify the change before tagging:

| Bump | When |
|---|---|
| **PATCH** | Wording/typo fix, no behavior change |
| **MINOR** | New capability, backward compatible — an existing recommendation flow still works |
| **MAJOR** | Breaks or invalidates prior output — a required output-format field removed/renamed, a reject-bar rule reversed |

Then: bump `metadata.version` in `SKILL.md`, rebuild the bundle
(`python package_skill.py`), move `CHANGELOG.md`'s entries under the new version heading,
and tag:

```
git tag -a vX.Y.Z -m "..." && git push origin vX.Y.Z
```

`release.yml` takes it from there — builds the bundle, checks the tag against `SKILL.md`,
and publishes the GitHub Release with it attached.

The API isn't part of any of this: it deploys continuously from `main` on Render, so a fix
ships the moment it's pushed, with no tag and no version bump. If the fix changed what
`api/instructions.md` tells the model to do, mirror it in `SKILL.md` too (or the reverse)
so the two don't quietly describe different mentors.

## Ground rules

- Explain the *why* behind a change so others can learn from it.
- Assume the reader owns nothing and knows nothing about the platform being recommended.
- No affiliate links, and no promoting a vendor without saying why it wins on the merits.
