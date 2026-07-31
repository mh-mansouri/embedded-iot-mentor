# Changelog

All notable changes to this skill are documented here. Versions follow the `metadata.version` field in `embedded-iot-mentor/SKILL.md`.

## 1.0.0 - 2026-07-31

First release.

- Platform selection (ESP32, Pico, STM32, nRF52) with primary plus alternatives and the reasoning for each pick.
- Separate hardware and firmware paths, with a check for whether firmware needs to be written at all (ESPHome, Meshtastic, Tasmota, WLED) before proposing custom code.
- Time and cost estimates as ranges, including running cost across deployed nodes, not just the one-off build.
- A reject bar applied to every recommended part, board, or tool: no maintained library, single-supplier part, unsolderable package, no debug path, and more.
- MVP-first project plans that stop at a working breadboard unless later phases are explicitly requested.
- Two-axis experience intake (code vs hardware) instead of a single skill level.
- Reference files for MCU selection, connectivity, cost estimation, PCB transition, power and battery, field deployment, OTA, EMC and compliance, and the functional-safety boundary, each read only on its own trigger.
- Deterministic helper scripts: `cost_estimator.py`, `footprint_hint.py`, `sleep_budget.py`.
- Worked examples covering non-standard reply shapes: no project yet, a narrow expert question, split experience levels, and a request that is only partly buildable.
- `package_skill.py` build/verify/install tooling and a `check-skill` CI workflow that fails if the committed `.skill` bundle drifts from the source folder.
