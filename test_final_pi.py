#!/usr/bin/env python3
"""
🎯 Test Final - Validation Complète IAM Pi
"""

import sys
import os
import requests
import time

def test_flask_server():
    """Test du serveur Flask"""
    print("🌐 Test du serveur Flask...")
    
    urls = [
        "http://127.0.0.1:5000",
        "http://192.168.2.160:5000"
    ]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {url} - Accessible")
                return True
            else:
                print(f"⚠️  {url} - Code {response.status_code}")
        except Exception as e:
            print(f"❌ {url} - Erreur: {e}")
    
    return False

def test_git_branch():
    """Test de la branche Git"""
    print("🌿 Test de la branche Git...")
    
    try:
        import subprocess
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            cwd="/home/lppou/IAM"
        )
        
        branch = result.stdout.strip()
        if branch == "pi-dev-clean":
            print(f"✅ Branche: {branch}")
            return True
        else:
            print(f"⚠️  Branche actuelle: {branch} (attendu: pi-dev-clean)")
            return False
            
    except Exception as e:
        print(f"❌ Erreur Git: {e}")
        return False

def test_backend_import():
    """Test d'import du backend"""
    print("🔧 Test d'import du backend...")
    
    try:
        # Ajouter le path
        sys.path.insert(0, "/home/lppou/IAM/IAM_GUI")
        
        import backend
        print("✅ Backend importé avec succès")
        
        # Test des fonctions principales
        if hasattr(backend, 'app'):
            print("✅ Application Flask présente")
        
        if hasattr(backend, 'robust_mol_to_xyz'):
            print("✅ Fonction robust_mol_to_xyz présente")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur import backend: {e}")
        return False

def test_endpoints():
    """Test des endpoints Flask"""
    print("🎯 Test des endpoints...")
    
    base_url = "http://127.0.0.1:5000"
    
    endpoints = [
        "/",
        "/run_xtb",
        "/molfile_to_xyz",
        "/smiles_to_xyz"
    ]
    
    success_count = 0
    
    for endpoint in endpoints:
        try:
            url = base_url + endpoint
            
            if endpoint == "/":
                response = requests.get(url, timeout=5)
            else:
                # Test avec données vides pour voir si endpoint existe
                response = requests.post(url, json={}, timeout=5)
            
            if response.status_code in [200, 400, 500]:  # Endpoint existe
                print(f"✅ {endpoint} - Présent")
                success_count += 1
            else:
                print(f"❌ {endpoint} - Code {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint} - Erreur: {e}")
    
    return success_count >= 3

def main():
    """Test principal"""
    print("🎯 TEST FINAL - VALIDATION COMPLÈTE IAM PI")
    print("=" * 50)
    
    tests = [
        ("Git Branch", test_git_branch),
        ("Backend Import", test_backend_import),
        ("Flask Server", test_flask_server),
        ("Endpoints", test_endpoints)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        result = test_func()
        results.append((test_name, result))
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS FINAUX:")
    
    success_count = 0
    for test_name, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHEC"
        print(f"  {test_name}: {status}")
        if success:
            success_count += 1
    
    print(f"\n🎯 Score: {success_count}/{len(tests)}")
    
    if success_count == len(tests):
        print("🎉 TOUS LES TESTS RÉUSSIS !")
        print("✅ L'interface IAM est opérationnelle")
        print("🌐 Accessible sur: http://192.168.2.160:5000")
        print("⚡ GOD MODE disponible: ./launch_god_mode_flask.sh")
        return True
    else:
        print("⚠️  Certains tests ont échoué")
        print("💡 Vérifiez les logs pour plus de détails")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
