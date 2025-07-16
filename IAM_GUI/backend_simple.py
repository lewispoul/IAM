#!/usr/bin/env python3
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import subprocess
import tempfile
import json
import traceback
from datetime import datetime

# Essayer d'importer RDKit
try:
    from rdkit import Chem
    from rdkit.Chem import AllChem
    from rdkit.Chem import rdDistGeom
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    print("Warning: RDKit not available, some features will be limited")

app = Flask(__name__, template_folder='templates')
CORS(app)

@app.route('/')
def index():
    return render_template("iam_viewer_connected.html")

@app.route('/test')
def test():
    return jsonify({"status": "OK", "message": "IAM Server is running", "rdkit": RDKIT_AVAILABLE})

@app.route('/run_xtb', methods=['POST'])
def run_xtb():
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file received"}), 400

        xyz_file = request.files["file"]
        if xyz_file.filename == "":
            return jsonify({"success": False, "error": "Empty filename"}), 400

        # Lire le contenu du fichier
        mol_string = xyz_file.read().decode("utf-8")
        
        # Créer un répertoire temporaire pour XTB
        with tempfile.TemporaryDirectory() as tempdir:
            xyz_path = os.path.join(tempdir, "molecule.xyz")
            with open(xyz_path, "w") as f:
                f.write(mol_string)
            
            # Commande XTB
            xtb_command = ["xtb", xyz_path, "--opt", "--json", "--gfn", "2"]
            result = subprocess.run(xtb_command, cwd=tempdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Vérifier si le fichier JSON existe
            json_path = os.path.join(tempdir, "xtbout.json")
            xtbopt_xyz_path = os.path.join(tempdir, "xtbopt.xyz")
            
            # Lire la géométrie optimisée
            if os.path.exists(xtbopt_xyz_path):
                with open(xtbopt_xyz_path, "r") as f:
                    xyz_optimized = f.read()
            else:
                xyz_optimized = mol_string
            
            if not os.path.exists(json_path):
                return jsonify({
                    "success": False,
                    "error": "XTB calculation failed",
                    "details": f"stdout: {result.stdout}\nstderr: {result.stderr}",
                    "xyz": xyz_optimized
                }), 500
            
            # Lire les résultats JSON
            with open(json_path, "r") as f:
                xtb_data = json.load(f)
            
            return jsonify({
                "success": True, 
                "xtb_json": xtb_data, 
                "xyz": xyz_optimized,
                "stdout": result.stdout[:1000],  # Limiter la sortie
                "stderr": result.stderr[:1000]
            })
            
    except Exception as e:
        return jsonify({
            "success": False, 
            "error": str(e), 
            "details": traceback.format_exc()
        }), 500

@app.route('/smiles_to_xyz', methods=['POST'])
def smiles_to_xyz():
    if not RDKIT_AVAILABLE:
        return jsonify({"success": False, "error": "RDKit not available"}), 500
    
    try:
        data = request.get_json()
        smiles = data.get('smiles', '')
        
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return jsonify({"success": False, "error": "Invalid SMILES"}), 400
            
        mol = Chem.AddHs(mol)
        if AllChem.EmbedMolecule(mol, AllChem.ETKDG()) != 0:
            # Fallback si l'embedding échoue
            AllChem.EmbedMolecule(mol)
        AllChem.MMFFOptimizeMolecule(mol)
        
        xyz = Chem.MolToXYZBlock(mol)
        return jsonify({"success": True, "xyz": xyz})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "details": traceback.format_exc()}), 500

@app.route('/molfile_to_xyz', methods=['POST'])
def molfile_to_xyz():
    if not RDKIT_AVAILABLE:
        return jsonify({"success": False, "error": "RDKit not available"}), 500
    
    try:
        data = request.get_json()
        molfile = data.get('molfile', '')
        
        mol = Chem.MolFromMolBlock(molfile)
        if mol is None:
            return jsonify({"success": False, "error": "Invalid MOL file"}), 400
            
        mol = Chem.AddHs(mol)
        if AllChem.EmbedMolecule(mol, AllChem.ETKDG()) != 0:
            # Fallback si l'embedding échoue
            AllChem.EmbedMolecule(mol)
        AllChem.MMFFOptimizeMolecule(mol)
        
        xyz = Chem.MolToXYZBlock(mol)
        return jsonify({"success": True, "xyz": xyz})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e), "details": traceback.format_exc()}), 500

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
        
        # Créer le dossier IAM_Results s'il n'existe pas
        results_dir = os.path.join('..', 'IAM_Results')
        os.makedirs(results_dir, exist_ok=True)
        
        save_path = os.path.join(results_dir, filename)
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
        
        possible_paths = [
            os.path.join('..', 'IAM_Results', filename),
            os.path.join('..', 'IAM_Knowledge', 'Molecules', filename),
            filename  # Chemin direct
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    xyz = f.read()
                return jsonify({"success": True, "xyz": xyz, "loaded_from": path})
        
        return jsonify({"success": False, "error": "File not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting IAM Molecule Viewer Server...")
    print("📍 Open your browser to: http://localhost:5000")
    print("🔬 RDKit available:", RDKIT_AVAILABLE)
    app.run(host='0.0.0.0', port=5000, debug=True)
