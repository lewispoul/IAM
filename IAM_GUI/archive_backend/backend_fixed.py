"""
Backend Flask pour l'interface IAM - Version corrigée
"""
import json
import os
import subprocess
import tempfile
import traceback

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from rdkit import Chem

print("Hello")


def get_available_port(start_port=5000):
    """Trouve un port disponible."""
    import socket
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return start_port


app = Flask(__name__, template_folder='templates')
CORS(app)


def configure_app():
    """Configure l'application Flask avec les meilleures pratiques."""
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = '/tmp/iam_uploads'
    app.config['SECRET_KEY'] = 'iam-secret-key-change-in-production'
    
    # Créer le dossier de upload s'il n'existe pas
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app


@app.errorhandler(404)
def not_found(error):
    """Gestionnaire d'erreur 404."""
    return jsonify({"success": False, "error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Gestionnaire d'erreur 500."""
    return jsonify({"success": False, "error": "Internal server error"}), 500


configure_app()


@app.errorhandler(Exception)
def handle_exception(e):
    """Gestionnaire d'erreur global."""
    return jsonify({
        "success": False,
        "error": str(e),
        "details": traceback.format_exc()
    }), 500


def embed_molecule_with_3d(mol):
    """
    Embed 3D coordinates using ETKDG if available, fallback to standard,
    and optimize with UFF or MMFF if available.
    """
    from rdkit.Chem import rdDistGeom
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
        from rdkit.Chem import rdForceFieldHelpers
        if hasattr(rdForceFieldHelpers, "UFFOptimizeMolecule"):
            rdForceFieldHelpers.UFFOptimizeMolecule(mol)
        elif hasattr(rdForceFieldHelpers, "MMFFOptimizeMolecule"):
            rdForceFieldHelpers.MMFFOptimizeMolecule(mol)
    except Exception:
        pass
    return mol


@app.route('/', methods=['GET', 'POST'])
def index():
    """Page principale."""
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
                xtb_command = [
                    "xtb", xyz_path, "--opt", "--json", "--gfn", "2"
                ]
                result = subprocess.run(
                    xtb_command, cwd=tempdir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, text=True
                )

                json_path = os.path.join(tempdir, "xtbout.json")
                if not os.path.exists(json_path):
                    results = {
                        "success": False,
                        "error": "Fichier xtbout.json non trouvé",
                        "details": f"stdout: {result.stdout}\n"
                                   f"stderr: {result.stderr}"
                    }
                else:
                    with open(json_path, "r") as f:
                        results = json.load(f)

        except Exception as e:
            results = {
                "success": False,
                "error": str(e),
                "details": traceback.format_exc()
            }

    return render_template("iam_viewer_connected.html", results=results)


@app.route('/run_xtb', methods=['POST'])
def run_xtb():
    """Endpoint pour lancer XTB."""
    if "file" not in request.files:
        return jsonify({
            "success": False,
            "error": "No file received",
            "details": "Aucun fichier reçu"
        }), 400

    xyz_file = request.files["file"]
    if xyz_file.filename == "":
        return jsonify({
            "success": False,
            "error": "Empty filename",
            "details": "Nom de fichier vide"
        }), 400

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
                result = subprocess.run(
                    psi4_command, cwd=tempdir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, text=True
                )
                # Parse output (simple: extract final energy, method, etc.)
                psi4_summary = {}
                if os.path.exists(psi4_out_path):
                    with open(psi4_out_path) as f:
                        out_lines = f.readlines()
                    for line in out_lines:
                        if 'Final energy is' in line:
                            psi4_summary['final_energy'] = float(
                                line.split()[-1]
                            )
                        if 'Psi4' in line and 'version' in line:
                            psi4_summary['psi4_version'] = line.strip()
                psi4_summary['stdout'] = result.stdout[-1000:]
                psi4_summary['stderr'] = result.stderr[-1000:]
                return jsonify({"success": True, "psi4_json": psi4_summary})
        except Exception:
            return jsonify({
                "success": False,
                "error": "Psi4 error",
                "details": traceback.format_exc()
            }), 500

    # Accept both XYZ and MOL input from frontend
    mol_string = xyz_file.read().decode("utf-8")
    # Heuristics: check for XYZ, else try MOL
    if is_xyz_format(mol_string):
        xyz_string = mol_string
    else:
        # Accept MOL if starts with 'Ketcher', 'INDIGO',
        # or contains 'V2000'/'V3000'
        if (mol_string.strip().startswith("Ketcher") or
            mol_string.strip().startswith("INDIGO") or
            "V2000" in mol_string or "V3000" in mol_string):
            try:
                xyz_string = molblock_to_xyz(mol_string)
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"MOL to XYZ conversion failed: {e}",
                    "details": traceback.format_exc()
                }), 400
        else:
            return jsonify({
                "success": False,
                "error": "Unknown molecule format. Please provide XYZ "
                         "or MOLfile (V2000/V3000)."
            }), 400

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
        # TODO: Use calc_type, charge, multiplicity, solvent, etc.
        # in xtb_command as needed
        result = subprocess.run(
            xtb_command, cwd=tempdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True
        )

        json_path = os.path.join(tempdir, "xtbout.json")
        if not os.path.exists(json_path):
            return jsonify({
                "success": False,
                "error": "Fichier xtbout.json non trouvé",
                "details": f"stdout: {result.stdout}\n"
                           f"stderr: {result.stderr}\n"
                           f"file_preview: {''.join(lines[:10])}"
            }), 500

        with open(json_path, "r") as f:
            xtb_data = json.load(f)

        return jsonify({
            "success": True,
            "xtb_json": xtb_data,
            "file_preview": ''.join(lines[:10])
        })


@app.route('/smiles_to_xyz', methods=['POST'])
def smiles_to_xyz():
    """Convertit SMILES en XYZ."""
    data = request.get_json()
    smiles = data.get('smiles', '')
    try:
        mol = Chem.MolFromSmiles(smiles)
        mol = Chem.AddHs(mol)
        mol = embed_molecule_with_3d(mol)
        xyz = Chem.MolToXYZBlock(mol)
        return jsonify({'success': True, 'xyz': xyz})
    except Exception:
        return jsonify({
            'success': False,
            'error': 'SMILES conversion error',
            'details': traceback.format_exc()
        })


@app.route('/molfile_to_xyz', methods=['POST'])
def molfile_to_xyz():
    """Convertit un fichier MOL en XYZ."""
    data = request.get_json()
    molfile = data.get('molfile', '')
    try:
        mol = Chem.MolFromMolBlock(molfile)
        mol = Chem.AddHs(mol)
        mol = embed_molecule_with_3d(mol)
        xyz = Chem.MolToXYZBlock(mol)
        return jsonify({'success': True, 'xyz': xyz})
    except Exception:
        return jsonify({
            'success': False,
            'error': 'Molfile conversion error',
            'details': traceback.format_exc()
        })


def is_xyz_format(mol_string: str) -> bool:
    """
    Check if the input string is in XYZ format.
    Returns True if the first line is an integer (atom count),
    and the second line is a comment or blank, and the rest look like
    atom lines.
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


def molblock_to_xyz(molblock: str) -> str:
    """
    Convert a MOLfile (V2000 or V3000) string to XYZ format using RDKit.
    - Cleans up line endings, whitespace, and non-printable characters
    - Removes '-INDIGO-' header and leading blank lines
    - Tries strictParsing=False if needed
    - Adds hydrogens, generates 3D coordinates
    - Returns XYZ string
    Raises ValueError if conversion fails.
    """
    import string
    try:
        # Clean up MOL block: normalize line endings, strip whitespace,
        # remove nulls and non-printables
        molblock_clean = molblock.replace('\r\n', '\n').replace('\r', '\n')
        molblock_clean = ''.join(
            c for c in molblock_clean if c in string.printable
        )
        # Patch for Indigo/Ketcher: remove '-INDIGO-' header
        # and leading blank lines
        molblock_clean = patch_molblock(molblock_clean)
        # Remove empty lines anywhere (extra safety)
        molblock_clean = '\n'.join([
            line for line in molblock_clean.split('\n') if line.strip()
        ])
        # Try parsing with and without sanitization, and with strictParsing
        mol = Chem.MolFromMolBlock(
            molblock_clean, sanitize=False, removeHs=False
        )
        if mol is None:
            mol = Chem.MolFromMolBlock(
                molblock_clean, sanitize=False, removeHs=False,
                strictParsing=False
            )
        if mol is None:
            print("[DEBUG] MOL block that failed to parse:")
            print(molblock_clean)
            raise ValueError(
                "RDKit could not parse MOL block. This MOL may be "
                "incompatible with RDKit. Try exporting as V2000, "
                "or use SMILES/XYZ instead."
            )
        try:
            Chem.SanitizeMol(mol)
        except Exception as e:
            raise ValueError(f"RDKit could not sanitize MOL block: {e}")
        mol = Chem.AddHs(mol)
        mol = embed_molecule_with_3d(mol)
        xyz = Chem.MolToXYZBlock(mol)
        if not xyz or len(xyz.strip().splitlines()) < 3:
            raise ValueError("XYZ conversion failed or empty output.")
        return xyz
    except Exception as e:
        raise ValueError(f"Failed to convert MOL to XYZ: {e}")


def patch_molblock(molblock: str) -> str:
    """
    Make a MOL block maximally compatible with RDKit:
    - Strip all leading and trailing blank lines.
    - If the first line starts with '-INDIGO-', 'CDK', 'ChemDraw',
      or is blank, replace it with 'Untitled'.
    - If the second line starts with '-INDIGO-', 'CDK', 'ChemDraw',
      or is blank, replace it with a single space.
    - Ensure no blank lines before the counts line
      (the line with 'V2000' or 'V3000').
    - Fix the counts line: first 9 fields must be integer strings.
    - Remove extra blank lines except after the counts line
      (exactly one blank line after counts line).
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
    if (not lines or not lines[0].strip() or
            any(lines[0].startswith(h) for h in known_headers)):
        if lines:
            lines[0] = 'Untitled'
        else:
            lines = ['Untitled']
    # 3. Fix second line
    if len(lines) < 2:
        lines.append(' ')
    elif (not lines[1].strip() or
          any(lines[1].startswith(h) for h in known_headers)):
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
    # 6. Remove extra blank lines except after counts line
    # (exactly one blank line after counts line)
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
