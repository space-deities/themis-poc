// src/extension.ts
import * as vscode from 'vscode';
import { createServer, IncomingMessage, ServerResponse } from 'http';
import { randomUUID } from 'crypto';
import { URL } from 'url';

type Prompt = {
  id: string;
  message: string;
  options?: string[];
  createdAt: number;
  answer?: string;                         // set when the user responds
  waiters: Array<(ans: string) => void>;   // resolvers waiting for the answer
};

let prompts = new Map<string, Prompt>();
let panel: vscode.WebviewPanel | undefined;
let serverStarted = false;

export function activate(context: vscode.ExtensionContext) {
  const disposable = vscode.commands.registerCommand('fops.openPrompter', () => {
    openPanel();
  });
  context.subscriptions.push(disposable);

  startServer(context);
}

export function deactivate() {}

/* ------------------------------ Webview Panel ------------------------------ */

function openPanel() {
  if (panel) {
    panel.reveal();
    return;
  }
  panel = vscode.window.createWebviewPanel(
    'fopsPrompter',
    'FOPs Prompter',
    vscode.ViewColumn.Active,
    { enableScripts: true }
  );

  panel.onDidDispose(() => (panel = undefined));

  updateWebview();

  panel.webview.onDidReceiveMessage((msg: any) => {
    if (msg?.type === 'answer') {
      const p = prompts.get(String(msg.id));
      if (p && !p.answer) {
        const ans = String(msg.answer ?? '');
        p.answer = ans;
        // resolve all pending waiters with the concrete string
        for (const w of p.waiters) w(ans);
        p.waiters = [];
        updateWebview();
      }
    } else if (msg?.type === 'clear') {
      // remove answered prompts from the list
      for (const [id, p] of prompts.entries()) {
        if (p.answer) prompts.delete(id);
      }
      updateWebview();
    }
  });
}

function updateWebview() {
  if (!panel) return;
  const list = Array.from(prompts.values())
    .sort((a, b) => a.createdAt - b.createdAt)
    .map((p) => ({
      id: p.id,
      message: p.message,
      options: p.options ?? ['r', 's', 'c'],
      answer: p.answer,
    }));
  panel.webview.html = renderHtml(list);
}

function renderHtml(items: Array<{ id: string; message: string; options: string[]; answer?: string }>) {
  const esc = (s: string) => s.replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]!));
  return `
    <!doctype html>
    <html>
    <body style="font-family: var(--vscode-font-family); padding: 12px;">
      <h2>FOPs Prompter</h2>
      ${items.length === 0 ? '<p>No prompts.</p>' : ''}
      <div>
        ${items
          .map(
            (item) => `
          <div style="border:1px solid var(--vscode-editorWidget-border); padding:10px; margin-bottom:8px; border-radius:8px;">
            <div><b>Message:</b> ${esc(item.message)}</div>
            <div><b>ID:</b> ${item.id}</div>
            <div><b>Status:</b> ${item.answer ? 'Answered: ' + esc(item.answer) : 'Waiting for your input'}</div>
            ${
              !item.answer
                ? `
              <div style="margin-top:8px;">
                ${(item.options || [])
                  .map((op: string) => `<button onclick="answer('${item.id}','${op}')">${op}</button>`)
                  .join('')}
                <input id="txt-${item.id}" placeholder="or type a custom response"/>
                <button onclick="custom('${item.id}')">Send</button>
              </div>`
                : ''
            }
          </div>
        `
          )
          .join('')}
      </div>
      <button onclick="clearAnswered()">Clear answered</button>
      <script>
        const vscode = acquireVsCodeApi();

        function answer(id, ans){
          vscode.postMessage({type:'answer', id, answer: String(ans)});
        }

        function custom(id){
          var el = document.getElementById('txt-'+id);
          // JSDoc cast keeps TS linters happy but is a no-op at runtime
          /** @type {{ value?: string } | null} */
          var input = el;
          var v = (input && typeof input.value === 'string') ? input.value : '';
          if(v){ vscode.postMessage({type:'answer', id, answer: v}); }
        }

        function clearAnswered(){
          vscode.postMessage({type:'clear'});
        }
      </script>
    </body>
    </html>
  `;
}

/* ------------------------------ HTTP Server ------------------------------- */

function startServer(context: vscode.ExtensionContext) {
  if (serverStarted) return;
  serverStarted = true;

  const port = vscode.workspace.getConfiguration().get<number>('fopsPrompter.port', 5533);

  const server = createServer(async (req: IncomingMessage, res: ServerResponse) => {
    try {
      if (!req.url) {
        res.statusCode = 400;
        return res.end('Bad Request');
      }
      const full = new URL(req.url, `http://localhost:${port}`);

      if (req.method === 'POST' && full.pathname === '/prompt') {
        const body = await readJson(req);
        const id = randomUUID();
        const p: Prompt = {
          id,
          message: String(body.message ?? ''),
          options: Array.isArray(body.options) ? body.options.map(String) : undefined,
          createdAt: Date.now(),
          waiters: [],
        };
        prompts.set(id, p);
        updateWebview();
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify({ id }));
        return;
      }

      if (req.method === 'GET' && full.pathname === '/wait') {
        const id = full.searchParams.get('id') || '';
        const p = prompts.get(id);
        if (!p) {
          res.statusCode = 404;
          return res.end('Unknown id');
        }
        if (p.answer) {
          res.setHeader('Content-Type', 'application/json');
          return res.end(JSON.stringify({ id, answer: p.answer }));
        }
        // wait until answered
        const ans = await new Promise<string>((resolve) => p.waiters.push(resolve));
        res.setHeader('Content-Type', 'application/json');
        return res.end(JSON.stringify({ id, answer: ans }));
      }

      if (req.method === 'POST' && full.pathname === '/answer') {
        const body = await readJson(req);
        const id = String(body.id ?? '');
        const ans = String(body.answer ?? '');
        const p = prompts.get(id);
        if (!p) {
          res.statusCode = 404;
          return res.end('Unknown id');
        }
        if (!p.answer) {
          p.answer = ans;
          for (const w of p.waiters) w(ans);
          p.waiters = [];
          updateWebview();
        }
        res.setHeader('Content-Type', 'application/json');
        return res.end(JSON.stringify({ ok: true }));
      }

      res.statusCode = 404;
      res.end('Not found');
    } catch (e: any) {
      res.statusCode = 500;
      res.end('Server error: ' + (e?.message || e));
    }
  });

  server.listen(port, '127.0.0.1', () => {
    console.log(`[FOPs Prompter] listening on http://127.0.0.1:${port}`);
    vscode.window.setStatusBarMessage(`FOPs Prompter: listening on ${port}`, 5000);
  });

  context.subscriptions.push({ dispose: () => server.close() });
}

/* --------------------------------- Utils ---------------------------------- */

function readJson(req: IncomingMessage): Promise<any> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    req.on('data', (c: Buffer) => chunks.push(c));
    req.on('end', () => {
      try {
        const raw = Buffer.concat(chunks).toString('utf8') || '{}';
        resolve(JSON.parse(raw));
      } catch (e) {
        reject(e);
      }
    });
    req.on('error', reject);
  });
}
