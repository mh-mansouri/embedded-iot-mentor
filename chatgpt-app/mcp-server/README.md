# The mentor as a ChatGPT connector (MCP server)

A [Model Context Protocol](https://modelcontextprotocol.io) server that hands ChatGPT the
whole skill — the rules, the reference library, and the three calculators — instead of
asking someone to build a GPT by hand. ChatGPT calls it a **custom connector**; the same
server works in Claude Desktop, Claude Code, or any other MCP client.

Unlike the Custom GPT route, nothing here is a copy. The documents are read from
`embedded-iot-mentor/references/` at request time and the calculators shell out to
`embedded-iot-mentor/scripts/`, so a runtime quoted through the connector is the number the
Claude skill would have quoted.

## Tools

| Tool | What it does |
|---|---|
| `mentor_guidance` | Returns the ported mentor rules — length limits, MVP-first framing, the reject bar, where to hand off. Call it before giving project advice. |
| `search` | Ranks the reference library against a query and returns ids. |
| `fetch` | Returns one reference document in full, by id. |
| `estimate_bom_cost` | Totals a BOM from `{qty, unit_price, description}` lines. |
| `hand_solder_hint` | Whether a named package (0402, SOT-23, QFN-32, BGA…) is realistic by hand. |
| `battery_runtime` | Runtime for a duty-cycled device, and whether sleep or wake dominates. |

`search` and `fetch` keep the names and shapes ChatGPT expects, so the connector also works
in deep research, not just ordinary chat.

## Run it

```bash
cd chatgpt-app/mcp-server
python -m venv .venv && . .venv/bin/activate    # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python server.py                 # http://127.0.0.1:8000/mcp
```

```bash
python server.py --transport stdio    # for a local client such as Claude Desktop
```

Needs Python 3.10 or newer, which the MCP SDK requires. Nothing else is installed — the
calculators are the skill's own standard-library scripts.

## Connect it to ChatGPT

ChatGPT reaches a connector over **HTTPS**, so `127.0.0.1` will not do. Either deploy the
server somewhere with a certificate, or put a tunnel in front of a local run:

```bash
cloudflared tunnel --url http://127.0.0.1:8000     # or: ngrok http 8000
```

Then, in ChatGPT: **Settings → Connectors → Create**, paste `https://<your-host>/mcp`, and
enable it in the conversation with the **+** menu. Custom connectors need developer mode on
a paid plan; availability differs by plan and region, and ChatGPT will say so if yours does
not have it.

An early call to `mentor_guidance` is what makes the answers behave like the skill rather
than like generic ChatGPT. The server asks for that in its own instructions, but a plain
*"use the embedded mentor"* at the start of a chat makes it certain.

## Deploying it

Any host that runs Python and terminates TLS will do. Two things matter:

- **`HOST=0.0.0.0`** — the default binds to loopback only, which a container will not serve.
- **The skill folder must ship with the server.** It reads `references/`, `examples/` and
  `scripts/` from `../../embedded-iot-mentor` by default; set `EIM_SKILL_DIR` if the layout
  is different where you deploy it.

| Variable | Default | Why |
|---|---|---|
| `HOST` | `127.0.0.1` | Set to `0.0.0.0` behind a proxy or in a container |
| `PORT` | `8000` | Most hosts assign one |
| `EIM_SKILL_DIR` | `../../embedded-iot-mentor` | Where the references and scripts live |
| `EIM_INSTRUCTIONS` | `../custom-gpt/instructions.md` | The rules `mentor_guidance` returns |
| `EIM_REPO_URL` | this repository on GitHub | Prefix for the citation links `search` returns |

The server has no authentication. Anything it exposes is public documentation and pure
arithmetic, but it will run scripts for anyone who can reach it, so put it behind whatever
access control your host offers rather than on an open port.
