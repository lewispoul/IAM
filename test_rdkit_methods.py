from rdkit import Chem
from rdkit.Chem import AllChem

def test_rdkit_methods(smiles):
    try:
        # Convert SMILES to molecule
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            print("Invalid SMILES input.")
            return

        # Add hydrogens
        mol = Chem.AddHs(mol)

        # Embed 3D coordinates
        params = AllChem.ETKDGv3() if hasattr(AllChem, "ETKDGv3") else AllChem.ETKDG()
        embed_result = AllChem.EmbedMolecule(mol, params)
        if embed_result != 0:
            print("Embedding molecule failed.")
            return

        # Optimize geometry
        if hasattr(AllChem, "UFFOptimizeMolecule"):
            AllChem.UFFOptimizeMolecule(mol)
        elif hasattr(AllChem, "MMFFOptimizeMolecule"):
            AllChem.MMFFOptimizeMolecule(mol)
        else:
            print("No force field optimization method available in RDKit.")
            return

        # Convert to XYZ format
        xyz = Chem.MolToXYZBlock(mol)
        print("3D coordinates successfully generated:")
        print(xyz)

    except Exception as e:
        print(f"Error during RDKit method testing: {e}")

if __name__ == "__main__":
    # Example SMILES input for testing
    test_smiles = "CCO"  # Ethanol
    test_rdkit_methods(test_smiles)
