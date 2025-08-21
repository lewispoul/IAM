#!/usr/bin/env python3
"""
✅ SOLUTION FINALE pour INDIGO
"""

import requests
import time

def test_indigo_final():
    print("🎯 TEST FINAL INDIGO")
    print("=" * 40)
    
    # Attendre que le serveur soit prêt
    time.sleep(2)
    
    # Contenu INDIGO exact du problème
    indigo_content = """-INDIGO-07222523152D

  5  5  0  0  0  0  0  0  0  0999 V2000
    3.5800   -2.9499    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    5.1200   -2.4496    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.0099   -3.4497    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    5.5097   -4.9897    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    4.0797   -4.4897    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  2  3  1  0  0  0  0
  3  4  1  0  0  0  0
  4  5  1  0  0  0  0
  5  1  1  0  0  0  0
M  END"""

    print("Contenu original INDIGO:")
    print(indigo_content[:150] + "...")
    
    # Test avec l'endpoint molfile_to_xyz
    try:
        response = requests.post('http://localhost:5000/molfile_to_xyz',
                               json={'mol_content': indigo_content},
                               timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                xyz = data.get('xyz', '')
                lines = xyz.split('\\n')
                atom_count = int(lines[0]) if lines and lines[0].isdigit() else 0
                
                print("\\n✅ SUCCÈS!")
                print(f"   Conversion INDIGO → XYZ réussie")
                print(f"   Nombre d'atomes: {atom_count}")
                print(f"   XYZ preview:")
                print("   " + "\\n   ".join(lines[:5]))
                
                return True
            else:
                error = data.get('error', 'Erreur inconnue')
                print(f"\\n❌ Échec conversion: {error}")
                return False
        else:
            print(f"\\n❌ HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"\\n❌ Erreur requête: {e}")
        return False

def test_simple_smiles():
    """Test que les SMILES fonctionnent toujours"""
    print("\\n🧪 Test SMILES (vérification)")
    
    try:
        response = requests.post('http://localhost:5000/smiles_to_xyz',
                               json={'smiles': 'CCO'},  # éthanol
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                xyz = data.get('xyz', '')
                lines = xyz.split('\\n')
                atom_count = int(lines[0]) if lines else 0
                print(f"✅ SMILES→XYZ : {atom_count} atomes pour éthanol")
                return True
            else:
                print(f"❌ SMILES failed: {data.get('error')}")
                return False
        else:
            print(f"❌ SMILES HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ SMILES error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 VALIDATION FINALE IAM")
    print("=" * 50)
    
    # Test server availability
    try:
        requests.get('http://localhost:5000/', timeout=3)
        print("✅ Serveur accessible")
    except:
        print("❌ Serveur non accessible")
        exit(1)
    
    # Tests
    indigo_ok = test_indigo_final()
    smiles_ok = test_simple_smiles()
    
    print("\\n" + "=" * 50)
    if indigo_ok and smiles_ok:
        print("🎉 TOUS LES TESTS RÉUSSIS!")
        print("   ✅ Problème INDIGO résolu")
        print("   ✅ SMILES fonctionnel") 
        print("   ✅ Système IAM opérationnel")
        print("\\n🌐 Interface disponible: http://localhost:5000")
    else:
        print("⚠️ Certains tests ont échoué")
        print(f"   INDIGO: {'✅' if indigo_ok else '❌'}")
        print(f"   SMILES: {'✅' if smiles_ok else '❌'}")
