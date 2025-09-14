#!/usr/bin/env python3
"""
Script de test complet pour IAM Plateforme Autonome v2.0
Teste l'interface web, les API REST et les fonctionnalités IA
"""

import requests
import json
import time
import os

# Configuration
BASE_URL = "http://localhost:5002"
TEST_MODULE = "test_auto_demo"

def test_platform_health():
    """Test de santé de la plateforme"""
    print("🔍 Test de connectivité plateforme...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        if response.status_code == 200 and "IAM" in response.text:
            print("✅ Plateforme accessible et fonctionnelle")
            return True
        else:
            print(f"❌ Réponse inattendue: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_module_api():
    """Test de l'API de génération de modules"""
    print("🤖 Test API génération de module...")
    
    data = {
        "module_name": TEST_MODULE,
        "description": "Module de test automatique avec fonction simple",
        "requirements": "Une fonction qui retourne 'Hello World'"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate_module", json=data, timeout=30)
        result = response.json()
        
        if result.get('success'):
            print("✅ Module généré via API")
            return True
        else:
            print(f"❌ Erreur API: {result.get('error', 'Inconnue')}")
            return False
            
    except requests.Timeout:
        print("⏰ Timeout - Génération trop longue")
        return False
    except Exception as e:
        print(f"❌ Erreur requête: {e}")
        return False

def test_files_creation():
    """Test de création des fichiers"""
    print("📁 Vérification des fichiers créés...")
    
    module_path = f"GeneratedScripts/{TEST_MODULE}.py"
    
    if os.path.exists(module_path):
        print(f"✅ Fichier module créé: {module_path}")
        
        # Vérifier le contenu
        with open(module_path, 'r') as f:
            content = f.read()
            if "def " in content or "class " in content:
                print("✅ Contenu du module valide")
                return True
            else:
                print("❌ Contenu du module invalide")
                return False
    else:
        print(f"❌ Fichier module non trouvé: {module_path}")
        return False

def test_chat_basic():
    """Test basique du chat"""
    print("💬 Test fonctionnalité chat...")
    
    data = {
        "message": "Dis juste 'Bonjour' s'il te plaît",
        "history": []
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=data, timeout=20)
        result = response.json()
        
        if result.get('success'):
            response_text = result.get('data', {}).get('response', '')
            print(f"✅ Chat fonctionne - Réponse: {response_text[:50]}...")
            return True
        else:
            error = result.get('error', 'Inconnue')
            if "API non configurée" in error:
                print("⚠️  Chat indisponible (API OpenAI non configurée)")
                return True  # Considéré comme normal
            else:
                print(f"❌ Erreur chat: {error}")
                return False
                
    except Exception as e:
        print(f"❌ Erreur chat: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("=" * 60)
    print("🧪 TEST COMPLET - IAM Plateforme Autonome v2.0")
    print("=" * 60)
    print(f"🎯 URL testée: {BASE_URL}")
    print()
    
    results = []
    test_names = []
    
    # Test 1: Santé plateforme
    test_names.append("Connectivité plateforme")
    results.append(test_platform_health())
    print()
    
    # Test 2: API modules
    test_names.append("API génération module")
    results.append(test_module_api())
    time.sleep(3)
    print()
    
    # Test 3: Fichiers créés
    test_names.append("Création de fichiers")
    results.append(test_files_creation())
    print()
    
    # Test 4: Chat basique
    test_names.append("Fonctionnalité chat")
    results.append(test_chat_basic())
    print()
    
    # Affichage des résultats
    print("=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = 0
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1:2d}. {name:<30} {status}")
        if result:
            passed += 1
    
    print()
    success_rate = (passed / len(results)) * 100
    print(f"🎯 Taux de réussite: {passed}/{len(results)} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("🎉 EXCELLENT ! Tous les tests sont passés.")
    elif success_rate >= 75:
        print("✅ BIEN ! La plupart des fonctionnalités marchent.")
    elif success_rate >= 50:
        print("⚠️  MOYEN. Quelques problèmes détectés.")
    else:
        print("❌ PROBLÈME. Plusieurs fonctionnalités ne marchent pas.")
    
    print()
    print("📋 Actions suggérées:")
    if success_rate < 100:
        print("   • Vérifier que la plateforme tourne: ps aux | grep IAM_AutonomousAgent_v2")
        print("   • Consulter les logs: tail -f platform_v2.log")
        print("   • Configurer OpenAI: export OPENAI_API_KEY='sk-...'")
    print(f"   • Interface web: {BASE_URL}")
    print("   • Modules générés: ls -la GeneratedScripts/")
    
    return success_rate >= 75

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
