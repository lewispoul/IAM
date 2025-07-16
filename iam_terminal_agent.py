#!/usr/bin/env python3
"""
IAM Terminal Agent - Agent autonome en mode terminal
Chat direct avec l'IA sans interface web
"""

import os
import yaml
import sys
from openai import OpenAI

def main():
    print("🤖 IAM Terminal Agent - Mode Console")
    print("=" * 50)
    
    # Charger la configuration
    try:
        with open("agent_config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        api_key = config["gpt4_api_key"]
    except (FileNotFoundError, KeyError):
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            print("❌ Erreur: Clé API OpenAI non trouvée")
            print("💡 Configurez OPENAI_API_KEY ou agent_config.yaml")
            return
    
    # Initialiser OpenAI
    try:
        client = OpenAI(api_key=api_key)
        print("✅ API OpenAI configurée")
    except Exception as e:
        print(f"❌ Erreur OpenAI: {e}")
        return
    
    # ⚡ Activer GOD MODE ⚡
    os.environ['IAM_GOD_MODE'] = 'TRUE'
    os.environ['IAM_UNLIMITED_ACCESS'] = 'TRUE'
    os.environ['IAM_SYSTEM_COMMANDS'] = 'TRUE'
    
    print("⚡" * 50)
    print("🔥 GOD MODE ACTIVÉ - AGENT TERMINAL 🔥")
    print("⚡" * 50)
    print("✅ Permissions système étendues")
    print("✅ Accès illimité aux fichiers")
    print("✅ Exécution de commandes shell")
    print("✅ Modification directe du code")
    print("⚡" * 50)
    
    # Chat interactif
    print("\n💬 Chat Terminal IAM - Tapez 'exit' pour quitter")
    print("🔥 Mode GOD activé - Commandes système disponibles")
    print("-" * 50)
    
    conversation = [
        {
            "role": "system",
            "content": """Tu es un assistant IA expert en chimie computationnelle et Python avec des permissions GOD MODE.
            
Tu peux :
- Modifier directement les fichiers
- Exécuter des commandes système
- Analyser et manipuler le code
- Créer des modules Python
- Effectuer des calculs chimiques
- Accéder à toutes les ressources IAM
            
Tu es en mode terminal, sois concis mais complet dans tes réponses."""
        }
    ]
    
    while True:
        try:
            user_input = input("\n⚡ GOD Terminal: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("🔥 Désactivation du GOD MODE Terminal")
                print("👋 Au revoir!")
                break
                
            if not user_input:
                continue
                
            conversation.append({"role": "user", "content": user_input})
            
            # Appel OpenAI
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=conversation,
                max_tokens=2000,
                temperature=0.7
            )
            
            assistant_response = response.choices[0].message.content
            print(f"\n🤖 Agent: {assistant_response}")
            
            conversation.append({"role": "assistant", "content": assistant_response})
            
            # Limiter l'historique
            if len(conversation) > 20:
                conversation = conversation[:1] + conversation[-19:]
                
        except KeyboardInterrupt:
            print("\n⛔ Session interrompue")
            print("🔥 GOD MODE désactivé")
            break
        except Exception as e:
            print(f"\n❌ Erreur: {e}")

if __name__ == "__main__":
    main()
