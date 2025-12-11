#!/bin/bash
# Simule un terminal et garde Railway heureux
echo "1" | python3 main.py
echo "✅ Script exécuté. Serveur en ligne."
# Garde le conteneur en vie avec un mini serveur
python3 -m http.server 8080
