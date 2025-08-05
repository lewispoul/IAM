import unittest
from flask import Flask, request
from IAM_GUI.backend import app

class TestSmilesToXYZ(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_valid_smiles(self):
        response = self.app.post('/smiles_to_xyz', json={"smiles": "CCO"})  # Ethanol
        data = response.get_json()
        self.assertTrue(data["success"], "Valid SMILES should succeed.")
        self.assertIn("xyz", data, "Response should contain XYZ coordinates.")

    def test_invalid_smiles(self):
        response = self.app.post('/smiles_to_xyz', json={"smiles": "INVALID_SMILES"})
        data = response.get_json()
        self.assertFalse(data["success"], "Invalid SMILES should fail.")
        self.assertIn("error", data, "Response should contain an error message.")

    def test_empty_smiles(self):
        response = self.app.post('/smiles_to_xyz', json={"smiles": ""})
        data = response.get_json()
        self.assertFalse(data["success"], "Empty SMILES should fail.")
        self.assertIn("error", data, "Response should contain an error message.")

    def test_large_molecule(self):
        response = self.app.post('/smiles_to_xyz', json={"smiles": "C" * 100})  # Large molecule with 100 carbons
        data = response.get_json()
        self.assertTrue(data["success"], "Large molecule SMILES should succeed.")
        self.assertIn("xyz", data, "Response should contain XYZ coordinates.")

if __name__ == "__main__":
    unittest.main()
