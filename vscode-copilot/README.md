# GitHub Copilot port of the Embedded / IoT Mentor

A Copilot-friendly port of the Claude skill in [`../embedded-iot-mentor/SKILL.md`](../embedded-iot-mentor/SKILL.md).
It is a prompt, not an extension — one file you paste in, no install step.

Carried over from the skill: mentor to a working MVP and stop there, split the hardware
path from the firmware path, prefer ready-made firmware over code to be written, say where
the reading ends up rather than stopping at the sensor, judge parts against a reject bar,
and hand off plainly on safety-critical, vehicle, and privacy questions instead of
answering past the edge of hobbyist advice.

## Files

| Path | What it is |
|---|---|
| `copilot-custom-instruction.md` | The ported instruction. This is the file you paste. |
| `examples/examples.md` | Sample prompts to try once it is in place. |

## Use it

**Repository-wide (recommended).** Copy `copilot-custom-instruction.md` to
`.github/copilot-instructions.md` in your project. Copilot Chat in VS Code applies it to
every request in that repository, with nothing to re-paste.

```bash
mkdir -p .github && cp vscode-copilot/copilot-custom-instruction.md .github/copilot-instructions.md
```

**One conversation.** Paste the file into the Copilot Chat prompt box, then ask your
question. Good for trying it out, or inside a repository whose instructions you should not
change.

Either way, start with a query from `examples/examples.md`.

## What it does not carry

The reference files, the helper scripts, and the worked examples stay on the Claude side.
This port keeps the mentor's judgement and its limits; it does not have the MCU tables,
the cost-estimation method, or the sleep-budget calculator behind them. For a real battery
runtime or a BOM total, use the skill — or check the number yourself.
