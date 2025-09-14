#!/usr/bin/env python3

import requests
import json
import sys

# Our INDIGO test content
mol_content = """  -INDIGO-07162507472D

  6  6  0  0  0  0  0  0  0  0999 V2000
    1.7848   -3.1751    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    3.5152   -3.1746    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    4.3802   -4.6746    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    5.8802   -4.6741    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.7452   -3.1741    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.7457   -1.6741    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  2  3  1  0  0  0  0
  3  4  1  0  0  0  0
  4  5  1  0  0  0  0
  5  6  1  0  0  0  0
  6  1  1  0  0  0  0
M  END"""

print("🧪 Test de conversion INDIGO MOL → XYZ")
print("="*50)

try:
    data = {'mol_content': mol_content}
    response = requests.post('http://localhost:5000/molfile_to_xyz', 
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps(data),
                            timeout=15)
    
    print(f"Status HTTP: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("✅ SUCCÈS! Conversion MOL → XYZ réussie")
            xyz_content = result.get('xyz', '')
            print(f"Contenu XYZ (premiers 300 caractères):")
            print("-" * 40)
            print(xyz_content[:300])
            print("-" * 40)
            print(f"Longueur totale: {len(xyz_content)} caractères")
        else:
            print("❌ ÉCHEC de conversion:")
            print(result.get('error', 'Erreur inconnue'))
    else:
        print("❌ ERREUR SERVEUR:")
        print(response.text[:500])
        
except requests.exceptions.Timeout:
    print("⏱️ TIMEOUT - Serveur trop lent")
except requests.exceptions.ConnectionError:
    print("🔌 ERREUR CONNEXION - Serveur non disponible")
except Exception as e:
    print(f"❌ ERREUR INATTENDUE: {e}")

print("\n🔍 Test debug de parsing...")
try:
    debug_data = {'mol_content': mol_content}
    debug_response = requests.post('http://localhost:5000/debug_mol_parsing', 
                                   headers={'Content-Type': 'application/json'},
                                   data=json.dumps(debug_data),
                                   timeout=10)
    
    print(f"Debug status: {debug_response.status_code}")
    debug_result = debug_response.json()
    print("Debug résultat:")
    print(json.dumps(debug_result, indent=2)[:400] + "...")
    
except Exception as e:
    print(f"❌ Erreur debug: {e}")
