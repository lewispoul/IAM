import os
import subprocess
from rdkit import Chem
from rdkit.Chem import AllChem

def generate_xyz_from_smiles(smiles, output_path):
    mol = Chem.MolFromSmiles(smiles)
    mol = Chem.AddHs(mol)
    AllChem.EmbedMolecule(mol, AllChem.ETKDG())
    AllChem.UFFOptimizeMolecule(mol)
    conf = mol.GetConformer()

    with open(output_path, "w") as f:
        f.write(f"{mol.GetNumAtoms()}\n")
        f.write("Generated from SMILES\n")
        for atom in mol.GetAtoms():
            pos = conf.GetAtomPosition(atom.GetIdx())
            f.write(f"{atom.GetSymbol()} {pos.x:.5f} {pos.y:.5f} {pos.z:.5f}\n")

def validate_xyz(file_path):
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
        num_atoms = int(lines[0].strip())
        if len(lines) < num_atoms + 2:
            raise ValueError("XYZ file too short for declared atom count.")
        for line in lines[2:2 + num_atoms]:
            parts = line.strip().split()
            if len(parts) != 4:
                raise ValueError(f"Invalid line format: {line}")
            float(parts[1])
            float(parts[2])
            float(parts[3])
        return True
    except Exception as e:
        raise RuntimeError(f"Invalid XYZ format: {e}")

def run_xtb(xyz_path, output_dir):
    env = os.environ.copy()
    xtb_path = os.environ.get("XTB_PATH")
    if xtb_path:
        env["PATH"] = f"{xtb_path}:{env['PATH']}"

    result = subprocess.run(
        ["xtb", xyz_path, "--opt", "--property"],
        cwd=output_dir,
        text=True,
        capture_output=True,
        env=env
    )
    if result.returncode != 0:
        raise RuntimeError(f"XTB failed:\n{result.stderr}")
    return parse_xtb_results(os.path.join(output_dir, "xtb.out"))

def parse_xtb_results(out_path):
    results = {}
    if not os.path.exists(out_path):
        raise FileNotFoundError(f"{out_path} not found")
    with open(out_path, "r") as f:
        for line in f:
            if "TOTAL ENERGY" in line:
                results["Total Energy"] = float(line.split()[-2])
            elif "HOMO-LUMO GAP" in line:
                results["HOMO-LUMO Gap"] = float(line.split()[-2])
            elif "GRADIENT NORM" in line:
                results["Gradient Norm"] = float(line.split()[-2])
    return results

def full_molecule_workflow(smiles, name, results_dir="notebooks/results"):
    output_dir = os.path.abspath(results_dir)
    os.makedirs(output_dir, exist_ok=True)

    xyz_path = os.path.join(output_dir, f"{name}.xyz")
    generate_xyz_from_smiles(smiles, xyz_path)
    validate_xyz(xyz_path)

    results = run_xtb(xyz_path, output_dir)
    results["XYZ path"] = xyz_path
    return results
