from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import subprocess
import tempfile
import json
import traceback

from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import rdDistGeom
from rdkit.Chem import rdForceFieldHelpers

app = Flask(__name__, template_folder='templates')
CORS(app)

# --- Global error handler ---
@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({
        "success": False,
        "error": str(e),
        "details": traceback.format_exc()
    }), 500

# --- RDKit 3D coordinate generation helpers ---
def embed_molecule_with_3d(mol):
    """
    Embed 3D coordinates using ETKDG if available, fallback to standard, and optimize with UFF or MMFF if available.
    """
    # Try ETKDG if available
    params = None
    if hasattr(rdDistGeom, "ETKDGv3"):
        params = rdDistGeom.ETKDGv3()
    elif hasattr(rdDistGeom, "ETKDGv2"):
        params = rdDistGeom.ETKDGv2()
    elif hasattr(rdDistGeom, "ETKDG"):
        params = rdDistGeom.ETKDG()
    if params is not None:
        rdDistGeom.EmbedMolecule(mol, params)
    else:
        rdDistGeom.EmbedMolecule(mol)
    # Optimize geometry if possible
    try:
        if hasattr(rdForceFieldHelpers, "UFFOptimizeMolecule"):
            rdForceFieldHelpers.UFFOptimizeMolecule(mol)
        elif hasattr(rdForceFieldHelpers, "MMFFOptimizeMolecule"):
            rdForceFieldHelpers.MMFFOptimizeMolecule(mol)
    except Exception:
        pass
    return mol


@app.route('/', methods=['GET', 'POST'])
def index():
    results = {}
    if request.method == 'POST':
        smiles = request.form.get('smiles')
        job_name = request.form.get('job_name', 'job')

        try:
            # Convertir SMILES → Molécule 3D
            mol = Chem.MolFromSmiles(smiles)
            mol = Chem.AddHs(mol)
            mol = embed_molecule_with_3d(mol)
            xyz = Chem.MolToXYZBlock(mol)
            with tempfile.TemporaryDirectory() as tempdir:
                xyz_path = os.path.join(tempdir, f"{job_name}.xyz")
                with open(xyz_path, "w") as f:
                    f.write(xyz)

                # Lancer XTB
                xtb_command = ["xtb", xyz_path, "--opt", "--json", "--gfn", "2"]
                result = subprocess.run(xtb_command, cwd=tempdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                json_path = os.path.join(tempdir, "xtbout.json")
                if not os.path.exists(json_path):
                    results = {"success": False, "error": "Fichier xtbout.json non trouvé", "details": f"stdout: {result.stdout}\nstderr: {result.stderr}"}
                else:
                    with open(json_path, "r") as f:
                        results = json.load(f)

        except Exception as e:
            results = {"success": False, "error": str(e), "details": traceback.format_exc()}

    return render_template("iam_viewer_connected.html", results=results)


@app.route('/run_xtb', methods=['POST'])
def run_xtb():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file received", "details": "Aucun fichier reçu"}), 400

    xyz_file = request.files["file"]
    if xyz_file.filename == "":
        return jsonify({"success": False, "error": "Empty filename", "details": "Nom de fichier vide"}), 400

    # Get job parameters
    method = request.form.get('method', 'xtb')
    basis = request.form.get('basis', 'def2-SVP')
    charge = request.form.get('charge', '0')
    multiplicity = request.form.get('multiplicity', '1')
    calc_type = request.form.get('calcType', 'opt')
    solvent = request.form.get('solvent', 'gas')
    functional = request.form.get('functional', None)

    if method == 'psi4':
        try:
            with tempfile.TemporaryDirectory() as tempdir:
                xyz_path = os.path.join(tempdir, "molecule.xyz")
                xyz_file.save(xyz_path)
                # Read XYZ for atom block
                with open(xyz_path) as f:
                    xyz_lines = f.readlines()
                atom_block = ''.join(xyz_lines[2:])  # skip first two lines
                # Prepare Psi4 input
                psi4_input = f"""
molecule {{
{charge} {multiplicity}
{atom_block}
}}
set {{
    basis {basis}
    scf_type pk
    reference rhf
}}
set_num_threads(1)
set_memory('1 GB')
energy_type = '{calc_type}'
method = '{functional or 'b3lyp'}'
solvent = '{solvent}'

# Calculation type
if energy_type == 'sp':
    energy(f"{method}/{basis}")
elif energy_type == 'opt':
    optimize(f"{method}/{basis}")
elif energy_type == 'freq':
    frequency(f"{method}/{basis}")
"""
                psi4_in_path = os.path.join(tempdir, "input.dat")
                with open(psi4_in_path, "w") as f:
                    f.write(psi4_input)
                # Run Psi4
                psi4_out_path = os.path.join(tempdir, "psi4.out")
                psi4_command = ["psi4", psi4_in_path, psi4_out_path]
                result = subprocess.run(psi4_command, cwd=tempdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                # Parse output (simple: extract final energy, method, etc.)
                psi4_summary = {}
                if os.path.exists(psi4_out_path):
                    with open(psi4_out_path) as f:
                        out_lines = f.readlines()
                    for line in out_lines:
                        if 'Final energy is' in line:
                            psi4_summary['final_energy'] = float(line.split()[-1])
                        if 'Psi4' in line and 'version' in line:
                            psi4_summary['psi4_version'] = line.strip()
                psi4_summary['stdout'] = result.stdout[-1000:]  # last 1000 chars
                psi4_summary['stderr'] = result.stderr[-1000:]
                return jsonify({"success": True, "psi4_json": psi4_summary})
        except Exception as e:
            return jsonify({"success": False, "error": "Psi4 error", "details": traceback.format_exc()}), 500

    # Accept both XYZ and MOL input from frontend
    mol_string = xyz_file.read().decode("utf-8")
    # Heuristics: check for XYZ, else try MOL
    if is_xyz_format(mol_string):
        xyz_string = mol_string
    else:
        # Accept MOL if starts with 'Ketcher', 'INDIGO', or contains 'V2000'/'V3000'
        if (mol_string.strip().startswith("Ketcher") or
            mol_string.strip().startswith("INDIGO") or
            "V2000" in mol_string or "V3000" in mol_string):
            try:
                xyz_string = molblock_to_xyz(mol_string)
            except Exception as e:
                return jsonify({"success": False, "error": f"MOL to XYZ conversion failed: {e}", "details": traceback.format_exc()}), 400
        else:
            return jsonify({"success": False, "error": "Unknown molecule format. Please provide XYZ or MOLfile (V2000/V3000)."}), 400

    with tempfile.TemporaryDirectory() as tempdir:
        xyz_path = os.path.join(tempdir, "molecule.xyz")
        with open(xyz_path, "w") as f:
            f.write(xyz_string)
        # Debug: print the first few lines of the received/converted file
        with open(xyz_path) as f:
            lines = f.readlines()
        print("--- Received/converted file content for XTB job ---")
        print(''.join(lines[:10]))
        print("--- End of file preview ---")

        xtb_command = ["xtb", xyz_path, "--opt", "--json", "--gfn", "2"]
        # TODO: Use calc_type, charge, multiplicity, solvent, etc. in xtb_command as needed
        result = subprocess.run(xtb_command, cwd=tempdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        json_path = os.path.join(tempdir, "xtbout.json")
        xtbopt_xyz_path = os.path.join(tempdir, "xtbopt.xyz")
        # --- PATCH: Always return the final geometry as 'xyz' ---
        if os.path.exists(xtbopt_xyz_path):
            with open(xtbopt_xyz_path, "r") as f:
                xyz_string_final = f.read()
        else:
            with open(xyz_path, "r") as f:
                xyz_string_final = f.read()

        if not os.path.exists(json_path):
            return jsonify({
                "success": False,
                "error": "Fichier xtbout.json non trouvé",
                "details": f"stdout: {result.stdout}\nstderr: {result.stderr}\nfile_preview: {''.join(lines[:10])}",
                "xyz": xyz_string_final
            }), 500

        with open(json_path, "r") as f:
            xtb_data = json.load(f)

        return jsonify({"success": True, "xtb_json": xtb_data, "file_preview": ''.join(lines[:10]), "xyz": xyz_string_final})

@app.route('/smiles_to_xyz', methods=['POST'])
def smiles_to_xyz():
    data = request.get_json()
    smiles = data.get('smiles', '')
    try:
        mol = Chem.MolFromSmiles(smiles)
        mol = Chem.AddHs(mol)
        mol = embed_molecule_with_3d(mol)
        xyz = Chem.MolToXYZBlock(mol)
        return jsonify({'success': True, 'xyz': xyz})
    except Exception as e:
        return jsonify({'success': False, 'error': 'SMILES conversion error', 'details': traceback.format_exc()})


@app.route('/molfile_to_xyz', methods=['POST'])
def molfile_to_xyz():
    data = request.get_json()
    molfile = data.get('molfile', '')
    try:
        mol = Chem.MolFromMolBlock(molfile)
        mol = Chem.AddHs(mol)
        mol = embed_molecule_with_3d(mol)
        xyz = Chem.MolToXYZBlock(mol)
        return jsonify({'success': True, 'xyz': xyz})
    except Exception as e:
        return jsonify({'success': False, 'error': 'Molfile conversion error', 'details': traceback.format_exc()})

def is_xyz_format(mol_string: str) -> bool:
    """
    Check if the input string is in XYZ format.
    Returns True if the first line is an integer (atom count),
    and the second line is a comment or blank, and the rest look like atom lines.
    """
    lines = mol_string.strip().splitlines()
    if len(lines) < 3:
        return False
    try:
        atom_count = int(lines[0].strip())
        # Optionally check that the number of atom lines matches atom_count
        if len(lines) >= atom_count + 2:
            return True
    except Exception:
        pass
    return False


def molblock_to_xyz(mol_block: str) -> str:
    import traceback
    from rdkit import Chem
    from rdkit.Chem import AllChem
    try:
        lines = mol_block.strip().splitlines()
        # Ajoute une ligne de titre si manquante ou suspecte
        if not lines or (not lines[0].strip() or 'V2000' in lines[0] or 'INDIGO' in lines[0].upper() or 'KETCHER' in lines[0].upper()):
            lines = ["Generated by IAM"] + lines
        mol_block_fixed = "\n".join(lines)

        mol = Chem.MolFromMolBlock(mol_block_fixed, sanitize=True)
        if mol is None:
            raise ValueError("RDKit failed to parse the MOL block.")

        mol = Chem.AddHs(mol)
        if AllChem.EmbedMolecule(mol, AllChem.ETKDG()) != 0:
            raise ValueError("Failed to generate 3D coordinates.")
        AllChem.UFFOptimizeMolecule(mol)

        conf = mol.GetConformer()
        atoms = mol.GetAtoms()
        xyz_lines = [f"{len(atoms)}", "Generated by IAM"]
        for atom in atoms:
            pos = conf.GetAtomPosition(atom.GetIdx())
            xyz_lines.append(f"{atom.GetSymbol()} {pos.x:.6f} {pos.y:.6f} {pos.z:.6f}")
        return "\n".join(xyz_lines)

    except Exception as e:
        print("❌ Error in molblock_to_xyz:", traceback.format_exc())
        raise ValueError(f"❌ MOL to XYZ conversion failed: {str(e)}")


# Example usage:
# patched_mol = patch_molblock(mol_string)
# mol = Chem.MolFromMolBlock(patched_mol)
# (In molblock_to_xyz, patch_molblock is now always called before parsing)


def patch_molblock(molblock: str) -> str:
    """
    Make a MOL block maximally compatible with RDKit:
    - Strip all leading and trailing blank lines.
    - If the first line starts with '-INDIGO-', 'CDK', 'ChemDraw', or is blank, replace it with 'Untitled'.
    - If the second line starts with '-INDIGO-', 'CDK', 'ChemDraw', or is blank, replace it with a single space.
    - Ensure no blank lines before the counts line (the line with 'V2000' or 'V3000').
    - Fix the counts line: first 9 fields must be integer strings.
    - Remove extra blank lines except after the counts line (exactly one blank line after counts line).
    - Remove any extra lines after 'M  END'.
    - Return the fixed MOL block with a trailing newline.
    """
    import re
    lines = molblock.splitlines()
    # 1. Strip all leading and trailing blank lines
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    # 2. Fix first line
    known_headers = ('-INDIGO-', 'CDK', 'ChemDraw')
    if not lines or not lines[0].strip() or any(lines[0].startswith(h) for h in known_headers):
        if lines:
            lines[0] = 'Untitled'
        else:
            lines = ['Untitled']
    # 3. Fix second line
    if len(lines) < 2:
        lines.append(' ')
    elif not lines[1].strip() or any(lines[1].startswith(h) for h in known_headers):
        lines[1] = ' '
    # 4. Find counts line and ensure no blank lines before it
    counts_idx = None
    for i, line in enumerate(lines):
        if 'V2000' in line or 'V3000' in line:
            counts_idx = i
            break
    if counts_idx is None:
        # Not a valid MOL block, return as is
        return '\n'.join(lines) + '\n'
    # Remove blank lines before counts line
    before_counts = [l for l in lines[:counts_idx] if l.strip()]
    # 5. Fix counts line fields
    fields = lines[counts_idx].split()
    for j in range(min(9, len(fields))):
        try:
            fields[j] = str(int(float(fields[j])))
        except Exception:
            pass
    fixed_counts = ' '.join(fields)
    # 6. Remove extra blank lines except after counts line (exactly one blank line after counts line)
    after_counts = lines[counts_idx+1:]
    # Remove all blank lines
    after_counts = [l for l in after_counts if l.strip()]
    # Insert exactly one blank line after counts line
    after_counts = [''] + after_counts if after_counts else ['']
    # 7. Remove any extra lines after 'M  END'
    if 'M  END' in after_counts:
        m_end_idx = after_counts.index('M  END')
        after_counts = after_counts[:m_end_idx+1]
    # 8. Rebuild
    fixed_lines = before_counts + [fixed_counts] + after_counts
    result = '\n'.join(fixed_lines)
    if not result.endswith('\n'):
        result += '\n'
    return result

# Example usage:
# molblock = patch_molblock(molblock)
# mol = Chem.MolFromMolBlock(molblock)


from flask import render_template

@app.route('/dashboard')
def dashboard():
    return render_template('IAM_StatusDashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
