"""Servidor local de teste: arquivos estáticos e proxy /api para Flask.
Não substitui a validação da implantação Nginx/Docker.
"""
import http.client
import sys
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from werkzeug.serving import make_server
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app import app

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / 'frontend'), **kwargs)
    def do_GET(self):
        if self.path.startswith('/api/'): self.proxy()
        else: super().do_GET()
    def do_POST(self):
        if self.path.startswith('/api/'): self.proxy()
        else: self.send_error(404)
    def proxy(self):
        body = self.rfile.read(int(self.headers.get('Content-Length', 0)))
        conn = http.client.HTTPConnection('127.0.0.1', 5000, timeout=15)
        conn.request(self.command, self.path[4:], body=body, headers={'Content-Type':self.headers.get('Content-Type','')})
        response = conn.getresponse(); data=response.read()
        self.send_response(response.status)
        self.send_header('Content-Type',response.getheader('Content-Type','application/json'))
        self.send_header('Content-Length',str(len(data))); self.end_headers()
        self.wfile.write(data); conn.close()
    def log_message(self,*args): pass

if __name__ == '__main__':
    api = make_server('127.0.0.1', 5000, app, threaded=True)
    threading.Thread(target=api.serve_forever, daemon=True).start()
    print('Teste local em http://127.0.0.1:3000', flush=True)
    try: ThreadingHTTPServer(('127.0.0.1',3000),Handler).serve_forever()
    finally: api.shutdown()
