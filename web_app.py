from flask import Flask, render_template_string, jsonify
import subprocess
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Système de Vote</title>
    <meta charset="utf-8">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .card { background: white; padding: 30px; border-radius: 15px; max-width: 800px; margin: 40px auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
        h1 { color: #2d3748; margin-top: 0; }
        .btn { background: #4299e1; color: white; padding: 14px 28px; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; margin-top: 20px; font-weight: bold; }
        .btn:hover { background: #3182ce; }
        .output { background: #f7fafc; padding: 20px; border-radius: 8px; margin-top: 20px; white-space: pre-wrap; font-family: 'Monaco', 'Menlo', monospace; font-size: 14px; border-left: 4px solid #4299e1; }
        .loading { color: #718096; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🗳️ Système de Vote Électronique</h1>
        <p>Application déployée sur Railway</p>
        <button class="btn" onclick="runVote()">▶️ Lancer le système de vote</button>
        <div id="output" class="output">La sortie apparaîtra ici...</div>
    </div>
    
    <script>
        async function runVote() {
            const output = document.getElementById('output');
            output.innerHTML = '<div class="loading">⏳ Exécution en cours...</div>';
            
            try {
                const response = await fetch('/run');
                if (!response.ok) {
                    throw new Error(`Erreur HTTP: ${response.status}`);
                }
                const text = await response.text();
                output.textContent = text;
            } catch (error) {
                output.textContent = `❌ Erreur: ${error.message}\\n\\nOuvrez directement: /run`;
            }
        }
        
        // Exécute automatiquement au chargement
        window.onload = runVote;
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
        # Exécute le script avec timeout
        result = subprocess.run(
            ['python', 'main.py'],
            input='1\n',
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=30
        )
        
        # Formate la sortie
        output_lines = []
        output_lines.append("=" * 50)
        output_lines.append("SORTIE DU SYSTÈME DE VOTE")
        output_lines.append("=" * 50)
        output_lines.append(result.stdout if result.stdout else "(Aucune sortie)")
        
        if result.stderr:
            output_lines.append("\n" + "=" * 50)
            output_lines.append("ERREURS")
            output_lines.append("=" * 50)
            output_lines.append(result.stderr)
            
        output_lines.append(f"\nCode de retour: {result.returncode}")
        
        return "\n".join(output_lines)
        
    except subprocess.TimeoutExpired:
        return "⏱️ Délai d'exécution dépassé (30s). Le script est peut-être bloqué."
    except FileNotFoundError:
        return "❌ Fichier 'main.py' introuvable."
    except Exception as e:
        return f"❌ Erreur inattendue: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
