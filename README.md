# embedded-iot-mentor

A Claude Code Agent Skill that acts as an embedded-systems / IoT project mentor: MCU and tool selection, hardware/software recommendations with alternatives, time & cost estimates, and MVP-first build plans through to production PCB.

Claude loads `SKILL.md` automatically when a conversation mentions embedded/IoT topics (ESP32, STM32, Arduino, KiCad, PlatformIO, PCB, firmware, etc.) — see the `description` in its frontmatter for the full trigger list. This README is for humans browsing the repo; it isn't read by Claude at runtime.

## Layout

- `SKILL.md` — the skill definition (role, style rules, recommendation process, output format).
- `references/` — detail loaded on demand: MCU selection, cost estimation, PCB transition checklist, power/battery notes, learning resources.
- `scripts/` — small deterministic helpers, run only when a concrete calculation is needed.

## Scripts

```bash
python scripts/cost_estimator.py 1 4.50 "ESP32 DevKit" 10 0.12 "10k resistor"
python scripts/footprint_hint.py 0603
```
