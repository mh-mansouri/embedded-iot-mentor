import * as vscode from 'vscode';

// The prompt lives in the sibling vscode-copilot/ folder rather than inside the
// extension, so there is only ever one copy of it to keep up to date.
const PROMPT_GLOB = '**/vscode-copilot/copilot-custom-instruction.md';

export function activate(context: vscode.ExtensionContext) {
  const disposable = vscode.commands.registerCommand('embeddedIoTMentor.openPrompt', async () => {
    const [promptUri] = await vscode.workspace.findFiles(PROMPT_GLOB, '**/node_modules/**', 1);

    if (!promptUri) {
      showFallback();
      return;
    }

    const document = await vscode.workspace.openTextDocument(promptUri);
    await vscode.window.showTextDocument(document, vscode.ViewColumn.One);
    await vscode.env.clipboard.writeText(document.getText());

    vscode.window.showInformationMessage(
      'Mentor prompt copied. Paste it into Copilot Chat, or save it as .github/copilot-instructions.md.'
    );
  });

  context.subscriptions.push(disposable);
}

export function deactivate() {}

function showFallback() {
  const panel = vscode.window.createWebviewPanel(
    'embeddedIoTMentor',
    'Embedded / IoT Mentor',
    vscode.ViewColumn.One,
    {}
  );

  panel.webview.html = getWebviewContent();
}

function getWebviewContent(): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline';" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Embedded / IoT Mentor</title>
</head>
<body>
  <h1>Embedded / IoT Mentor</h1>
  <p>No mentor prompt was found in this workspace.</p>
  <p>
    Open a folder that contains <code>vscode-copilot/copilot-custom-instruction.md</code>
    and run the command again, or copy that file from the
    <code>embedded-iot-mentor</code> repository into your project.
  </p>
</body>
</html>`;
}
