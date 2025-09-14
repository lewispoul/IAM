#!/usr/bin/env python3
# test_chatgpt_agent.py - Test de l'agent ChatGPT avec accès complet

import sys
import os
sys.path.append('/home/lppou/IAM')

from IAM_FileManager import IAMFileManager
from IAM_CodeExecutor import IAMCodeExecutor
from IAM_ChatGPT_Integration import IAMChatGPTAgent
import yaml

def test_file_manager():
    """Test du gestionnaire de fichiers"""
    print("🔍 Test du gestionnaire de fichiers...")
    
    fm = IAMFileManager()
    
    # Test liste des fichiers
    result = fm.list_directory("IAM")
    if result.get("success"):
        print(f"✅ Liste des fichiers: {len(result['items'])} éléments trouvés")
    else:
        print(f"❌ Erreur: {result.get('error')}")
    
    # Test création d'un fichier temporaire
    test_content = "print('Hello from ChatGPT Agent!')\n"
    result = fm.write_file("IAM/test_temp.py", test_content)
    if result.get("success"):
        print("✅ Création de fichier: OK")
    else:
        print(f"❌ Erreur création: {result.get('error')}")
    
    # Test lecture du fichier
    result = fm.read_file("IAM/test_temp.py")
    if result.get("success"):
        print("✅ Lecture de fichier: OK")
    else:
        print(f"❌ Erreur lecture: {result.get('error')}")
    
    # Nettoyer
    fm.delete_file("IAM/test_temp.py")
    print("🧹 Fichier temporaire supprimé")

def test_code_executor():
    """Test de l'exécuteur de code"""
    print("\n🔍 Test de l'exécuteur de code...")
    
    ce = IAMCodeExecutor()
    
    # Test code Python simple
    test_code = """
import math
result = math.sqrt(16)
print(f"√16 = {result}")
"""
    result = ce.execute_python_code(test_code)
    if result.get("success"):
        print("✅ Exécution Python: OK")
        print(f"   Sortie: {result['stdout'].strip()}")
    else:
        print(f"❌ Erreur Python: {result.get('error')}")
    
    # Test commande shell
    result = ce.execute_shell_command("echo 'Hello from shell'")
    if result.get("success"):
        print("✅ Exécution shell: OK")
        print(f"   Sortie: {result['stdout'].strip()}")
    else:
        print(f"❌ Erreur shell: {result.get('error')}")

def test_chatgpt_integration():
    """Test de l'intégration ChatGPT"""
    print("\n🔍 Test de l'intégration ChatGPT...")
    
    try:
        # Charger la configuration
        with open("/home/lppou/IAM/agent_config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        api_key = config.get("gpt4_api_key")
        if not api_key or api_key == "VOTRE_CLE_API_ICI":
            print("❌ Clé API non configurée dans agent_config.yaml")
            return
        
        print("✅ Configuration API: OK")
        print("✅ Agent ChatGPT prêt à être utilisé")
        
    except Exception as e:
        print(f"❌ Erreur configuration: {str(e)}")

def main():
    """Test principal"""
    print("🧪 Test de l'agent ChatGPT IAM avec accès complet")
    print("=" * 55)
    
    test_file_manager()
    test_code_executor()
    test_chatgpt_integration()
    
    print("\n" + "=" * 55)
    print("🎉 Tests terminés!")
    print("\nPour lancer l'agent complet:")
    print("./launch_chatgpt_agent.sh")
    print("ou")
    print("python3 IAM_Agent.py --full-agent")

if __name__ == "__main__":
    main()
