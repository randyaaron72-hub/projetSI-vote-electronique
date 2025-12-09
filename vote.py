from hash import HashFunctions
from signature import RSASignature
import base64

class Voter:
    """Classe représentant un électeur"""
    
    def __init__(self, voter_id, hash_algorithm='sha256'):
        self.voter_id = voter_id
        self.hash_algorithm = hash_algorithm
        self.hashed_id = None
        self.private_key_pem = None  # Clé privée de l'électeur (à conserver secrète)
        self.public_key_pem = None   # Clé publique (à partager avec l'autorité)
    
    def hash_id(self):
        """
        Hache l'ID de l'électeur
        Retourne: hash de l'ID
        """
        self.hashed_id = HashFunctions.hash_voter_id(self.voter_id, self.hash_algorithm)
        return self.hashed_id
    
    def generate_keys(self):
        """
        Génère la paire de clés cryptographiques pour l'électeur
        IMPORTANT: La clé privée doit être conservée par l'électeur
        """
        rsa = RSASignature()
        private_key, public_key = rsa.generate_keys()
        
        # Exporter les clés en format PEM
        self.private_key_pem = rsa.export_private_key_pem(private_key)
        self.public_key_pem = rsa.export_public_key_pem(public_key)
        
        return self.private_key_pem, self.public_key_pem
    
    def get_registration_data(self):
        """
        Retourne les données nécessaires pour l'enregistrement
        Retourne: (hashed_id, public_key_pem)
        """
        if not self.hashed_id:
            self.hash_id()
        
        if not self.public_key_pem:
            raise ValueError("Clés non générées. Appelez generate_keys() d'abord.")
        
        return self.hashed_id, self.public_key_pem
    
    def create_vote_message(self, candidate):
        """
        Crée le message de vote
        Entrée: candidate (str)
        Retourne: message du vote
        """
        return f"Je vote {candidate}"
    
    def sign_vote(self, vote_message, private_key_pem=None):
        """
        Signe un vote avec la clé privée de l'électeur
        Entrée: 
            - vote_message (str): Message du vote
            - private_key_pem (str): Clé privée (optionnel si déjà dans l'objet)
        Retourne: dict avec toutes les informations du vote signé
        """
        if private_key_pem is None:
            private_key_pem = self.private_key_pem
        
        if not private_key_pem:
            raise ValueError("Clé privée non disponible.")
        
        # Étape 1: Hacher le message du vote
        vote_hash = HashFunctions.hash_vote(vote_message, self.hash_algorithm)
        
        # Étape 2: Signer le hash avec la clé privée
        rsa = RSASignature()
        signature = rsa.sign_with_private_key(vote_hash, private_key_pem)
        signature_b64 = base64.b64encode(signature).decode('utf-8')
        
        return {
            'vote_message': vote_message,
            'vote_hash': vote_hash,
            'signature': signature,
            'signature_b64': signature_b64,
            'hashed_id': self.hashed_id
        }
    
    def save_private_key(self, filename):
        """
        Sauvegarde la clé privée dans un fichier
        ATTENTION: Ce fichier doit être gardé SECRET
        """
        if not self.private_key_pem:
            raise ValueError("Clé privée non générée.")
        
        with open(filename, 'w') as f:
            f.write(self.private_key_pem)
        
        print(f"✓ Clé privée sauvegardée dans: {filename}")
        print("⚠️  ATTENTION: Gardez ce fichier SECRET et en sécurité!")
    
    def load_private_key(self, filename):
        """
        Charge une clé privée depuis un fichier
        """
        with open(filename, 'r') as f:
            self.private_key_pem = f.read()
        
        print(f"✓ Clé privée chargée depuis: {filename}")
    
    def display_keys(self):
        """
        Affiche les informations sur les clés (pour démo uniquement)
        """
        print("\n" + "="*60)
        print("INFORMATIONS CRYPTOGRAPHIQUES DE L'ÉLECTEUR")
        print("="*60)
        print(f"ID Haché ({self.hash_algorithm.upper()}): {self.hashed_id[:64]}...")
        print(f"\nClé Publique (à partager):")
        print(self.public_key_pem[:100] + "...")
        print(f"\n⚠️  Clé Privée (SECRÈTE - ne pas partager):")
        print(self.private_key_pem[:100] + "...")
        print("="*60)