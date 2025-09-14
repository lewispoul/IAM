#!/usr/bin/env python3
"""
Script de test rapide pour IAM
"""
import sys
import os
sys.path.append('/home/lppou/IAM')

def test_imports():
    print("🧪 Test des imports...")
    try:
        import flask
        print("✅ Flask")
        import rdkit
        print("✅ RDKit")
        import numpy
        print("✅ NumPy")
        import pandas
        print("✅ Pandas")
        return True
    except Exception as e:
        print(f"❌ Erreur import: {e}")
        return False

def test_xtb():
    print("🧪 Test XTB...")
    import subprocess
    try:
        result = subprocess.run(['xtb', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ XTB fonctionnel")
            return True
        else:
            print("❌ XTB erreur")
            return False
    except:
        print("❌ XTB non trouvé")
        return False

def test_backend():
    print("🧪 Test backend...")
    try:
        from IAM_GUI.backend import app
        print("✅ Backend importable")
        return True
    except Exception as e:
        print(f"❌ Backend erreur: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTS IAM")
    print("="*40)
    
    tests = [test_imports, test_xtb, test_backend]
    passed = 0
    
    for test in tests:
        if test():
            passed += 1
    
    print("="*40)
    print(f"📊 Résultats: {passed}/{len(tests)} tests réussis")
    
    if passed == len(tests):
        print("🎉 Tous les tests sont OK!")
        print("   Vous pouvez démarrer IAM avec: ./start_iam.sh")
    else:
        print("⚠️  Certains tests ont échoué")
        print("   Vérifiez l'installation des dépendances")
