#!/usr/bin/env python3
"""
Test spécifique pour le format INDIGO qui pose problème
"""

import sys
sys.path.append('/home/lppou/IAM/IAM_GUI')

def test_indigo_format():
    """Test du format INDIGO spécifique"""
    
    # Le contenu exact qui pose problème
    indigo_mol = """-INDIGO-07222523152D

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

    print("🧪 Test format INDIGO problématique")
    print("=" * 50)
    
    print("Original MOL:")
    print(indigo_mol[:200] + "...")
    
    # Test avec notre fonction patch
    try:
        from backend import patch_molblock
        patched = patch_molblock(indigo_mol)
        print("\\n✅ Patch réussi!")
        print("MOL corrigé:")
        print(patched[:300] + "...")
        
        # Test avec RDKit
        from rdkit import Chem
        mol = Chem.MolFromMolBlock(patched, sanitize=False)
        if mol:
            print(f"\\n✅ RDKit parse réussi: {mol.GetNumAtoms()} atomes")
            
            # Test conversion XYZ
            try:
                from backend import embed_molecule_with_3d
                mol = Chem.AddHs(mol, addCoords=False)
                mol = embed_molecule_with_3d(mol)
                xyz = Chem.MolToXYZBlock(mol)
                print(f"✅ Conversion XYZ réussie: {len(xyz)} caractères")
                print("Preview XYZ:")
                print(xyz[:200] + "...")
                
            except Exception as e:
                print(f"❌ Erreur conversion XYZ: {e}")
        else:
            print("❌ RDKit parse échoué")
            
    except Exception as e:
        print(f"❌ Erreur patch: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_indigo_format()
