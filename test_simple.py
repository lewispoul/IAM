#!/usr/bin/env python3

"""
Test simple et direct du Function Calling
"""

import yaml
from IAM_ChatGPT_Integration import IAMChatGPTAgent

def test_simple():
    """Test simple avec la vraie API"""
    print("🧪 Test simple du Function Calling")
    print("=" * 50)
    
    # Charger la configuration
    with open("agent_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    # Créer l'agent
    agent = IAMChatGPTAgent(
        api_key=config["gpt4_api_key"],
        model=config.get("gpt4_model", "gpt-4o")
    )
    
    # Activer le mode GOD
    agent.enable_god_mode()
    
    print("\n✅ Agent créé et configuré")
    
    # Test simple : demander à l'agent de lire README.md
    print("\n📝 Test: Demande de lecture du fichier README.md")
    print("-" * 50)
    
    try:
        response, conversation = agent.chat(
            "Salut ! Peux-tu lire le fichier README.md et me dire en 2-3 phrases ce qu'il contient ?"
        )
        
        print(f"🤖 Réponse de l'agent:")
        print(response)
        
        # Analyser la réponse
        if "README" in response or "fichier" in response.lower():
            print("\n✅ SUCCESS: L'agent a mentionné le fichier README")
        else:
            print("\n❌ ECHEC: L'agent n'a pas lu le fichier")
        
        if len(response) > 100:
            print("✅ SUCCESS: Réponse détaillée (probablement basée sur le contenu du fichier)")
        else:
            print("❌ ECHEC: Réponse trop courte")
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")

if __name__ == "__main__":
    test_simple()
