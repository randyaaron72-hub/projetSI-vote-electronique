from flask import Flask
import subprocess

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>🛠️ Debug Vote System</h1>
    <p><a href="/raw">🔍 Voir la sortie BRUTE de main.py</a></p>
    <p><a href="/force">⚡ Forcer l'exécution complète</a></p>
    '''
@app.route('/raw')
def raw():
    result = subprocess.run(['python', 'main.py'], 
                          input='1\n', 
                          capture_output=True, 
                          text=True)
    return f'<pre>Code: {result.returncode}\n\nSTDOUT:\n{result.stdout or "(vide)"}\n\nSTDERR:\n{result.stderr or "(vide)"}</pre>'

@app.route('/force')
def force():
    result = subprocess.run(['python', '-c', """
import sys
# Simule TOUS les inputs possibles
fake_inputs = ["1", "2", "oui", "non", "test", "exit"]
input_counter = 0
def fake_input(prompt=""):
    global input_counter
    value = fake_inputs[input_counter % len(fake_inputs)]
    input_counter += 1
    print(f"{prompt}[AUTO:{value}]")
    return value
import builtins
builtins.input = fake_input
# Exécute le main
with open('main.py', 'r') as f:
    exec(f.read())
"""], capture_output=True, text=True)
    return f'<pre>{result.stdout}\n{result.stderr}</pre>'

if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
