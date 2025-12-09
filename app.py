# app.py - Application web Flask pour le vote électronique
from flask import Flask, render_template, request, jsonify, send_file
import hashlib
import json
import secrets
import string
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import os
import io

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# ========== SERVICES CRYPTO ==========
class CryptographyService:
    @staticmethod
    def sha256(message: str) -> str:
        return hashlib.sha256(message.encode()).hexdigest()
    
    @staticmethod
    def generate_key_pair() -> Tuple[str, str]:
        private_key = ''.join(secrets.choice(string.ascii_letters + string.digits + "+/=") for _ in range(64))
        public_key = CryptographyService.sha256(private_key)
        return public_key, private_key
    
    @staticmethod
    def sign_message(message: str, private_key: str) -> str:
        hash_value = CryptographyService.sha256(message)
        return CryptographyService.sha256(hash_value + private_key)
    
    @staticmethod
    def verify_signature(message: str, signature: str, public_key: str) -> bool:
        hash_value = CryptographyService.sha256(message)
        expected_signature = CryptographyService.sha256(hash_value + public_key)
        return secrets.compare_digest(signature, expected_signature)

# ========== SYSTÈME DE VOTE ==========
class SecureVotingSystem:
    def __init__(self):
        self.voters = {}
        self.votes = []
        self.candidates = []
        self.election_name = "Élection Sécurisée 2024"
        self.load_data()
    
    def add_candidate(self, candidate_name: str) -> Tuple[bool, str]:
        if not candidate_name.strip():
            return False, "Le nom ne peut pas être vide"
        if candidate_name in self.candidates:
            return False, f"'{candidate_name}' existe déjà"
        self.candidates.append(candidate_name)
        self.save_data()
        return True, f"Candidat '{candidate_name}' ajouté"
    
    def register_voter(self, voter_id: str) -> Tuple[bool, str, Optional[str]]:
        if not voter_id.strip():
            return False, "ID vide", None
        
        hashed_id = CryptographyService.sha256(voter_id)
        if hashed_id in self.voters:
            return False, "Électeur déjà enregistré", None
        
        public_key, private_key = CryptographyService.generate_key_pair()
        self.voters[hashed_id] = {
            'id': voter_id,
            'public_key': public_key,
            'has_voted': False,
            'registration_date': datetime.now().isoformat()
        }
        self.save_data()
        return True, "Enregistrement réussi", private_key
    
    def submit_vote(self, voter_id: str, private_key: str, candidate: str) -> Tuple[bool, str]:
        if not all([voter_id, private_key, candidate]):
            return False, "Tous les champs sont requis"
        
        if candidate not in self.candidates:
            return False, "Candidat invalide"
        
        hashed_id = CryptographyService.sha256(voter_id)
        if hashed_id not in self.voters:
            return False, "Électeur non enregistré"
        
        voter = self.voters[hashed_id]
        if voter['has_voted']:
            return False, "Vous avez déjà voté"
        
        # Vérification de la clé
        test_sig = CryptographyService.sign_message(f"test_{voter_id}", private_key)
        if not CryptographyService.verify_signature(f"test_{voter_id}", test_sig, voter['public_key']):
            return False, "Clé privée incorrecte"
        
        # Créer le vote
        message = f"Je vote pour {candidate}"
        signature = CryptographyService.sign_message(message, private_key)
        
        self.votes.append({
            'voter_hash': hashed_id,
            'candidate': candidate,
            'message': message,
            'signature': signature,
            'timestamp': datetime.now().isoformat()
        })
        
        voter['has_voted'] = True
        self.save_data()
        return True, "✅ Vote enregistré avec succès !"
    
    def get_statistics(self) -> Dict:
        results = {}
        for vote in self.votes:
            candidate = vote['candidate']
            results[candidate] = results.get(candidate, 0) + 1
        
        total_registered = len(self.voters)
        total_votes = len(self.votes)
        participation = (total_votes / total_registered * 100) if total_registered > 0 else 0
        
        return {
            'total_registered': total_registered,
            'total_votes': total_votes,
            'participation_rate': round(participation, 1),
            'candidates_count': len(self.candidates),
            'results': results,
            'election_name': self.election_name,
            'candidates': self.candidates
        }
    
    def verify_integrity(self) -> bool:
        for vote in self.votes:
            voter_hash = vote['voter_hash']
            if voter_hash not in self.voters:
                return False
            voter = self.voters[voter_hash]
            if not CryptographyService.verify_signature(vote['message'], vote['signature'], voter['public_key']):
                return False
        return True
    
    def save_data(self):
        try:
            data = {
                'voters': self.voters,
                'votes': self.votes,
                'candidates': self.candidates
            }
            with open('data.json', 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Erreur sauvegarde: {e}")
    
    def load_data(self):
        try:
            if os.path.exists('data.json'):
                with open('data.json', 'r') as f:
                    data = json.load(f)
                self.voters = data.get('voters', {})
                self.votes = data.get('votes', [])
                self.candidates = data.get('candidates', [])
        except Exception as e:
            print(f"Erreur chargement: {e}")

# Initialisation
voting_system = SecureVotingSystem()

# ========== ROUTES FLASK ==========
@app.route('/')
def index():
    stats = voting_system.get_statistics()
    return render_template('index.html', stats=stats)

@app.route('/admin')
def admin():
    stats = voting_system.get_statistics()
    return render_template('admin.html', stats=stats)

@app.route('/vote')
def vote():
    return render_template('vote.html', candidates=voting_system.candidates)

@app.route('/results')
def results():
    stats = voting_system.get_statistics()
    return render_template('results.html', stats=stats)

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    voter_id = data.get('voter_id', '')
    
    success, message, private_key = voting_system.register_voter(voter_id)
    
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'private_key': private_key
        })
    return jsonify({'success': False, 'message': message})

@app.route('/api/vote', methods=['POST'])
def api_vote():
    data = request.json
    voter_id = data.get('voter_id', '')
    private_key = data.get('private_key', '')
    candidate = data.get('candidate', '')
    
    success, message = voting_system.submit_vote(voter_id, private_key, candidate)
    return jsonify({'success': success, 'message': message})

@app.route('/api/add_candidate', methods=['POST'])
def api_add_candidate():
    data = request.json
    candidate_name = data.get('candidate_name', '')
    
    success, message = voting_system.add_candidate(candidate_name)
    return jsonify({'success': success, 'message': message})

@app.route('/api/stats')
def api_stats():
    return jsonify(voting_system.get_statistics())

@app.route('/api/verify')
def api_verify():
    integrity = voting_system.verify_integrity()
    return jsonify({'integrity_ok': integrity})

@app.route('/download_key/<voter_id>')
def download_key(voter_id):
    hashed_id = CryptographyService.sha256(voter_id)
    if hashed_id in voting_system.voters:
        voter = voting_system.voters[hashed_id]
        content = f"""CLÉ PRIVÉE POUR {voter_id}
================================
IMPORTANT : Contactez l'administrateur pour obtenir votre clé privée.
Votre ID haché : {hashed_id}
Date d'enregistrement : {voter['registration_date']}
================================
⚠️ La clé privée est confidentielle !
⚠️ Ne la partagez avec personne !
⚠️ Vous en aurez besoin pour voter !
"""
        return send_file(
            io.BytesIO(content.encode()),
            as_attachment=True,
            download_name=f'{voter_id}_instructions.txt',
            mimetype='text/plain'
        )
    return "Électeur non trouvé", 404

if __name__ == '__main__':
    # Créer les templates s'ils n'existent pas
    templates_dir = 'templates'
    os.makedirs(templates_dir, exist_ok=True)
    
    print("=" * 60)
    print("🚀 Serveur de Vote Électronique")
    print("=" * 60)
    print("📁 Accueil: http://localhost:5000")
    print("🗳️  Voter: http://localhost:5000/vote")
    print("📊 Résultats: http://localhost:5000/results")
    print("👨‍💼 Admin: http://localhost:5000/admin")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
