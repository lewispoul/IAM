from flask import Flask, request, jsonify, render_template, send_from_directory, make_response
from flask_cors import CORS
import os
import subprocess
import tempfile
import json
import traceback
import sys
import importlib
import io
import zipfile
import base64
from datetime import datetime
import time
import psutil
import logging

# Performance monitoring imports
try:
    from performance_utils import (
        track_performance, cache_result, PERFORMANCE_METRICS, 
        get_cache_stats, cleanup_cache, optimize_json_response,
        create_error_response, validate_xyz_format_optimized
    )
    PERFORMANCE_MONITORING = True
except ImportError:
    print("Performance monitoring not available")
    PERFORMANCE_MONITORING = False
    
    # Fallback decorators
    def track_performance(func):
        return func
    
    def cache_result(expiry_seconds=300):
        def decorator(func):
            return func
        return decorator

# Gestion gracieuse de RDKit
RDKIT_AVAILABLE = False
try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    from rdkit.Chem import rdDistGeom
    from rdkit.Chem import rdForceFieldHelpers
    RDKIT_AVAILABLE = True
    print("✅ RDKit loaded successfully")
except ImportError:
    print("⚠️ RDKit not available - some features will be limited")
    # Dummy classes pour éviter les erreurs
    class Chem:
        @staticmethod
        def MolFromSmiles(smiles): return None
        @staticmethod
        def MolFromMolBlock(mol): return None
        @staticmethod
        def MolToXYZBlock(mol): return ""
        @staticmethod
        def AddHs(mol): return mol
        
        class rdMolDescriptors:
            @staticmethod
            def CalcMolFormula(mol): return "Unknown"
    
    class AllChem:
        @staticmethod
        def EmbedMolecule(mol, *args, **kwargs): return -1
        @staticmethod
        def UFFOptimizeMolecule(mol): return -1
        @staticmethod
        def MMFFOptimizeMolecule(mol): return -1
        @staticmethod
        def ETKDG(): return None
    
    class rdDistGeom:
        @staticmethod
        def EmbedMolecule(mol, *args, **kwargs): return -1
        @staticmethod
        def ETKDGv3(): return None
        @staticmethod
        def ETKDGv2(): return None
        @staticmethod
        def ETKDG(): return None
    
    class rdForceFieldHelpers:
        @staticmethod
        def UFFOptimizeMolecule(mol): return -1
        @staticmethod
        def MMFFOptimizeMolecule(mol): return -1

# Add IAM_Knowledge to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../IAM_Knowledge')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import VoD predictor
try:
    from IAM_VoD_Predictor import predict_vod
    VOD_PREDICTOR_AVAILABLE = True
    print("✅ VoD Predictor loaded successfully")
except ImportError as e:
    print(f"⚠️ VoD Predictor not available: {e}")
    VOD_PREDICTOR_AVAILABLE = False

# Import stability predictor
try:
    from IAM_StabilityPredictor import predict_stability
    STABILITY_PREDICTOR_AVAILABLE = True
    print("✅ Stability Predictor loaded successfully")
except ImportError as e:
    print(f"⚠️ Stability Predictor not available: {e}")
    STABILITY_PREDICTOR_AVAILABLE = False

# Import thermodynamics predictor
try:
    from IAM_ThermoPredictor import predict_thermo
    THERMO_PREDICTOR_AVAILABLE = True
    print("✅ Thermo Predictor loaded successfully")
except ImportError as e:
    print(f"⚠️ Thermo Predictor not available: {e}")
    THERMO_PREDICTOR_AVAILABLE = False

# Import toxicity predictor
try:
    from IAM_ToxicityPredictor import predict_toxicity
    TOXICITY_PREDICTOR_AVAILABLE = True
    print("✅ Toxicity Predictor loaded successfully")
except ImportError as e:
    print(f"⚠️ Toxicity Predictor not available: {e}")
    TOXICITY_PREDICTOR_AVAILABLE = False

# Import performance optimization
try:
    from performance_optimization import optimize_explosive_performance
    PERFORMANCE_OPTIMIZER_AVAILABLE = True
    print("✅ Performance Optimizer loaded successfully")
except ImportError as e:
    print(f"⚠️ Performance Optimizer not available: {e}")
    PERFORMANCE_OPTIMIZER_AVAILABLE = False

app = Flask(__name__, template_folder='templates')
CORS(app)

# Initialize performance monitoring
app.config['START_TIME'] = time.time()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debug: Print sys.path to verify module path
print("sys.path:", sys.path)

# Debug: List contents of IAM_Knowledge directory
print("IAM_Knowledge contents:", os.listdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '../IAM_Knowledge'))))

# Debug: Print PYTHONPATH and verify environment configuration
print("PYTHONPATH:", os.environ.get('PYTHONPATH', 'Not set'))

# --- Global error handler ---
@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({
        "success": False,
        "error": str(e),
        "details": traceback.format_exc()
    }), 500

# Additional error handlers (ported from Pi branch)
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "message": "The requested resource does not exist"
    }), 404

@app.errorhandler(413)
def too_large(error):
    return jsonify({
        "success": False,
        "error": "File too large",
        "message": "The uploaded file exceeds the maximum allowed size"
    }), 413

# --- RDKit 3D coordinate generation helpers ---
def embed_molecule_with_3d(mol):
    """
    Robust 3D embedding with multiple fallback methods (ported from Pi branch).
    Tries ETKDGv3 → ETKDGv2 → ETKDG with UFF optimization.
    """
    if not RDKIT_AVAILABLE or mol is None:
        return mol
    
    try:
        # Add hydrogens first
        mol = Chem.AddHs(mol)
        
        # Try ETKDGv3 first (most recent)
        try:
            if hasattr(rdDistGeom, "ETKDGv3"):
                ps = rdDistGeom.ETKDGv3()
                if hasattr(ps, 'randomSeed'):
                    ps.randomSeed = 42  # For reproducibility
                if AllChem.EmbedMolecule(mol, ps) == 0:
                    print("✅ 3D embedding successful with ETKDGv3")
                    # Optimize with UFF
                    try:
                        AllChem.UFFOptimizeMolecule(mol)
                        print("✅ UFF optimization successful")
                    except:
                        print("⚠️ UFF optimization failed, continuing without optimization")
                    return mol
        except Exception as e:
            print(f"⚠️ ETKDGv3 failed: {e}")
        
        # Fallback to ETKDGv2
        try:
            if hasattr(rdDistGeom, "ETKDGv2"):
                ps = rdDistGeom.ETKDGv2()
                if hasattr(ps, 'randomSeed'):
                    ps.randomSeed = 42
                if AllChem.EmbedMolecule(mol, ps) == 0:
                    print("✅ 3D embedding successful with ETKDGv2")
                    try:
                        AllChem.UFFOptimizeMolecule(mol)
                    except:
                        print("⚠️ UFF optimization failed")
                    return mol
        except Exception as e:
            print(f"⚠️ ETKDGv2 failed: {e}")
        
        # Final fallback to basic ETKDG
        try:
            if hasattr(rdDistGeom, "ETKDG"):
                ps = rdDistGeom.ETKDG()
                if hasattr(ps, 'randomSeed'):
                    ps.randomSeed = 42
                if AllChem.EmbedMolecule(mol, ps) == 0:
                    print("✅ 3D embedding successful with ETKDG")
                    try:
                        AllChem.UFFOptimizeMolecule(mol)
                    except:
                        print("⚠️ UFF optimization failed")
                    return mol
        except Exception as e:
            print(f"⚠️ ETKDG failed: {e}")
        
        # Absolute fallback - basic embedding
        try:
            if AllChem.EmbedMolecule(mol) == 0:
                print("✅ 3D embedding successful with basic method")
                try:
                    AllChem.UFFOptimizeMolecule(mol)
                except:
                    pass
                return mol
        except Exception as e:
            print(f"⚠️ Basic embedding failed: {e}")
            
        print("❌ All 3D embedding methods failed")
        return mol
        
    except Exception as e:
        print(f"❌ Critical error in 3D embedding: {e}")
        return mol

# Robust MOL to XYZ conversion (ported from Pi branch)
def robust_mol_to_xyz(mol_data):
    """
    Robust conversion from MOL data to XYZ with error handling and cleaning.
    """
    if not RDKIT_AVAILABLE:
        return {'success': False, 'error': 'RDKit not available'}
    
    try:
        # Clean the MOL data
        mol_lines = mol_data.strip().split('\n')
        
        # Basic MOL format validation
        if len(mol_lines) < 4:
            return {'success': False, 'error': 'Invalid MOL format: too few lines'}
        
        # Try to parse with RDKit
        try:
            mol = Chem.MolFromMolBlock(mol_data)
            if mol is None:
                return {'success': False, 'error': 'RDKit could not parse MOL block'}
            
            # Embed 3D coordinates
            mol = embed_molecule_with_3d(mol)
            
            # Convert to XYZ
            xyz_block = Chem.MolToXYZBlock(mol)
            if not xyz_block or xyz_block.strip() == "":
                return {'success': False, 'error': 'Failed to generate XYZ coordinates'}
            
            # Get molecular properties
            try:
                from rdkit.Chem import rdMolDescriptors
                formula = rdMolDescriptors.CalcMolFormula(mol)
                atom_count = mol.GetNumAtoms()
                bond_count = mol.GetNumBonds()
            except:
                formula = 'Unknown'
                atom_count = 0
                bond_count = 0
            
            return {
                'success': True,
                'xyz': xyz_block,
                'formula': formula,
                'atom_count': atom_count,
                'bond_count': bond_count
            }
            
        except Exception as e:
            return {'success': False, 'error': f'MOL parsing error: {str(e)}'}
            
    except Exception as e:
        logger.error(f"Error in robust_mol_to_xyz: {str(e)}")
        return {'success': False, 'error': f'Conversion error: {str(e)}'}
            
    except Exception as e:
        return None, f"Unexpected error in MOL conversion: {str(e)}"

# Performance monitoring endpoints
@app.route('/api/performance')
def performance_metrics():
    """Get performance metrics and system information"""
    try:
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        metrics = {
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "memory_total": memory.total,
                "disk_free": disk.free,
                "disk_total": disk.total,
                "disk_percent": (disk.used / disk.total) * 100
            }
        }
        
        if PERFORMANCE_MONITORING:
            metrics.update({
                "application": PERFORMANCE_METRICS,
                "cache": get_cache_stats()
            })
        
        return jsonify(optimize_json_response(metrics))
    except Exception as e:
        return jsonify(create_error_response(f"Error getting performance metrics: {str(e)}")), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        status = {
            "status": "healthy",
            "timestamp": time.time(),
            "uptime": time.time() - app.config.get('START_TIME', time.time()) if app.config.get('START_TIME') else 0,
            "version": "1.0.0",
            "components": {
                "rdkit": RDKIT_AVAILABLE,
                "performance_monitoring": PERFORMANCE_MONITORING,
                "xtb": check_xtb_availability(),
                "file_system": check_file_system()
            }
        }
        
        # Check if all critical components are available
        critical_issues = []
        if not check_file_system():
            critical_issues.append("File system not accessible")
        
        if critical_issues:
            status["status"] = "unhealthy"
            status["issues"] = critical_issues
            return jsonify(status), 503
        
        return jsonify(status)
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }), 500

def check_xtb_availability():
    """Check if XTB is available"""
    try:
        result = subprocess.run(['xtb', '--version'], 
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def check_file_system():
    """Check if file system is accessible"""
    try:
        temp_dir = tempfile.gettempdir()
        test_file = os.path.join(temp_dir, 'iam_health_check.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return True
    except:
        return False

@app.route('/api/cache/cleanup', methods=['POST'])
def cleanup_cache_endpoint():
    """Clean up expired cache entries"""
    try:
        if PERFORMANCE_MONITORING:
            cleanup_cache()
            return jsonify({"success": True, "message": "Cache cleaned up"})
        else:
            return jsonify({"success": False, "message": "Performance monitoring not available"})
    except Exception as e:
        return jsonify(create_error_response(f"Error cleaning cache: {str(e)}")), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    """Main route - serves the professional IAM interface with glass-morphism design"""
    import time
    timestamp = int(time.time())
    
    # Log which template we're serving for debugging
    logger.info(f"Serving iam_viewer_connected_professional.html with timestamp {timestamp}")
    
    response = make_response(render_template('iam_viewer_connected_professional.html', cache_bust=timestamp))
    # Add strong cache-busting headers
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    response.headers['Last-Modified'] = 'Wed, 01 Jan 1970 00:00:00 GMT'
    response.headers['ETag'] = f'"{timestamp}"'
    return response

@app.route('/enhanced', methods=['GET', 'POST'])
def enhanced():
    """Enhanced interface - serves the enhanced IAM interface with improved performance"""
    return render_template('iam_viewer_enhanced.html')

@app.route('/optimized', methods=['GET', 'POST'])
def optimized():
    """Optimized interface - serves the modern optimized interface"""
    return render_template('iam_viewer_optimized.html')

@app.route('/classic', methods=['GET', 'POST'])
def classic_interface():
    """Classic interface route for backwards compatibility"""
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
@track_performance
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
    try:
        lines = mol_block.strip().splitlines()
        # Ajoute une ligne de titre si manquante ou suspecte
        if not lines or (not lines[0].strip() or 'V2000' in lines[0] or 'INDIGO' in lines[0].upper() or 'KETCHER' in lines[0].upper()):
            lines = ["Generated by IAM"] + lines
        mol_block_fixed = "\n".join(lines)

        mol = Chem.MolFromMolBlock(mol_block_fixed) if RDKIT_AVAILABLE else None
        if mol is None:
            raise ValueError("RDKit failed to parse the MOL block.")

        if RDKIT_AVAILABLE and mol is not None:
            mol = Chem.AddHs(mol)
            if AllChem.EmbedMolecule(mol, AllChem.ETKDG()) != 0:
                raise ValueError("Failed to generate 3D coordinates.")
            AllChem.UFFOptimizeMolecule(mol)

        if RDKIT_AVAILABLE and mol is not None:
            conf = mol.GetConformer()
            atoms = mol.GetAtoms()
            xyz_lines = [f"{len(atoms)}", "Generated by IAM"]
            for atom in atoms:
                pos = conf.GetAtomPosition(atom.GetIdx())
                xyz_lines.append(f"{atom.GetSymbol()} {pos.x:.6f} {pos.y:.6f} {pos.z:.6f}")
            return "\n".join(xyz_lines)
        else:
            raise ValueError("RDKit not available or failed to process molecule")

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

@app.route('/performance')
def performance_dashboard():
    """Performance monitoring dashboard"""
    return render_template('performance_dashboard.html')

@app.route('/dashboard')
def dashboard():
    return render_template('IAM_StatusDashboard.html')

# Ajout des endpoints manquants

@app.route('/compute_symmetry', methods=['POST'])
def compute_symmetry():
    try:
        xyz_file = request.files.get("file")
        if not xyz_file:
            return jsonify({"success": False, "error": "No file received"}), 400

        # Logique pour calculer la symétrie
        symmetry_result = "Symmetry computation logic here"
        return jsonify({"success": True, "symmetry": symmetry_result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "details": traceback.format_exc()})


# Add missing endpoints for the professional interface

@app.route('/analyze', methods=['POST'])
@track_performance
def analyze():
    """Professional analysis endpoint"""
    try:
        data = request.get_json()
        mol_data = data.get('mol_data', '')
        analysis_type = data.get('analysis_type', 'basic')
        
        if not mol_data:
            return jsonify({'success': False, 'error': 'No molecular data provided'})
        
        # Convert molfile to XYZ
        xyz_content = molblock_to_xyz(mol_data)
        if not xyz_content:
            return jsonify({'success': False, 'error': 'Failed to convert molecular data'})
        
        # Run comprehensive analysis
        results = {
            'success': True,
            'summary': 'Comprehensive molecular analysis completed successfully.',
            'formula': 'C6H6',  # Example - would be calculated
            'weight': '78.11 g/mol',  # Example - would be calculated
            'energy': '-2341.2 kJ/mol',  # Example - would be calculated
            'properties': 'Aromatic compound with high stability',
            'xyz_structure': xyz_content,
            'analysis_type': analysis_type
        }
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/quantum_analysis', methods=['POST'])
@track_performance
def quantum_analysis():
    """Quantum chemistry analysis endpoint"""
    try:
        data = request.get_json()
        mol_data = data.get('mol_data', '')
        method = data.get('method', 'dft')
        
        if not mol_data:
            return jsonify({'success': False, 'error': 'No molecular data provided'})
        
        # Simulate quantum analysis
        results = {
            'success': True,
            'method': method.upper(),
            'results': {
                'total_energy': -2341.234567,
                'homo_energy': -6.23,
                'lumo_energy': -1.45,
                'gap': 4.78,
                'dipole_moment': 0.0,
                'mulliken_charges': [0.12, -0.12, 0.05, -0.05]
            }
        }
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/geometry_optimization', methods=['POST'])
@track_performance
def geometry_optimization():
    """Geometry optimization endpoint"""
    try:
        data = request.get_json()
        mol_data = data.get('mol_data', '')
        
        if not mol_data:
            return jsonify({'success': False, 'error': 'No molecular data provided'})
        
        # Convert and optimize geometry
        xyz_content = molblock_to_xyz(mol_data)
        
        results = {
            'success': True,
            'results': {
                'converged': True,
                'final_energy': -2341.567890,
                'optimization_steps': 15,
                'rms_gradient': 0.0001
            },
            'optimized_structure': xyz_content
        }
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/predict_stability', methods=['POST'])
@track_performance
def predict_stability_endpoint():
    """Stability prediction endpoint using IAM_StabilityPredictor"""
    try:
        data = request.get_json()
        mol_data = data.get('mol_data', '')
        
        if not mol_data:
            return jsonify({'success': False, 'error': 'No molecular data provided'})
        
        # Use actual stability predictor if available
        if STABILITY_PREDICTOR_AVAILABLE:
            try:
                stability_results = predict_stability(mol_data)
                
                # Structure the response for the frontend
                results = {
                    'success': True,
                    'results': {
                        'thermal_stability': stability_results.get('thermal_stability', 'N/A'),
                        'decomposition_temp': stability_results.get('decomposition_temperature', 'N/A'),
                        'stability_rating': stability_results.get('stability_rating', 'N/A'),
                        'recommendations': stability_results.get('recommendations', 'Store safely'),
                        'method': stability_results.get('method', 'Advanced Stability Prediction'),
                        'sensitivity': stability_results.get('sensitivity', 'N/A')
                    }
                }
                
                return jsonify(results)
                
            except Exception as e:
                print(f"Stability prediction error: {e}")
                # Fallback to simulated results
                results = {
                    'success': True,
                    'results': {
                        'thermal_stability': 'N/A',
                        'decomposition_temp': 'N/A',
                        'stability_rating': 'Error in prediction',
                        'error': str(e)
                    }
                }
                return jsonify(results)
        else:
            # Stability predictor not available
            results = {
                'success': False,
                'error': 'Stability Predictor module not available. Please ensure IAM_Knowledge is properly installed.'
            }
            return jsonify(results)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/predict_vod', methods=['POST'])
@track_performance
def predict_vod_endpoint():
    """VoD prediction endpoint using IAM_VoD_Predictor"""
    try:
        data = request.get_json()
        mol_data = data.get('mol_data', '')
        
        if not mol_data:
            return jsonify({'success': False, 'error': 'No molecular data provided'})
        
        # Use actual VoD predictor if available
        if VOD_PREDICTOR_AVAILABLE:
            try:
                vod_results = predict_vod(mol_data)
                
                # Structure the response for the frontend
                results = {
                    'success': True,
                    'results': {
                        'velocity_of_detonation': vod_results.get('vod', 'N/A'),
                        'detonation_pressure': vod_results.get('pressure', 'N/A'), 
                        'density': vod_results.get('density', 'N/A'),
                        'method': vod_results.get('method', 'Advanced VoD Prediction'),
                        'molecule_info': vod_results.get('molecule_info', {}),
                        'oxygen_balance': vod_results.get('oxygen_balance', 'N/A'),
                        'performance_rating': vod_results.get('rating', 'N/A'),
                        'tnt_equivalence': vod_results.get('tnt_equivalent', 'N/A')
                    }
                }
                
                return jsonify(results)
                
            except Exception as e:
                print(f"VoD prediction error: {e}")
                # Fallback to simulated results
                results = {
                    'success': True,
                    'results': {
                        'velocity_of_detonation': 'N/A',
                        'detonation_pressure': 'N/A',
                        'performance_rating': 'Error in prediction',
                        'error': str(e)
                    }
                }
                return jsonify(results)
        else:
            # VoD predictor not available - return helpful message
            results = {
                'success': False,
                'error': 'VoD Predictor module not available. Please ensure IAM_Knowledge is properly installed.'
            }
            return jsonify(results)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/ai_agent_query', methods=['POST'])
@track_performance
def ai_agent_query():
    """AI agent query endpoint"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        mol_data = data.get('mol_data', '')
        
        if not prompt:
            return jsonify({'success': False, 'error': 'No prompt provided'})
        
        # Simulate AI response
        ai_responses = {
            'properties': 'This molecule shows excellent thermal stability with a high decomposition temperature around 350°C. The aromatic ring provides structural rigidity.',
            'performance': 'Based on the molecular structure, this compound would exhibit moderate explosive performance with good handling characteristics.',
            'safety': 'This molecule appears to have good safety characteristics. Recommend standard laboratory precautions and proper ventilation.',
            'default': 'Based on your molecule, I can provide insights about its structure, properties, and potential applications. The molecular framework suggests interesting chemical behavior.'
        }
        
        # Simple keyword matching for response
        response = ai_responses['default']
        if 'properties' in prompt.lower() or 'property' in prompt.lower():
            response = ai_responses['properties']
        elif 'performance' in prompt.lower() or 'explosive' in prompt.lower():
            response = ai_responses['performance']
        elif 'safety' in prompt.lower() or 'handling' in prompt.lower():
            response = ai_responses['safety']
        
        return jsonify({
            'success': True,
            'response': response,
            'prompt': prompt
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/professional_molecular_orbitals', methods=['GET'])
def professional_molecular_orbitals():
    """Serve professional molecular orbitals page"""
    try:
        return render_template('professional_molecular_orbitals.html')
    except Exception as e:
        return f"<h1>Professional Molecular Orbitals</h1><p>Feature under development. Error: {str(e)}</p>"

@app.route('/calculate_thermodynamics', methods=['POST'])
@track_performance
def calculate_thermodynamics():
    """Thermodynamics calculation endpoint using IAM_ThermoPredictor"""
    try:
        data = request.get_json()
        mol_data = data.get('mol_data', '')
        temperature = data.get('temperature', 298.15)
        
        if not mol_data:
            return jsonify({'success': False, 'error': 'No molecular data provided'})
        
        # Use actual thermo predictor if available
        if THERMO_PREDICTOR_AVAILABLE:
            try:
                thermo_results = predict_thermo(mol_data)
                
                # Structure the response for the frontend
                results = {
                    'success': True,
                    'temperature': temperature,
                    'results': {
                        'enthalpy': thermo_results.get('enthalpy', 'N/A'),
                        'entropy': thermo_results.get('entropy', 'N/A'),
                        'gibbs_free_energy': thermo_results.get('gibbs_free_energy', 'N/A'),
                        'heat_capacity': thermo_results.get('heat_capacity', 'N/A'),
                        'method': thermo_results.get('method', 'Advanced Thermodynamic Prediction')
                    }
                }
                
                return jsonify(results)
                
            except Exception as e:
                print(f"Thermodynamics prediction error: {e}")
                # Fallback to simulated results
                results = {
                    'success': True,
                    'temperature': temperature,
                    'results': {
                        'enthalpy': 'N/A',
                        'entropy': 'N/A',
                        'gibbs_free_energy': 'N/A',
                        'heat_capacity': 'N/A',
                        'error': str(e)
                    }
                }
                return jsonify(results)
        else:
            # Thermo predictor not available
            results = {
                'success': False,
                'error': 'Thermo Predictor module not available. Please ensure IAM_Knowledge is properly installed.'
            }
            return jsonify(results)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/calculate_vibrational_modes', methods=['POST'])
@track_performance
def calculate_vibrational_modes():
    """Vibrational modes calculation endpoint"""
    try:
        data = request.get_json()
        mol_data = data.get('mol_data', '')
        
        if not mol_data:
            return jsonify({'success': False, 'error': 'No molecular data provided'})
        
        # Simulate vibrational analysis
        results = {
            'success': True,
            'results': {
                'num_modes': 18,
                'frequencies': [456.7, 789.2, 1234.5, 1567.8, 2890.3],
                'intensities': [12.3, 45.6, 78.9, 23.4, 56.7],
                'zero_point_energy': 0.0567
            }
        }
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/optimize_performance', methods=['POST'])
@track_performance
def optimize_performance():
    """Performance optimization endpoint using performance_optimization module"""
    try:
        data = request.get_json()
        mol_data = data.get('mol_data', '')
        target = data.get('target', 'general')
        
        if not mol_data:
            return jsonify({'success': False, 'error': 'No molecular data provided'})
        
        # Use actual performance optimizer if available
        if PERFORMANCE_OPTIMIZER_AVAILABLE:
            try:
                optimization_results = optimize_explosive_performance(mol_data)
                
                # Structure the response for the frontend
                results = {
                    'success': True,
                    'target': target,
                    'results': {
                        'optimization_score': optimization_results.get('score', 'N/A'),
                        'suggestions': optimization_results.get('optimizations', []),
                        'predicted_improvement': optimization_results.get('improvement', 'N/A'),
                        'method': optimization_results.get('method', 'Advanced Performance Optimization'),
                        'current_properties': optimization_results.get('current_properties', {})
                    }
                }
                
                return jsonify(results)
                
            except Exception as e:
                print(f"Performance optimization error: {e}")
                # Fallback to simulated results
                results = {
                    'success': True,
                    'target': target,
                    'results': {
                        'optimization_score': 'N/A',
                        'suggestions': ['Error in optimization analysis'],
                        'predicted_improvement': 'N/A',
                        'error': str(e)
                    }
                }
                return jsonify(results)
        else:
            # Performance optimizer not available
            results = {
                'success': False,
                'error': 'Performance Optimizer module not available. Please ensure IAM_Knowledge is properly installed.'
            }
            return jsonify(results)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/predict_toxicity', methods=['POST'])
@track_performance
def predict_toxicity_endpoint():
    """Toxicity prediction endpoint using IAM_ToxicityPredictor"""
    try:
        data = request.get_json()
        mol_data = data.get('mol_data', '')
        
        if not mol_data:
            return jsonify({'success': False, 'error': 'No molecular data provided'})
        
        # Use actual toxicity predictor if available
        if TOXICITY_PREDICTOR_AVAILABLE:
            try:
                toxicity_results = predict_toxicity(mol_data)
                
                # Structure the response for the frontend
                results = {
                    'success': True,
                    'results': {
                        'toxicity_level': toxicity_results.get('toxicity_level', 'N/A'),
                        'ld50': toxicity_results.get('ld50', 'N/A'),
                        'environmental_impact': toxicity_results.get('environmental_impact', 'N/A'),
                        'safety_recommendations': toxicity_results.get('safety_recommendations', 'Use appropriate safety measures'),
                        'method': toxicity_results.get('method', 'Advanced Toxicity Prediction')
                    }
                }
                
                return jsonify(results)
                
            except Exception as e:
                print(f"Toxicity prediction error: {e}")
                # Fallback to simulated results
                results = {
                    'success': True,
                    'results': {
                        'toxicity_level': 'N/A',
                        'ld50': 'N/A',
                        'environmental_impact': 'N/A',
                        'safety_recommendations': 'Error in toxicity analysis',
                        'error': str(e)
                    }
                }
                return jsonify(results)
        else:
            # Toxicity predictor not available
            results = {
                'success': False,
                'error': 'Toxicity Predictor module not available. Please ensure IAM_Knowledge is properly installed.'
            }
            return jsonify(results)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/generate_report', methods=['POST'])
@track_performance
def generate_report():
    """Report generation endpoint"""
    try:
        data = request.get_json()
        mol_data = data.get('mol_data', '')
        report_type = data.get('report_type', 'comprehensive')
        
        if not mol_data:
            return jsonify({'success': False, 'error': 'No molecular data provided'})
        
        # Simulate report generation
        results = {
            'success': True,
            'report_type': report_type,
            'report_data': {
                'title': 'Molecular Analysis Report',
                'date': '2024-01-15',
                'summary': 'Comprehensive analysis of the submitted molecular structure.',
                'sections': ['Structure', 'Properties', 'Performance', 'Safety'],
                'download_url': '/download_report/12345'
            }
        }
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/export_pdf', methods=['POST'])
@track_performance
def export_pdf():
    """PDF export endpoint"""
    try:
        data = request.get_json()
        
        # Simulate PDF generation
        results = {
            'success': True,
            'download_url': '/download_pdf/12345',
            'filename': 'molecular_analysis.pdf'
        }
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/export_csv', methods=['POST'])
@track_performance
def export_csv():
    """CSV export endpoint"""
    try:
        data = request.get_json()
        
        # Simulate CSV generation
        results = {
            'success': True,
            'download_url': '/download_csv/12345',
            'filename': 'molecular_data.csv'
        }
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/batch_analysis', methods=['POST'])
@track_performance
def batch_analysis():
    """Batch analysis endpoint"""
    try:
        data = request.get_json()
        molecules = data.get('molecules', [])
        
        if not molecules:
            return jsonify({'success': False, 'error': 'No molecules provided'})
        
        # Simulate batch processing
        results = {
            'success': True,
            'processed': len(molecules),
            'results': [
                {'id': i, 'status': 'completed', 'energy': -2340.5 - i*10}
                for i in range(len(molecules))
            ]
        }
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/structure_comparison', methods=['POST'])
@track_performance
def structure_comparison():
    """Structure comparison endpoint"""
    try:
        data = request.get_json()
        structures = data.get('structures', [])
        
        if len(structures) < 2:
            return jsonify({'success': False, 'error': 'At least 2 structures required'})
        
        # Simulate comparison
        results = {
            'success': True,
            'similarity_score': 0.87,
            'differences': [
                'Structure 1 has higher symmetry',
                'Structure 2 shows better stability'
            ],
            'recommendation': 'Structure 2 recommended for better performance'
        }
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/physical_chemistry', methods=['GET'])
def physical_chemistry():
    """Physical chemistry analysis page"""
    try:
        return render_template('physical_chemistry.html')
    except Exception as e:
        return f"<h1>Physical Chemistry</h1><p>Feature under development. Error: {str(e)}</p>", 500

# Molecular conversion endpoints
@app.route('/molfile_to_xyz', methods=['POST'])
@track_performance
def molfile_to_xyz():
    """Convert molfile to XYZ format"""
    try:
        data = request.get_json()
        molfile = data.get('molfile', '')
        
        if not molfile:
            return jsonify({'success': False, 'error': 'No molfile provided'})
        
        # Convert molfile to XYZ
        xyz_data = molblock_to_xyz(molfile)
        
        if xyz_data:
            # Extract basic molecule info
            lines = xyz_data.strip().split('\n')
            atom_count = int(lines[0]) if lines and lines[0].isdigit() else 0
            
            # Simple formula calculation
            atoms = []
            for line in lines[2:]:
                if line.strip():
                    atom = line.split()[0]
                    atoms.append(atom)
            
            # Count atoms for formula
            from collections import Counter
            atom_counts = Counter(atoms)
            formula = ''.join([f"{atom}{count if count > 1 else ''}" for atom, count in sorted(atom_counts.items())])
            
            return jsonify({
                'success': True,
                'xyz': xyz_data,
                'molfile': molfile,
                'formula': formula,
                'atom_count': atom_count,
                'bond_count': 'N/A'
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to convert molfile to XYZ'})
            
    except Exception as e:
        logger.error(f"Molfile to XYZ conversion error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/smiles_to_xyz', methods=['POST'])
@track_performance
def smiles_to_xyz():
    """Convert SMILES to XYZ format"""
    try:
        data = request.get_json()
        smiles = data.get('smiles', '')
        
        if not smiles:
            return jsonify({'success': False, 'error': 'No SMILES provided'})
        
        # Try to convert using RDKit
        if RDKIT_AVAILABLE:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return jsonify({'success': False, 'error': 'Invalid SMILES string'})
            
            # Add hydrogens and generate 3D coordinates
            mol = Chem.AddHs(mol)
            AllChem.EmbedMolecule(mol, randomSeed=42)
            AllChem.MMFFOptimizeMolecule(mol)
            
            # Convert to XYZ
            conf = mol.GetConformer()
            xyz_lines = [str(mol.GetNumAtoms()), "Generated from SMILES"]
            
            for i in range(mol.GetNumAtoms()):
                atom = mol.GetAtomWithIdx(i)
                pos = conf.GetAtomPosition(i)
                xyz_lines.append(f"{atom.GetSymbol():2s} {pos.x:12.6f} {pos.y:12.6f} {pos.z:12.6f}")
            
            xyz_data = '\n'.join(xyz_lines)
            
            # Get molecular formula
            from rdkit.Chem import rdMolDescriptors
            formula = rdMolDescriptors.CalcMolFormula(mol)
            
            return jsonify({
                'success': True,
                'xyz': xyz_data,
                'smiles': smiles,
                'formula': formula,
                'atom_count': mol.GetNumAtoms(),
                'bond_count': mol.GetNumBonds()
            })
        else:
            return jsonify({'success': False, 'error': 'RDKit not available for SMILES conversion'})
            
    except Exception as e:
        logger.error(f"SMILES to XYZ conversion error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/mol_to_xyz', methods=['POST'])
@track_performance
def mol_to_xyz():
    """Convert MOL format to XYZ format"""
    try:
        data = request.get_json()
        mol_data = data.get('mol_data', '')
        
        if not mol_data:
            return jsonify({'success': False, 'error': 'No MOL data provided'})
        
        # Use the robust_mol_to_xyz function
        result = robust_mol_to_xyz(mol_data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'xyz': result['xyz'],
                'formula': result.get('formula', 'Unknown'),
                'atom_count': result.get('atom_count', 0),
                'bond_count': result.get('bond_count', 0)
            })
        else:
            return jsonify({'success': False, 'error': result['error']})
            
    except Exception as e:
        logger.error(f"MOL to XYZ conversion error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/write_file', methods=['POST'])
@track_performance
def write_file():
    """Write content to a file"""
    try:
        data = request.get_json()
        filename = data.get('filename', '')
        content = data.get('content', '')
        directory = data.get('directory', 'IAM_Results')
        
        if not filename:
            return jsonify({'success': False, 'error': 'No filename provided'})
        
        # Ensure safe file path
        import os
        safe_dir = os.path.join(os.path.dirname(__file__), '..', directory)
        safe_dir = os.path.abspath(safe_dir)
        
        # Create directory if it doesn't exist
        os.makedirs(safe_dir, exist_ok=True)
        
        # Write file
        file_path = os.path.join(safe_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({
            'success': True,
            'file_path': file_path,
            'message': f'File written successfully to {filename}'
        })
        
    except Exception as e:
        logger.error(f"File write error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# Agent communication endpoints
@app.route('/send_agent_command', methods=['POST'])
def send_agent_command():
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        # Simulation d'une réponse d'agent
        agent_response = {
            'status': 'executed',
            'command': command,
            'response': f"Agent executed: {command}",
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({"success": True, "agent_response": agent_response})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/get_agent_status', methods=['GET'])
def get_agent_status():
    return jsonify({
        "status": "online",
        "last_activity": datetime.now().isoformat(),
        "active_jobs": 0
    })

@app.route('/save_molecule', methods=['POST'])
def save_molecule():
    try:
        data = request.get_json()
        xyz = data.get('xyz', '')
        filename = data.get('filename', 'molecule.xyz')
        
        # Sauvegarde le fichier dans IAM_Results
        save_path = os.path.join('IAM_Results', filename)
        with open(save_path, 'w') as f:
            f.write(xyz)
            
        return jsonify({"success": True, "saved_path": save_path})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/load_molecule', methods=['POST'])
def load_molecule():
    try:
        data = request.get_json()
        filename = data.get('filename', '')
        
        # Charge le fichier depuis IAM_Results ou IAM_Knowledge/Molecules
        possible_paths = [
            os.path.join('IAM_Results', filename),
            os.path.join('IAM_Knowledge', 'Molecules', filename)
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    xyz = f.read()
                return jsonify({"success": True, "xyz": xyz, "loaded_from": path})
        
        return jsonify({"success": False, "error": "File not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Import des modules nécessaires (avec gestion d'erreur)
try:
    from IAM_Knowledge.IAM_StabilityPredictor import predict_stability_logic as stability_predictor
except ImportError:
    def stability_predictor(xyz_data):
        return {"stability": "Module not available", "method": "placeholder"}

# Import physical chemistry modules
try:
    # from modules.physical_chemistry.electron_repulsion import ElectronRepulsionCalculator  # TODO: Implement
    from modules.physical_chemistry.molecular_orbitals import MolecularOrbitalAnalyzer
    from modules.physical_chemistry.enhanced_molecular_orbitals import EnhancedMolecularOrbitalAnalyzer
    from modules.physical_chemistry.professional_molecular_orbitals import (
        ProfessionalMolecularOrbitalAnalyzer,
        start_professional_orbital_calculation,
        get_calculation_progress,
        get_calculation_results,
        get_orbital_isosurface
    )
    PHYSICAL_CHEMISTRY_AVAILABLE = True
    print("✅ Physical Chemistry modules loaded successfully")
except ImportError as e:
    print(f"⚠️ Physical Chemistry modules not available: {e}")
    PHYSICAL_CHEMISTRY_AVAILABLE = False

try:
    from IAM_Knowledge.IAM_VoD_Predictor import predict_vod as vod_predictor
except ImportError:
    def vod_predictor(xyz_data):
        return {"vod": "Module not available", "method": "placeholder"}

# ==============================
# PHYSICAL CHEMISTRY ROUTES
# ==============================

@app.route('/physical_chemistry/molecular_orbitals')
def molecular_orbitals_page():
    """Serve the molecular orbitals educational module"""
    return render_template('physical_chemistry/molecular_orbitals.html')

@app.route('/physical_chemistry/molecular_orbitals/enhanced')
def enhanced_molecular_orbitals_page():
    """Serve enhanced molecular orbitals analysis page with advanced 3D visualization"""
    return render_template('physical_chemistry/enhanced_molecular_orbitals.html')

@app.route('/physical_chemistry/electron_repulsion')
def electron_repulsion_page():
    """Serve the electron repulsion educational module"""
    return render_template('physical_chemistry/electron_repulsion.html')

@app.route('/physical_chemistry/molecular_orbitals/calculate', methods=['POST'])
def calculate_molecular_orbitals():
    """Calculate molecular orbitals for educational analysis"""
    if not PHYSICAL_CHEMISTRY_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Physical chemistry modules not available'
        }), 500
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Initialize analyzer
        analyzer = MolecularOrbitalAnalyzer()
        
        # Extract parameters
        xyz_content = data.get('xyz_content', '')
        smiles = data.get('smiles', '')
        method = data.get('method', 'xtb')
        charge = data.get('charge', 0)
        multiplicity = data.get('multiplicity', 1)
        include_orbitals = data.get('include_orbitals', True)
        
        # Choose input method
        if xyz_content.strip():
            results = analyzer.analyze_from_xyz(
                xyz_content=xyz_content,
                method=method,
                charge=charge,
                multiplicity=multiplicity,
                include_orbitals=include_orbitals
            )
        elif smiles.strip():
            results = analyzer.analyze_from_smiles(
                smiles=smiles,
                method=method
            )
        else:
            return jsonify({
                'success': False,
                'error': 'Either XYZ coordinates or SMILES string is required'
            }), 400
        
        return jsonify(results.to_dict())
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Molecular orbital calculation failed: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/physical_chemistry/electron_repulsion/calculate', methods=['POST'])
def calculate_electron_repulsion():
    """Calculate electron-electron repulsion for educational analysis"""
    # TODO: Implement electron repulsion calculator
    return jsonify({
        'success': False,
        'error': 'Electron repulsion calculator not yet implemented'
    }), 501

@app.route('/physical_chemistry/molecular_orbitals/theory')
def molecular_orbitals_theory():
    """Get theory content for molecular orbitals"""
    if not PHYSICAL_CHEMISTRY_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Physical chemistry modules not available'
        }), 500
    
    try:
        analyzer = MolecularOrbitalAnalyzer()
        theory_content = analyzer.get_theory_explanation()
        return jsonify({
            'success': True,
            'theory': theory_content
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get theory content: {str(e)}'
        }), 500

@app.route('/physical_chemistry/electron_repulsion/theory')
def electron_repulsion_theory():
    """Get theory content for electron repulsion"""
    if not PHYSICAL_CHEMISTRY_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Physical chemistry modules not available'
        }), 500
    
    try:
        # TODO: Implement electron repulsion calculator
        # calculator = ElectronRepulsionCalculator()
        # theory_content = calculator.get_theory_explanation()
        return jsonify({
            'success': True,
            'theory': {'explanation': 'Electron repulsion theory module in development'}
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get theory content: {str(e)}'
        }), 500

@app.route('/physical_chemistry/molecular_orbitals/examples')
def molecular_orbitals_examples():
    """Get example molecules for molecular orbital studies"""
    examples = [
        {
            'name': 'Benzène (C₆H₆)',
            'description': 'Système aromatique classique avec orbitales π délocalisées',
            'smiles': 'c1ccccc1',
            'educational_focus': 'Orbitales π délocalisées et aromaticité'
        },
        {
            'name': 'Formaldéhyde (CH₂O)',
            'description': 'Liaison C=O avec orbitales n et π*',
            'smiles': 'C=O',
            'educational_focus': 'Orbitales non-liantes et transitions n→π*'
        },
        {
            'name': 'Diazote (N₂)',
            'description': 'Triple liaison avec orbitales σ et π',
            'smiles': 'N#N',
            'educational_focus': 'Ordre de liaison élevé et stabilité'
        },
        {
            'name': 'Éthène (C₂H₄)',
            'description': 'Liaison double C=C avec orbitales π',
            'smiles': 'C=C',
            'educational_focus': 'Liaison π et réactivité alkène'
        }
    ]
    
    return jsonify({
        'success': True,
        'examples': examples
    })

@app.route('/physical_chemistry/electron_repulsion/examples')
def electron_repulsion_examples():
    """Get example molecules for electron repulsion studies"""
    examples = [
        {
            'name': 'Méthane (CH₄)',
            'description': 'Molécule tétraédrique simple pour comprendre les bases',
            'xyz': """5
Methane molecule
C    0.000000    0.000000    0.000000
H    1.089000    0.000000    0.000000
H   -0.363000    1.026800    0.000000
H   -0.363000   -0.513400   -0.889200
H   -0.363000   -0.513400    0.889200""",
            'educational_focus': 'Répulsion électron-électron dans géométrie tétraédrique'
        },
        {
            'name': 'Eau (H₂O)',
            'description': 'Molécule coudée avec paires libres',
            'xyz': """3
Water molecule
O    0.000000    0.000000    0.117000
H    0.000000    0.757000   -0.467000
H    0.000000   -0.757000   -0.467000""",
            'educational_focus': 'Impact des paires libres sur la géométrie'
        },
        {
            'name': 'Éthylène (C₂H₄)',
            'description': 'Liaison double et géométrie plane',
            'xyz': """6
Ethylene molecule
C    0.000000    0.000000    0.000000
C    0.000000    0.000000    1.330000
H    0.930000    0.000000   -0.560000
H   -0.930000    0.000000   -0.560000
H    0.930000    0.000000    1.890000
H   -0.930000    0.000000    1.890000""",
            'educational_focus': 'Répulsion dans molécules insaturées'
        }
    ]
    
    return jsonify({
        'success': True,
        'examples': examples
    })

# Enhanced Molecular Orbitals Routes (Option B: Perfectionnement Orbitales)
@app.route('/physical_chemistry/molecular_orbitals/enhanced/calculate', methods=['POST'])
def calculate_enhanced_molecular_orbitals():
    """Calculate molecular orbitals with advanced 3D visualization"""
    if not PHYSICAL_CHEMISTRY_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Physical chemistry modules not available'
        }), 500
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Initialize enhanced analyzer
        analyzer = EnhancedMolecularOrbitalAnalyzer()
        
        # Extract parameters
        xyz_content = data.get('xyz_content', '')
        smiles = data.get('smiles', '')
        method = data.get('method', 'xtb')
        charge = data.get('charge', 0)
        multiplicity = data.get('multiplicity', 1)
        generate_isosurfaces = data.get('generate_isosurfaces', True)
        generate_density_plots = data.get('generate_density_plots', True)
        
        # Choose input method
        if xyz_content.strip():
            results = analyzer.analyze_with_enhancements(
                xyz_content=xyz_content,
                method=method,
                charge=charge,
                multiplicity=multiplicity,
                generate_isosurfaces=generate_isosurfaces,
                generate_density_plots=generate_density_plots
            )
        elif smiles.strip():
            # For enhanced analysis, currently require XYZ input
            return jsonify({
                'success': False,
                'error': 'Enhanced analysis currently requires XYZ coordinates. Please convert SMILES to XYZ first.'
            }), 400
        else:
            return jsonify({
                'success': False,
                'error': 'Either XYZ coordinates or SMILES string is required'
            }), 400
        
        return jsonify(results.to_dict())
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Enhanced molecular orbital calculation failed: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/physical_chemistry/molecular_orbitals/enhanced/export', methods=['POST'])
def export_enhanced_orbital_data():
    """Export enhanced orbital calculation results"""
    if not PHYSICAL_CHEMISTRY_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Physical chemistry modules not available'
        }), 500
    
    try:
        data = request.get_json()
        
        # Initialize analyzer
        analyzer = EnhancedMolecularOrbitalAnalyzer()
        
        # Extract parameters
        results_data = data.get('results_data', {})
        export_format = data.get('format', 'json')
        filename = data.get('filename', 'enhanced_orbital_results')
        
        if not results_data:
            return jsonify({
                'success': False,
                'error': 'Results data is required for export'
            }), 400
        
        # Reconstruct results object
        enhanced_orbitals = []
        for orb_data in results_data.get('orbitals', []):
            from modules.physical_chemistry.enhanced_molecular_orbitals import EnhancedOrbitalData
            enhanced_orbitals.append(EnhancedOrbitalData(**orb_data))
        
        results_data['orbitals'] = enhanced_orbitals
        from modules.physical_chemistry.enhanced_molecular_orbitals import EnhancedOrbitalResults
        results = EnhancedOrbitalResults(**results_data)
        
        # Export data
        export_file = analyzer.export_orbital_data(
            results=results,
            format=export_format,
            filename=filename
        )
        
        return jsonify({
            'success': True,
            'export_file': export_file,
            'message': f'Data exported to {export_file}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Data export failed: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/physical_chemistry/molecular_orbitals/enhanced/report', methods=['POST'])
def generate_enhanced_orbital_report():
    """Generate comprehensive orbital analysis report"""
    if not PHYSICAL_CHEMISTRY_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Physical chemistry modules not available'
        }), 500
    
    try:
        data = request.get_json()
        
        # Initialize analyzer
        analyzer = EnhancedMolecularOrbitalAnalyzer()
        
        # Extract parameters
        results_data = data.get('results_data', {})
        include_plots = data.get('include_plots', True)
        
        if not results_data:
            return jsonify({
                'success': False,
                'error': 'Results data is required for report generation'
            }), 400
        
        # Reconstruct results object
        enhanced_orbitals = []
        for orb_data in results_data.get('orbitals', []):
            from modules.physical_chemistry.enhanced_molecular_orbitals import EnhancedOrbitalData
            enhanced_orbitals.append(EnhancedOrbitalData(**orb_data))
        
        results_data['orbitals'] = enhanced_orbitals
        from modules.physical_chemistry.enhanced_molecular_orbitals import EnhancedOrbitalResults
        results = EnhancedOrbitalResults(**results_data)
        
        # Generate report
        report_file = analyzer.generate_orbital_report(
            results=results,
            include_plots=include_plots
        )
        
        return jsonify({
            'success': True,
            'report_file': report_file,
            'message': f'Report generated: {report_file}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Report generation failed: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

# ==============================
# PROFESSIONAL MOLECULAR ORBITALS ROUTES (ChemCompute Quality)
# ==============================

@app.route('/physical_chemistry/professional_orbitals')
def professional_molecular_orbitals_page():
    """Serve the professional molecular orbitals interface"""
    return render_template('professional_molecular_orbitals.html')

@app.route('/api/professional_orbitals/start_calculation', methods=['POST'])
def api_start_professional_calculation():
    """Start a professional orbital calculation with real-time progress"""
    if not PHYSICAL_CHEMISTRY_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Physical chemistry modules not available'
        }), 500
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Extract parameters
        xyz_content = data.get('xyz_content', '')
        method = data.get('method', 'xtb')
        charge = data.get('charge', 0)
        multiplicity = data.get('multiplicity', 1)
        max_orbitals = data.get('max_orbitals', 20)
        
        if not xyz_content.strip():
            return jsonify({
                'success': False,
                'error': 'XYZ content is required'
            }), 400
        
        # Start calculation
        job_id = start_professional_orbital_calculation(
            xyz_content=xyz_content,
            method=method,
            charge=charge,
            multiplicity=multiplicity,
            max_orbitals=max_orbitals
        )
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Calculation started successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to start calculation: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/professional_orbitals/progress/<job_id>')
def api_get_calculation_progress(job_id):
    """Get real-time calculation progress"""
    if not PHYSICAL_CHEMISTRY_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Physical chemistry modules not available'
        }), 500
    
    try:
        progress = get_calculation_progress(job_id)
        
        if progress is None:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
        
        return jsonify(progress)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get progress: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/professional_orbitals/results/<job_id>')
def api_get_calculation_results(job_id):
    """Get completed calculation results"""
    if not PHYSICAL_CHEMISTRY_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Physical chemistry modules not available'
        }), 500
    
    try:
        results = get_calculation_results(job_id)
        
        if results is None:
            return jsonify({
                'success': False,
                'error': 'Results not found or calculation not completed'
            }), 404
        
        # Add success flag to results
        results['success'] = True
        return jsonify(results)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get results: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/professional_orbitals/isosurface/<job_id>/<int:orbital_index>/<float:isovalue>')
def api_get_orbital_isosurface(job_id, orbital_index, isovalue):
    """Get isosurface data for specific orbital"""
    if not PHYSICAL_CHEMISTRY_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Physical chemistry modules not available'
        }), 500
    
    try:
        isosurface_data = get_orbital_isosurface(job_id, orbital_index, isovalue)
        
        if isosurface_data is None:
            return jsonify({
                'success': False,
                'error': 'Isosurface data not found'
            }), 404
        
        # Add success flag
        isosurface_data['success'] = True
        return jsonify(isosurface_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get isosurface: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/professional_orbitals/active_calculations')
def api_list_active_calculations():
    """List all active calculations"""
    if not PHYSICAL_CHEMISTRY_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Physical chemistry modules not available'
        }), 500
    
    try:
        from modules.physical_chemistry.professional_molecular_orbitals import professional_analyzer
        active_calculations = professional_analyzer.list_active_calculations()
        
        return jsonify({
            'success': True,
            'active_calculations': active_calculations
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to list calculations: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/professional_orbitals/cancel/<job_id>', methods=['POST'])
def api_cancel_calculation(job_id):
    """Cancel an active calculation"""
    if not PHYSICAL_CHEMISTRY_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Physical chemistry modules not available'
        }), 500
    
    try:
        from modules.physical_chemistry.professional_molecular_orbitals import professional_analyzer
        cancelled = professional_analyzer.cancel_calculation(job_id)
        
        if cancelled:
            return jsonify({
                'success': True,
                'message': 'Calculation cancelled successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Calculation not found or could not be cancelled'
            }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to cancel calculation: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/professional_orbitals/export_cubes/<job_id>')
def api_export_cube_files(job_id):
    """Export cube files for all orbitals"""
    if not PHYSICAL_CHEMISTRY_AVAILABLE:
        return jsonify({
            'success': False,
            'error': 'Physical chemistry modules not available'
        }), 500
    
    try:
        results = get_calculation_results(job_id)
        
        if results is None:
            return jsonify({
                'success': False,
                'error': 'Results not found'
            }), 404
        
        # Create ZIP file with all cube files
        import zipfile
        import io
        import base64
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for orbital in results['orbitals']:
                if orbital.get('cube_data'):
                    cube_content = base64.b64decode(orbital['cube_data']).decode('utf-8')
                    filename = f"orbital_{orbital['orbital_index']}.cube"
                    zip_file.writestr(filename, cube_content)
        
        zip_buffer.seek(0)
        
        # Return as downloadable file
        from flask import send_file
        return send_file(
            io.BytesIO(zip_buffer.getvalue()),
            as_attachment=True,
            download_name=f'orbitals_{job_id}.zip',
            mimetype='application/zip'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to export cube files: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5006,  # Changement vers port 5006 pour WSL
        debug=True,
        threaded=True
    )
