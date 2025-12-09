import json
import os
from datetime import datetime

class VotingDatabase:
    """Gestion de la base de données des votes"""
    
    def __init__(self, db_file='votes.json'):
        self.db_file = db_file
        self.data = {
            'registered_voters': {},  # {hashed_id: {"public_key": "...", "has_voted": False}}
            'votes': [],              # Liste des votes avec signatures
            'candidates': []          # Liste des candidats
        }
        self.load_database()
    
    def load_database(self):
        """Charge la base de données depuis le fichier"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except:
                pass
    
    def save_database(self):
        """Sauvegarde la base de données dans le fichier"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
    
    def register_voter(self, hashed_id, public_key_pem):
        """
        Enregistre un électeur avec sa clé publique
        Entrée: 
            - hashed_id (str): Hash de l'ID de l'électeur
            - public_key_pem (str): Clé publique au format PEM
        Retourne: True si enregistré, False si déjà existant
        """
        if hashed_id in self.data['registered_voters']:
            return False
        
        self.data['registered_voters'][hashed_id] = {
            'public_key': public_key_pem,
            'has_voted': False,
            'registration_date': datetime.now().isoformat()
        }
        self.save_database()
        return True
    
    def is_voter_registered(self, hashed_id):
        """
        Vérifie si un électeur est enregistré
        """
        return hashed_id in self.data['registered_voters']
    
    def has_voted(self, hashed_id):
        """
        Vérifie si un électeur a déjà voté
        """
        if hashed_id not in self.data['registered_voters']:
            return False
        return self.data['registered_voters'][hashed_id]['has_voted']
    
    def mark_as_voted(self, hashed_id):
        """
        Marque un électeur comme ayant voté
        """
        if hashed_id in self.data['registered_voters']:
            self.data['registered_voters'][hashed_id]['has_voted'] = True
            self.save_database()
            return True
        return False
    
    def get_public_key(self, hashed_id):
        """
        Récupère la clé publique d'un électeur
        """
        if hashed_id in self.data['registered_voters']:
            return self.data['registered_voters'][hashed_id]['public_key']
        return None
    
    def add_vote(self, hashed_id, vote_message, vote_hash, signature_b64, candidate):
        """
        Enregistre un vote dans la base de données
        Entrée: 
            - hashed_id (str): Hash de l'ID de l'électeur
            - vote_message (str): Message du vote en clair
            - vote_hash (str): Hash du message
            - signature_b64 (str): Signature en base64
            - candidate (str): Nom du candidat
        """
        vote_record = {
            'voter_hash': hashed_id,
            'vote_message': vote_message,
            'vote_hash': vote_hash,
            'signature': signature_b64,
            'candidate': candidate,
            'timestamp': datetime.now().isoformat()
        }
        self.data['votes'].append(vote_record)
        self.save_database()
    
    def get_vote_count(self):
        """Retourne le nombre total de votes"""
        return len(self.data['votes'])
    
    def get_results(self):
        """
        Calcule et retourne les résultats du vote
        Retourne: dict {candidat: nombre_votes}
        """
        results = {}
        for vote in self.data['votes']:
            candidate = vote['candidate']
            results[candidate] = results.get(candidate, 0) + 1
        return results
    
    def initialize_candidates(self, candidates):
        """
        Initialise la liste des candidats
        """
        self.data['candidates'] = candidates
        self.save_database()
    
    def get_candidates(self):
        """Retourne la liste des candidats"""
        return self.data['candidates']
    
    def reset_database(self):
        """Réinitialise complètement la base de données"""
        self.data = {
            'registered_voters': {},
            'votes': [],
            'candidates': []
        }
        self.save_database()
    
    def get_statistics(self):
        """Retourne les statistiques du vote"""
        total_registered = len(self.data['registered_voters'])
        total_voted = sum(1 for v in self.data['registered_voters'].values() if v['has_voted'])
        
        return {
            'total_registered': total_registered,
            'total_voted': total_voted,
            'total_votes': len(self.data['votes']),
            'participation_rate': (total_voted / total_registered * 100) if total_registered > 0 else 0,
            'results': self.get_results()
        }