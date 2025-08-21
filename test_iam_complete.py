#!/usr/bin/env python3
"""
Test simple du système IAM intégré
"""

import sys
sys.path.append('/home/lppou/IAM')

from IAM_Molecule_Engine.iam_molecule_engine import generate_xyz_from_smiles, full_molecule_workflow
import tempfile
import os

def test_iam_integration():
    """Test de l'intégration IAM complète"""
    
    print("🧪 Test Integration IAM")
    print("=" * 40)
    
    # Test 1: Génération XYZ depuis SMILES
    print("\n1. Test SMILES → XYZ:")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            xyz_path = os.path.join(tmpdir, 'water.xyz')
            generate_xyz_from_smiles('O', xyz_path)
            
            with open(xyz_path, 'r') as f:
                xyz_content = f.read()
            
            print("   ✅ SMILES → XYZ réussi")
            print(f"   Preview: {xyz_content[:100]}...")
            
    except Exception as e:
        print(f"   ❌ Erreur SMILES → XYZ: {e}")
    
    # Test 2: Workflow complet (si XTB disponible)
    print("\n2. Test Workflow complet SMILES → XYZ → XTB:")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            results = full_molecule_workflow('O', 'water_test', tmpdir)
            print("   ✅ Workflow complet réussi")
            print(f"   Résultats: {results}")
            
    except Exception as e:
        print(f"   ❌ Workflow échoué (normal si XTB non configuré): {e}")
    
    # Test 3: Autres molécules
    print("\n3. Test autres molécules:")
    test_smiles = ['CCO', 'CC', 'c1ccccc1']  # éthanol, éthane, benzène
    
    for smiles in test_smiles:
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                xyz_path = os.path.join(tmpdir, f'mol_{smiles.replace("c", "C")}.xyz')
                generate_xyz_from_smiles(smiles, xyz_path)
                
                with open(xyz_path, 'r') as f:
                    lines = f.readlines()
                    atom_count = int(lines[0].strip()) if lines else 0
                
                print(f"   ✅ {smiles} → {atom_count} atomes")
                
        except Exception as e:
            print(f"   ❌ {smiles} → Erreur: {e}")
    
    print("\n🏁 Test terminé")

if __name__ == "__main__":
    test_iam_integration()
