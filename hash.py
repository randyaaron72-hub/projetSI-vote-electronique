import hashlib

class HashFunctions:
    """Fonctions de hachage cryptographique"""
    
    @staticmethod
    def sha256(data):
        """
        Hachage SHA-256
        Entrée: data (str ou bytes)
        Sortie: hash en hexadécimal (str)
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).hexdigest()
    
    
    
    @staticmethod
    def hash_voter_id(voter_id, algorithm='sha256'):
        """
        Hache l'ID d'un votant
        Entrée: voter_id (str), algorithm (str)
        Sortie: hash de l'ID
        """
        if algorithm == 'sha256':
            return HashFunctions.sha256(voter_id)
        else:
            raise ValueError("Algorithme non supporté. Utilisez 'sha256'")
    
    @staticmethod
    def hash_vote(vote_message, algorithm='sha256'):
        """
        Hache le message de vote (ex: "Je vote Candidat A")
        Entrée: vote_message (str), algorithm (str)
        Sortie: hash du vote
        """
        if algorithm == 'sha256':
            return HashFunctions.sha256(vote_message)
        else:
            raise ValueError("Algorithme non supporté. Utilisez 'sha256'")