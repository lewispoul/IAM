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

# Import du module IAM existant
import sys
sys.path.append('/home/lppou/IAM')
from IAM_Molecule_Engine.iam_molecule_engine import generate_xyz_from_smiles, full_molecule_workflow

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
    try:
        from rdkit.Chem import rdDepictor, rdDistGeom, rdForceFieldHelpers
        
        # Generate 2D coordinates first if needed
        rdDepictor.Compute2DCoords(mol)
        
        # Try ETKDG if available
        params = None
        if hasattr(rdDistGeom, "ETKDGv3"):
            params = rdDistGeom.ETKDGv3()
        elif hasattr(rdDistGeom, "ETKDGv2"):
            params = rdDistGeom.ETKDGv2()
        elif hasattr(rdDistGeom, "ETKDG"):
            params = rdDistGeom.ETKDG()
            
        if params is not None:
            result = rdDistGeom.EmbedMolecule(mol, params)
        else:
            result = rdDistGeom.EmbedMolecule(mol)
            
        if result != 0:
            print(f"⚠️ Embedding failed with code {result}, retrying with basic method")
            rdDistGeom.EmbedMolecule(mol)
            
        # Optimize geometry if possible
        try:
            if hasattr(rdForceFieldHelpers, "UFFOptimizeMolecule"):
                rdForceFieldHelpers.UFFOptimizeMolecule(mol)
            elif hasattr(rdForceFieldHelpers, "MMFFOptimizeMolecule"):
                rdForceFieldHelpers.MMFFOptimizeMolecule(mol)
        except Exception as e:
            print(f"⚠️ Force field optimization failed: {e}")
            
    except Exception as e:
        print(f"⚠️ 3D embedding failed: {e}")
        
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

    return render_template("index_old_ui.html", results=results)


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

    # Accept both XYZ and MOL input from frontend with robust parsing
    mol_string = xyz_file.read().decode("utf-8")
    
    # Check format and convert to XYZ
    if is_xyz_format(mol_string):
        xyz_string = mol_string
        print("📄 Format détecté: XYZ")
    else:
        # Try MOL format conversion with our robust function
        print("📄 Format détecté: MOL, conversion en cours...")
        try:
            xyz_string = robust_mol_to_xyz(mol_string, "xtb_endpoint")
            print("✅ Conversion MOL → XYZ réussie")
        except Exception as e:
            return jsonify({
                "success": False, 
                "error": f"Échec conversion MOL → XYZ: {str(e)}", 
                "details": traceback.format_exc(),
                "mol_preview": mol_string[:300] + "..." if len(mol_string) > 300 else mol_string
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
    """Convert SMILES to XYZ using IAM_Molecule_Engine"""
    try:
        data = request.get_json()
        smiles = data.get('smiles', '').strip()
        
        if not smiles:
            return jsonify({
                'success': False,
                'error': 'SMILES vide'
            })
        
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            xyz_path = os.path.join(tmpdir, 'molecule.xyz')
            
            try:
                generate_xyz_from_smiles(smiles, xyz_path)
                
                with open(xyz_path, 'r') as f:
                    xyz_content = f.read()
                
                return jsonify({
                    'success': True,
                    'xyz': xyz_content,
                    'message': f'Conversion SMILES→XYZ réussie pour {smiles}'
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Erreur conversion SMILES→XYZ: {str(e)}'
                })
                
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur endpoint SMILES: {str(e)}',
            'details': traceback.format_exc()
        })


@app.route('/molfile_to_xyz', methods=['POST'])
def molfile_to_xyz():
    """Enhanced MOL to XYZ conversion with robust error handling"""
    try:
        data = request.get_json()
        
        # Support multiple parameter names: 'molfile', 'mol', 'mol_content'
        molfile = data.get('molfile') or data.get('mol') or data.get('mol_content', '')
        
        if not molfile.strip():
            return jsonify({
                'success': False,
                'error': 'Fichier MOL vide'
            }), 400
        
        # Use our enhanced conversion function
        xyz = robust_mol_to_xyz(molfile, "molfile_endpoint")
        
        return jsonify({
            'success': True, 
            'xyz': xyz,
            'message': 'Conversion MOL → XYZ réussie'
        })
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': f'Erreur conversion MOL→XYZ: {str(e)}',
            'details': traceback.format_exc()
        }), 500


def robust_mol_to_xyz(mol_content: str, source: str = "unknown") -> str:
    """
    Robust MOL to XYZ conversion with multiple fallback strategies
    """
    if not mol_content.strip():
        raise ValueError("Contenu MOL vide")
    
    mol = None
    
    # Strategy 1: Try avec fix_indigo_mol d'abord (pour les formats INDIGO)
    if 'INDIGO' in mol_content.upper() or '-INDIGO-' in mol_content:
        try:
            fixed_mol = fix_indigo_mol(mol_content)
            print(f"🔧 MOL INDIGO corrigé pour {source}")
            mol = Chem.MolFromMolBlock(fixed_mol, sanitize=False)
            if mol:
                print(f"✅ Succès avec fix_indigo_mol pour {source}")
        except Exception as e1:
            print(f"⚠️ Tentative INDIGO échouée: {e1}")
    
    # Strategy 2: Try with patch_molblock (notre fonction complexe)
    if mol is None:
        try:
            patched_mol = patch_molblock(mol_content)
            print(f"🔧 MOL patché avec patch_molblock pour {source}")
            mol = Chem.MolFromMolBlock(patched_mol, sanitize=False)
            if mol:
                print(f"✅ Succès avec patch_molblock pour {source}")
        except Exception as e2:
            print(f"⚠️ Tentative patch_molblock échouée: {e2}")
    
    # Strategy 3: Try direct parsing without sanitization
    if mol is None:
        try:
            mol = Chem.MolFromMolBlock(mol_content, sanitize=False)
            if mol:
                print(f"✅ Succès parsing direct pour {source}")
        except Exception as e3:
            print(f"⚠️ Tentative direct échouée: {e3}")
    
    # Strategy 4: Try with sanitization
    if mol is None:
        try:
            mol = Chem.MolFromMolBlock(mol_content, sanitize=True)
            if mol:
                print(f"✅ Succès avec sanitization pour {source}")
        except Exception as e4:
            print(f"⚠️ Tentative sanitize échouée: {e4}")
    
    if mol is None:
        raise ValueError(f"Impossible de parser le MOL depuis {source}. Contenu: {mol_content[:200]}...")
    
    # Add hydrogens and generate 3D coordinates
    try:
        # Update property cache
        for atom in mol.GetAtoms():
            atom.UpdatePropertyCache(strict=False)
        
        # Add hydrogens carefully
        try:
            mol = Chem.AddHs(mol, addCoords=False)
        except Exception as e:
            print(f"⚠️ AddHs failed: {e}, continuing without explicit hydrogens")
        
        # Generate 3D coordinates
        mol = embed_molecule_with_3d(mol)
        
        # Convert to XYZ
        xyz = Chem.MolToXYZBlock(mol)
        
        return xyz
        
    except Exception as e:
        raise ValueError(f"Erreur génération 3D pour {source}: {str(e)}")

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
    Fix INDIGO MOL blocks for RDKit compatibility
    """
    lines = molblock.strip().splitlines()
    
    if not lines:
        return molblock
    
    # Fix INDIGO header
    if lines[0].startswith('-INDIGO-'):
        lines[0] = 'Molecule'
    
    # Ensure second line exists
    if len(lines) < 2:
        lines.insert(1, '')
    
    # Find and fix counts line  
    for i, line in enumerate(lines):
        if 'V2000' in line:
            # Extract numbers before V2000 and handle floats like "5."
            import re
            numbers = re.findall(r'\\d+\\.?\\d*', line.replace('V2000', '').strip())
            if len(numbers) >= 2:
                try:
                    atoms = int(float(numbers[0]))  # Convert "5." to 5
                    bonds = int(float(numbers[1]))  # Convert "5." to 5
                    # Create standard counts line with proper spacing
                    fixed_counts = f"{atoms:3d}{bonds:3d}  0  0  0  0  0  0  0  0999 V2000"
                    lines[i] = fixed_counts
                    print(f"🔧 Counts line: '{line}' → '{fixed_counts}'")
                except (ValueError, IndexError):
                    print(f"⚠️ Failed to parse counts line: '{line}'")
            break
    
    return '\\n'.join(lines) + '\\n'

# Example usage:
# molblock = patch_molblock(molblock)
# mol = Chem.MolFromMolBlock(molblock)


def fix_indigo_mol(molblock: str) -> str:
    """
    Version SIMPLE pour corriger spécifiquement les fichiers MOL INDIGO
    """
    lines = molblock.strip().split('\n')
    
    if len(lines) < 4:
        return molblock
    
    # Corriger le header (3 premières lignes)
    lines[0] = 'Molecule'
    lines[1] = '  IAM'
    lines[2] = ''
    
    # Corriger la ligne de comptage (ligne 3, index 3)
    counts_line = lines[3].strip()
    
    # Extraire le nombre d'atomes et de liaisons
    parts = counts_line.split()
    
    if len(parts) >= 2:
        try:
            num_atoms = int(parts[0])
            num_bonds = int(parts[1])
            
            # Reformater avec le bon espacement
            lines[3] = f"{num_atoms:3d}{num_bonds:3d}  0  0  0  0            999 V2000"
            
        except ValueError:
            pass
    
    return '\n'.join(lines)


from flask import render_template

@app.route('/dashboard')
def dashboard():
    return render_template('IAM_StatusDashboard.html')


@app.route('/predict_performance', methods=['POST'])
def predict_performance():
    """Endpoint pour prédiction de performance avec IAM_PerformancePredictor"""
    try:
        data = request.get_json()
        molecular_formula = data.get('molecular_formula', 'C1H1N1O1')
        density = data.get('density', 1.5)
        heat_formation = data.get('heat_formation', 0)
        
        # Import et utilisation du module existant
        sys.path.append('/home/lppou/IAM')
        from IAM_PerformancePredictor import IAM_PerformancePredictor
        
        predictor = IAM_PerformancePredictor()
        results = predictor.full_prediction(
            molecular_formula=molecular_formula,
            density=density,
            heat_formation=heat_formation
        )
        
        return jsonify({
            'success': True,
            'data': results,
            'message': 'Performance prediction completed'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Performance prediction error: {str(e)}',
            'details': traceback.format_exc()
        })


@app.route('/run_iam_workflow', methods=['POST'])
def run_iam_workflow():
    """Execute full IAM workflow: SMILES → XYZ → XTB → Results"""
    try:
        data = request.get_json()
        smiles = data.get('smiles', '').strip()
        name = data.get('name', 'molecule').strip()
        
        if not smiles:
            return jsonify({
                'success': False,
                'error': 'SMILES vide'
            })
        
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                results = full_molecule_workflow(smiles, name, tmpdir)
                
                # Lire le fichier XYZ généré
                xyz_path = results.get('XYZ path')
                xyz_content = ''
                if xyz_path and os.path.exists(xyz_path):
                    with open(xyz_path, 'r') as f:
                        xyz_content = f.read()
                
                return jsonify({
                    'success': True,
                    'iam_results': results,
                    'xyz_content': xyz_content,
                    'message': f'Workflow IAM complet réussi pour {smiles}'
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Erreur workflow IAM: {str(e)}',
                    'details': traceback.format_exc()
                })
                
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur endpoint IAM: {str(e)}',
            'details': traceback.format_exc()
        })


@app.route('/debug_mol_parsing', methods=['POST'])
def debug_mol_parsing():
    """Debug endpoint for MOL parsing issues"""
    try:
        data = request.get_json()
        mol_content = data.get('mol_content', '')
        
        if not mol_content.strip():
            return jsonify({
                'success': False,
                'error': 'Contenu MOL vide'
            })
        
        debug_info = {
            'original_length': len(mol_content),
            'lines_count': len(mol_content.splitlines()),
            'first_line': mol_content.splitlines()[0] if mol_content.splitlines() else '',
            'contains_v2000': 'V2000' in mol_content,
            'contains_indigo': 'INDIGO' in mol_content.upper(),
            'contains_m_end': 'M  END' in mol_content
        }
        
        # Try our patch function
        try:
            patched = patch_molblock(mol_content)
            debug_info['patch_success'] = True
            debug_info['patched_preview'] = patched[:200]
            
            # Try RDKit parsing
            mol = Chem.MolFromMolBlock(patched, sanitize=False)
            if mol:
                debug_info['rdkit_success'] = True
                debug_info['atom_count'] = mol.GetNumAtoms()
            else:
                debug_info['rdkit_success'] = False
                debug_info['rdkit_error'] = 'RDKit returned None'
                
        except Exception as e:
            debug_info['patch_success'] = False
            debug_info['patch_error'] = str(e)
        
        return jsonify({
            'success': True,
            'debug_info': debug_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Debug error: {str(e)}',
            'details': traceback.format_exc()
        })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
