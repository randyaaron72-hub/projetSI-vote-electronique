from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

# Données de démonstration
candidats = {
    "candidat_A": {"nom": "Alice Martin", "parti": "Parti Progrès"},
    "candidat_B": {"nom": "Bob Dupont", "parti": "Union Démocratique"},
    "candidat_C": {"nom": "Charlie Leroy", "parti": "Écologie Active"}
}

votes = {"candidat_A": 0, "candidat_B": 0, "candidat_C": 0, "blanc": 0}

@app.route('/')
def accueil():
    """Page d'accueil"""
    return render_template('index.html', 
                         candidats=candidats,
                         total_votes=sum(votes.values()))

@app.route('/voter', methods=['POST'])
def voter():
    """Endpoint pour voter"""
    try:
        data = request.json
        candidat = data.get('candidat')
        
        if candidat in votes:
            votes[candidat] += 1
            return jsonify({
                "success": True,
                "message": "Vote enregistré avec succès",
                "transaction_id": f"TX{datetime.now().timestamp()}"
            })
        else:
            votes['blanc'] += 1
            return jsonify({
                "success": True,
                "message": "Vote blanc enregistré"
            })
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/resultats')
def resultats():
    """Afficher les résultats"""
    return jsonify({
        "resultats": votes,
        "total": sum(votes.values()),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/demonstration')
def demonstration():
    """Mode démonstration API"""
    return jsonify({
        "etapes": [
            "1. Initialisation du système sécurisé",
            "2. Authentification biométrique",
            "3. Vote chiffré",
            "4. Enregistrement blockchain",
            "5. Calcul décentralisé"
        ],
        "simulation": {
            "electeurs": 1000,
            "votes_valides": 950,
            "votes_blancs": 50,
            "participations": "95%"
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=DEBUG)
