# ========== 1. DIAGNOSTIC ET EXÉCUTION DE VOTRE SCRIPT ==========
print("🚀 [Wrapper] Démarrage du système de vote sur Railway...")
print(f"📁 Répertoire de travail : {os.getcwd()}")
print(f"🐍 Version Python : {sys.version}")

# --- NOUVEAU : Vérification détaillée du fichier ---
print("\n🔍 [Diagnostic] Vérification du fichier 'main.py'...")
if not os.path.exists("main.py"):
    print("❌ ERREUR : Le fichier 'main.py' est INTROUVABLE dans le répertoire courant.")
    print("   Liste des fichiers présents :")
    for file in os.listdir('.'):
        print(f"   - {file}")
    sys.exit(1)
else:
    print("✅ Fichier 'main.py' trouvé.")
    # Afficher les 5 premières lignes pour confirmer que c'est le bon fichier
    try:
        with open("main.py", 'r') as f:
            lines = [next(f) for _ in range(5)]
        print("   Extrait (5 premières lignes) :")
        for line in lines:
            print(f"   | {line.rstrip()}")
    except:
        print("   (Impossible de lire le contenu)")

# --- NOUVEAU : Vérification des dépendances ---
print("\n📦 [Diagnostic] Vérification des dépendances...")
if os.path.exists("requirements.txt"):
    print("✅ Fichier 'requirements.txt' trouvé.")
else:
    print("ℹ️  Aucun fichier 'requirements.txt' trouvé. (Ce n'est pas forcément un problème)")

# --- EXÉCUTION avec plus de verbosité et gestion des erreurs ---
print("\n▶️  Exécution de 'main.py' en mode démonstration...")
try:
    # On utilise Popen avec un timeout pour mieux contrôler
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    # Envoyer la commande '1' et récupérer la sortie
    stdout_data, stderr_data = process.communicate(input="1\n", timeout=45)
    return_code = process.returncode
    
    print("✅ 'main.py' a terminé son exécution.")
    print(f"📝 Code de retour : {return_code}")
    
    if stdout_data:
        print("--- Début de la sortie de votre script (STDOUT) ---")
        print(stdout_data)
        print("--- Fin de la sortie ---")
    else:
        print("ℹ️  Aucune sortie standard (stdout) produite par le script.")
    
    if stderr_data:
        print("⚠️  Messages d'erreur (STDERR) :")
        print(stderr_data)
        
except subprocess.TimeoutExpired:
    print("⏱️  'main.py' a dépassé le temps d'exécution (45s). Il est peut-être bloqué en attente d'une entrée.")
    print("   Essayez d'ajouter plus de lignes d'entrée dans le 'input' ci-dessous.")
    process.kill()
    stdout_data, stderr_data = process.communicate()
    
except FileNotFoundError:
    print("❌ ERREUR : Python ou le fichier 'main.py' introuvable.")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Erreur inattendue lors de l'exécution : {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

# Si aucune sortie n'a été capturée, on définit une variable par défaut
if 'stdout_data' not in locals() or not stdout_data:
    stdout_data = "Aucune sortie capturée. Vérifiez les logs Railway pour les erreurs ci-dessus."
    result = type('obj', (object,), {'stdout': stdout_data, 'returncode': 1})
