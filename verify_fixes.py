#!/usr/bin/env python3

"""
Vérification rapide des corrections Function Calling
"""

def verify_fixes():
    print("🔍 VERIFICATION DES CORRECTIONS FUNCTION CALLING")
    print("=" * 60)
    
    try:
        # 1. Import
        from IAM_ChatGPT_Integration import IAMChatGPTAgent
        from IAM_FileManager import IAMFileManager
        print("✅ 1. Imports OK")
        
        # 2. Test du chemin de base
        fm = IAMFileManager(base_path="/home/lppou/IAM")
        fm.enable_god_mode()
        result = fm.read_file("README.md")
        if result.get("success"):
            print("✅ 2. Chemin de base corrigé - README.md accessible")
        else:
            print("❌ 2. Problème de chemin:", result.get("error"))
            return False
        
        # 3. Test de l'agent (sans API pour aller vite)
        agent = IAMChatGPTAgent(api_key="fake-key-for-test")
        agent.enable_god_mode()
        
        # Vérifier que le mode GOD est activé dans file_manager
        if agent.file_manager.god_mode:
            print("✅ 3. Mode GOD activé dans file_manager")
        else:
            print("❌ 3. Mode GOD pas activé dans file_manager")
            return False
        
        # 4. Test de fonction directe
        direct_result = agent.handle_function_call("read_file", {"path": "README.md"})
        if direct_result.get("success"):
            content_size = len(direct_result.get("content", ""))
            print(f"✅ 4. Function call direct OK - {content_size} caractères lus")
        else:
            print("❌ 4. Function call direct échoué:", direct_result.get("error"))
            return False
        
        print("\n🎉 TOUTES LES CORRECTIONS SONT APPLIQUÉES!")
        print("✅ Le Function Calling devrait maintenant fonctionner avec l'API OpenAI")
        return True
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False

def test_with_real_api():
    """Test avec la vraie API si configurée"""
    try:
        import yaml
        with open("agent_config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        api_key = config.get("gpt4_api_key", "")
        if not api_key or api_key.startswith("your_"):
            print("\n⚠️ API OpenAI non configurée - test avec vraie API ignoré")
            return
        
        print("\n🚀 TEST AVEC VRAIE API OPENAI")
        print("-" * 40)
        
        from IAM_ChatGPT_Integration import IAMChatGPTAgent
        agent = IAMChatGPTAgent(api_key=api_key)
        agent.enable_god_mode()
        
        # Test simple et rapide
        response, _ = agent.chat("Dis-moi juste 'OUI' si tu peux lire le fichier README.md")
        
        print(f"Réponse: {response}")
        
        if "OUI" in response.upper() or "README" in response:
            print("✅ Function Calling avec API fonctionne!")
        else:
            print("❌ Function Calling avec API ne fonctionne pas encore")
            
    except Exception as e:
        print(f"❌ Erreur test API: {e}")

if __name__ == "__main__":
    success = verify_fixes()
    
    if success:
        print("\n📋 PROCHAINES ÉTAPES:")
        print("1. Testez avec: python test_chatgpt_function_calling.py")
        print("2. Ou lancez l'agent: python IAM_Agent.py --full-agent")
        print("3. Demandez à l'agent de lire un fichier pour vérifier")
        
        # Test optionnel avec vraie API
        test_with_real_api()
    else:
        print("\n❌ Il y a encore des problèmes à corriger")
        print("Vérifiez les erreurs ci-dessus")
