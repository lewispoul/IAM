#!/usr/bin/env python3
"""
Test script for MOL parsing functionality
"""

import requests

# Test MOL content - a simple water molecule with proper format
TEST_MOL = """
  Marvin  01010101

  3  2  0  0  0  0            999 V2000
    0.0000    0.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
    0.7571    0.5861    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   -0.7571    0.5861    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  1  3  1  0  0  0  0
M  END
"""

# INDIGO format test
INDIGO_MOL = """
  Marvin  01010101

  3  2  0  0  0  0            999 V2000
    0.0000    0.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
    0.7571    0.5861    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   -0.7571    0.5861    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  1  3  1  0  0  0  0
M  END
"""

def test_mol_conversion(mol_content, test_name):
    """Test MOL to XYZ conversion"""
    url = "http://localhost:5000/molfile_to_xyz"
    
    try:
        response = requests.post(url, 
                               json={'mol_content': mol_content},
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ {test_name}: SUCCESS")
                print(f"   XYZ length: {len(result.get('xyz_content', ''))}")
                print(f"   Preview: {result.get('xyz_content', '')[:100]}...")
                return True
            else:
                print(f"❌ {test_name}: FAILED")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ {test_name}: HTTP ERROR {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ {test_name}: EXCEPTION - {e}")
        return False

def test_debug_endpoint(mol_content, test_name):
    """Test debug endpoint"""
    url = "http://localhost:5000/debug_mol_parsing"
    
    try:
        response = requests.post(url,
                               json={'mol_content': mol_content},
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                debug_info = result.get('debug_info', {})
                print(f"🔍 {test_name} DEBUG:")
                print(f"   Lines: {debug_info.get('lines_count')}")
                print(f"   V2000: {debug_info.get('contains_v2000')}")
                print(f"   INDIGO: {debug_info.get('contains_indigo')}")
                print(f"   RDKit: {debug_info.get('rdkit_success')}")
                if debug_info.get('rdkit_success'):
                    print(f"   Atoms: {debug_info.get('atom_count')}")
                return True
            else:
                print(f"❌ {test_name} DEBUG: FAILED")
                print(f"   Error: {result.get('error')}")
                return False
        else:
            print(f"❌ {test_name} DEBUG: HTTP ERROR {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ {test_name} DEBUG: EXCEPTION - {e}")
        return False

def check_server():
    """Check if server is running"""
    try:
        response = requests.get("http://localhost:5000/")
        return response.status_code == 200
    except:
        return False

def main():
    print("🧪 Testing MOL Parsing System")
    print("=" * 40)
    
    # Check server
    if not check_server():
        print("❌ Server not running on localhost:5000")
        print("Please start the backend with: cd IAM_GUI && python backend.py")
        return
    
    print("✅ Server is running")
    print()
    
    # Test standard MOL
    print("Testing Standard MOL format:")
    test_debug_endpoint(TEST_MOL, "Standard MOL")
    test_mol_conversion(TEST_MOL, "Standard MOL")
    print()
    
    # Test INDIGO MOL
    print("Testing INDIGO MOL format:")
    test_debug_endpoint(INDIGO_MOL, "INDIGO MOL")
    test_mol_conversion(INDIGO_MOL, "INDIGO MOL")
    print()
    
    # Test empty content
    print("Testing empty content:")
    test_mol_conversion("", "Empty Content")
    print()
    
    print("🏁 Testing complete")

if __name__ == "__main__":
    main()
