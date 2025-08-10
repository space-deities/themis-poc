import time
import json
import urllib.request
import urllib.error

EXT_PORT = 5533  # keep in sync with VS Code extension setting

def ask_vscode(message: str, options=None, *, timeout=3600):
    """Send a prompt to the VS Code extension and wait for the answer.
    Raises URLError if the extension is not reachable.
    """
    options = options or ['r','s','c']
    data = json.dumps({'message': message, 'options': options}).encode('utf-8')
    req = urllib.request.Request(f'http://127.0.0.1:{EXT_PORT}/prompt', data=data, headers={'Content-Type':'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=2) as resp:
        payload = json.loads(resp.read().decode('utf-8'))
    prompt_id = payload['id']
    with urllib.request.urlopen(f'http://127.0.0.1:{EXT_PORT}/wait?id={prompt_id}', timeout=timeout) as resp:
        ans_payload = json.loads(resp.read().decode('utf-8'))
        return ans_payload['answer']
