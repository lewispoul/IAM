#!/usr/bin/env python3

"""
Test d'intégration complète du backend IAM corrigé
Simule les requêtes du frontend
"""

import requests
import json
import time
import subprocess
import os
import signal
import sys

def test_backend_integration():
    """Test complet du backend avec serveur Flask"""
    print("🧪 Test d'intégration backend IAM")
    
    # Démarrer le backend Flask
    print("🚀 Démarrage du serveur Flask...")
    backend_proc = subprocess.Popen(
        [sys.executable, 'backend.py'],
        cwd='/home/lppou/IAM/IAM_GUI',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        # Attendre que le serveur démarre
        time.sleep(3)
        
        # Test 1: Endpoint racine
        print("🌐 Test 1: Endpoint racine...")
        try:
            resp = requests.get('http://localhost:5000/', timeout=5)
            print(f"✅ Status: {resp.status_code}")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        # Test 2: Conversion SMILES→XYZ
        print("🔬 Test 2: SMILES→XYZ...")
        try:
            data = {"smiles": "CCO"}
            resp = requests.post('http://localhost:5000/smiles_to_xyz', 
                               json=data, timeout=10)
            result = resp.json()
            if result.get('success'):
                print("✅ SMILES→XYZ OK")
                print(f"   XYZ preview: {result.get('xyz', '')[:50]}...")
            else:
                print(f"❌ Erreur SMILES: {result.get('error')}")
        except Exception as e:
            print(f"❌ Exception SMILES: {e}")
        
        # Test 3: Conversion MOL→XYZ (comme Ketcher)
        print("🧬 Test 3: MOL→XYZ...")
        test_mol = """IAM_Molecule
  IAM-Generated
  
  3  2  0  0  0  0  0  0  0  0999 V2000
    1.5000   -0.2500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.0000    0.2500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -1.5000   -0.2500    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  2  3  1  0  0  0  0
M  END
"""
        try:
            data = {"mol": test_mol}
            resp = requests.post('http://localhost:5000/molfile_to_xyz',
                               json=data, timeout=10)
            result = resp.json()
            if result.get('success'):
                print("✅ MOL→XYZ OK")
                print(f"   XYZ preview: {result.get('xyz', '')[:50]}...")
            else:
                print(f"❌ Erreur MOL: {result.get('error')}")
        except Exception as e:
            print(f"❌ Exception MOL: {e}")
        
        # Test 4: Calcul XTB
        print("⚛️ Test 4: Calcul XTB...")
        try:
            xyz_data = """3
Test molecule
C     0.000000    0.000000    0.000000
C     1.540000    0.000000    0.000000
O     2.040000    1.000000    0.000000
"""
            data = {"xyz": xyz_data}
            resp = requests.post('http://localhost:5000/run_xtb',
                               json=data, timeout=30)
            result = resp.json()
            if result.get('success'):
                print("✅ XTB Calcul OK")
                print(f"   Méthode: {result.get('method')}")
            else:
                print(f"⚠️ XTB Info: {result.get('error', 'Pas de détails')}")
                # XTB peut échouer si pas installé, c'est normal
        except Exception as e:
            print(f"⚠️ XTB Exception: {e}")
            
        print("🎉 Tests d'intégration terminés!")
        
    finally:
        # Arrêter le serveur
        print("🛑 Arrêt du serveur...")
        backend_proc.terminate()
        try:
            backend_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_proc.kill()

if __name__ == "__main__":
    test_backend_integration()
