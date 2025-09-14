"""
Physical Chemistry Routes for IAM Educational Platform
Routes for educational modules covering physical chemistry concepts
"""

from flask import Blueprint, request, jsonify, render_template
import json
import traceback

# Import educational modules
from ..modules.physical_chemistry.electron_repulsion import ElectronRepulsionCalculator
from ..modules.physical_chemistry.molecular_orbitals import MolecularOrbitalAnalyzer

physical_chemistry_bp = Blueprint('physical_chemistry', __name__, url_prefix='/physical_chemistry')

# Initialize calculators
electron_repulsion_calc = ElectronRepulsionCalculator()
molecular_orbital_analyzer = MolecularOrbitalAnalyzer()


@physical_chemistry_bp.route('/electron_repulsion')
def electron_repulsion_page():
    """Serve the electron repulsion educational module"""
    return render_template('physical_chemistry/electron_repulsion.html')


@physical_chemistry_bp.route('/molecular_orbitals')
def molecular_orbitals_page():
    """Serve the molecular orbitals educational module"""
    return render_template('physical_chemistry/molecular_orbitals.html')


@physical_chemistry_bp.route('/electron_repulsion/calculate', methods=['POST'])
def calculate_electron_repulsion():
    """Calculate electron-electron repulsion for educational analysis"""
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
        
        if not xyz_content.strip():
            return jsonify({
                'success': False,
                'error': 'XYZ coordinates are required'
            }), 400
        
        # Run calculation
        results = electron_repulsion_calc.analyze_from_xyz(
            xyz_content=xyz_content,
            method=method,
            charge=charge,
            multiplicity=multiplicity
        )
        
        return jsonify(results.to_dict())
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Calculation failed: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500


@physical_chemistry_bp.route('/molecular_orbitals/calculate', methods=['POST'])
def calculate_molecular_orbitals():
    """Calculate molecular orbitals for educational analysis"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Extract parameters
        xyz_content = data.get('xyz_content', '')
        smiles = data.get('smiles', '')
        method = data.get('method', 'xtb')
        charge = data.get('charge', 0)
        multiplicity = data.get('multiplicity', 1)
        include_orbitals = data.get('include_orbitals', True)
        
        # Choose input method
        if xyz_content.strip():
            results = molecular_orbital_analyzer.analyze_from_xyz(
                xyz_content=xyz_content,
                method=method,
                charge=charge,
                multiplicity=multiplicity,
                include_orbitals=include_orbitals
            )
        elif smiles.strip():
            results = molecular_orbital_analyzer.analyze_from_smiles(
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


@physical_chemistry_bp.route('/electron_repulsion/theory')
def electron_repulsion_theory():
    """Get theory content for electron repulsion"""
    try:
        theory_content = electron_repulsion_calc.get_theory_explanation()
        return jsonify({
            'success': True,
            'theory': theory_content
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get theory content: {str(e)}'
        }), 500


@physical_chemistry_bp.route('/molecular_orbitals/theory')
def molecular_orbitals_theory():
    """Get theory content for molecular orbitals"""
    try:
        theory_content = molecular_orbital_analyzer.get_theory_explanation()
        return jsonify({
            'success': True,
            'theory': theory_content
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get theory content: {str(e)}'
        }), 500


@physical_chemistry_bp.route('/electron_repulsion/examples')
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


@physical_chemistry_bp.route('/molecular_orbitals/examples')
def molecular_orbitals_examples():
    """Get example molecules for molecular orbital studies"""
    examples = [
        {
            'name': 'Benzène (C₆H₆)',
            'description': 'Système aromatique classique avec orbitales π délocalisées',
            'smiles': 'c1ccccc1',
            'xyz': """12
Benzene molecule
C    1.390000    0.000000    0.000000
C    0.695000    1.204000    0.000000
C   -0.695000    1.204000    0.000000
C   -1.390000    0.000000    0.000000
C   -0.695000   -1.204000    0.000000
C    0.695000   -1.204000    0.000000
H    2.470000    0.000000    0.000000
H    1.235000    2.139000    0.000000
H   -1.235000    2.139000    0.000000
H   -2.470000    0.000000    0.000000
H   -1.235000   -2.139000    0.000000
H    1.235000   -2.139000    0.000000""",
            'educational_focus': 'Orbitales π délocalisées et aromaticité'
        },
        {
            'name': 'Formaldéhyde (CH₂O)',
            'description': 'Liaison C=O avec orbitales n et π*',
            'smiles': 'C=O',
            'xyz': """4
Formaldehyde molecule
C    0.000000    0.000000    0.000000
O    0.000000    0.000000    1.210000
H    0.943000    0.000000   -0.544000
H   -0.943000    0.000000   -0.544000""",
            'educational_focus': 'Orbitales non-liantes et transitions n→π*'
        },
        {
            'name': 'Diazote (N₂)',
            'description': 'Triple liaison avec orbitales σ et π',
            'smiles': 'N#N',
            'xyz': """2
Nitrogen molecule
N    0.000000    0.000000    0.000000
N    0.000000    0.000000    1.098000""",
            'educational_focus': 'Ordre de liaison élevé et stabilité'
        },
        {
            'name': 'Éthène (C₂H₄)',
            'description': 'Liaison double C=C avec orbitales π',
            'smiles': 'C=C',
            'xyz': """6
Ethylene molecule
C    0.000000    0.000000    0.000000
C    0.000000    0.000000    1.330000
H    0.930000    0.000000   -0.560000
H   -0.930000    0.000000   -0.560000
H    0.930000    0.000000    1.890000
H   -0.930000    0.000000    1.890000""",
            'educational_focus': 'Liaison π et réactivité alkène'
        }
    ]
    
    return jsonify({
        'success': True,
        'examples': examples
    })


@physical_chemistry_bp.route('/modules')
def list_modules():
    """List all available physical chemistry modules"""
    modules = [
        {
            'id': 'electron_repulsion',
            'name': 'Répulsion Électron-Électron',
            'description': 'Analyse de la répulsion électronique et géométrie moléculaire',
            'url': '/physical_chemistry/electron_repulsion',
            'theory_url': '/physical_chemistry/electron_repulsion/theory',
            'examples_url': '/physical_chemistry/electron_repulsion/examples',
            'topics': [
                'Théorie VSEPR',
                'Répulsion électron-électron', 
                'Géométrie moléculaire',
                'Énergie de répulsion'
            ]
        },
        {
            'id': 'molecular_orbitals',
            'name': 'Orbitales Moléculaires',
            'description': 'Analyse des orbitales moléculaires et structure électronique',
            'url': '/physical_chemistry/molecular_orbitals',
            'theory_url': '/physical_chemistry/molecular_orbitals/theory',
            'examples_url': '/physical_chemistry/molecular_orbitals/examples',
            'topics': [
                'HOMO-LUMO',
                'Gap énergétique',
                'Réactivité chimique',
                'Orbitales frontières'
            ]
        }
    ]
    
    return jsonify({
        'success': True,
        'modules': modules
    })
