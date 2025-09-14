# Endpoints Flask pour stoichiomety_calculator
# Import du module
from GeneratedScripts.stoichiomety_calculator import *

from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/upload_reaction', methods=['POST'])
def upload_reaction():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        calculator = StoichiometryCalculator(filepath)
        return jsonify({'message': 'File uploaded successfully', 'compounds': calculator.table.to_dict(orient='records')}), 200

@app.route('/update_compound', methods=['POST'])
def update_compound():
    data = request.json
    reaction_file = data.get('reaction_file')
    compound_name = data.get('compound_name')
    update_data = data.get('update_data', {})
    
    try:
        calculator = StoichiometryCalculator(reaction_file)
        calculator.update_table(compound_name, **update_data)
        return jsonify({'message': 'Compound updated successfully', 'table': calculator.table.to_dict(orient='records')}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/calculate_yield', methods=['POST'])
def calculate_yield():
    data = request.json
    reaction_file = data.get('reaction_file')
    
    try:
        calculator = StoichiometryCalculator(reaction_file)
        calculator.calculate_yield()
        return jsonify({'message': 'Yield calculated successfully', 'table': calculator.table.to_dict(orient='records')}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/export_table', methods=['POST'])
def export_table():
    data = request.json
    reaction_file = data.get('reaction_file')
    filename = data.get('filename', 'stoichiometry.csv')
    file_format = data.get('file_format', 'csv')
    
    try:
        calculator = StoichiometryCalculator(reaction_file)
        export_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        calculator.export_table(export_path, file_format)
        return send_file(export_path, as_attachment=True)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)