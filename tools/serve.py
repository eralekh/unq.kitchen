#!/usr/bin/env python3
"""UNQ Kitchen — local helper app.

Run from the site folder:
    python3 tools/serve.py

Opens the editor in your browser. Saving writes data/data.json (with a .bak backup)
and rebuilds every output page by running tools/build.py.
Flags: --port N (default 8765), --no-open (don't launch a browser).
"""
import http.server, socketserver, json, os, subprocess, sys, webbrowser, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data', 'data.json')
PORT = int(sys.argv[sys.argv.index('--port') + 1]) if '--port' in sys.argv else 8765
OPEN = '--no-open' not in sys.argv


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.split('?')[0] == '/api/data':
            try:
                with open(DATA, encoding='utf-8') as f:
                    self._json(200, {'ok': True, 'data': json.load(f)})
            except Exception as e:
                self._json(500, {'ok': False, 'error': str(e)})
            return
        if self.path == '/':
            self.path = '/editor/'
        return super().do_GET()

    def do_POST(self):
        if self.path.split('?')[0] != '/api/data':
            self._json(404, {'ok': False, 'error': 'not found'})
            return
        length = int(self.headers.get('Content-Length', 0))
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw)
        except Exception as e:
            self._json(400, {'ok': False, 'error': 'invalid JSON: ' + str(e)})
            return
        try:
            if os.path.exists(DATA):
                shutil.copy(DATA, DATA[:-5] + '.bak.json')
            with open(DATA, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'build.py')],
                               capture_output=True, text=True, timeout=60)
            self._json(200 if r.returncode == 0 else 500,
                       {'ok': r.returncode == 0, 'build': (r.stdout + r.stderr).strip()})
        except Exception as e:
            self._json(500, {'ok': False, 'error': str(e)})

    def log_message(self, *a):
        pass


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


if __name__ == '__main__':
    os.chdir(ROOT)
    with Server(('127.0.0.1', PORT), Handler) as httpd:
        url = f'http://127.0.0.1:{PORT}/editor/'
        print(f'UNQ Kitchen editor running at  {url}')
        print('Press Ctrl+C to stop.')
        if OPEN:
            try:
                webbrowser.open(url)
            except Exception:
                pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nStopped.')
