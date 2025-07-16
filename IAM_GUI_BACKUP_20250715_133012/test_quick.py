#!/usr/bin/env python3

"""
Test rapide du backend IAM corrigé
"""

import sys
import os

# Ajouter le chemin du backend
sys.path.insert(0, '/home/lppou/IAM/IAM_GUI')

def test_backend_fixes():
    """Test les corrections du backend"""
    print("🧪 Test des corrections backend IAM")
    
    try:
        # Test 1: Import backend
        print("📦 Test 1: Import backend...")
        import backend
        print("✅ Backend importé avec succès")
        
        # Test 2: Test patch_molblock avec contenu Ketcher problématique
        print("🔧 Test 2: patch_molblock...")
        test_mol = """IAM_Molecule
  IAM-Generated
  
  3  2  0  0  0  0  0  0  0  0999 V2000
    1.5000   -0.2500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.0000    0.2500    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -1.5000   -0.2500    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  2  3  1  0  0  0  0
M  END
"""
        try:
            patched = backend.patch_molblock(test_mol)
            print("✅ patch_molblock OK")
            
            # Vérifier le format de la ligne de comptage
            lines = patched.splitlines()
            counts_line = lines[3] if len(lines) > 3 else ""
            print(f"   Ligne de comptage: '{counts_line}'")
            
        except Exception as e:
            print(f"❌ patch_molblock failed: {e}")
        
        # Test 3: Test robust_mol_to_xyz
        print("🔄 Test 3: robust_mol_to_xyz...")
        try:
            if backend.RDKIT_AVAILABLE:
                xyz = backend.robust_mol_to_xyz(test_mol, "test")
                print("✅ robust_mol_to_xyz OK")
                print(f"   XYZ preview: {xyz[:60]}...")
            else:
                print("⚠️ RDKit non disponible, test skippé")
        except Exception as e:
            print(f"❌ robust_mol_to_xyz failed: {e}")
        
        # Test 4: Vérifier les endpoints
        print("🌐 Test 4: Endpoints disponibles...")
        app_routes = []
        for rule in backend.app.url_map.iter_rules():
            app_routes.append(f"{rule.methods} {rule.rule}")
        
        expected_endpoints = ['/run_xtb', '/molfile_to_xyz', '/smiles_to_xyz']
        for endpoint in expected_endpoints:
            found = any(endpoint in route for route in app_routes)
            status = "✅" if found else "❌"
            print(f"   {status} {endpoint}")
        
        print("🎉 Tests terminés!")
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_backend_fixes()
