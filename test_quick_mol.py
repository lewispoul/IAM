#!/usr/bin/env python3
"""
Test rapide MOL→XYZ
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'IAM_GUI'))

try:
    import backend
    
    # MOL de test simple (éthane)
    test_mol = '''
  Molecule
  
  2  1  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.5000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
M  END
'''
    
    print("🧪 Test MOL→XYZ simple")
    try:
        xyz = backend.robust_mol_to_xyz(test_mol, "test_simple")
        print("✅ SUCCÈS!")
        print(f"XYZ généré: {len(xyz)} caractères")
        print("Premières lignes:")
        for line in xyz.split('\n')[:5]:
            print(f"  {line}")
    except Exception as e:
        print(f"❌ ÉCHEC: {e}")
        
except Exception as e:
    print(f"Erreur import: {e}")
