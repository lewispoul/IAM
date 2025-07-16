#!/usr/bin/env python3
"""
Test simple du backend IAM pour débugger les problèmes RDKit
"""

import sys
sys.path.append('/home/lppou/IAM/IAM_GUI')

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    print("✅ RDKit importé avec succès")
    
    # Test SMILES
    mol = Chem.MolFromSmiles('C')
    print(f"✅ SMILES 'C' parsé: {mol is not None}")
    
    # Test MOL simple
    mol_data = """
  Mrv2014 01012021

  1  0  0  0  0  0            999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
M  END
"""
    
    mol2 = Chem.MolFromMolBlock(mol_data)
    print(f"✅ MOL parsé: {mol2 is not None}")
    
    if mol2 is None:
        print("❌ Problème avec le MOL block")
        # Essayer un MOL plus complet
        mol_data2 = """
  Mrv2425 03152025

  1  0  0  0  0  0            999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
M  END
"""
        mol3 = Chem.MolFromMolBlock(mol_data2, sanitize=False)
        print(f"✅ MOL sans sanitize: {mol3 is not None}")
    
    # Test des fonctions backend
    from backend import smiles_to_xyz_conversion
    xyz = smiles_to_xyz_conversion('C')
    print(f"✅ Conversion SMILES→XYZ: {len(xyz)} caractères")
    print("Premier XYZ:", xyz[:100])
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
