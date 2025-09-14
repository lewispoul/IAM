#!/usr/bin/env python3
"""
Script de test pour vérifier les corrections IAM Molecule Viewer
"""

import subprocess
import time
import requests
import json
import sys

def test_backend_startup():
    """Test si le backend démarre correctement"""
    print("🧪 Test 1: Démarrage du backend...")
    
    # Démarrer le backend en arrière-plan
    process = subprocess.Popen(
        ["python", "backend.py"],
        cwd="/home/lppou/IAM/IAM_GUI",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Attendre un peu pour le démarrage
    time.sleep(3)
    
    try:
        # Tester si le backend répond
        response = requests.get("http://localhost:5000", timeout=5)
        print(f"✅ Backend démarré (status: {response.status_code})")
        return True, process
    except Exception as e:
        print(f"❌ Erreur démarrage backend: {e}")
        return False, process

def test_smiles_conversion():
    """Test la conversion SMILES → XYZ"""
    print("\n🧪 Test 2: Conversion SMILES → XYZ...")
    
    try:
        # Test avec une molécule simple (méthane)
        data = {"smiles": "C"}
        response = requests.post(
            "http://localhost:5000/smiles_to_xyz",
            json=data,
            timeout=10
        )
        
        result = response.json()
        if result.get("success") and "xyz" in result:
            print("✅ Conversion SMILES → XYZ fonctionne")
            print(f"   XYZ généré: {len(result['xyz'].split())} mots")
            return True
        else:
            print(f"❌ Erreur conversion SMILES: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test SMILES: {e}")
        return False

def test_mol_conversion():
    """Test la conversion MOL → XYZ"""
    print("\n🧪 Test 3: Conversion MOL → XYZ...")
    
    # MOL simple pour test (méthane)
    mol_data = """
  Mrv2014 01012021

  1  0  0  0  0  0            999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
M  END
"""
    
    try:
        data = {"molfile": mol_data}
        response = requests.post(
            "http://localhost:5000/molfile_to_xyz",
            json=data,
            timeout=10
        )
        
        result = response.json()
        if result.get("success") and "xyz" in result:
            print("✅ Conversion MOL → XYZ fonctionne")
            print(f"   XYZ généré: {len(result['xyz'].split())} mots")
            return True
        else:
            print(f"❌ Erreur conversion MOL: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test MOL: {e}")
        return False

def test_vod_prediction():
    """Test la prédiction VoD"""
    print("\n🧪 Test 4: Prédiction VoD...")
    
    # XYZ simple pour test
    xyz_data = """5
Methane
C 0.000000 0.000000 0.000000
H 1.089000 0.000000 0.000000
H -0.363000 1.026804 0.000000
H -0.363000 -0.513402 0.889165
H -0.363000 -0.513402 -0.889165"""
    
    try:
        data = {"xyz": xyz_data}
        response = requests.post(
            "http://localhost:5000/predict_vod",
            json=data,
            timeout=10
        )
        
        result = response.json()
        if "vod_predicted" in result:
            print(f"✅ Prédiction VoD fonctionne: {result['vod_predicted']} m/s")
            return True
        else:
            print(f"❌ Erreur prédiction VoD: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test VoD: {e}")
        return False

def cleanup_process(process):
    """Arrêter le processus backend"""
    try:
        process.terminate()
        time.sleep(2)
        if process.poll() is None:
            process.kill()
        print("\n🔧 Backend arrêté")
    except:
        pass

def main():
    """Fonction principale de test"""
    print("🚀 Tests de validation des corrections IAM Molecule Viewer")
    print("=" * 60)
    
    # Test 1: Démarrage
    backend_ok, process = test_backend_startup()
    if not backend_ok:
        print("\n❌ ÉCHEC: Le backend ne démarre pas")
        return
    
    # Test 2: SMILES
    smiles_ok = test_smiles_conversion()
    
    # Test 3: MOL
    mol_ok = test_mol_conversion()
    
    # Test 4: VoD
    vod_ok = test_vod_prediction()
    
    # Nettoyage
    cleanup_process(process)
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS:")
    print(f"   Backend startup: {'✅' if backend_ok else '❌'}")
    print(f"   SMILES → XYZ:    {'✅' if smiles_ok else '❌'}")
    print(f"   MOL → XYZ:       {'✅' if mol_ok else '❌'}")
    print(f"   VoD Prediction:  {'✅' if vod_ok else '❌'}")
    
    total_tests = 4
    passed_tests = sum([backend_ok, smiles_ok, mol_ok, vod_ok])
    
    print(f"\n🎯 SCORE: {passed_tests}/{total_tests} tests réussis")
    
    if passed_tests == total_tests:
        print("🎉 TOUS LES TESTS PASSENT - Les corrections fonctionnent !")
    else:
        print("⚠️  CERTAINS TESTS ÉCHOUENT - Vérifications nécessaires")

if __name__ == "__main__":
    main()
