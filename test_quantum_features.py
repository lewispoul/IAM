#!/usr/bin/env python3
"""
Test script for advanced quantum chemistry features in IAM
"""

import unittest
import requests
import json
import os
import sys
import tempfile

# Add IAM_GUI to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'IAM_GUI'))

class TestQuantumFeatures(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        cls.base_url = "http://localhost:5000"
        cls.test_xyz = """2
methane molecule
C  0.0000  0.0000  0.0000
H  1.0000  1.0000  1.0000
"""

    def test_vibrational_modes_endpoint(self):
        """Test the vibrational modes calculation endpoint"""
        url = f"{self.base_url}/calculate_vibrational_modes"
        data = {
            'mol_data': self.test_xyz,
            'method': 'xtb',
            'basis': 'def2-SVP',
            'charge': 0,
            'multiplicity': 1
        }
        
        response = requests.post(url, json=data)
        self.assertEqual(response.status_code, 200)
        
        result = response.json()
        self.assertTrue(result['success'])
        self.assertIn('results', result)
        self.assertIn('frequencies', result['results'])
        self.assertIn('intensities', result['results'])
        self.assertIn('zero_point_energy', result['results'])

    def test_cube_file_endpoint(self):
        """Test the cube file serving endpoint"""
        job_id = "test_job_123"
        cube_type = "homo"
        
        url = f"{self.base_url}/get_cube/{job_id}/{cube_type}"
        response = requests.get(url)
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertTrue(result['success'])
        self.assertIn('cube_data', result)
        self.assertIn('metadata', result)

    def test_performance_prediction_endpoint(self):
        """Test the performance prediction endpoint"""
        url = f"{self.base_url}/predict_performance"
        data = {
            'mol_data': self.test_xyz
        }
        
        response = requests.post(url, json=data)
        self.assertEqual(response.status_code, 200)
        
        result = response.json()
        # Note: This might fail if VoD predictor is not available
        if result['success']:
            self.assertIn('performance_data', result)
        else:
            # Expected if VoD predictor module is not available
            self.assertIn('error', result)

    def test_quantum_analysis_endpoint(self):
        """Test the enhanced quantum analysis endpoint"""
        url = f"{self.base_url}/quantum_analysis"
        data = {
            'mol_data': self.test_xyz,
            'method': 'dft',
            'basis': 'def2-SVP',
            'functional': 'B3LYP'
        }
        
        response = requests.post(url, json=data)
        self.assertEqual(response.status_code, 200)
        
        result = response.json()
        self.assertTrue(result['success'])
        self.assertIn('quantum_properties', result)
        self.assertIn('bond_orders', result['quantum_properties'])
        self.assertIn('dipole_moment', result['quantum_properties'])
        self.assertIn('polarizability', result['quantum_properties'])

    def test_chemcompute_interface_accessibility(self):
        """Test that the ChemCompute interface is accessible"""
        url = f"{self.base_url}/chemcompute"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response.headers['content-type'])

    def test_run_quantum_endpoint(self):
        """Test the enhanced quantum calculation endpoint"""
        url = f"{self.base_url}/run_quantum"
        
        # Create a temporary XYZ file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xyz', delete=False) as f:
            f.write(self.test_xyz)
            temp_file_path = f.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'method': 'xtb',
                    'charge': '0',
                    'multiplicity': '1',
                    'calcType': 'opt',
                    'basis': 'def2-SVP'
                }
                
                response = requests.post(url, files=files, data=data)
                self.assertEqual(response.status_code, 200)
                
                result = response.json()
                # Should succeed with XTB or show specific error
                self.assertIn('success', result)
                
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

def run_tests():
    """Run the test suite"""
    unittest.main(verbosity=2)

if __name__ == '__main__':
    print("Testing Advanced Quantum Chemistry Features for IAM")
    print("=" * 50)
    run_tests()