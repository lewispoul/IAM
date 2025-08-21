#!/usr/bin/env python3

import re
from rdkit import Chem

def fix_mol_indigo_simple(mol_str: str) -> str:
    """Version ultra-simple qui corrige juste le header INDIGO"""
    lines = mol_str.strip().split('\n')
    
    if len(lines) < 4:
        return mol_str
    
    # Corriger seulement les 3 premières lignes
    lines[0] = 'Molecule'
    lines[1] = '  IAM'  
    lines[2] = ''
    
    return '\n'.join(lines)

# Test simple
if __name__ == "__main__":
    # MOL INDIGO qui pose problème
    indigo_mol = """-INDIGO-07222523152D

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

    print("🧪 Test fix INDIGO ultra-simple")
    print("AVANT:", indigo_mol.split('\n')[0])
    
    # Avant correction
    mol_before = Chem.MolFromMolBlock(indigo_mol, sanitize=False)
    print(f"RDKit AVANT: {mol_before}")
    
    # Correction simple
    fixed = fix_mol_indigo_simple(indigo_mol)
    print("APRÈS:", fixed.split('\n')[0])
    
    # Après correction  
    mol_after = Chem.MolFromMolBlock(fixed, sanitize=False)
    print(f"RDKit APRÈS: {mol_after}")
    
    if mol_after:
        print(f"✅ SUCCÈS: {mol_after.GetNumAtoms()} atomes")
    else:
        print("❌ Échec")
