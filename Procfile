web: python -c "
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

# Mini serveur web
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Vote System Online')
    def log_message(self, *args):
        pass

# Lance ton script EN PARALLÈLE
import subprocess
subprocess.Popen(['python', 'main.py'], stdin=subprocess.PIPE).communicate(input=b'1\\n')

# Démarre le serveur
port = int(os.getenv('PORT', 8080))
HTTPServer(('0.0.0.0', port), Handler).serve_forever()
"
