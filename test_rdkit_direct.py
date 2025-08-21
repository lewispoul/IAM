#!/usr/bin/env python3
"""
Direct test of RDKit MOL parsing
"""

from rdkit import Chem
from rdkit.Chem import rdDistGeom, rdForceFieldHelpers

# Test MOL content - water molecule with proper format
WATER_MOL = """
  Marvin  01010101

  3  2  0  0  0  0            999 V2000
    0.0000    0.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
    0.7571    0.5861    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   -0.7571    0.5861    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  1  3  1  0  0  0  0
M  END
""".strip()

# Better formatted water molecule
WATER_MOL_2 = """
  Marvin  01010101

  3  2  0  0  0  0            999 V2000
    0.0000    0.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
    0.7571    0.5861    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   -0.7571    0.5861    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  1  3  1  0  0  0  0
M  END
"""

def test_rdkit_parsing():
    """Test RDKit MOL parsing directly"""
    
    print("🧪 Testing RDKit MOL parsing directly")
    print("=" * 50)
    
    # Test basic parsing
    print("\n1. Testing basic mol parsing (sanitize=False):")
    mol = Chem.MolFromMolBlock(WATER_MOL, sanitize=False)
    print(f"   Result: {mol}")
    if mol:
        print(f"   Atoms: {mol.GetNumAtoms()}")
        print(f"   Bonds: {mol.GetNumBonds()}")
    
    print("\n2. Testing with sanitize=True:")
    mol2 = Chem.MolFromMolBlock(WATER_MOL, sanitize=True)
    print(f"   Result: {mol2}")
    if mol2:
        print(f"   Atoms: {mol2.GetNumAtoms()}")
        print(f"   Bonds: {mol2.GetNumBonds()}")
    
    print("\n3. Testing alternative format:")
    mol3 = Chem.MolFromMolBlock(WATER_MOL_2, sanitize=False)
    print(f"   Result: {mol3}")
    if mol3:
        print(f"   Atoms: {mol3.GetNumAtoms()}")
        print(f"   Bonds: {mol3.GetNumBonds()}")
    
    # Try simple methane
    print("\n4. Testing simple methane:")
    methane_mol = """
  Methane

  5  4  0  0  0  0            999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.0920    0.0000    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   -0.3640    1.0296    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   -0.3640   -0.5148    0.8910 H   0  0  0  0  0  0  0  0  0  0  0  0
   -0.3640   -0.5148   -0.8910 H   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  1  3  1  0  0  0  0
  1  4  1  0  0  0  0
  1  5  1  0  0  0  0
M  END
"""
    mol4 = Chem.MolFromMolBlock(methane_mol, sanitize=False)
    print(f"   Result: {mol4}")
    if mol4:
        print(f"   Atoms: {mol4.GetNumAtoms()}")
        print(f"   Bonds: {mol4.GetNumBonds()}")
        
        # Try to add 3D coordinates
        print("\n5. Testing 3D coordinate generation:")
        try:
            Chem.rdDepictor.Compute2DCoords(mol4)
            rdDistGeom.EmbedMolecule(mol4)
            xyz = Chem.MolToXYZBlock(mol4)
            print("   ✅ 3D coordinates generated successfully!")
            print(f"   XYZ preview: {xyz[:200]}...")
        except Exception as e:
            print(f"   ❌ 3D generation failed: {e}")
    
    print("\n🏁 Direct RDKit test complete")

if __name__ == "__main__":
    test_rdkit_parsing()
