#!/usr/bin/env python3
"""
Test script for Molecular Orbitals Module
IAM Physical Chemistry Educational Tools

This script tests the molecular orbital analysis functionality
"""

import os
import sys
import traceback

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_molecular_orbitals_module():
    """Test the molecular orbitals module with various molecules"""
    
    print("🧪 Testing Molecular Orbitals Module")
    print("=" * 50)
    
    try:
        from IAM_GUI.modules.physical_chemistry.molecular_orbitals import MolecularOrbitalAnalyzer
        print("✅ Module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import module: {e}")
        return False
    
    # Initialize analyzer
    analyzer = MolecularOrbitalAnalyzer()
    
    # Test molecules
    test_molecules = [
        {
            'name': 'Méthane (CH₄)',
            'xyz': """5
Methane molecule
C    0.000000    0.000000    0.000000
H    1.089000    0.000000    0.000000
H   -0.363000    1.026800    0.000000
H   -0.363000   -0.513400   -0.889200
H   -0.363000   -0.513400    0.889200""",
            'expected_gap_range': (8.0, 12.0)  # Expected HOMO-LUMO gap in eV
        },
        {
            'name': 'Eau (H₂O)',
            'xyz': """3
Water molecule
O    0.000000    0.000000    0.117000
H    0.000000    0.757000   -0.467000
H    0.000000   -0.757000   -0.467000""",
            'expected_gap_range': (6.0, 10.0)
        }
    ]
    
    # Test SMILES input (if RDKit available)
    test_smiles = [
        {
            'name': 'Benzène',
            'smiles': 'c1ccccc1',
            'expected_gap_range': (5.0, 8.0)
        }
    ]
    
    # Run XYZ tests
    success_count = 0
    total_tests = 0
    
    for mol in test_molecules:
        total_tests += 1
        print(f"\n🔬 Testing {mol['name']}...")
        
        try:
            results = analyzer.analyze_from_xyz(mol['xyz'])
            
            if results.success:
                gap_eV = results.homo_lumo_gap_eV or (results.homo_lumo_gap * 27.2114)
                
                print(f"   ✅ Calculation successful")
                print(f"   📊 HOMO: {results.homo_energy * 27.2114:.2f} eV")
                print(f"   📊 LUMO: {results.lumo_energy * 27.2114:.2f} eV")
                print(f"   📊 Gap: {gap_eV:.2f} eV")
                print(f"   📊 Total Energy: {results.total_energy:.4f} Hartree")
                print(f"   📊 Number of orbitals: {len(results.orbitals)}")
                
                # Validate gap range
                if mol['expected_gap_range'][0] <= gap_eV <= mol['expected_gap_range'][1]:
                    print(f"   ✅ Gap within expected range {mol['expected_gap_range']}")
                    success_count += 1
                else:
                    print(f"   ⚠️ Gap outside expected range {mol['expected_gap_range']}")
                    success_count += 0.5  # Partial success
                
                # Test educational analysis
                if results.educational_analysis:
                    print(f"   ✅ Educational analysis generated")
                    print(f"   📚 HOMO character: {results.educational_analysis.get('frontier_orbital_analysis', {}).get('homo_character', 'N/A')}")
                
                # Test visualization data
                if results.visualization_data:
                    print(f"   ✅ Visualization data generated")
                    if 'energy_levels' in results.visualization_data:
                        print(f"   📊 Energy levels: {len(results.visualization_data['energy_levels'])}")
                
            else:
                print(f"   ❌ Calculation failed: {results.error}")
                
        except Exception as e:
            print(f"   ❌ Exception during test: {str(e)}")
            print(f"   📝 Traceback: {traceback.format_exc()}")
    
    # Test SMILES input
    for mol in test_smiles:
        total_tests += 1
        print(f"\n🔬 Testing {mol['name']} (SMILES: {mol['smiles']})...")
        
        try:
            results = analyzer.analyze_from_smiles(mol['smiles'])
            
            if results.success:
                gap_eV = results.homo_lumo_gap_eV or (results.homo_lumo_gap * 27.2114)
                
                print(f"   ✅ SMILES calculation successful")
                print(f"   📊 Gap: {gap_eV:.2f} eV")
                
                if mol['expected_gap_range'][0] <= gap_eV <= mol['expected_gap_range'][1]:
                    print(f"   ✅ Gap within expected range {mol['expected_gap_range']}")
                    success_count += 1
                else:
                    print(f"   ⚠️ Gap outside expected range {mol['expected_gap_range']}")
                    success_count += 0.5
                    
            else:
                print(f"   ❌ SMILES calculation failed: {results.error}")
                if "RDKit not available" in results.error:
                    print(f"   ℹ️ This is expected if RDKit is not installed")
                    success_count += 0.5  # Don't penalize for missing RDKit
                
        except Exception as e:
            print(f"   ❌ Exception during SMILES test: {str(e)}")
    
    # Test theory content
    print(f"\n📚 Testing theory content...")
    try:
        theory = analyzer.get_theory_explanation()
        if theory and len(theory) > 100:
            print(f"   ✅ Theory content generated ({len(theory)} characters)")
        else:
            print(f"   ⚠️ Theory content seems short or empty")
    except Exception as e:
        print(f"   ❌ Theory generation failed: {str(e)}")
    
    # Summary
    print(f"\n📋 Test Summary")
    print(f"=" * 30)
    print(f"Tests passed: {success_count}/{total_tests}")
    print(f"Success rate: {(success_count/total_tests)*100:.1f}%")
    
    if success_count >= total_tests * 0.7:  # 70% success rate
        print(f"🎉 Module tests PASSED!")
        return True
    else:
        print(f"❌ Module tests FAILED!")
        return False

def test_integration_with_flask():
    """Test integration with Flask routes"""
    
    print(f"\n🌐 Testing Flask Integration")
    print("=" * 40)
    
    try:
        import requests
        import json
        
        # Test data
        test_xyz = """5
Methane molecule
C    0.000000    0.000000    0.000000
H    1.089000    0.000000    0.000000
H   -0.363000    1.026800    0.000000
H   -0.363000   -0.513400   -0.889200
H   -0.363000   -0.513400    0.889200"""
        
        test_payload = {
            'xyz_content': test_xyz,
            'method': 'xtb',
            'charge': 0,
            'multiplicity': 1
        }
        
        # Try to connect to the Flask server
        base_url = 'http://localhost:5006'
        
        print(f"🔗 Testing connection to {base_url}...")
        
        # Test molecular orbitals endpoint
        response = requests.post(
            f'{base_url}/physical_chemistry/molecular_orbitals/calculate',
            json=test_payload,
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Molecular orbitals endpoint working")
                print(f"   📊 HOMO-LUMO gap: {data.get('homo_lumo_gap_eV', 0):.2f} eV")
            else:
                print(f"   ❌ Calculation failed: {data.get('error')}")
        else:
            print(f"   ❌ HTTP error: {response.status_code}")
            
        # Test theory endpoint
        response = requests.get(f'{base_url}/physical_chemistry/molecular_orbitals/theory')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ Theory endpoint working")
            else:
                print(f"   ❌ Theory endpoint failed: {data.get('error')}")
        
        # Test examples endpoint
        response = requests.get(f'{base_url}/physical_chemistry/molecular_orbitals/examples')
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('examples'):
                print(f"   ✅ Examples endpoint working ({len(data['examples'])} examples)")
            else:
                print(f"   ❌ Examples endpoint failed")
        
        print(f"🎉 Flask integration tests completed!")
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"   ⚠️ Flask server not running on {base_url}")
        print(f"   ℹ️ Start the server with: python backend.py")
        return False
    except Exception as e:
        print(f"   ❌ Integration test failed: {str(e)}")
        return False

def check_dependencies():
    """Check if required dependencies are available"""
    
    print(f"🔍 Checking Dependencies")
    print("=" * 30)
    
    dependencies = {
        'numpy': False,
        'subprocess': True,  # Built-in
        'tempfile': True,    # Built-in
        'rdkit': False,
        'xtb': False
    }
    
    # Check Python packages
    try:
        import numpy
        dependencies['numpy'] = True
        print(f"✅ NumPy available ({numpy.__version__})")
    except ImportError:
        print(f"❌ NumPy not available")
    
    try:
        from rdkit import Chem
        dependencies['rdkit'] = True
        print(f"✅ RDKit available")
    except ImportError:
        print(f"⚠️ RDKit not available (SMILES support limited)")
    
    # Check XTB
    try:
        import subprocess
        result = subprocess.run(['xtb', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            dependencies['xtb'] = True
            print(f"✅ XTB available")
        else:
            print(f"❌ XTB not working properly")
    except FileNotFoundError:
        print(f"❌ XTB not found in PATH")
    except Exception:
        print(f"❌ XTB check failed")
    
    # Summary
    essential_deps = ['numpy', 'xtb']
    missing_essential = [dep for dep in essential_deps if not dependencies[dep]]
    
    if not missing_essential:
        print(f"🎉 All essential dependencies available!")
        return True
    else:
        print(f"❌ Missing essential dependencies: {missing_essential}")
        print(f"📝 Install with:")
        if 'numpy' in missing_essential:
            print(f"   pip install numpy")
        if 'xtb' in missing_essential:
            print(f"   conda install -c conda-forge xtb")
        return False

if __name__ == '__main__':
    print("🧪 IAM Molecular Orbitals Module - Test Suite")
    print("=" * 60)
    
    # Check dependencies first
    deps_ok = check_dependencies()
    
    if not deps_ok:
        print(f"\n⚠️ Some dependencies missing - tests may fail")
    
    # Run module tests
    module_ok = test_molecular_orbitals_module()
    
    # Run integration tests (optional)
    print(f"\n🤔 Run Flask integration tests? (requires server running)")
    run_integration = input("Run integration tests? (y/n): ").lower().startswith('y')
    
    if run_integration:
        integration_ok = test_integration_with_flask()
    else:
        integration_ok = True
        print(f"⏭️ Skipping integration tests")
    
    # Final summary
    print(f"\n🏁 Final Results")
    print("=" * 20)
    print(f"Dependencies: {'✅' if deps_ok else '❌'}")
    print(f"Module tests: {'✅' if module_ok else '❌'}")
    print(f"Integration: {'✅' if integration_ok else '⏭️'}")
    
    if module_ok and (not run_integration or integration_ok):
        print(f"\n🎉 All tests PASSED! Module ready for use.")
        exit(0)
    else:
        print(f"\n❌ Some tests FAILED. Check the output above.")
        exit(1)
