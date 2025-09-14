# Endpoints Flask pour density_calculator
# Import du module
from GeneratedScripts.density_calculator import *

@app.route('/api/density_calculator/parse_formula', methods=['POST'])
def density_calc_parse_formula():
    """Parse une formule chimique"""
    try:
        data = request.json
        formula = data.get('formula', '')
        
        if not formula:
            return jsonify({'success': False, 'error': 'Formule chimique requise'}), 400
        
        composition = parse_chemical_formula(formula)
        
        return jsonify({
            'success': True,
            'composition': composition,
            'formula': formula
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/density_calculator/calculate_density', methods=['POST'])
def density_calc_calculate():
    """Calcule la densité d'un explosif"""
    try:
        data = request.json
        formula = data.get('formula', '')
        
        if not formula:
            return jsonify({'success': False, 'error': 'Formule chimique requise'}), 400
        
        # Parse la formule
        composition = parse_chemical_formula(formula)
        
        # Calcule la masse molaire
        molar_mass = calculate_molar_mass(composition)
        
        # Calcule la densité
        density = kamlet_jacobs_density(molar_mass, composition)
        
        return jsonify({
            'success': True,
            'formula': formula,
            'composition': composition,
            'molar_mass': molar_mass,
            'density': density,
            'unit': 'g/cm³'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
