#!/usr/bin/env python3
"""
Test script pour vérifier le fonctionnement du backend XTB
"""
import requests
import json

def test_smiles_to_xyz():
    """Test de la conversion SMILES vers XYZ"""
    url = "http://localhost:5000/smiles_to_xyz"
    data = {"smiles": "C"}  # Méthane
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print("✅ Conversion SMILES → XYZ réussie")
            print(f"XYZ: {result['xyz'][:100]}...")
            return True
        else:
            print(f"❌ Erreur dans la conversion: {result.get('error')}")
    else:
        print(f"❌ Erreur HTTP: {response.status_code}")
    return False

def test_xtb_calculation():
    """Test d'un calcul XTB"""
    url = "http://localhost:5000/run_xtb"
    
    # Créer un fichier XYZ simple (méthane)
    xyz_content = """5

C   0.0000   0.0000   0.0000
H   1.0900   0.0000   0.0000  
H  -0.3633   1.0281   0.0000
H  -0.3633  -0.5140   0.8902
H  -0.3633  -0.5140  -0.8902"""
    
    files = {'file': ('methane.xyz', xyz_content, 'text/plain')}
    data = {
        'method': 'xtb',
        'calcType': 'sp',  # Single point au lieu d'optimisation
        'charge': '0',
        'multiplicity': '1'
    }
    
    response = requests.post(url, files=files, data=data)
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print("✅ Calcul XTB réussi")
            xtb_data = result.get("xtb_json", {})
            energy = xtb_data.get("total energy")
            if energy:
                print(f"Énergie totale: {energy} Eh")
            return True
        else:
            print(f"❌ Erreur dans le calcul XTB: {result.get('error')}")
            print(f"Détails: {result.get('details', '')[:500]}...")
    else:
        print(f"❌ Erreur HTTP: {response.status_code}")
    return False

if __name__ == "__main__":
    print("🧪 Test du backend IAM Molecule Viewer")
    print("=" * 50)
    
    try:
        # Test 1: Conversion SMILES
        print("\n1. Test conversion SMILES → XYZ")
        smiles_ok = test_smiles_to_xyz()
        
        # Test 2: Calcul XTB
        print("\n2. Test calcul XTB")
        xtb_ok = test_xtb_calculation()
        
        # Résumé
        print("\n" + "=" * 50)
        print("📊 Résumé des tests:")
        print(f"SMILES → XYZ: {'✅' if smiles_ok else '❌'}")
        print(f"Calcul XTB: {'✅' if xtb_ok else '❌'}")
        
        if smiles_ok and xtb_ok:
            print("\n🎉 Tous les tests sont réussis ! Le backend fonctionne.")
        else:
            print("\n⚠️  Certains tests ont échoué. Vérifiez les logs.")
            
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
