from flask import Flask, render_template_string
import subprocess
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head><title>Système de Vote</title>
<style>
body { font-family: sans-serif; margin: 40px; background: #f0f2f5; }
.card { background: white; padding: 30px; border-radius: 15px; max-width: 800px; margin: auto; box-shadow: 0 5px 20px rgba(0,0,0,0.1); }
.btn { background: #0070f3; color: white; padding: 14px 28px; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; margin: 10px; }
.output { background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 20px; white-space: pre-wrap; font-family: monospace; }
</style>
</head>
<body>
<div class="card">
<h1>🗳️ Système de Vote Électronique</h1>
<p>Application déployée sur Railway</p>
<button class="btn" onclick="runVote()">▶️ Lancer le système de vote</button>
<div id="output" class="output">Cliquez pour exécuter</div>
</div>
<script>
async function runVote() {
    document.getElementById('output').textContent = 'Exécution en cours...';
    const response = await fetch('/run');
    const text = await response.text();
    document.getElementById('output').textContent = text;
}
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/run')
def run_vote():
    """Exécute votre main.py et retourne la sortie"""
    try:
        result = subprocess.run(
            ['python', 'main.py'],
            input='1\n',
            capture_output=True,
            text=True,
            timeout=30
        )
        output = f"✅ Sortie du script :\n{result.stdout}"
        if result.stderr:
            output += f"\n⚠️ Erreurs :\n{result.stderr}"
        return output
    except Exception as e:
        return f"❌ Erreur : {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
