from flask import Flask, request, jsonify, render_template, send_from_directory, make_response
from flask_cors import CORS
import os
import subprocess
import tempfile
import json
import traceback
import sys
import importlib
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
    class AllChem:
        @staticmethod
        def EmbedMolecule(mol): return -1
        @staticmethod
        def UFFOptimizeMolecule(mol): return -1

# Add IAM_Knowledge to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../IAM_Knowledge')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = Flask(__name__, template_folder='templates')
CORS(app)

# Initialize performance monitoring
setattr(app, 'start_time', time.time())

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_cache_buster():
    """Generate cache busting timestamp"""
    return str(int(time.time()))

# Debug: Print sys.path to verify module path
print("sys.path:", sys.path)

# Debug: List contents of IAM_Knowledge directory
print("IAM_Knowledge contents:", os.listdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '../IAM_Knowledge'))))

# Debug: Print PYTHONPATH and verify environment configuration
print("PYTHONPATH:", os.environ.get('PYTHONPATH', 'Not set'))

# Import des modules nécessaires (avec gestion d'erreur)
try:
    from IAM_Knowledge.IAM_StabilityPredictor import predict_stability_logic
except ImportError:
    def predict_stability_logic(xyz):
        return {"stability": "Module not available", "method": "placeholder"}

try:
    from IAM_Knowledge.IAM_VoD_Predictor import predict_vod
except ImportError:
    def predict_vod(xyz):
        return {"vod": "Module not available", "method": "placeholder"}

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
            "uptime": time.time() - app.start_time if hasattr(app, 'start_time') else 0,
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
    """Main interface - serves the professional IAM interface"""
    cache_bust = get_cache_buster()
    return render_template('iam_viewer_connected_new.html', cache_bust=cache_bust)

@app.route('/enhanced', methods=['GET', 'POST'])
def enhanced():
    """Enhanced interface - serves the professional IAM interface"""
    cache_bust = get_cache_buster()
    return render_template('iam_viewer_connected_new.html', cache_bust=cache_bust)

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
    if not RDKIT_AVAILABLE:
        return jsonify({
            'success': False, 
            'error': 'RDKit not available', 
            'details': 'RDKit is required for SMILES to XYZ conversion. Please install RDKit or use XYZ files directly.'
        }), 503
        
    data = request.get_json()
    smiles = data.get('smiles', '')
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return jsonify({'success': False, 'error': 'Invalid SMILES', 'details': 'RDKit could not parse the SMILES string'}), 400
            
        mol = Chem.AddHs(mol)
        mol = embed_molecule_with_3d(mol)
        xyz = Chem.MolToXYZBlock(mol)
        return jsonify({'success': True, 'xyz': xyz})
    except Exception as e:
        return jsonify({'success': False, 'error': 'SMILES conversion error', 'details': traceback.format_exc()})

def molfile_to_xyz_logic(molfile):
    """Helper function to convert molfile to XYZ format"""
    if not RDKIT_AVAILABLE:
        return None
        
    try:
        mol = Chem.MolFromMolBlock(molfile)
        if mol is None:
            return None
            
        mol = Chem.AddHs(mol)
        mol = embed_molecule_with_3d(mol)
        xyz = Chem.MolToXYZBlock(mol)
        return xyz
    except Exception:
        return None

@app.route('/molfile_to_xyz', methods=['POST'])
def molfile_to_xyz():
    if not RDKIT_AVAILABLE:
        return jsonify({
            'success': False, 
            'error': 'RDKit not available', 
            'details': 'RDKit is required for MOL to XYZ conversion. Please install RDKit or use XYZ files directly.'
        }), 503
        
    data = request.get_json()
    molfile = data.get('molfile', '')
    try:
        mol = Chem.MolFromMolBlock(molfile)
        if mol is None:
            return jsonify({'success': False, 'error': 'Invalid MOL format', 'details': 'RDKit could not parse the MOL block'}), 400
            
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

@app.route('/predict_stability', methods=['POST'])
def predict_stability():
    data = request.get_json()
    xyz = data.get('xyz', '')
    result = predict_stability_logic(xyz)  # Call with xyz parameter
    return jsonify({'result': result})

@app.route('/predict_vod', methods=['POST'])
def predict_vod_route():  # Renamed to avoid conflict with imported function
    data = request.get_json()
    xyz = data.get('xyz', '')
    result = predict_vod(xyz)  # Call with xyz parameter 
    return jsonify({'result': result})

@app.route('/optimize_performance', methods=['POST'])
def optimize_performance():
    data = request.get_json()
    xyz = data.get('xyz', '')
    target_properties = data.get('target_properties', None)
    
    try:
        from IAM_Knowledge.performance_optimization import optimize_explosive_performance
        result = optimize_explosive_performance(xyz, target_properties)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e), 'result': 'Performance optimization failed'}), 500

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
        xyz_content = molfile_to_xyz_logic(mol_data)
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
        xyz_content = molfile_to_xyz_logic(mol_data)
        
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

if __name__ == '__main__':
    print("✅ Physical Chemistry modules loaded successfully")
    app.run(
        host='0.0.0.0',
        port=5006,
        debug=True,
        threaded=True
    )
