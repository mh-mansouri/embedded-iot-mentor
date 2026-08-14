# Where this project is listed, and how to list it

Everything here needs an account or a login, which is why it is a checklist and not a
workflow. The files each directory expects are already in the repository — the work left is
the submission itself.

Publish to the official registry first. PulseMCP ingests it, Glama indexes the repository,
and only Smithery and the Marketplace need doing by hand — so one submission covers most of
the ground.

## MCP directories

| Where | What it needs | State |
|---|---|---|
| [Official MCP registry](https://registry.modelcontextprotocol.io) | [`server.json`](../server.json) at the repository root | **Listed** as `io.github.mh-mansouri/embedded-iot-mentor` |
| [Smithery](https://smithery.ai/new) | A running HTTPS server — **not** `smithery.yaml` any more | **Listed** at `mh-mansouri/embedded-iot-mentor` |
| [Glama](https://glama.ai/mcp/servers) | [`glama.json`](../glama.json); indexes public repositories on its own | File written; listing follows automatically |
| [PulseMCP](https://www.pulsemcp.com/submit) | Nothing — it ingests the official registry daily and processes weekly | **Follows automatically** from the registry listing |

**Submit to the official registry** (one time, from a checkout):

```bash
# The image must exist first: publish-image.yml pushes it on every tag.
curl -L "https://github.com/modelcontextprotocol/registry/releases/latest/download/mcp-publisher_$(uname -s)_$(uname -m).tar.gz" | tar xz mcp-publisher
./mcp-publisher login github        # opens a browser; proves you own the namespace
./mcp-publisher publish             # reads ./server.json
```

`mcp-publisher login github -token <PAT>` works too, and skips the browser.

The namespace `io.github.mh-mansouri/*` is owned by whoever can log in as that GitHub
account, so nobody else can claim the name.

Three rules the schema validates clean and the registry still rejects, all found the hard
way — an OCI package must carry **neither** `registryBaseUrl` **nor** `version` (the whole
reference goes in `identifier`, tag included), and the image itself must carry
`LABEL io.modelcontextprotocol.server.name` matching the name being published. That label is
in [the Dockerfile](../chatgpt-app/mcp-server/Dockerfile); changing the server name means
rebuilding the image.

**Keep it current.** `server.json` carries a version, and `test_server.py` fails when it
drifts from `SKILL.md`. Re-run `mcp-publisher publish` after a release, or the registry
advertises an image tag that is one version behind.

## The hosted connector

One instance runs on Render's free plan, deployed from [`render.yaml`](../render.yaml):

| | |
|---|---|
| Service | `https://embedded-iot-mentor-mcp.onrender.com` — `/mcp` for clients, `/healthz` to ping |
| Through Smithery | `embedded-iot-mentor--mh-mansouri.run.tools` |

It idles after about fifteen minutes without traffic and the next request pays the cold
start, so treat it as a demo instance rather than something to depend on. Anyone wanting
their own runs `docker run -p 8000:8000 ghcr.io/mh-mansouri/embedded-iot-mentor-mcp:latest`.

Smithery no longer builds from a repository — it proxies a URL you host — so the
`smithery.yaml` that used to configure a build path was removed; the "Through Smithery"
URL above is a proxy in front of the same hosted connector.

## VS Code Marketplace

**Published**:
[`mh-mansouri.embedded-iot-mentor-vscode`](https://marketplace.visualstudio.com/items?itemName=mh-mansouri.embedded-iot-mentor-vscode).
[`publish-extension.yml`](./workflows/publish-extension.yml) pushes every tag from here on;
until the `VSCE_PAT` secret existed it skipped itself rather than failing the release.

The setup, recorded because it is worse than the docs suggest: the publisher id **must**
equal `publisher` in `vscode-extension/package.json`, and the token is an Azure DevOps PAT
scoped **Marketplace → Manage**. Creating that PAT needs an Azure DevOps *organisation*,
which now refuses to be created without a linked Azure *subscription* — so the chain is
Microsoft account → Azure subscription (card required, nothing charged) → DevOps org → PAT.
Budget an hour, not the ten minutes the docs imply.

> **`VSCE_PAT` expires 31 August 2026.** Azure's default is 30 days and its date picker is
> read-only, so it was left alone. When a `publish-extension` run fails on authentication,
> this is why: make a new PAT with the same scope and replace the secret.

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
