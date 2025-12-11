#!/usr/bin/env python3
"""
Wrapper final pour Railway.
1. Exécute votre script main.py en mode automatique.
2. Lance un mini serveur web pour garder l'application en vie et répondre aux requêtes.
"""

import subprocess
import sys
import os
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# ========== 1. EXÉCUTION DE VOTRE SCRIPT ==========
print("🚀 [Wrapper] Démarrage du système de vote sur Railway...")
print(f"📁 Répertoire de travail : {os.getcwd()}")
print(f"🐍 Version Python : {sys.version}")

try:
    # Exécute main.py avec '1' comme choix automatique
    print("▶️  Exécution de 'main.py' en mode démonstration...")
    result = subprocess.run(
        [sys.executable, "main.py"],
        input="1\n",
        text=True,
        capture_output=True,
        timeout=60  # Timeout au cas où
    )
    
    print("✅ 'main.py' a terminé son exécution.")
    print("--- Début de la sortie de votre script ---")
    print(result.stdout)
    if result.stderr:
        print("⚠️  Messages d'erreur :")
        print(result.stderr)
    print(f"📝 Code de retour : {result.returncode}")
    print("--- Fin de la sortie ---\n")

except subprocess.TimeoutExpired:
    print("⏱️  'main.py' a dépassé le temps d'exécution prévu (peut être normal).")
except FileNotFoundError:
    print("❌ ERREUR CRITIQUE : Fichier 'main.py' introuvable.")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erreur lors de l'exécution de 'main.py' : {e}")

# ========== 2. SERVEUR WEB POUR RAILWAY ==========
print("🌐 [Wrapper] Démarrage du serveur web pour Railway...")

class HealthHandler(BaseHTTPRequestHandler):
    """Gère les requêtes HTTP simples."""
    def do_GET(self):
        if self.path == '/':
            # Page d'accueil simple
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = f"""
            <!DOCTYPE html>
            <html>
            <head><title>Système de Vote - En Ligne</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: sans-serif; margin: 40px; background: #f5f5f5; }}
                .card {{ background: white; padding: 30px; border-radius: 15px; max-width: 800px; margin: auto; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
                h1 {{ color: #2c3e50; }}
                pre {{ background: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; overflow: auto; }}
                .status {{ color: #27ae60; font-weight: bold; }}
            </style>
            </head>
            <body>
                <div class="card">
                    <h1>🗳️ Système de Vote Électronique Sécurisé</h1>
                    <p class="status">✅ Application déployée avec succès sur Railway</p>
                    <p>Votre logique de vote a été exécutée en arrière-plan. Vous pouvez fermer cet onglet.</p>
                    <h3>Sortie du script :</h3>
                    <pre>{result.stdout if 'result' in locals() else 'Aucune sortie capturée.'}</pre>
                    <hr>
                    <p><small>URL du projet : <strong>{os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'Non définie')}</strong></small></p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
        elif self.path == '/health':
            # Endpoint pour les checks de santé Railway (optionnel mais recommandé)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Page non trouvee')

def run_server():
    """Lance le serveur web."""
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f"🌍 Serveur web accessible sur le port {port}")
    print(f"🔗 L'application devrait être publique à l'URL : {os.environ.get('RAILWAY_PUBLIC_DOMAIN', '(en cours de generation)')}")
    server.serve_forever()

# Lancer le serveur dans un thread pour qu'il ne bloque pas
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()
print("✅ [Wrapper] Prêt à recevoir des requêtes web.\n")

# ========== 3. GARDER LE PROCESSUS PRINCIPAL EN VIE ==========
# Cette boucle empêche le script wrapper de se terminer.
try:
    while True:
        time.sleep(3600)  # Dort par période d'1 heure
except KeyboardInterrupt:
    print("\n👋 Arrêt du wrapper.")
