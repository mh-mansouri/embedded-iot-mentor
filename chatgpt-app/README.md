# ChatGPT port of the Embedded / IoT Mentor

The mentor is judgement written down, not a Claude feature, so it ports. This folder is the
ChatGPT side of it, in two routes.

| Route | What you do | Worth it when |
|---|---|---|
| [`custom-gpt/`](./custom-gpt/) | Build a GPT: paste one instruction file, upload the knowledge files | Always start here — 10 minutes in the browser, works on any plan that can create a GPT |
| [`mcp-server/`](./mcp-server/) | Run a small MCP server and add it as a custom connector | You want the calculators to be real, the references to stay in sync, and no per-machine setup for the next person |

Both routes carry what matters: MVP first, the hardware path kept apart from the firmware
path, ready-made firmware ahead of firmware to be written, the reject bar applied before
anything is recommended, regional buy-ability, and the hand-off on safety-critical, vehicle,
and privacy questions. Both read the same `custom-gpt/instructions.md`, so the two cannot
drift apart.

The difference is what happens behind the rules. The GPT gets copies of the reference files
and scripts, uploaded once. The connector reads them from the skill folder on every call, so
a fix to the skill lands in ChatGPT without re-uploading anything.

## Build a GPT (route A)

```bash
python build_chatgpt_bundle.py     # -> dist/embedded-iot-mentor-gpt.zip
```

Unzip it, then in ChatGPT: **Explore GPTs → Create**, open the **Configure** tab, and

1. paste `instructions.md` into **Instructions**;
2. upload everything in `knowledge/` under **Knowledge** — 12 reference documents and the 3
   helper scripts;
3. tick **Code Interpreter & Data Analysis**. The mentor is told to *run* `sleep_budget.py`
   rather than estimate a battery runtime in prose, and without the sandbox it cannot;
4. copy the name, description and conversation starters from `gpt-config.json`.

Then try a prompt from [`examples/examples.md`](./examples/examples.md).

Nothing here is imported automatically — ChatGPT has no import format for a GPT, so the
build script's job is to assemble the upload set and check it fits: instructions under
8000 characters, knowledge under 20 files, and no instruction pointing at a file that is not
in the bundle.

```bash
python build_chatgpt_bundle.py --check    # what CI runs
```

## Run the connector (route B)

See [`mcp-server/README.md`](./mcp-server/README.md). Short version:

```bash
pip install -r mcp-server/requirements.txt
python mcp-server/server.py          # http://127.0.0.1:8000/mcp
```

ChatGPT reaches a connector over HTTPS, so a local run needs a tunnel; then add the URL
under **Settings → Connectors**. Custom connectors need developer mode on a paid plan.

## Layout

| Path | What it is |
|---|---|
| `custom-gpt/instructions.md` | The ported mentor, trimmed to ChatGPT's 8000-character instruction limit. Both routes use it. |
| `custom-gpt/gpt-config.json` | Name, description, conversation starters and capability switches to copy into the builder. |
| `mcp-server/server.py` | The connector: six tools over MCP, no logic of its own. |
| `build_chatgpt_bundle.py` | Assembles and validates the upload set. |
| `examples/examples.md` | Prompts that exercise the behaviours the port is supposed to keep. |
| `dist/` | **Generated.** Not committed. |

## What each route gives up

The GPT's knowledge files are copies: rebuild the bundle and re-upload after editing the
skill, or it will answer from a stale reference. The connector avoids that but has to be
running somewhere ChatGPT can reach.

Both are missing one thing the Claude skill has: the mentor's full instructions. `SKILL.md`
is around 19 000 characters and ChatGPT's instruction box holds 8000, so the port is
compressed — the same rules with the worked reasoning and most of the examples taken out.
For the full version, use the skill.
