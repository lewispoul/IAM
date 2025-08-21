#!/usr/bin/env python3
"""
Backend Flask minimaliste pour debug
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import traceback

app = Flask(__name__, template_folder='templates')
CORS(app)

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({
        "success": False,
        "error": str(e),
        "details": traceback.format_exc()
    }), 500

@app.route('/')
def index():
    return render_template("iam_viewer_connected.html", results={})

@app.route('/smiles_to_xyz', methods=['POST'])
def smiles_to_xyz():
    return jsonify({
        'success': True,
        'xyz': '3\\nGenerated from SMILES\\nO 0.0 0.0 0.0\\nH 1.0 0.0 0.0\\nH 0.0 1.0 0.0\\n'
    })

@app.route('/run_xtb', methods=['POST'])
def run_xtb():
    return jsonify({
        'success': True,
        'xtb_json': {
            'energy': -5.123,
            'homo_lumo_gap': 12.34,
            'dipole': 1.85
        }
    })

if __name__ == '__main__':
    print("🚀 Démarrage backend minimal IAM...")
    app.run(host='0.0.0.0', port=5000, debug=True)
