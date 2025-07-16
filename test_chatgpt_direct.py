#!/usr/bin/env python3

"""
Test direct du IAMChatGPTAgent pour vérifier le Function Calling
"""

import yaml
from IAM_ChatGPT_Integration import IAMChatGPTAgent

def test_direct():
    """Test direct sans API OpenAI"""
    print("🧪 Test DIRECT du Function Calling (sans API)")
    print("=" * 50)
    
    # Test avec configuration factice
    agent = IAMChatGPTAgent(api_key="fake-key-for-testing")
    agent.enable_god_mode()
    
    print("\n1. Test direct de read_file")
    result = agent.handle_function_call("read_file", {"path": "README.md"})
    
    if result.get("success"):
        content = result.get("content", "")
        print(f"✅ Lecture réussie!")
        print(f"📊 Taille: {len(content)} caractères")
        print(f"📄 Début du contenu:")
        print("-" * 40)
        print(content[:300] + "..." if len(content) > 300 else content)
        print("-" * 40)
    else:
        print(f"❌ Erreur: {result.get('error')}")
    
    print("\n2. Test direct de list_files")
    list_result = agent.handle_function_call("list_files", {"path": ""})
    
    if list_result.get("success"):
        items = list_result.get("items", [])
        print(f"✅ Listage réussi: {len(items)} éléments")
        print("📁 Premiers fichiers:")
        for item in items[:5]:
            print(f"  - {item['name']} ({item['type']})")
    else:
        print(f"❌ Erreur: {list_result.get('error')}")

def test_with_api():
    """Test avec API OpenAI si configurée"""
    print("\n🧪 Test AVEC API OpenAI")
    print("=" * 50)
    
    try:
        with open("agent_config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        api_key = config.get("gpt4_api_key")
        if not api_key or api_key.startswith("your_"):
            print("❌ Clé API non configurée - sautant le test API")
            return
        
        agent = IAMChatGPTAgent(api_key=api_key)
        agent.enable_god_mode()
        
        print("🤖 Test avec vraie API...")
        response, history = agent.chat("Peux-tu lire le fichier README.md et me dire ce qu'il contient?")
        
        print(f"🤖 Réponse de l'agent:")
        print("-" * 40)
        print(response)
        print("-" * 40)
        
    except FileNotFoundError:
        print("❌ Fichier agent_config.yaml non trouvé")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_direct()
    test_with_api()
