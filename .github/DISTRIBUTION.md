# Where this project is listed, and how to list it

Everything here needs an account or a login, which is why it is a checklist and not a
workflow. The files each directory expects are already in the repository — the work left is
the submission itself.

## MCP directories

| Where | What it needs | State |
|---|---|---|
| [Official MCP registry](https://registry.modelcontextprotocol.io) | [`server.json`](../server.json) at the repository root | File written and schema-validated; not yet submitted |
| [Smithery](https://smithery.ai/new) | [`smithery.yaml`](../smithery.yaml) at the repository root | File written; not yet submitted |
| [Glama](https://glama.ai/mcp/servers) | [`glama.json`](../glama.json); indexes public repositories on its own | File written; listing follows automatically |
| [PulseMCP](https://www.pulsemcp.com/submit) | A form — repository URL and one description | Not yet submitted |

**Submit to the official registry** (one time, from a checkout):

```bash
# The image must exist first: publish-image.yml pushes it on every tag.
curl -L "https://github.com/modelcontextprotocol/registry/releases/latest/download/mcp-publisher_$(uname -s)_$(uname -m).tar.gz" | tar xz mcp-publisher
./mcp-publisher login github        # opens a browser; proves you own the namespace
./mcp-publisher publish             # reads ./server.json
```

The namespace `io.github.mh-mansouri/*` is owned by whoever can log in as that GitHub
account, so nobody else can claim the name.

**Keep it current.** `server.json` carries a version, and `test_server.py` fails when it
drifts from `SKILL.md`. Re-run `mcp-publisher publish` after a release, or the registry
advertises an image tag that is one version behind.

## VS Code Marketplace

One-time setup, then [`publish-extension.yml`](./workflows/publish-extension.yml) does it on
every tag:

1. Create a publisher at <https://marketplace.visualstudio.com/manage>. The id **must** equal
   `publisher` in `vscode-extension/package.json` — currently `mh-mansouri`.
2. Make an Azure DevOps personal access token: scope **Marketplace → Manage**, organisation
   **All accessible organisations**.
3. Add it as the repository secret `VSCE_PAT`.

Until that secret exists the workflow skips itself rather than failing the release.

## Repository presentation

Settings the API cannot set for you:

- **Topics** — done, set through the API:
  `agent-skills` `arduino` `chatgpt` `claude` `claude-code` `claude-skill` `embedded`
  `esp32` `iot` `mcp` `mcp-server` `microcontroller` `vscode-extension`
- **Social preview** (Settings → General → Social preview → Upload):
  [`social-preview.png`](./social-preview.png), 1280×640. Rebuild it by opening
  [`social-preview.html`](./social-preview.html) and screenshotting at that size.
- **Description**: the one-liner from `server.json` fits the field and matches the card.

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
  production line. Also ships as a ChatGPT GPT, an MCP connector and a VS Code extension.
```
