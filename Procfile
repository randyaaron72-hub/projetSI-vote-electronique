web: python -c "
import sys, os, subprocess
print('🚀 Démarrage...')
# Exécute main.py en arrière-plan avec input auto
proc = subprocess.Popen(['python', 'main.py'], stdin=subprocess.PIPE, text=True)
proc.communicate(input='1\\n2\\n3\\n')
print('✅ Script exécuté')
# Lance un serveur web simple POUR DE VRAI
from http.server import HTTPServer, BaseHTTPRequestHandler
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
port = int(os.environ.get('PORT', 8080))
print(f'🌐 Serveur sur port {port}')
HTTPServer(('0.0.0.0', port), Handler).serve_forever()
"
