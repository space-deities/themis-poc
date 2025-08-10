# FOPs Prompter (VS Code Extension)

This extension shows interactive prompts from your running FOPs (Python) code and sends your response back.

## Quick start

1. Open this folder in VS Code.
2. Run `npm install`.
3. Press `F5` to launch the Extension Development Host.
4. In the Command Palette, run **FOPs: Open Prompter** to open the UI.
5. Run your Python process that posts prompts to `http://localhost:5533/` (by default).

## Protocol

The extension runs a local HTTP server:

- `POST /prompt` with JSON `{ "message": string, "options": ["r","s","c"] }` → returns `{ "id": string }`.
- `GET /wait?id=...` → blocks until the user answers → returns `{ "id": string, "answer": "r"|"s"|"c"|"text" }`.
- `POST /answer` with JSON `{ "id": string, "answer": string }` → sets an answer programmatically (used by the webview).

You may change the port via **Settings → FOPs Prompter: Port**.
