#!/usr/bin/env python3

import requests
import json

# Le contenu MOL INDIGO qui pose problème
indigo_mol_content = """-INDIGO-07222523152D

  5  5  0  0  0  0  0  0  0  0999 V2000
    3.5800   -2.9499    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    5.1200   -2.4496    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.6603   -2.9499    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    6.6603   -4.4502    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    5.1200   -4.9506    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  2  3  1  0  0  0  0
  3  4  1  0  0  0  0
  4  5  1  0  0  0  0
  5  1  1  0  0  0  0
M  END"""

def test_backend_molfile_endpoint():
    print("🧪 Test endpoint MOL → XYZ avec INDIGO")
    print("=" * 50)
    
    try:
        response = requests.post(
            'http://localhost:5000/molfile_to_xyz',
            json={'mol_content': indigo_mol_content},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                xyz = data.get('xyz_content', '')
                print(f"✅ Succès! XYZ généré:")
                print(f"   Longueur: {len(xyz)} caractères")
                if xyz:
                    lines = xyz.split('\\n')
                    if len(lines) >= 2:
                        print(f"   Atomes: {lines[0]} (selon header XYZ)")
                        print(f"   Preview: {lines[1] if len(lines) > 1 else ''}")
            else:
                print(f"❌ Échec: {data.get('error', 'Erreur inconnue')}")
                if 'details' in data:
                    print(f"   Détails: {data['details'][:200]}...")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(f"   Réponse: {response.text[:300]}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur réseau: {e}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_backend_molfile_endpoint()
