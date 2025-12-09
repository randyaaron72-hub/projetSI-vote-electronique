from database import VotingDatabase
from vote import Voter
from hash import HashFunctions
from signature import RSASignature
import base64

class VotingSystem:
    """Système de vote électronique sécurisé avec signature numérique"""
    
    def __init__(self, db_file='votes.json', hash_algorithm='sha256'):
        self.db = VotingDatabase(db_file)
        self.hash_algorithm = hash_algorithm
    
    def setup_election(self, candidates):
        """
        Configure une élection avec la liste des candidats
        """
        self.db.initialize_candidates(candidates)
        print(f"✓ Élection configurée avec {len(candidates)} candidats")
    
    def register_voter(self, voter_id):
        """
        PHASE 1: ENREGISTREMENT D'UN ÉLECTEUR
        - Génère une paire de clés (privée + publique)
        - Stocke la clé publique dans la base de données
        - Remet la clé privée à l'électeur (à conserver secrètement)
        
        Retourne: (success, message, private_key_pem, voter_object)
        """
        print("\n" + "="*60)
        print("PHASE 1: ENREGISTREMENT DE L'ÉLECTEUR")
        print("="*60)
        
        # Créer l'objet électeur
        voter = Voter(voter_id, self.hash_algorithm)
        
        # Hacher l'ID
        hashed_id = voter.hash_id()
        print(f"✓ ID haché: {hashed_id[:32]}...")
        
        # Vérifier si déjà enregistré
        if self.db.is_voter_registered(hashed_id):
            return False, "❌ Cet électeur est déjà enregistré!", None, None
        
        # Générer la paire de clés
        print("\n🔐 Génération de la paire de clés RSA...")
        private_key_pem, public_key_pem = voter.generate_keys()
        print("✓ Paire de clés générée")
        
        # Stocker la clé publique dans la base de données
        self.db.register_voter(hashed_id, public_key_pem)
        print("✓ Clé publique stockée dans la base de données")
        
        print("\n📋 IMPORTANT:")
        print("   - Votre clé PUBLIQUE a été enregistrée par l'autorité électorale")
        print("   - Votre clé PRIVÉE vous est remise (à conserver secrètement)")
        print("   - Vous aurez besoin de votre clé privée pour voter le jour J")
        
        return True, "✓ Enregistrement réussi", private_key_pem, voter
    
    def submit_vote(self, voter_id, candidate, private_key_pem):
        """
        PHASE 2: SOUMISSION D'UN VOTE (JOUR DU VOTE)
        - L'électeur crée son message de vote
        - Hache le message (empreinte numérique)
        - Signe l'empreinte avec sa clé privée
        - Envoie: vote en clair + signature + identifiant
        
        Retourne: (success, message)
        """
        print("\n" + "="*60)
        print("PHASE 2: SOUMISSION DU VOTE")
        print("="*60)
        
        # Vérifier que le candidat existe
        if candidate not in self.db.get_candidates():
            return False, "❌ Candidat invalide"
        
        # Créer l'objet électeur
        voter = Voter(voter_id, self.hash_algorithm)
        hashed_id = voter.hash_id()
        
        # Vérifier que l'électeur est enregistré
        if not self.db.is_voter_registered(hashed_id):
            return False, "❌ Électeur non enregistré"
        
        # Vérifier s'il a déjà voté
        if self.db.has_voted(hashed_id):
            return False, "❌ REJETÉ: Vous avez déjà voté!"
        
        print(f"✓ Électeur vérifié (ID haché: {hashed_id[:32]}...)")
        
        # Créer le message de vote
        vote_message = voter.create_vote_message(candidate)
        print(f"\n📝 Message de vote: \"{vote_message}\"")
        
        # Hacher le message
        vote_hash = HashFunctions.hash_vote(vote_message, self.hash_algorithm)
        print(f"✓ Empreinte numérique (hash): {vote_hash[:32]}...")
        
        # Signer avec la clé privée de l'électeur
        print("\n🔏 Signature du vote avec votre clé privée...")
        voter.private_key_pem = private_key_pem
        voter.hashed_id = hashed_id
        
        try:
            signed_vote = voter.sign_vote(vote_message)
            print("✓ Vote signé")
        except Exception as e:
            return False, f"❌ Erreur lors de la signature: {e}"
        
        # Vérification de la signature par le serveur
        print("\n" + "="*60)
        print("PHASE 3: VÉRIFICATION PAR LE SERVEUR")
        print("="*60)
        
        return self._verify_and_record_vote(
            hashed_id, 
            vote_message, 
            vote_hash, 
            signed_vote['signature'], 
            signed_vote['signature_b64'],
            candidate
        )
    
    def _verify_and_record_vote(self, hashed_id, vote_message, vote_hash, signature, signature_b64, candidate):
        """
        PHASE 3: VÉRIFICATION ET ENREGISTREMENT (CÔTÉ SERVEUR)
        - Recalcule le hash du message reçu
        - Récupère la clé publique de l'électeur
        - Déchiffre la signature avec la clé publique
        - Compare les deux hash
        - Si identiques: vote valide
        """
        # Récupérer la clé publique depuis la base de données
        public_key_pem = self.db.get_public_key(hashed_id)
        if not public_key_pem:
            return False, "❌ Clé publique introuvable"
        
        print("✓ Clé publique de l'électeur récupérée")
        
        # Recalculer le hash localement
        print("\n🔍 Vérification de l'intégrité...")
        local_hash = HashFunctions.hash_vote(vote_message, self.hash_algorithm)
        print(f"   Hash reçu    : {vote_hash[:32]}...")
        print(f"   Hash calculé : {local_hash[:32]}...")
        
        if local_hash != vote_hash:
            return False, "❌ INTÉGRITÉ COMPROMISE: Le message a été modifié!"
        
        print("✓ Intégrité vérifiée (hashs identiques)")
        
        # Vérifier la signature avec la clé publique
        print("\n🔓 Vérification de la signature...")
        rsa = RSASignature()
        is_valid = rsa.verify_with_public_key(vote_hash, signature, public_key_pem)
        
        if not is_valid:
            return False, "❌ SIGNATURE INVALIDE: Vote rejeté!"
        
        print("✓ Signature valide")
        print("\n✅ AUTHENTIFICATION RÉUSSIE:")
        print("   • Authenticité: Le vote provient bien de cet électeur")
        print("   • Intégrité: Le bulletin n'a pas été modifié")
        print("   • Non-répudiation: L'électeur ne peut nier avoir voté")
        
        # Enregistrer le vote
        self.db.mark_as_voted(hashed_id)
        self.db.add_vote(hashed_id, vote_message, vote_hash, signature_b64, candidate)
        
        print("\n✓ Vote enregistré avec succès!")
        
        return True, "✓ Vote accepté et enregistré"
    
    def display_results(self):
        """Affiche les résultats de l'élection"""
        stats = self.db.get_statistics()
        
        print("\n" + "="*60)
        print("RÉSULTATS DE L'ÉLECTION")
        print("="*60)
        print(f"Électeurs enregistrés: {stats['total_registered']}")
        print(f"Électeurs ayant voté: {stats['total_voted']}")
        print(f"Taux de participation: {stats['participation_rate']:.1f}%")
        print(f"Total votes enregistrés: {stats['total_votes']}")
        print("\nRésultats par candidat:")
        print("-" * 40)
        
        results = stats['results']
        if results:
            sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
            for candidate, votes in sorted_results:
                percentage = (votes / stats['total_votes'] * 100) if stats['total_votes'] > 0 else 0
                print(f"{candidate}: {votes} votes ({percentage:.1f}%)")
        else:
            print("Aucun vote enregistré")
        
        print("="*60)
    
    def get_candidates(self):
        """Retourne la liste des candidats"""
        return self.db.get_candidates()
    
    def reset_election(self):
        """Réinitialise l'élection"""
        self.db.reset_database()
        print("✓ Élection réinitialisée")