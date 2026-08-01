# Changelog

All notable changes to this skill are documented here. Versions follow the `metadata.version` field in `embedded-iot-mentor/SKILL.md`.

## Unreleased

Ports of the mentor to VS Code. No change to the skill itself, so `metadata.version` stays at 1.1.0.

- New `vscode-copilot/`: the mentor as a GitHub Copilot custom instruction, installable repository-wide as `.github/copilot-instructions.md` or pasted into a single chat. Carries the MVP-first framing, the split between hardware and firmware paths, the preference for ready-made firmware, the two-axis experience question, regional buy-ability, the reject bar, and the hand-off on safety-critical, vehicle, and privacy questions. It does not carry the reference files or the helper scripts.
- New `vscode-extension/`: a scaffold VS Code extension whose one command finds the prompt in the open workspace, opens it, and copies it to the clipboard. Ships the `Run Extension` launch profile and build tasks it needs.
- `node_modules/`, `vscode-extension/dist/`, and `*.vsix` added to `.gitignore`.

## 1.1.0 - 2026-07-31

Added the viewing layer — the hop from a working device to a person actually looking at the reading, which the first release left to chance.

- New `references/data-and-dashboards.md`: routes from device to viewer (own web page, BLE and a phone app, Home Assistant, MQTT plus Node-RED, InfluxDB and Grafana, hosted dashboards, LoRaWAN network servers, SD-card logging, a custom app) with what each needs, what it costs to run, and the effort it takes.
- New recommendation step, *Where the data is seen*, and a matching row in the output format, so a plan says where readings land instead of stopping at the firmware.
- Clarifying question about who looks at the data and from where, because "see it on my phone" at home and from elsewhere are different builds.
- Reject-bar entry for hosted services whose free tier cannot hold the project's update rate, retention, or node count, or that cannot export the data back out.
- Traps named explicitly: port forwarding a hobby device, free-tier boundaries, retention, an always-on box as a single point of failure, buffering through outages, and whose clock timestamps a reading.

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
