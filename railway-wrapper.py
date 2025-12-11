#!/usr/bin/env python3
"""
Wrapper pour exécuter main.py en mode automatique sur Railway
Sans modifier votre code original !
"""

import os
import sys
import subprocess
import time

print("🔧 Wrapper Railway - Démarrage...")

# 1. Créer un fichier d'entrée automatique
input_commands = "1\n"  # Sélectionne automatiquement le mode 1 (démonstration)
input_commands += "\n"  # Réponses supplémentaires si besoin

# 2. Sauvegarder les commandes dans un fichier
with open("auto_input.txt", "w") as f:
    f.write(input_commands)

# 3. Exécuter votre script original avec redirection d'entrée
try:
    print("🚀 Exécution de votre application en mode automatique...")
    
    # Méthode 1: Redirection stdin depuis le fichier
    with open("auto_input.txt", "r") as input_file:
        result = subprocess.run(
            [sys.executable, "main.py"],
            stdin=input_file,
            capture_output=True,
            text=True,
            timeout=30
        )
    
    # Afficher la sortie
    print("\n" + "="*60)
    print("SORTIE DE VOTRE APPLICATION:")
    print("="*60)
    print(result.stdout)
    
    if result.stderr:
        print("\n⚠️  ERREURS:")
        print(result.stderr)
    
    print(f"\n✅ Code de sortie: {result.returncode}")
    
    # Garder le conteneur en vie pour Railway
    print("\n🔄 Application en mode serveur...")
    print(f"📡 Port: {os.environ.get('PORT', '8080')}")
    print("🌐 En attente de requêtes...")
    
    # Garder le processus en vie
    while True:
        time.sleep(3600)  # Sleep 1 heure
        
except subprocess.TimeoutExpired:
    print("⏱️  Timeout - Lancement du mode serveur...")
except Exception as e:
    print(f"❌ Erreur: {e}")
finally:
    # Nettoyage
    if os.path.exists("auto_input.txt"):
        os.remove("auto_input.txt")
