#!/usr/bin/env python3
"""
Test du Function Calling pour IAM_ChatGPT_Integration.py
Ce script teste si l'agent peut réellement accéder aux fichiers et exécuter du code.
"""

import os
import yaml
from IAM_ChatGPT_Integration import IAMChatGPTAgent


def test_function_calling():
    """Test complet du Function Calling"""
    
    print("🧪 Test du Function Calling IAM ChatGPT Agent")
    print("=" * 50)
    
    # Charger la configuration
    try:
        with open("agent_config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        api_key = config["gpt4_api_key"]
    except FileNotFoundError:
        print("❌ Fichier agent_config.yaml non trouvé")
        print("💡 Créez ce fichier avec votre clé API OpenAI:")
        print("gpt4_api_key: 'votre_cle_api_ici'")
        return
    except KeyError:
        print("❌ Clé 'gpt4_api_key' non trouvée dans agent_config.yaml")
        return
    
    # Créer l'agent
    agent = IAMChatGPTAgent(api_key=api_key)
    agent.enable_god_mode()
    
    print("\n🔥 Agent créé avec MODE GOD activé")
    
    # Tests séquentiels
    tests = [
        {
            "name": "Test 1: Lecture d'un fichier existant",
            "message": "Peux-tu lire le fichier README.md et me dire ce qu'il contient?",
            "expected": "devrait lire le contenu du fichier README.md"
        },
        {
            "name": "Test 2: Liste des fichiers du répertoire",
            "message": "Liste-moi tous les fichiers Python (.py) dans le répertoire courant",
            "expected": "devrait lister les fichiers .py"
        },
        {
            "name": "Test 3: Exécution de code Python simple",
            "message": "Exécute ce code Python: print('Hello from IAM Agent!'); import os; print(f'Répertoire courant: {os.getcwd()}')",
            "expected": "devrait exécuter le code et afficher le résultat"
        },
        {
            "name": "Test 4: Création d'un fichier de test",
            "message": "Crée un fichier test_function_calling.txt avec le contenu 'Test réussi! Function Calling fonctionne.'",
            "expected": "devrait créer le fichier avec le contenu spécifié"
        }
    ]
    
    conversation = None
    
    for i, test in enumerate(tests, 1):
        print(f"\n{'='*20} {test['name']} {'='*20}")
        print(f"📝 Message: {test['message']}")
        print(f"🎯 Attendu: {test['expected']}")
        print("-" * 60)
        
        try:
            response, conversation = agent.chat(test['message'], conversation)
            print(f"🤖 Réponse: {response}")
            
            # Vérification spéciale pour le test 4
            if i == 4:
                if os.path.exists("test_function_calling.txt"):
                    with open("test_function_calling.txt", "r") as f:
                        content = f.read()
                    print(f"✅ Fichier créé avec succès! Contenu: {content}")
                else:
                    print("❌ Fichier non créé")
            
        except Exception as e:
            print(f"❌ Erreur dans le test {i}: {e}")
        
        print("-" * 60)
        input("Appuyez sur Entrée pour continuer...")
    
    print("\n🎉 Tests terminés!")
    print("Si vous voyez du contenu de fichiers et des résultats d'exécution,")
    print("alors le Function Calling fonctionne correctement!")


def test_direct_functions():
    """Test direct des fonctions sans API OpenAI"""
    print("\n🔧 Test direct des fonctions (sans OpenAI)")
    print("=" * 50)
    
    from IAM_FileManager import IAMFileManager
    from IAM_CodeExecutor import IAMCodeExecutor
    
    file_manager = IAMFileManager()
    file_manager.enable_god_mode()
    
    code_executor = IAMCodeExecutor()
    
    # Test lecture de fichier
    print("\n📖 Test lecture README.md:")
    result = file_manager.read_file("README.md")
    if "error" in result:
        print(f"❌ Erreur: {result['error']}")
    else:
        print(f"✅ Succès: {len(result.get('content', ''))} caractères lus")
    
    # Test liste de fichiers
    print("\n📁 Test liste des fichiers:")
    result = file_manager.list_directory("")
    if "error" in result:
        print(f"❌ Erreur: {result['error']}")
    else:
        files = result.get('files', [])
        py_files = [f for f in files if f.endswith('.py')]
        print(f"✅ Succès: {len(py_files)} fichiers Python trouvés")
    
    # Test exécution de code
    print("\n🐍 Test exécution Python:")
    result = code_executor.execute_python_code("print('Test direct réussi!')")
    if "error" in result:
        print(f"❌ Erreur: {result['error']}")
    else:
        print(f"✅ Succès: {result.get('output', 'Pas de sortie')}")


if __name__ == "__main__":
    print("Choisissez le type de test:")
    print("1. Test complet avec Function Calling (nécessite API OpenAI)")
    print("2. Test direct des fonctions (sans API)")
    
    choice = input("Votre choix (1 ou 2): ").strip()
    
    if choice == "1":
        test_function_calling()
    elif choice == "2":
        test_direct_functions()
    else:
        print("Choix invalide. Exécution du test direct...")
        test_direct_functions()
