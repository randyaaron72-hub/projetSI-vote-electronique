from voting_system import VotingSystem
import os

def display_banner():
    """Affiche la bannière du système"""
    print("\n" + "="*60)
    print(" "*10 + "SYSTÈME DE VOTE ÉLECTRONIQUE SÉCURISÉ")
    print(" "*8 + "Avec Signature Numérique et Hachage RSA")
    print("="*60)

def demo_mode():
    """Mode démonstration complète du processus"""
    print("\n🔹 MODE DÉMONSTRATION - Processus complet")
    
    system = VotingSystem(db_file='votes_demo.json', hash_algorithm='sha256')
    
    # Configuration de l'élection
    print("\n" + "▶"*30)
    print("CONFIGURATION DE L'ÉLECTION")
    print("▶"*30)
    candidates = ["Alice Dupont", "Bob Martin", "Charlie Durand"]
    system.setup_election(candidates)
    print("\nCandidats:")
    for i, candidate in enumerate(candidates, 1):
        print(f"  {i}. {candidate}")
    
    # Scénario 1: Enregistrement d'un électeur
    print("\n" + "▶"*30)
    print("SCÉNARIO 1: Enregistrement d'un électeur")
    print("▶"*30)
    success, msg, private_key1, voter1 = system.register_voter("ELECTEUR001")
    
    if success:
        # Sauvegarder la clé privée (simulation)
        voter1.save_private_key("electeur001_private_key.pem")
        voter1.display_keys()
    
    input("\n[Appuyez sur Entrée pour continuer au vote...]")
    
    # Scénario 2: Vote de l'électeur
    print("\n" + "▶"*30)
    print("SCÉNARIO 2: Vote de l'électeur")
    print("▶"*30)
    success, msg = system.submit_vote("ELECTEUR001", "Alice Dupont", private_key1)
    
    input("\n[Appuyez sur Entrée pour voir la tentative de double vote...]")
    
    # Scénario 3: Tentative de double vote
    print("\n" + "▶"*30)
    print("SCÉNARIO 3: Tentative de double vote")
    print("▶"*30)
    success, msg = system.submit_vote("ELECTEUR001", "Bob Martin", private_key1)
    print(msg)
    
    input("\n[Appuyez sur Entrée pour enregistrer d'autres électeurs...]")
    
    # Autres électeurs
    print("\n" + "▶"*30)
    print("SCÉNARIO 4: Autres électeurs")
    print("▶"*30)
    
    # Électeur 2
    success, msg, private_key2, voter2 = system.register_voter("ELECTEUR002")
    if success:
        print(f"\n{msg}")
        system.submit_vote("ELECTEUR002", "Bob Martin", private_key2)
    
    # Électeur 3
    success, msg, private_key3, voter3 = system.register_voter("ELECTEUR003")
    if success:
        print(f"\n{msg}")
        system.submit_vote("ELECTEUR003", "Alice Dupont", private_key3)
    
    # Électeur 4
    success, msg, private_key4, voter4 = system.register_voter("ELECTEUR004")
    if success:
        print(f"\n{msg}")
        system.submit_vote("ELECTEUR004", "Charlie Durand", private_key4)
    
    # Résultats
    input("\n[Appuyez sur Entrée pour voir les résultats...]")
    system.display_results()

def interactive_mode():
    """Mode interactif pour utilisation réelle"""
    print("\n🔹 MODE INTERACTIF")
    
    # Choix de l'algorithme
    hash_algo = 'sha256' 
    
    system = VotingSystem(db_file='votes_interactive.json', hash_algorithm=hash_algo)
    print(f"✓ Système initialisé avec {hash_algo.upper()}")
    
    # Dictionnaire pour stocker les clés privées (simulation)
    private_keys = {}
    
    while True:
        print("\n" + "="*60)
        print("MENU PRINCIPAL")
        print("="*60)
        print("1. Configurer une nouvelle élection (Admin)")
        print("2. S'enregistrer comme électeur")
        print("3. Voter")
        print("4. Afficher les résultats")
        print("5. Réinitialiser l'élection (Admin)")
        print("6. Quitter")
        
        choice = input("\nChoix: ")
        
        if choice == '1':
            print("\n--- Configuration de l'élection ---")
            nb_candidates = int(input("Nombre de candidats: "))
            candidates = []
            for i in range(nb_candidates):
                name = input(f"Nom du candidat {i+1}: ")
                candidates.append(name)
            system.setup_election(candidates)
        
        elif choice == '2':
            print("\n--- Enregistrement d'un électeur ---")
            voter_id = input("Entrez votre ID: ")
            
            success, msg, private_key_pem, voter = system.register_voter(voter_id)
            print(msg)
            
            if success:
                # Sauvegarder la clé privée
                filename = f"{voter_id}_private_key.pem"
                voter.save_private_key(filename)
                
                # Stocker en mémoire pour cet exemple
                private_keys[voter_id] = private_key_pem
                
                print(f"\n✅ Votre clé privée a été sauvegardée dans: {filename}")
                print("⚠️  Conservez ce fichier en lieu sûr!")
                print("    Vous en aurez besoin pour voter.")
        
        elif choice == '3':
            candidates = system.get_candidates()
            if not candidates:
                print("❌ Aucune élection configurée. Contactez l'administrateur.")
                continue
            
            print("\n--- Processus de vote ---")
            voter_id = input("Entrez votre ID: ")
            
            # Vérifier si la clé privée est disponible
            if voter_id in private_keys:
                print("✓ Clé privée trouvée en mémoire")
                private_key_pem = private_keys[voter_id]
            else:
                # Charger depuis le fichier
                filename = f"{voter_id}_private_key.pem"
                if os.path.exists(filename):
                    with open(filename, 'r') as f:
                        private_key_pem = f.read()
                    print(f"✓ Clé privée chargée depuis {filename}")
                else:
                    print(f"❌ Clé privée introuvable. Vous devez d'abord vous enregistrer.")
                    continue
            
            print("\nCandidats disponibles:")
            for i, candidate in enumerate(candidates, 1):
                print(f"  {i}. {candidate}")
            
            choice_candidate = input("\nNuméro du candidat choisi: ")
            try:
                idx = int(choice_candidate) - 1
                if 0 <= idx < len(candidates):
                    candidate = candidates[idx]
                    success, msg = system.submit_vote(voter_id, candidate, private_key_pem)
                    print(f"\n{msg}")
                else:
                    print("❌ Numéro invalide")
            except:
                print("❌ Entrée invalide")
        
        elif choice == '4':
            system.display_results()
        
        elif choice == '5':
            confirm = input("⚠️  Voulez-vous vraiment réinitialiser? (oui/non): ")
            if confirm.lower() == 'oui':
                system.reset_election()
                private_keys.clear()
        
        elif choice == '6':
            print("\n👋 Au revoir!")
            break
        
        else:
            print("❌ Choix invalide")

def main():
    """Fonction principale"""
    display_banner()
    
    print("\n📚 Principe du système:")
    print("   1. Enregistrement: Génération de clés (privée + publique)")
    print("      → Clé publique stockée par l'autorité électorale")
    print("      → Clé privée remise à l'électeur (à conserver secrètement)")
    print("   2. Vote: L'électeur signe son vote avec sa clé privée")
    print("   3. Vérification: Le serveur vérifie avec la clé publique")
    print("      → Authenticité + Intégrité + Non-répudiation")
    
    print("\nModes disponibles:")
    print("1. Mode démonstration (processus complet expliqué)")
    print("2. Mode interactif (utilisation réelle)")
    
    mode = input("\nChoisir le mode: ")
    
    if mode == '1':
        demo_mode()
    elif mode == '2':
        interactive_mode()
    else:
        print("❌ Mode invalide")

if __name__ == "__main__":
    main()