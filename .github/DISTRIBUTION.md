# Where this project is listed, and how to list it

Everything here needs an account or a login, which is why it is a checklist and not a
workflow.

## Repository presentation

Settings the API cannot set for you:

- **Topics** — set through the API. Now that the project is just the skill and the REST
  API, drop `mcp`, `mcp-server`, `chatgpt`, and `vscode-extension` if they're still set,
  keeping `agent-skills` `arduino` `claude` `claude-code` `claude-skill` `embedded`
  `esp32` `iot` `microcontroller`.
- **Social preview** (Settings → General → Social preview → Upload):
  [`social-preview.png`](./social-preview.png), 1280×640. Rebuild it by opening
  [`social-preview.html`](./social-preview.html) and screenshotting at that size.

## Skill directories

| Where | How |
|---|---|
| [agentskills.io](https://agentskills.io) | Submit the repository; it reads `SKILL.md` frontmatter |
| `awesome-claude-skills` lists | A pull request adding one line — see the entry drafted below |

Suggested entry, matching the terse style those lists use:

```markdown
- [Embedded / IoT Mentor](https://github.com/mh-mansouri/embedded-iot-mentor) — Picks the
  microcontroller, board and toolchain for a hardware project, estimates cost and battery
  life from real duty-cycle numbers, and plans to a working breadboard instead of a
  production line. Also ships as a REST API.
```

## Retired

This project used to also ship as a VS Code extension and an MCP connector (ChatGPT
custom connector, plus listings on the official MCP registry, Smithery, and Glama). Both
were dropped to keep the surface to just the skill and the API — see CHANGELOG.md for the
version this happened in. If any of those listings or the `VSCE_PAT` secret are still
live, they're safe to take down; nothing in this repository publishes to them any more.
