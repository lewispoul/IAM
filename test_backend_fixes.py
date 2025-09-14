#!/usr/bin/env python3
"""
Test rapide du backend corrigé
"""

import sys
sys.path.append('/home/lppou/IAM/IAM_GUI')
import backend

def test_backend():
    print('🧪 Test du backend corrigé')
    print('=' * 40)
    
    # Test 1: SMILES
    try:
        xyz = backend.smiles_to_xyz_conversion('C')
        print('✅ Conversion SMILES→XYZ fonctionne')
        print(f'   Longueur XYZ: {len(xyz)} chars')
    except Exception as e:
        print(f'❌ Erreur SMILES: {e}')
    
    # Test 2: Détection XYZ
    test_xyz = '''5
Test molecule
C 0.0 0.0 0.0
H 1.0 0.0 0.0
H 0.0 1.0 0.0
H 0.0 0.0 1.0
H -1.0 0.0 0.0'''
    
    if backend.is_xyz_format(test_xyz):
        print('✅ Détection format XYZ fonctionne')
    else:
        print('❌ Détection format XYZ échoue')
    
    # Test 3: MOL simple
    mol_simple = '''
  -USER-

  1  0  0  0  0  0            999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
M  END
'''
    
    try:
        xyz = backend.mol_to_xyz(mol_simple)
        print('✅ Conversion MOL→XYZ simple fonctionne')
        print(f'   Longueur XYZ: {len(xyz)} chars')
    except Exception as e:
        print(f'⚠️  Erreur MOL simple: {e}')
    
    print('🎯 Tests terminés')

if __name__ == '__main__':
    test_backend()
