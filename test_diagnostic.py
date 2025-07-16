#!/usr/bin/env python3

import yaml
import sys
import os

# Ajouter le répertoire courant au PATH Python
sys.path.insert(0, '/home/lppou/IAM')

def test_imports():
    """Test des imports"""
    print("🔧 Test des imports...")
    try:
        from IAM_ChatGPT_Integration import IAMChatGPTAgent
        print("✅ IAMChatGPTAgent importé avec succès")
        
        from IAM_FileManager import IAMFileManager  
        print("✅ IAMFileManager importé avec succès")
        
        from IAM_CodeExecutor import IAMCodeExecutor
        print("✅ IAMCodeExecutor importé avec succès")
        
        return True
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_file_access():
    """Test d'accès aux fichiers"""
    print("\n🔧 Test d'accès aux fichiers...")
    
    # Test direct
    readme_path = "/home/lppou/IAM/README.md"
    if os.path.exists(readme_path):
        print("✅ README.md existe")
        with open(readme_path, 'r') as f:
            content = f.read()
        print(f"✅ Contenu lu: {len(content)} caractères")
        return True
    else:
        print("❌ README.md non trouvé")
        return False

def test_config():
    """Test de la configuration"""
    print("\n🔧 Test de la configuration...")
    try:
        with open("/home/lppou/IAM/agent_config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        api_key = config.get("gpt4_api_key", "")
        if api_key and api_key.startswith("sk-"):
            print("✅ Clé API configurée")
            return True
        else:
            print("❌ Clé API manquante ou invalide")
            return False
    except Exception as e:
        print(f"❌ Erreur de configuration: {e}")
        return False

def main():
    print("🚀 Diagnostic du système IAM ChatGPT")
    print("=" * 50)
    
    # Tests étape par étape
    imports_ok = test_imports()
    files_ok = test_file_access()  
    config_ok = test_config()
    
    print("\n📊 Résumé:")
    print(f"Imports: {'✅' if imports_ok else '❌'}")
    print(f"Fichiers: {'✅' if files_ok else '❌'}")
    print(f"Config: {'✅' if config_ok else '❌'}")
    
    if imports_ok and files_ok and config_ok:
        print("\n🎉 Tous les tests passent ! Vous pouvez tester l'agent.")
        print("Exécutez: python test_chatgpt_function_calling.py")
    else:
        print("\n❌ Il y a des problèmes à corriger.")

if __name__ == "__main__":
    main()
