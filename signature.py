from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

class RSASignature:
    """Gestion de la signature numérique RSA"""
    
    def __init__(self, key_size=2048):
        self.private_key = None
        self.public_key = None
        self.key_size = key_size
    
    def generate_keys(self):
        """
        Génère une paire de clés RSA (privée et publique)
        Retourne: (private_key, public_key)
        """
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.key_size,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        return self.private_key, self.public_key
    
    def sign_with_private_key(self, hash_message, private_key_pem):
        """
        Signe un hash avec une clé privée fournie (format PEM)
        Entrée: 
            - hash_message (str): Hash du message à signer
            - private_key_pem (str): Clé privée au format PEM
        Sortie: signature (bytes)
        """
        # Charger la clé privée depuis le PEM
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode('utf-8') if isinstance(private_key_pem, str) else private_key_pem,
            password=None,
            backend=default_backend()
        )
        
        # Convertir le hash en bytes
        if isinstance(hash_message, str):
            hash_message = hash_message.encode('utf-8')
        
        # Signer le hash
        signature = private_key.sign(
            hash_message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature
    
    def verify_with_public_key(self, hash_message, signature, public_key_pem):
        """
        Vérifie une signature avec une clé publique fournie (format PEM)
        Entrée: 
            - hash_message (str): Hash du message original
            - signature (bytes): Signature à vérifier
            - public_key_pem (str): Clé publique au format PEM
        Sortie: True si valide, False sinon
        """
        try:
            # Charger la clé publique depuis le PEM
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode('utf-8') if isinstance(public_key_pem, str) else public_key_pem,
                backend=default_backend()
            )
            
            # Convertir le hash en bytes
            if isinstance(hash_message, str):
                hash_message = hash_message.encode('utf-8')
            
            # Vérifier la signature
            public_key.verify(
                signature,
                hash_message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            print(f"Erreur de vérification: {e}")
            return False
    
    def export_public_key_pem(self, public_key=None):
        """
        Exporte la clé publique en format PEM
        Retourne: str (clé publique au format PEM)
        """
        if public_key is None:
            public_key = self.public_key
        
        if not public_key:
            raise ValueError("Clé publique non disponible.")
        
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')
    
    def export_private_key_pem(self, private_key=None):
        """
        Exporte la clé privée en format PEM
        Retourne: str (clé privée au format PEM)
        """
        if private_key is None:
            private_key = self.private_key
        
        if not private_key:
            raise ValueError("Clé privée non disponible.")
        
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return pem.decode('utf-8')