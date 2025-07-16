#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__, template_folder='templates')
CORS(app)

@app.route('/')
def index():
    return render_template("iam_clean.html")

@app.route('/test')
def test():
    return jsonify({"status": "OK", "message": "Clean IAM Server is running"})

@app.route('/run_xtb', methods=['POST'])
def run_xtb():
    # Demo results
    fake_results = {
        "total_energy": -4.2384756,
        "homo": -9.234,
        "lumo": -2.156,
        "gap": 7.078,
        "dipole_moment": 1.234,
        "status": "converged"
    }
    
    return jsonify({
        "success": True,
        "xtb_json": fake_results,
        "xyz": "9\n\nC     0.000   0.000   0.000\nH     1.000   0.000   0.000\nH    -0.333   0.943   0.000\nH    -0.333  -0.471   0.816\nH    -0.333  -0.471  -0.816\nO     2.000   0.000   0.000\nH     2.500   0.000   0.866\nH     2.500   0.000  -0.866\nN     0.000   2.000   0.000",
        "stdout": "Calculation completed successfully",
        "stderr": ""
    })

@app.route('/smiles_to_xyz', methods=['POST'])
def smiles_to_xyz():
    # Demo XYZ for ethanol
    fake_xyz = """9

C     0.000   0.000   0.000
C     1.500   0.000   0.000
O     2.000   1.000   0.000
H    -0.500   0.866   0.000
H    -0.500  -0.866   0.000
H    -0.500   0.000   0.866
H     1.500   0.000  -1.000
H     2.000   0.000   0.866
H     2.900   1.000   0.000"""
    
    return jsonify({"success": True, "xyz": fake_xyz})

@app.route('/send_agent_command', methods=['POST'])
def send_agent_command():
    data = request.get_json()
    command = data.get('command', '')
    
    responses = {
        "help": "Available commands: analyze, optimize, predict, status, clear",
        "analyze": "Molecular analysis completed. Found atoms, calculated properties.",
        "optimize": "Geometry optimization initiated using XTB/GFN2-xTB method",
        "predict": "Performance prediction: Calculating VoD and stability parameters",
        "status": "All systems operational. XTB engine ready.",
        "clear": "Terminal cleared successfully"
    }
    
    response_text = responses.get(command.lower(), f"Executed: {command}")
    
    return jsonify({
        "success": True,
        "agent_response": {
            "response": response_text,
            "timestamp": "2025-07-15T12:00:00Z"
        }
    })

if __name__ == '__main__':
    print("🚀 Starting Clean IAM Server...")
    print("📍 Open: http://localhost:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
