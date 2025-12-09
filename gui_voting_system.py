# [file name]: gui_voting_system.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import os
from voting_system import VotingSystem

class VotingSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Système de Vote Électronique Sécurisé")
        self.root.geometry("1000x700")
        
        # Variables
        self.system = None
        self.hash_algorithm = tk.StringVar(value="sha256")
        self.voter_id = tk.StringVar()
        self.selected_candidate = tk.StringVar()
        self.private_keys = {}
        
        # Configuration des styles
        self.setup_styles()
        
        # Création des onglets
        self.create_tabs()
        
        # Initialisation du système
        self.init_system()
        
    def setup_styles(self):
        """Configure les styles pour l'interface"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Couleurs
        self.bg_color = "#f0f0f0"
        self.primary_color = "#2c3e50"
        self.secondary_color = "#3498db"
        self.success_color = "#27ae60"
        self.warning_color = "#e74c3c"
        
        style.configure("Title.TLabel", 
                       font=("Arial", 16, "bold"),
                       foreground=self.primary_color)
        style.configure("Header.TLabel",
                       font=("Arial", 12, "bold"))
        style.configure("Primary.TButton",
                       background=self.secondary_color,
                       foreground="white",
                       font=("Arial", 10, "bold"))
        style.map("Primary.TButton",
                 background=[('active', '#2980b9')])
        
        self.root.configure(bg=self.bg_color)
    
    def create_tabs(self):
        """Crée les onglets principaux"""
        tab_control = ttk.Notebook(self.root)
        
        # Onglet Élection
        self.tab_election = ttk.Frame(tab_control)
        tab_control.add(self.tab_election, text='🔧 Configuration Élection')
        self.create_election_tab()
        
        # Onglet Électeurs
        self.tab_voters = ttk.Frame(tab_control)
        tab_control.add(self.tab_voters, text='👥 Gestion Électeurs')
        self.create_voters_tab()
        
        # Onglet Vote
        self.tab_vote = ttk.Frame(tab_control)
        tab_control.add(self.tab_vote, text='🗳️ Bureau de Vote')
        self.create_vote_tab()
        
        # Onglet Résultats
        self.tab_results = ttk.Frame(tab_control)
        tab_control.add(self.tab_results, text='📊 Résultats')
        self.create_results_tab()
        
        # Onglet Logs
        self.tab_logs = ttk.Frame(tab_control)
        tab_control.add(self.tab_logs, text='📜 Journal d\'activité')
        self.create_logs_tab()
        
        tab_control.pack(expand=1, fill="both")
    
    def init_system(self):
        """Initialise le système de vote"""
        try:
            self.system = VotingSystem(db_file='votes_gui.json', 
                                      hash_algorithm=self.hash_algorithm.get())
            self.log_message("Système initialisé avec succès", "info")
        except Exception as e:
            self.log_message(f"Erreur d'initialisation: {e}", "error")
    
    def create_election_tab(self):
        """Crée l'onglet de configuration de l'élection"""
        # Frame principale avec padding
        main_frame = ttk.Frame(self.tab_election, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, 
                               text="Configuration de l'Élection",
                               style="Title.TLabel")
        title_label.pack(pady=(0, 20))
        
        # Sélection algorithme
        algo_frame = ttk.LabelFrame(main_frame, text="Paramètres de Sécurité", padding="10")
        algo_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Radiobutton(algo_frame, text="SHA-256 (recommandé)", 
                       variable=self.hash_algorithm, value="sha256",
                       command=self.update_algorithm).pack(anchor=tk.W, pady=5)
        
        
        # Configuration des candidats
        candidates_frame = ttk.LabelFrame(main_frame, text="Liste des Candidats", padding="10")
        candidates_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Zone de texte pour les candidats
        self.candidates_text = scrolledtext.ScrolledText(candidates_frame, 
                                                        height=10,
                                                        font=("Arial", 10))
        self.candidates_text.pack(fill=tk.BOTH, expand=True)
        
        # Boutons d'action
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="🔧 Configurer l'Élection",
                  command=self.setup_election,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="🔄 Réinitialiser",
                  command=self.reset_election).pack(side=tk.LEFT)
        
        # Charger les candidats existants
        self.load_existing_candidates()
    
    def create_voters_tab(self):
        """Crée l'onglet de gestion des électeurs"""
        main_frame = ttk.Frame(self.tab_voters, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, 
                               text="Gestion des Électeurs",
                               style="Title.TLabel")
        title_label.pack(pady=(0, 20))
        
        # Frame d'enregistrement
        register_frame = ttk.LabelFrame(main_frame, text="Enregistrement d'Électeur", padding="15")
        register_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(register_frame, text="ID de l'électeur:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.voter_id_entry = ttk.Entry(register_frame, textvariable=self.voter_id, width=30)
        self.voter_id_entry.grid(row=0, column=1, padx=(10, 0), pady=5)
        
        ttk.Button(register_frame, text="📝 Enregistrer l'électeur",
                  command=self.register_voter,
                  style="Primary.TButton").grid(row=0, column=2, padx=(20, 0), pady=5)
        
        # Frame d'affichage des électeurs
        voters_frame = ttk.LabelFrame(main_frame, text="Électeurs Enregistrés", padding="10")
        voters_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview pour afficher les électeurs
        columns = ('ID Haché', 'A voté', 'Date d\'enregistrement')
        self.voters_tree = ttk.Treeview(voters_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.voters_tree.heading(col, text=col)
            self.voters_tree.column(col, width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(voters_frame, orient=tk.VERTICAL, command=self.voters_tree.yview)
        self.voters_tree.configure(yscrollcommand=scrollbar.set)
        
        self.voters_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bouton de rafraîchissement
        ttk.Button(voters_frame, text="🔄 Rafraîchir",
                  command=self.refresh_voters_list).pack(pady=(10, 0))
    
    def create_vote_tab(self):
        """Crée l'onglet de vote"""
        main_frame = ttk.Frame(self.tab_vote, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, 
                               text="Bureau de Vote Électronique",
                               style="Title.TLabel")
        title_label.pack(pady=(0, 20))
        
        # Frame d'identification
        id_frame = ttk.LabelFrame(main_frame, text="Identification", padding="15")
        id_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(id_frame, text="Votre ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.vote_id_entry = ttk.Entry(id_frame, width=30)
        self.vote_id_entry.grid(row=0, column=1, padx=(10, 0), pady=5)
        
        ttk.Button(id_frame, text="🔍 Vérifier l'éligibilité",
                  command=self.check_eligibility).grid(row=0, column=2, padx=(20, 0), pady=5)
        
        # Frame sélection candidat
        candidate_frame = ttk.LabelFrame(main_frame, text="Choix du Candidat", padding="15")
        candidate_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Frame pour les boutons radio des candidats
        self.candidate_frame_inner = ttk.Frame(candidate_frame)
        self.candidate_frame_inner.pack(fill=tk.BOTH, expand=True)
        
        # Frame clé privée
        key_frame = ttk.LabelFrame(main_frame, text="Clé Privée", padding="15")
        key_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.key_path = tk.StringVar()
        ttk.Label(key_frame, text="Fichier de clé privée:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(key_frame, textvariable=self.key_path, width=40, state='readonly').grid(row=0, column=1, padx=(10, 0), pady=5)
        
        ttk.Button(key_frame, text="📁 Parcourir...",
                  command=self.browse_private_key).grid(row=0, column=2, padx=(10, 0), pady=5)
        
        # Bouton de vote
        self.vote_button = ttk.Button(main_frame, 
                                     text="🗳️ SOUMETTRE LE VOTE",
                                     command=self.submit_vote,
                                     style="Primary.TButton",
                                     state='disabled')
        self.vote_button.pack(pady=10)
        
        # Status du vote
        self.vote_status = ttk.Label(main_frame, text="", font=("Arial", 10))
        self.vote_status.pack()
    
    def create_results_tab(self):
        """Crée l'onglet des résultats"""
        main_frame = ttk.Frame(self.tab_results, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, 
                               text="Résultats de l'Élection",
                               style="Title.TLabel")
        title_label.pack(pady=(0, 20))
        
        # Frame statistiques
        stats_frame = ttk.LabelFrame(main_frame, text="Statistiques", padding="15")
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Labels pour les statistiques
        self.total_voters_label = ttk.Label(stats_frame, text="Électeurs enregistrés: --", font=("Arial", 10))
        self.total_voters_label.pack(anchor=tk.W, pady=2)
        
        self.voted_label = ttk.Label(stats_frame, text="Électeurs ayant voté: --", font=("Arial", 10))
        self.voted_label.pack(anchor=tk.W, pady=2)
        
        self.participation_label = ttk.Label(stats_frame, text="Taux de participation: --%", font=("Arial", 10))
        self.participation_label.pack(anchor=tk.W, pady=2)
        
        # Frame résultats détaillés
        results_frame = ttk.LabelFrame(main_frame, text="Résultats par Candidat", padding="15")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview pour les résultats
        columns = ('Candidat', 'Votes', 'Pourcentage')
        self.results_tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="🔄 Actualiser les résultats",
                  command=self.refresh_results,
                  style="Primary.TButton").pack()
    
    def create_logs_tab(self):
        """Crée l'onglet des logs"""
        main_frame = ttk.Frame(self.tab_logs, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, 
                               text="Journal d'Activité du Système",
                               style="Title.TLabel")
        title_label.pack(pady=(0, 20))
        
        # Zone de texte pour les logs
        self.logs_text = scrolledtext.ScrolledText(main_frame,
                                                  height=20,
                                                  font=("Courier New", 9),
                                                  wrap=tk.WORD)
        self.logs_text.pack(fill=tk.BOTH, expand=True)
        
        # Boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="📋 Copier les logs",
                  command=self.copy_logs).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="🧹 Effacer les logs",
                  command=self.clear_logs).pack(side=tk.LEFT)
    
    def update_algorithm(self):
        """Met à jour l'algorithme de hachage"""
        if self.system:
            self.system.hash_algorithm = self.hash_algorithm.get()
            self.log_message(f"Algorithme changé en {self.hash_algorithm.get().upper()}", "info")
    
    def load_existing_candidates(self):
        """Charge les candidats existants depuis la base de données"""
        if self.system:
            candidates = self.system.get_candidates()
            if candidates:
                self.candidates_text.delete(1.0, tk.END)
                for candidate in candidates:
                    self.candidates_text.insert(tk.END, candidate + "\n")
    
    def setup_election(self):
        """Configure une nouvelle élection"""
        candidates_text = self.candidates_text.get(1.0, tk.END).strip()
        
        if not candidates_text:
            messagebox.showerror("Erreur", "Veuillez saisir au moins un candidat")
            return
        
        candidates = [c.strip() for c in candidates_text.split('\n') if c.strip()]
        
        try:
            self.system.setup_election(candidates)
            self.log_message(f"Élection configurée avec {len(candidates)} candidats", "success")
            messagebox.showinfo("Succès", f"Élection configurée avec {len(candidates)} candidats")
            self.refresh_voters_list()
        except Exception as e:
            self.log_message(f"Erreur de configuration: {e}", "error")
            messagebox.showerror("Erreur", f"Échec de configuration: {e}")
    
    def reset_election(self):
        """Réinitialise l'élection"""
        if messagebox.askyesno("Confirmation", 
                              "Êtes-vous sûr de vouloir réinitialiser toute l'élection?\n"
                              "Toutes les données seront perdues."):
            try:
                self.system.reset_election()
                self.private_keys.clear()
                self.log_message("Élection réinitialisée", "warning")
                messagebox.showinfo("Succès", "Élection réinitialisée")
                self.refresh_voters_list()
                self.refresh_results()
                self.candidates_text.delete(1.0, tk.END)
            except Exception as e:
                self.log_message(f"Erreur de réinitialisation: {e}", "error")
    
    def register_voter(self):
        """Enregistre un nouvel électeur"""
        voter_id = self.voter_id.get().strip()
        
        if not voter_id:
            messagebox.showerror("Erreur", "Veuillez saisir un ID d'électeur")
            return
        
        try:
            success, msg, private_key, voter = self.system.register_voter(voter_id)
            
            if success:
                # Demander où sauvegarder la clé privée
                filename = filedialog.asksaveasfilename(
                    defaultextension=".pem",
                    filetypes=[("Fichiers PEM", "*.pem"), ("Tous les fichiers", "*.*")],
                    initialfile=f"{voter_id}_private_key.pem"
                )
                
                if filename:
                    voter.save_private_key(filename)
                    self.private_keys[voter_id] = private_key
                    
                    self.log_message(f"Électeur {voter_id} enregistré - clé sauvegardée: {filename}", "success")
                    messagebox.showinfo("Succès", 
                                      f"Électeur enregistré avec succès!\n\n"
                                      f"Clé privée sauvegardée dans:\n{filename}\n\n"
                                      f"⚠️ Conservez ce fichier en sécurité!")
                    
                    self.voter_id.set("")
                    self.refresh_voters_list()
            else:
                self.log_message(f"Échec enregistrement: {msg}", "error")
                messagebox.showerror("Erreur", msg)
                
        except Exception as e:
            self.log_message(f"Erreur lors de l'enregistrement: {e}", "error")
            messagebox.showerror("Erreur", f"Erreur: {e}")
    
    def refresh_voters_list(self):
        """Rafraîchit la liste des électeurs"""
        if not self.system:
            return
        
        # Effacer les anciennes entrées
        for item in self.voters_tree.get_children():
            self.voters_tree.delete(item)
        
        # Récupérer les données depuis la base de données
        try:
            with open(self.system.db.db_file, 'r') as f:
                import json
                data = json.load(f)
            
            for hashed_id, info in data.get('registered_voters', {}).items():
                voted = "✓" if info.get('has_voted') else "✗"
                date = info.get('registration_date', 'N/A')
                self.voters_tree.insert('', tk.END, values=(hashed_id[:50] + "...", voted, date))
                
        except Exception as e:
            self.log_message(f"Erreur lors du chargement des électeurs: {e}", "error")
    
    def check_eligibility(self):
        """Vérifie l'éligibilité d'un électeur"""
        voter_id = self.vote_id_entry.get().strip()
        
        if not voter_id:
            messagebox.showerror("Erreur", "Veuillez saisir votre ID")
            return
        
        try:
            # Vérifier l'enregistrement
            voter = self.system.db
            hashed_id = self.hash_voter_id(voter_id)
            
            if not voter.is_voter_registered(hashed_id):
                self.vote_status.config(text="❌ Électeur non enregistré", foreground="red")
                self.vote_button.config(state='disabled')
                return
            
            if voter.has_voted(hashed_id):
                self.vote_status.config(text="❌ Vous avez déjà voté!", foreground="red")
                self.vote_button.config(state='disabled')
                return
            
            # Charger les candidats
            candidates = self.system.get_candidates()
            
            if not candidates:
                self.vote_status.config(text="❌ Aucune élection configurée", foreground="red")
                self.vote_button.config(state='disabled')
                return
            
            # Afficher les candidats
            self.display_candidates(candidates)
            
            self.vote_status.config(text="✓ Éligible pour voter", foreground="green")
            self.vote_button.config(state='normal')
            
        except Exception as e:
            self.log_message(f"Erreur de vérification: {e}", "error")
            self.vote_status.config(text=f"Erreur: {str(e)}", foreground="red")
    
    def display_candidates(self, candidates):
        """Affiche les candidats sous forme de boutons radio"""
        # Effacer les anciens boutons
        for widget in self.candidate_frame_inner.winfo_children():
            widget.destroy()
        
        # Créer de nouveaux boutons radio
        for i, candidate in enumerate(candidates):
            rb = ttk.Radiobutton(self.candidate_frame_inner,
                                text=candidate,
                                variable=self.selected_candidate,
                                value=candidate)
            rb.pack(anchor=tk.W, pady=2)
        
        if candidates:
            self.selected_candidate.set(candidates[0])
    
    def browse_private_key(self):
        """Ouvre un dialogue pour sélectionner le fichier de clé privée"""
        filename = filedialog.askopenfilename(
            title="Sélectionner votre clé privée",
            filetypes=[("Fichiers PEM", "*.pem"), ("Tous les fichiers", "*.*")]
        )
        
        if filename:
            self.key_path.set(filename)
    
    def submit_vote(self):
        """Soumet un vote"""
        voter_id = self.vote_id_entry.get().strip()
        candidate = self.selected_candidate.get()
        key_file = self.key_path.get()
        
        if not all([voter_id, candidate, key_file]):
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return
        
        if not os.path.exists(key_file):
            messagebox.showerror("Erreur", "Fichier de clé privée introuvable")
            return
        
        try:
            # Lire la clé privée
            with open(key_file, 'r') as f:
                private_key_pem = f.read()
            
            # Soumettre le vote
            success, msg = self.system.submit_vote(voter_id, candidate, private_key_pem)
            
            if success:
                self.log_message(f"Vote accepté pour {voter_id}: {candidate}", "success")
                messagebox.showinfo("Succès", "Votre vote a été enregistré avec succès!")
                self.vote_status.config(text="✓ Vote enregistré", foreground="green")
                self.vote_button.config(state='disabled')
                
                # Réinitialiser les champs
                self.vote_id_entry.delete(0, tk.END)
                self.key_path.set("")
                
                # Actualiser les résultats
                self.refresh_results()
                self.refresh_voters_list()
            else:
                self.log_message(f"Vote rejeté pour {voter_id}: {msg}", "error")
                messagebox.showerror("Erreur", msg)
                self.vote_status.config(text=f"❌ {msg}", foreground="red")
                
        except Exception as e:
            self.log_message(f"Erreur lors du vote: {e}", "error")
            messagebox.showerror("Erreur", f"Erreur: {e}")
    
    def refresh_results(self):
        """Rafraîchit les résultats"""
        if not self.system:
            return
        
        try:
            stats = self.system.db.get_statistics()
            
            # Mettre à jour les statistiques
            self.total_voters_label.config(text=f"Électeurs enregistrés: {stats['total_registered']}")
            self.voted_label.config(text=f"Électeurs ayant voté: {stats['total_voted']}")
            self.participation_label.config(text=f"Taux de participation: {stats['participation_rate']:.1f}%")
            
            # Effacer l'ancien treeview
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            # Ajouter les nouveaux résultats
            results = stats['results']
            total_votes = stats['total_votes']
            
            for candidate, votes in sorted(results.items(), key=lambda x: x[1], reverse=True):
                percentage = (votes / total_votes * 100) if total_votes > 0 else 0
                self.results_tree.insert('', tk.END, values=(candidate, votes, f"{percentage:.1f}%"))
            
        except Exception as e:
            self.log_message(f"Erreur lors du rafraîchissement des résultats: {e}", "error")
    
    def log_message(self, message, level="info"):
        """Ajoute un message au journal"""
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Couleurs selon le niveau
        colors = {
            "info": "black",
            "success": "green",
            "error": "red",
            "warning": "orange"
        }
        
        color = colors.get(level, "black")
        prefix = {
            "info": "[INFO]",
            "success": "[SUCCÈS]",
            "error": "[ERREUR]",
            "warning": "[ATTENTION]"
        }.get(level, "[INFO]")
        
        full_message = f"{timestamp} {prefix} {message}\n"
        
        # Insérer dans le widget de texte
        self.logs_text.insert(tk.END, full_message)
        
        # Appliquer la couleur (nécessite tkinter Text tag configuration)
        self.logs_text.tag_config(level, foreground=color)
        start = self.logs_text.index(f"end-{len(full_message)+1}c")
        end = self.logs_text.index("end-1c")
        self.logs_text.tag_add(level, start, end)
        
        # Auto-scroll vers le bas
        self.logs_text.see(tk.END)
        
        # Afficher aussi dans la console
        print(full_message.strip())
    
    def copy_logs(self):
        """Copie les logs dans le presse-papier"""
        logs = self.logs_text.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(logs)
        messagebox.showinfo("Succès", "Logs copiés dans le presse-papier")
    
    def clear_logs(self):
        """Efface les logs"""
        if messagebox.askyesno("Confirmation", "Effacer tous les logs?"):
            self.logs_text.delete(1.0, tk.END)
            self.log_message("Journal effacé", "warning")
    
    def hash_voter_id(self, voter_id):
        """Fonction utilitaire pour hacher un ID"""
        from hash import HashFunctions
        return HashFunctions.hash_voter_id(voter_id, self.hash_algorithm.get())

def main():
    """Fonction principale"""
    root = tk.Tk()
    app = VotingSystemGUI(root)
    
    # Centre la fenêtre
    root.eval('tk::PlaceWindow . center')
    
    # Message de bienvenue
    app.log_message("Système de Vote Électronique démarré", "info")
    app.log_message(f"Algorithme de hachage: {app.hash_algorithm.get().upper()}", "info")
    
    root.mainloop()

if __name__ == "__main__":
    main()