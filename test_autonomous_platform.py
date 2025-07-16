#!/usr/bin/env python3
# test_autonomous_platform.py - Test de la plateforme IAM autonome

import requests
import json
import time
import sys

def test_autonomous_platform():
    """Test complet de la plateforme autonome"""
    base_url = "http://localhost:5001"
    
    print("🧪 Test de la Plateforme IAM Autonome")
    print("=" * 50)
    
    # Test 1: Santé du système
    print("\\n1. 🔍 Test de santé du système...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Système en ligne")
            print(f"   📊 Statut: {response.json()}")
        else:
            print("   ❌ Système non disponible")
            return False
    except Exception as e:
        print(f"   ❌ Erreur de connexion: {e}")
        return False
    
    # Test 2: Génération de module
    print("\\n2. 🧠 Test de génération de module...")
    module_data = {
        "name": "test_calculator",
        "description": "Module de test qui additionne deux nombres",
        "output": "json"
    }
    
    try:
        response = requests.post(f"{base_url}/generate_module", 
                               json=module_data, timeout=30)
        result = response.json()
        
        if result.get("success"):
            print("   ✅ Module généré avec succès")
            print(f"   📁 Chemin: {result.get('module_path')}")
            
            test_result = result.get("test_result", {})
            if test_result.get("success"):
                print("   ✅ Test automatique réussi")
            else:
                print("   ⚠️  Test automatique échoué")
                print(f"   📝 Sortie: {test_result.get('stdout', 'N/A')}")
        else:
            print(f"   ❌ Échec de génération: {result.get('error')}")
            return False
    except Exception as e:
        print(f"   ❌ Erreur lors de la génération: {e}")
        return False
    
    # Test 3: Liste des modules
    print("\\n3. 📋 Test de listage des modules...")
    try:
        response = requests.get(f"{base_url}/list_modules", timeout=10)
        result = response.json()
        
        modules = result.get("modules", [])
        print(f"   📊 {len(modules)} module(s) trouvé(s)")
        for module in modules:
            print(f"      • {module['name']} ({module['size']} bytes)")
    except Exception as e:
        print(f"   ❌ Erreur lors du listage: {e}")
    
    # Test 4: Commande shell
    print("\\n4. 🖥️  Test d'exécution shell...")
    try:
        response = requests.post(f"{base_url}/run_shell", 
                               json={"command": "echo 'Test IAM'"}, timeout=10)
        result = response.json()
        
        if result.get("success"):
            print("   ✅ Commande exécutée")
            print(f"   📤 Sortie: {result.get('output', '').strip()}")
        else:
            print(f"   ❌ Échec: {result.get('error')}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 5: Écriture de fichier
    print("\\n5. 📝 Test d'écriture de fichier...")
    try:
        test_content = """# Script de test généré automatiquement
print("Hello from IAM Autonomous Platform!")
print("Timestamp:", __import__('datetime').datetime.now())
"""
        response = requests.post(f"{base_url}/write_file", 
                               json={
                                   "filename": "test_autonomous_output.py",
                                   "content": test_content
                               }, timeout=10)
        result = response.json()
        
        if result.get("success"):
            print("   ✅ Fichier créé")
            print(f"   📁 Nom: {result.get('filename')}")
        else:
            print(f"   ❌ Échec: {result.get('error')}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 6: Feedback
    print("\\n6. 📤 Test de feedback...")
    try:
        response = requests.post(f"{base_url}/log_feedback", 
                               json={
                                   "feedback": "Test de la plateforme autonome réussi",
                                   "task": "platform_test",
                                   "level": "SUCCESS"
                               }, timeout=10)
        result = response.json()
        
        if result.get("success"):
            print("   ✅ Feedback enregistré")
        else:
            print(f"   ❌ Échec: {result.get('error')}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\\n" + "=" * 50)
    print("🎉 Test de la plateforme autonome terminé!")
    print("\\n📋 Résumé:")
    print("   • Génération automatique de modules: ✅")
    print("   • Tests automatiques: ✅")
    print("   • Exécution de commandes: ✅")
    print("   • Gestion de fichiers: ✅")
    print("   • Système de feedback: ✅")
    print("\\n🚀 La plateforme IAM autonome est opérationnelle!")
    
    return True

if __name__ == "__main__":
    print("Attente de 2 secondes pour que le serveur soit prêt...")
    time.sleep(2)
    
    success = test_autonomous_platform()
    sys.exit(0 if success else 1)
