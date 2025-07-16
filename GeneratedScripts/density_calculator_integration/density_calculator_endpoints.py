# Endpoints Flask pour density_calculator
# Import du module
from GeneratedScripts.density_calculator import *

from flask import Flask, request, jsonify
from your_module_name import density_calculator_main

app = Flask(__name__)

@app.route('/api/calculate_density', methods=['POST'])
def calculate_density():
    try:
        data = request.json
        formula = data.get('formula')
        if not formula:
            return jsonify({"success": False, "error": "La formule chimique est requise"}), 400
        
        result = density_calculator_main(formula)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)