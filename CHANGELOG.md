# Changelog

All notable changes to this skill are documented here. Versions follow the `metadata.version` field in `embedded-iot-mentor/SKILL.md`.

## 1.1.2 - 2026-08-01

The connector stops being taken on trust, and the ports become findable.

### The connector

- `search` now resolves three vocabulary gaps between how the library writes and how people
  ask: *microcontroller* reaches the MCU cheatsheet, *wifi* reaches the connectivity notes.
  Before this, "which microcontroller should I pick" returned `worked-examples` instead of
  the file written to answer it.
- The server reported a version hardcoded at build time, which went stale one release later.
  It reads `SKILL.md` now.
- New `chatgpt-app/mcp-server/test_server.py`, run by CI on every push: ranking asserted
  against eleven real questions, every document round-tripped through `fetch`, the
  calculators checked on their numbers — including the README's own claim that 15 µA against
  8 mA of sleep current turns 3.8 years into 8.3 days — and a check that a part description
  containing a semicolon stays text instead of being run.

### Distribution

- New `server.json`, `smithery.yaml` and `glama.json`: listing metadata for the MCP
  directories. `server.json` is validated against the published registry schema, and the
  connector's tests fail when its version drifts from the skill's.
- New `publish-image.yml`: the connector is published to `ghcr.io` on every tag, so it can be
  run with one `docker run` and the registry listing points at a package that resolves. The
  job starts the image and waits for `/healthz` before it will leave it behind.
- New `publish-extension.yml`: publishes to the VS Code Marketplace once a `VSCE_PAT` secret
  exists, and skips itself until then rather than failing a tagged release.
- The extension gets an icon, keywords, and a README written as a Marketplace page.
- CI, release and licence badges; a 1280×640 social preview card, with the HTML that
  generated it kept beside it.
- New `.github/DISTRIBUTION.md`: what is listed where, and what each remaining submission
  needs. All of it needs a login, so none of it can be a workflow.

## 1.1.1 - 2026-08-01

Distribution only — the mentor itself is unchanged from 1.1.0. Every route now starts from
something you download or click rather than something you build.

- The release workflow builds and attaches the VS Code extension as a `.vsix`. Until it is on
  the Marketplace, *Install from VSIX* is the only way to run the extension, and a `.vsix`
  built on a laptop is whatever that laptop had installed.
- The extension carries a real `publisher` and follows the repository's version, which the
  release workflow now checks the way it already checked `metadata.version`. The version lives
  in the `.vsix` filename and nowhere else, so a stale one ships a mislabelled download.
- The release workflow is idempotent: run it again from the Actions tab against a tag that
  already has a release and it refreshes the notes and re-uploads the assets, instead of
  failing the way `gh release create` does.
- New **Try it** table at the top of all three READMEs — a direct download for the skill, the
  `.vsix`, the GPT, and the Render button — because the install instructions came after four
  screens of what the skill does.
- The connector's README names Render's free-plan idle timeout. The cold start after it is
  long enough for ChatGPT to give up on the first call and look broken.

## 1.1.0 - 2026-08-01

Added the viewing layer — the hop from a working device to a person actually looking at the reading, which the first release left to chance — and ported the mentor to VS Code and ChatGPT.

### The skill

- New `references/data-and-dashboards.md`: routes from device to viewer (own web page, BLE and a phone app, Home Assistant, MQTT plus Node-RED, InfluxDB and Grafana, hosted dashboards, LoRaWAN network servers, SD-card logging, a custom app) with what each needs, what it costs to run, and the effort it takes.
- New recommendation step, *Where the data is seen*, and a matching row in the output format, so a plan says where readings land instead of stopping at the firmware.
- Clarifying question about who looks at the data and from where, because "see it on my phone" at home and from elsewhere are different builds.
- Reject-bar entry for hosted services whose free tier cannot hold the project's update rate, retention, or node count, or that cannot export the data back out.
- Traps named explicitly: port forwarding a hobby device, free-tier boundaries, retention, an always-on box as a single point of failure, buffering through outages, and whose clock timestamps a reading.

### Ports

The ports carry the mentor's judgement to other assistants. None of them changes the skill.

- New `vscode-copilot/`: the mentor as a GitHub Copilot custom instruction, installable repository-wide as `.github/copilot-instructions.md` or pasted into a single chat. Carries the MVP-first framing, the split between hardware and firmware paths, the preference for ready-made firmware, the two-axis experience question, regional buy-ability, the reject bar, and the hand-off on safety-critical, vehicle, and privacy questions. It does not carry the reference files or the helper scripts.
- New `vscode-extension/`: a scaffold VS Code extension whose one command finds the prompt in the open workspace, opens it, and copies it to the clipboard. Ships the `Run Extension` launch profile and build tasks it needs, and carries the repository metadata and licence copy that `vsce package` requires, so it builds and packages warning-free on a clean checkout.
- New `chatgpt-app/`: the mentor for ChatGPT, in two routes that share one instruction file. `custom-gpt/instructions.md` is the skill compressed to ChatGPT's 8000-character limit, with the reference files and helper scripts uploaded as GPT knowledge and run in Code Interpreter; `mcp-server/server.py` is an MCP server for use as a ChatGPT custom connector, exposing `mentor_guidance`, `search`, `fetch`, `estimate_bom_cost`, `hand_solder_hint` and `battery_runtime`.
- The connector reimplements nothing: it reads `references/` and `examples/` from the skill folder and shells out to the skill's own `scripts/`, so a battery runtime quoted through ChatGPT is the number the skill would have quoted, and a fix to the skill needs no re-upload.
- `search` and `fetch` keep the names and response shapes ChatGPT expects, so the connector works in deep research as well as ordinary chat. Ranking weights a term by its share across the library and divides by document length, so `worked-examples.md` stops answering every query.
- New `chatgpt-app/build_chatgpt_bundle.py`: assembles the upload set and fails on ChatGPT's limits — instructions over 8000 characters, more than 20 knowledge files, or an instruction naming a knowledge file that is not in the bundle. Added to the `check-skill` CI workflow, because growing the skill is what trips it.
- `chatgpt-app/dist/`, `.venv/`, `node_modules/`, `vscode-extension/dist/` and `*.vsix` are not committed.

### Distribution

- New `.github/workflows/release.yml`: pushing a `v*` tag builds both bundles, checks the tag against `metadata.version`, takes the notes from this file, and publishes a GitHub Release with `embedded-iot-mentor.skill` and `embedded-iot-mentor-gpt.zip` attached. Attaching them by hand was the step that got skipped.
- New `chatgpt-app/mcp-server/Dockerfile` and `render.yaml`: the connector deploys from the repository with no configuration, because ChatGPT only reaches a connector over HTTPS and a local run needs a tunnel.
- New `/healthz` route on the connector, so a host has something to ping — `/mcp` answers a POST inside a session and reads as a failure to an ordinary health check.

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
