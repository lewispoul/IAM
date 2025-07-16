#!/usr/bin/env python3
"""
IAM Terminal Agent - Agent GOD MODE pour terminal uniquement
Version simplifiée sans interface web
"""

import os
import sys
import json
import logging
from datetime import datetime
from openai import OpenAI


class IAMTerminalAgent:
    """Agent GOD MODE pour terminal avec permissions étendues"""
    
    def __init__(self):
        # ⚡ Activation automatique du GOD MODE ⚡
        self.enable_god_mode()
        
        # Configuration OpenAI
        self.setup_openai()
        
        # Configuration logging
        self.setup_logging()
        
    def enable_god_mode(self):
        """⚡ Activer le mode GOD avec permissions étendues ⚡"""
        self.god_mode = True
        self.unlimited_access = True
        
        print("⚡" * 60)
        print("🔥🔥🔥 IAM TERMINAL AGENT - GOD MODE ACTIVÉ 🔥🔥🔥")
        print("⚡" * 60)
        print("✅ Permissions système étendues ACTIVÉES")
        print("✅ Accès illimité aux fichiers ACTIVÉ")
        print("✅ Exécution de commandes shell ACTIVÉE")
        print("✅ Modification directe du code ACTIVÉE")
        print("✅ Génération de modules sans restrictions")
        print("✅ Chat IA avec permissions étendues")
        print("⚡" * 60)
        
        # Définir les variables d'environnement
        os.environ['IAM_GOD_MODE'] = 'TRUE'
        os.environ['IAM_UNLIMITED_ACCESS'] = 'TRUE'
        os.environ['IAM_SYSTEM_COMMANDS'] = 'TRUE'
        
    def setup_openai(self):
        """Configuration de l'API OpenAI"""
        api_key = os.environ.get('OPENAI_API_KEY')
        
        if not api_key or api_key.startswith('your_api'):
            print("⚠️  ATTENTION: OPENAI_API_KEY non définie ou invalide.")
            print("📋 Mode DÉMO activé.")
            self.client = None
            self.demo_mode = True
        else:
            try:
                self.client = OpenAI()
                # Test rapide de la connexion
                self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=1
                )
                self.demo_mode = False
                print("✅ OpenAI API configurée - Mode IA complet")
            except Exception as e:
                print(f"❌ Erreur OpenAI: {e}")
                print("📋 Mode DÉMO activé")
                self.client = None
                self.demo_mode = True
                
    def setup_logging(self):
        """Configuration du logging"""
        os.makedirs("IAM_Logs", exist_ok=True)
        log_file = "IAM_Logs/terminal_agent.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def execute_command(self, command):
        """⚡ Exécuter une commande système (GOD MODE) ⚡"""
        if not self.god_mode:
            return "❌ GOD MODE requis pour les commandes système"
            
        try:
            import subprocess
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = f"Return code: {result.returncode}\n"
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
                
            self.logger.info(f"Command executed: {command}")
            return output
            
        except Exception as e:
            error_msg = f"❌ Erreur lors de l'exécution: {e}"
            self.logger.error(error_msg)
            return error_msg
            
    def modify_file(self, filepath, content):
        """⚡ Modifier un fichier (GOD MODE) ⚡"""
        if not self.god_mode:
            return "❌ GOD MODE requis pour modifier les fichiers"
            
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            msg = f"✅ Fichier modifié: {filepath}"
            self.logger.info(msg)
            return msg
            
        except Exception as e:
            error_msg = f"❌ Erreur lors de la modification: {e}"
            self.logger.error(error_msg)
            return error_msg
            
    def read_file(self, filepath):
        """Lire un fichier"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            return f"📁 Contenu de {filepath}:\n{content}"
        except Exception as e:
            return f"❌ Erreur lecture: {e}"
            
    def chat_with_ai(self, message, conversation_history):
        """Chat avec l'IA"""
        if self.demo_mode:
            return "🤖 [MODE DÉMO] Bonjour ! L'API OpenAI n'est pas configurée. Je peux quand même vous aider avec des commandes système et la manipulation de fichiers en mode GOD.", conversation_history
            
        try:
            # Construire le contexte
            messages = [
                {
                    "role": "system",
                    "content": """Tu es IAM, un assistant IA en mode GOD avec permissions étendues.
Tu peux:
- Exécuter des commandes système
- Modifier des fichiers
- Analyser du code
- Générer des scripts Python
- Accéder à tout le système de fichiers

Réponds de manière concise et technique. Si l'utilisateur demande d'exécuter une commande ou modifier un fichier, explique ce que tu vas faire."""
                }
            ]
            
            # Ajouter l'historique
            messages.extend(conversation_history[-10:])  # Garder les 10 derniers messages
            
            # Ajouter le message actuel
            messages.append({"role": "user", "content": message})
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Mettre à jour l'historique
            conversation_history.append({"role": "user", "content": message})
            conversation_history.append({"role": "assistant", "content": ai_response})
            
            return ai_response, conversation_history
            
        except Exception as e:
            return f"❌ Erreur IA: {e}", conversation_history
            
    def process_command(self, user_input, conversation_history):
        """Traiter une commande utilisateur"""
        user_input = user_input.strip()
        
        # Commandes spéciales GOD MODE
        if user_input.startswith("/exec "):
            command = user_input[6:]
            return self.execute_command(command), conversation_history
            
        elif user_input.startswith("/read "):
            filepath = user_input[6:]
            return self.read_file(filepath), conversation_history
            
        elif user_input.startswith("/write "):
            parts = user_input[7:].split(" ", 1)
            if len(parts) == 2:
                filepath, content = parts
                return self.modify_file(filepath, content), conversation_history
            else:
                return "❌ Usage: /write <fichier> <contenu>", conversation_history
                
        elif user_input.startswith("/help"):
            help_text = """
⚡ COMMANDES GOD MODE DISPONIBLES ⚡

/exec <commande>     - Exécuter une commande système
/read <fichier>      - Lire un fichier
/write <fichier> <contenu> - Écrire dans un fichier
/help               - Afficher cette aide
/status             - Statut de l'agent
/exit               - Quitter

Toute autre commande sera envoyée à l'IA.
"""
            return help_text, conversation_history
            
        elif user_input.startswith("/status"):
            status = f"""
⚡ STATUT IAM TERMINAL AGENT ⚡

GOD MODE: {'✅ ACTIVÉ' if self.god_mode else '❌ DÉSACTIVÉ'}
API OpenAI: {'✅ CONNECTÉE' if not self.demo_mode else '❌ MODE DÉMO'}
Permissions étendues: {'✅ ACTIVÉES' if self.unlimited_access else '❌ DÉSACTIVÉES'}
"""
            return status, conversation_history
            
        else:
            # Chat normal avec l'IA
            return self.chat_with_ai(user_input, conversation_history)
            
    def run(self):
        """Lancer l'agent en mode interactif"""
        print("\n🚀 IAM TERMINAL AGENT - GOD MODE PRÊT")
        print("⚡ Tapez /help pour voir les commandes disponibles")
        print("⚡ Tapez /exit pour quitter\n")
        
        conversation_history = []
        
        while True:
            try:
                user_input = input("⚡ GOD MODE: ").strip()
                
                if user_input.lower() in ["exit", "quit", "/exit"]:
                    print("🔥 Désactivation du GOD MODE")
                    print("👋 Au revoir!")
                    break
                    
                if not user_input:
                    continue
                    
                response, conversation_history = self.process_command(user_input, conversation_history)
                print(f"🤖 IAM: {response}\n")
                
            except KeyboardInterrupt:
                print("\n⛔ Session interrompue")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}\n")


if __name__ == "__main__":
    agent = IAMTerminalAgent()
    agent.run()
