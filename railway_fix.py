from flask import Flask
import subprocess
import sys

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <html><body style="margin:40px;font-family:sans-serif">
    <h1>🔧 DEBUG Système de Vote</h1>
    <h3><a href="/run1">Test 1: Avec '1'</a></h3>
    <h3><a href="/run2">Test 2: Avec '1\\n2\\n3'</a></h3>
    <h3><a href="/run3">Test 3: Mode FORCÉ</a></h3>
    </body></html>
    '''

@app.route('/run1')
def run1():
    result = subprocess.run([sys.executable, "main.py"], input="1\n", capture_output=True, text=True)
    return f'''
    <pre>
    Code: {result.returncode}
    === STDOUT ===
    {result.stdout or '(VIDE)'}
    === STDERR ===
    {result.stderr or '(VIDE)'}
    </pre>
    <a href="/">← Retour</a>
    '''

@app.route('/run2')
def run2():
    result = subprocess.run([sys.executable, "main.py"], input="1\n2\n3\noui\n", capture_output=True, text=True)
    return f'<pre>{result.stdout or "(VIDE)"}</pre><a href="/">← Retour</a>'

@app.route('/run3')
def run3():
    # Mode FORCÉ : Remplace input() pendant l'exécution
    code = '''
import sys
import io
sys.stdin = io.StringIO("1\\n2\\n3\\ntest\\n")
try:
    import main
    if hasattr(main, 'main'):
        main.main()
except Exception as e:
    print(f"ERREUR: {e}")
'''
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    return f'<pre>{result.stdout or "(VIDE)"}{result.stderr or ""}</pre><a href="/">← Retour</a>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
