#!/usr/bin/env python3
"""
Fix rapide pour le problème INDIGO
"""

def quick_test_indigo():
    print("🔧 Test rapide INDIGO")
    
    # Contenu INDIGO simplifié
    mol_indigo = """-INDIGO-07222523152D

  5  5  0  0  0  0  0  0  0  0999 V2000
    3.5800   -2.9499    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    5.1200   -2.4496    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
M  END"""
    
    # Fix manuel simple
    lines = mol_indigo.splitlines()
    
    # 1. Remplacer header INDIGO
    if lines[0].startswith('-INDIGO-'):
        lines[0] = 'Molecule'
    
    # 2. Trouver et fixer la ligne de comptage
    for i, line in enumerate(lines):
        if 'V2000' in line:
            # Remplacer "0999" par "0"
            fixed_line = line.replace('0999', '  0')
            lines[i] = fixed_line
            print(f"Ligne originale: '{line}'")
            print(f"Ligne corrigée: '{fixed_line}'")
            break
    
    fixed_mol = '\\n'.join(lines)
    print("\\nMOL corrigé:")
    print(fixed_mol)
    
    # Test avec RDKit
    try:
        from rdkit import Chem
        mol = Chem.MolFromMolBlock(fixed_mol, sanitize=False)
        if mol:
            print(f"\\n✅ RDKit réussi: {mol.GetNumAtoms()} atomes")
            return True
        else:
            print("\\n❌ RDKit échoué")
            return False
    except Exception as e:
        print(f"\\n❌ Erreur RDKit: {e}")
        return False

if __name__ == "__main__":
    quick_test_indigo()
