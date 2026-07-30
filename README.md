# Embedded / IoT Mentor — a Claude Skill

A skill for [Claude](https://claude.ai) that acts as an experienced embedded-systems mentor:
it picks the microcontroller, board, and toolchain for your project, estimates what it will
cost and how long it will take, and hands you a build plan that stops at a **working
breadboard** instead of a production line you didn't ask for.

Most embedded advice fails in one of two directions — a parts list with no plan, or a
production roadmap for someone who hasn't blinked an LED yet. This skill asks what you've
actually built before, then answers at that level.

## What it does

- **Picks a platform** — ESP32, Pico, STM32, nRF52 — and says plainly why that one, plus one
  or two alternatives and when each would win instead.
- **Separates the hardware path from the firmware path**, so you know what to buy and what to
  install without conflating them.
- **Estimates time and cost** as ranges, and flags what actually drives them.
- **Plans to MVP and stops there.** Engineering prototype, pre-production, and production
  phases exist, but you only get them when you ask.
- **Names the risks** — power budget, part availability, no debug path, certification, the
  learning curve on whatever it just recommended.
- **Rejects its own suggestions** against a fixed bar: no maintained library, single-supplier
  part, a package you can't solder, no serial console — it drops the candidate and picks again.

## Why it exists

The failure modes it's built to catch:

- **A beginner pointed at an STM32 with an ST-Link** because a forum said it was "more
  professional" — three evenings lost to toolchain setup before the first LED.
- **A battery project designed around a dev board** whose regulator idles at 20 mA, so the
  "two month" runtime is really four days. The board was never the problem; nobody costed the
  sleep current.
- **A first PCB ordered with 0402 passives and a QFN**, hand-assembled with a soldering iron,
  and dead on arrival with no test points to find out why.

## Install

**Option A — one file.** Download [`embedded-iot-mentor.skill`](./embedded-iot-mentor.skill)
and open it in Claude. (Skill saving must be enabled for your account or organization.)

**Option B — Claude Code.** Unpack it into your skills directory:

```bash
python package_skill.py --install                                     # for your user
python package_skill.py --install --skills-dir <repo>/.claude/skills  # for one project
```

Or install a bundle you already have, with no copy of this repo:

```bash
python package_skill.py --install-from embedded-iot-mentor.skill
```

Or by hand — a `.skill` is just a zip:

```bash
mkdir -p ~/.claude/skills && unzip embedded-iot-mentor.skill -d ~/.claude/skills/
```

```powershell
# Windows: Expand-Archive refuses any extension but .zip, so rename a copy first
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item embedded-iot-mentor.skill "$env:TEMP\embedded-iot-mentor.zip"
Expand-Archive "$env:TEMP\embedded-iot-mentor.zip" -DestinationPath "$HOME\.claude\skills" -Force
```

Claude Code picks it up on the next session — `/skills` lists it, and Claude also loads it on
its own when a conversation matches the description.

## Use it

Just describe the project. For example:

> I want to log soil moisture in a greenhouse and see it on my phone. I've done a couple of
> Arduino sketches. Budget maybe €100, and I'd like it running in a month.

or

> Which board for a battery sensor that has to last a year on a coin cell? I've shipped
> firmware before, so don't dumb it down.

or

> I have an ESP32 and a BME280 sitting in a drawer. What's worth building with them?

It will ask a couple of short questions if the goal, experience level, power source, or
timeline are still unclear — then answer in tables rather than essays.

## Good to know

- **Prices and stock go stale.** Estimates are ranges, not quotes. Check LCSC, Digi-Key, or
  your local supplier before ordering.
- **It cannot verify part availability** in your country, and that is the most common reason
  a good plan stalls.
- **It stops at MVP by design.** Ask explicitly for the later phases.
- **Not for safety-critical work.** It will help you to a prototype for medical, automotive,
  or safety systems, then tell you plainly where hobbyist advice ends.

## Layout

The skill itself lives in `embedded-iot-mentor/`. Everything at the repository root is
packaging and project metadata that the skill never reads.

| Path | What it is |
|---|---|
| `embedded-iot-mentor/SKILL.md` | The instructions Claude follows. Most changes go here. |
| `embedded-iot-mentor/references/` | Detail read on a trigger: MCU selection, cost estimation, PCB checklist, power/battery notes, learning resources. |
| `embedded-iot-mentor/scripts/` | Small deterministic helpers, run only when a concrete number is asked for. |
| `embedded-iot-mentor/examples/` | Worked scenarios showing the *shape* a reply should take when a request doesn't fit the standard mould. |
| `embedded-iot-mentor.skill` | **Generated.** A zip of the folder above — don't edit by hand. |
| `package_skill.py` | Builds, verifies, and installs the bundle. |

Keeping the skill in its own folder matters: the spec requires a skill's `name` to match its
folder name, so building it straight from the repository root would break the moment someone
downloaded the repo as a ZIP and got `embedded-iot-mentor-main/`.

## Build

```bash
python package_skill.py          # -> ./embedded-iot-mentor.skill
python package_skill.py --check  # validate source + bundle, build nothing
```

A `.skill` file is a zip archive holding the skill folder — the format is defined by the
[Agent Skills specification](https://agentskills.io/specification). The packer bundles
everything under `embedded-iot-mentor/`, so a new reference file is picked up automatically
with no build-script edit. Text files are stored with LF and zip timestamps are pinned, so
the bundle is byte-identical whoever builds it.

`--check` is the gate, and CI runs it on every push and pull request. It fails when:

- the frontmatter breaks a spec constraint (`name` pattern/length, folder match, `description` length);
- `SKILL.md` points at a `references/…` or `scripts/…` file that doesn't exist;
- the committed `.skill` doesn't match the source folder.

That last one matters because the bundle is committed: edit the skill, forget to rebuild, and
the download would ship a different version than the source folder.

## Scripts

```bash
python embedded-iot-mentor/scripts/cost_estimator.py 1 4.50 "ESP32 DevKit" 10 0.12 "10k resistor"
python embedded-iot-mentor/scripts/footprint_hint.py 0603
python embedded-iot-mentor/scripts/sleep_budget.py --capacity 2000 --active-ma 80 \
    --active-ms 250 --sleep-ua 15 --interval-s 600
```

`sleep_budget.py` takes duty-cycle inputs rather than an average current, because the
average is the number nobody knows up front. Same firmware, same battery, sleep current
changed from 15 µA to a dev board's 8 mA regulator: **3.8 years becomes 8.3 days.**

## Contributing

Improvements are welcome — especially hands-on knowledge about parts, suppliers, and what
actually goes wrong on a bench. See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

Released under the [MIT License](./LICENSE) — free to use, share, and build on.
