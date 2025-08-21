#!/usr/bin/env python3
"""Test rapide du fix INDIGO"""

# Test MOL INDIGO problématique 
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

def fix_indigo_mol(molblock):
    lines = molblock.strip().split('\n')
    if len(lines) < 4:
        return molblock
    
    lines[0] = 'Molecule'
    lines[1] = '  IAM'
    lines[2] = ''
    
    counts_line = lines[3].strip()
    parts = counts_line.split()
    
    if len(parts) >= 2:
        try:
            num_atoms = int(parts[0])
            num_bonds = int(parts[1])
            lines[3] = f"{num_atoms:3d}{num_bonds:3d}  0  0  0  0            999 V2000"
        except ValueError:
            pass
    
    return '\n'.join(lines)

# Test simple
print("🧪 Test fix rapide")
try:
    from rdkit import Chem
    
    print("AVANT:")
    mol_before = Chem.MolFromMolBlock(indigo_mol, sanitize=False)
    print(f"  RDKit: {mol_before}")
    
    fixed = fix_indigo_mol(indigo_mol)
    print("\\nAPRÈS:")
    print("  " + "\\n  ".join(fixed.split('\\n')[:4]))
    
    mol_after = Chem.MolFromMolBlock(fixed, sanitize=False)
    print(f"  RDKit: {mol_after}")
    
    if mol_after:
        print(f"  ✅ {mol_after.GetNumAtoms()} atomes, {mol_after.GetNumBonds()} liaisons")
    
except Exception as e:
    print(f"❌ {e}")
    
print("\\n🚀 Continuons avec la réparation complète de l'interface IAM!")
