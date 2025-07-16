#!/usr/bin/env python3
"""
🧪 Test Upload XYZ et Géométrie Retournée
"""

import requests
import json

# Test 1: Upload XYZ simple
test_xyz = """2
Test ethane
C 0.0 0.0 0.0
C 1.5 0.0 0.0
"""

print("🧪 Test 1: Upload fichier XYZ")
print("=" * 40)

try:
    # Test de l'endpoint run_xtb avec données XYZ
    response = requests.post(
        'http://localhost:5000/run_xtb',
        json={'xyz': test_xyz},
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Requête réussie")
        
        # Vérifier la présence de géométrie
        if 'xyz' in result:
            print("✅ Géométrie retournée!")
            xyz_data = result['xyz']
            lines = xyz_data.strip().split('\n')
            print(f"   📊 {lines[0]} atomes dans la géométrie")
            print(f"   📐 Longueur XYZ: {len(xyz_data)} caractères")
        else:
            print("❌ Pas de géométrie retournée")
            
        if 'optimized_xyz' in result:
            print("✅ Géométrie optimisée disponible")
        
        if 'xtb_json' in result:
            print("✅ Données XTB JSON disponibles")
            xtb_data = result['xtb_json']
            if 'total energy' in xtb_data:
                energy = xtb_data['total energy']
                print(f"   ⚡ Énergie: {energy:.6f} Eh")
        
        print(f"   🎯 Succès: {result.get('success', False)}")
        if 'error' in result:
            print(f"   ⚠️ Erreur: {result['error']}")
            
    else:
        print(f"❌ Erreur HTTP {response.status_code}")
        print(f"   Réponse: {response.text[:200]}...")

except Exception as e:
    print(f"❌ Erreur de test: {e}")

print("\n🧪 Test 2: Validation format XYZ")
print("=" * 40)

# Test direct de validation XYZ
test_cases = [
    ("XYZ valide", test_xyz),
    ("XYZ invalide", "invalid content"),
    ("XYZ complexe", """6
Benzene test
C 1.4 0.0 0.0
C 0.7 1.2 0.0
C -0.7 1.2 0.0
C -1.4 0.0 0.0
C -0.7 -1.2 0.0
C 0.7 -1.2 0.0""")
]

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'IAM_GUI'))

try:
    import backend
    
    for name, content in test_cases:
        is_valid = backend.is_xyz_format(content)
        print(f"   {name}: {'✅ Valide' if is_valid else '❌ Invalide'}")
        
except Exception as e:
    print(f"❌ Erreur import backend: {e}")

print("\n🎯 Tests terminés")
print("🔍 Vérifiez les logs du backend pour plus de détails")
