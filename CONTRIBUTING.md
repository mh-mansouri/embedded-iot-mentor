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
| `embedded-iot-mentor.skill` | **Generated.** A zip of the folder above — don't edit by hand. |
| `package_skill.py` | Builds, verifies, and installs the bundle. |

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
4. Confirm the gate passes:
   ```bash
   python package_skill.py --check
   ```
   This is exactly what CI runs. It checks the frontmatter against the
   [Agent Skills spec](https://agentskills.io/specification), confirms every file `SKILL.md`
   references exists, and confirms the committed bundle matches the source folder.
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

## Ground rules

- Explain the *why* behind a change so others can learn from it.
- Assume the reader owns nothing and knows nothing about the platform being recommended.
- No affiliate links, and no promoting a vendor without saying why it wins on the merits.
