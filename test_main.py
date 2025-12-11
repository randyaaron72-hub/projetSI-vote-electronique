#!/usr/bin/env python3
"""Test direct de main.py pour voir ce qui se passe"""

import subprocess
import sys

print("🧪 TEST DIRECT DE main.py")
print("=" * 50)

# Test 1: Exécution normale
print("\n1️⃣ Exécution avec '1\\n' comme input :")
result = subprocess.run(
    [sys.executable, "main.py"],
    input="1\n",
    capture_output=True,
    text=True,
    timeout=10
)
print(f"Code retour: {result.returncode}")
print(f"Sortie (stdout):\n{result.stdout if result.stdout else '(VIDE)'}")
print(f"Erreurs (stderr):\n{result.stderr if result.stderr else '(AUCUNE)'}")

# Test 2: Avec plusieurs inputs au cas où
print("\n" + "=" * 50)
print("2️⃣ Exécution avec '1\\n2\\n3\\n' comme input :")
result2 = subprocess.run(
    [sys.executable, "main.py"],
    input="1\n2\n3\ntest\noui\n",
    capture_output=True,
    text=True,
    timeout=10
)
print(f"Code retour: {result2.returncode}")
print(f"Sortie:\n{result2.stdout if result2.stdout else '(VIDE)'}")

# Test 3: Exécution DIRECTE sans subprocess
print("\n" + "=" * 50)
print("3️⃣ Exécution directe dans Python :")
try:
    import main
    print("✅ Import réussi")
    # Si votre main.py a une fonction main()
    if hasattr(main, 'main'):
        print("🔍 Fonction main() trouvée, tentative d'appel...")
        main.main()
except Exception as e:
    print(f"❌ Erreur: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("🎯 Conclusion : Si tout est VIDE, votre main.py a probablement un input() bloquant")
print("Solution : Ajoutez ce patch au DÉBUT de main.py :")
print("""
import sys
if not sys.stdin.isatty():
    def input(prompt=""):
        print(prompt, "[AUTO:1]")
        return "1"
""")
