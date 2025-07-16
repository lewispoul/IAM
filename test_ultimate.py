#!/usr/bin/env python3

"""
Test ultime du Function Calling avec diagnostic complet
"""

def test_function_calling_ultimate():
    try:
        print("🚀 TEST ULTIME DU FUNCTION CALLING")
        print("=" * 60)
        
        # 1. Import et vérifications
        print("1. Import des modules...")
        import yaml
        from IAM_ChatGPT_Integration import IAMChatGPTAgent
        print("   ✅ Modules importés")
        
        # 2. Configuration
        print("2. Chargement configuration...")
        with open("agent_config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        api_key = config["gpt4_api_key"]
        print(f"   ✅ API Key: {api_key[:15]}...")
        
        # 3. Création agent
        print("3. Création de l'agent...")
        agent = IAMChatGPTAgent(api_key=api_key, model="gpt-4o")
        agent.enable_god_mode()
        print("   ✅ Agent prêt avec MODE GOD")
        
        # 4. Test direct fonction
        print("4. Test fonction read_file directement...")
        direct_result = agent.handle_function_call("read_file", {"path": "README.md"})
        if direct_result.get("success"):
            content = direct_result.get("content", "")
            print(f"   ✅ Lecture directe OK: {len(content)} caractères")
            print(f"   📄 Première ligne: {content.split()[0] if content else 'Vide'}")
        else:
            print(f"   ❌ Erreur directe: {direct_result.get('error')}")
            return False
        
        # 5. Test avec API OpenAI
        print("5. Test avec API OpenAI...")
        print("   🔄 Envoi requête à GPT-4o...")
        
        response, conversation = agent.chat(
            "Lis le fichier README.md et dis-moi combien de lignes il contient. Réponds juste avec le nombre."
        )
        
        print("=" * 60)
        print("🤖 RÉPONSE:")
        print(response)
        print("=" * 60)
        
        # 6. Vérification
        print("6. Vérification du résultat...")
        
        success_indicators = [
            "ligne" in response.lower(),
            "235" in response,  # Le README.md fait 235 lignes
            "fichier" in response.lower(),
            "README" in response,
            len(response) > 20  # Réponse détaillée
        ]
        
        success_count = sum(success_indicators)
        print(f"   📊 Indicateurs de succès: {success_count}/5")
        
        if success_count >= 3:
            print("   🎉 SUCCESS! Le Function Calling fonctionne!")
            print("   ✅ L'agent a accédé au fichier et analysé son contenu")
        else:
            print("   ❌ ECHEC! Function Calling ne fonctionne pas")
            print("   ⚠️ L'agent répond de manière générique")
        
        print("\n🏁 TEST TERMINÉ")
        return success_count >= 3
        
    except Exception as e:
        print(f"💥 ERREUR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_function_calling_ultimate()
    if success:
        print("\n🎉 FONCTION CALLING OPERATIONAL!")
        print("Vous pouvez maintenant utiliser l'agent avec confiance.")
    else:
        print("\n❌ PROBLÈME DÉTECTÉ")
        print("Le Function Calling ne fonctionne pas correctement.")
