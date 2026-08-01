# Embedded / IoT Mentor — VS Code extension scaffold

A minimal VS Code extension that puts the mentor prompt one command away instead of one
file-tree hunt away. It adds a single command, **Embedded / IoT Mentor: Open Copilot
Prompt**, which finds `vscode-copilot/copilot-custom-instruction.md` in the open workspace,
opens it, and copies it to the clipboard so it can go straight into Copilot Chat.

You do not need this extension to use the prompt — see
[`vscode-copilot/`](https://github.com/mh-mansouri/embedded-iot-mentor/tree/main/vscode-copilot)
for the paste-it-yourself route, which is the one most people should take. That link is
absolute on purpose: this README ships inside the `.vsix`, where a relative path out of the
extension folder resolves to nothing.

## What is here

| Path | What it is |
|---|---|
| `package.json` | Extension metadata and the one contributed command. |
| `tsconfig.json` | TypeScript settings — compiles `src/` to `dist/`. |
| `src/extension.ts` | Activation, the command, and the fallback panel shown when no prompt file is in the workspace. |
| `.vscode/` | `Run Extension` launch profile and the build tasks it depends on. |
| `LICENSE` | A copy of the repository's MIT licence, so it ships inside the `.vsix` too. |

## Run it

1. Open the `vscode-extension` folder in VS Code — **this folder, not the repository root**,
   or the launch profile will not be picked up.
2. `npm install`
3. Press <kbd>F5</kbd>, or pick the **Run Extension** profile from the Run and Debug view.
   That compiles `src/` and opens an Extension Development Host window.
4. In that new window, open a folder containing `vscode-copilot/copilot-custom-instruction.md`
   — this repository is the obvious choice — and run the command from the palette.

## Scope

This is a scaffold. It does not call the Copilot API or register a chat participant; it
only shortens the path to the prompt. `publisher` is a placeholder, so change it before
packaging with `vsce`.
