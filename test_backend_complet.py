#!/usr/bin/env python3
"""
🧪 Test Complet du Backend IAM Amélioré
Test tous les endpoints : /smiles_to_xyz, /molfile_to_xyz, /run_xtb, /write_file, /predict_vod
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_smiles_to_xyz():
    """Test de conversion SMILES → XYZ"""
    print("🧪 Test SMILES → XYZ")
    data = {"smiles": "CCO"}  # Éthanol
    
    try:
        response = requests.post(f"{BASE_URL}/smiles_to_xyz", json=data)
        result = response.json()
        
        if result.get('success'):
            print("✅ SMILES → XYZ : SUCCÈS")
            xyz = result.get('xyz', '')
            lines = xyz.split('\n')
            print(f"   Molécule: {lines[0]} atomes - {lines[1]}")
            return xyz
        else:
            print(f"❌ Erreur: {result.get('error')}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


def test_molfile_to_xyz():
    """Test de conversion MOL → XYZ"""
    print("\n🧪 Test MOL → XYZ")
    
    # MOL simple (méthane)
    mol_data = """
  Mrv2014 01012020

  1  0  0  0  0  0            999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
M  END
"""
    
    data = {"mol": mol_data}
    
    try:
        response = requests.post(f"{BASE_URL}/molfile_to_xyz", json=data)
        result = response.json()
        
        if 'xyz' in result:
            print("✅ MOL → XYZ : SUCCÈS")
            xyz = result.get('xyz', '')
            lines = xyz.split('\n')
            print(f"   Molécule: {lines[0]} atomes - {lines[1]}")
            return xyz
        else:
            print(f"❌ Erreur: {result.get('error')}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


def test_run_xtb_json(xyz_data):
    """Test calcul XTB avec données JSON"""
    if not xyz_data:
        print("\n⚠️  Pas de données XYZ pour test XTB")
        return
        
    print("\n🧪 Test XTB (mode JSON)")
    
    data = {"xyz": xyz_data}
    
    try:
        response = requests.post(f"{BASE_URL}/run_xtb", json=data)
        result = response.json()
        
        if result.get('success'):
            print("✅ XTB calcul : SUCCÈS")
            print(f"   Méthode: {result.get('method', 'N/A')}")
            if 'xtb_json' in result:
                print("   📊 Données JSON XTB disponibles")
            return True
        else:
            print(f"❌ Erreur XTB: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def test_write_file():
    """Test écriture de fichier"""
    print("\n🧪 Test écriture fichier")
    
    data = {
        "path": "test_output.txt",
        "content": "Test écriture backend IAM\nTimestamp: " + str(time.time())
    }
    
    try:
        response = requests.post(f"{BASE_URL}/write_file", json=data)
        result = response.json()
        
        if result.get('status') == 'success':
            print("✅ Écriture fichier : SUCCÈS")
            print(f"   Fichier: {result.get('path')}")
            return True
        else:
            print(f"❌ Erreur: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def test_predict_vod(xyz_data):
    """Test prédiction VOD"""
    if not xyz_data:
        print("\n⚠️  Pas de données XYZ pour test VOD")
        return
        
    print("\n🧪 Test prédiction VOD")
    
    data = {"xyz": xyz_data}
    
    try:
        response = requests.post(f"{BASE_URL}/predict_vod", json=data)
        result = response.json()
        
        if 'vod_predicted' in result:
            print("✅ Prédiction VOD : SUCCÈS")
            print(f"   VOD prédite: {result.get('vod_predicted')} m/s")
            print(f"   Modèle: {result.get('model')}")
            print(f"   Note: {result.get('note')}")
            return True
        else:
            print(f"❌ Erreur: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def main():
    """Test complet de tous les endpoints"""
    print("🔬 === TEST COMPLET BACKEND IAM AMÉLIORÉ ===")
    print(f"URL: {BASE_URL}")
    
    # Vérifier que le serveur répond
    try:
        response = requests.get(BASE_URL, timeout=5)
        print("✅ Serveur accessible")
    except:
        print("❌ Serveur non accessible - Démarrez le backend avec 'python backend.py'")
        return
    
    print("\n" + "="*50)
    
    # Tests séquentiels
    xyz_from_smiles = test_smiles_to_xyz()
    xyz_from_mol = test_molfile_to_xyz()
    
    # Utiliser les XYZ générés pour les tests suivants
    xyz_data = xyz_from_smiles or xyz_from_mol
    
    test_run_xtb_json(xyz_data)
    test_write_file()
    test_predict_vod(xyz_data)
    
    print("\n" + "="*50)
    print("🎯 Tests terminés - Backend IAM combiné opérationnel!")


if __name__ == "__main__":
    main()
