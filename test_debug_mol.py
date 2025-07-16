#!/usr/bin/env python3
"""
🔧 Test Debug MOL Parsing - Diagnostic Avancé
"""

import sys
import os

# Ajouter les chemins requis
current_dir = os.path.dirname(os.path.abspath(__file__))
gui_path = os.path.join(current_dir, 'IAM_GUI')
sys.path.insert(0, gui_path)

print("🔧 TEST DEBUG MOL PARSING")
print("=" * 40)

try:
    import backend
    print("✅ Backend importé")
    
    # Test avec différents formats MOL problématiques
    test_mols = {
        "ketcher_simple": """
  Ketcher 12152318552D 1   1.00000     0.00000     0

  2  1  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.4000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
M  END
""",
        "minimal_mol": """2  1  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 C   0  0
    1.4000    0.0000    0.0000 C   0  0
  1  2  1  0
M  END""",
        
        "broken_mol": """
PROBLEMATIC MOL

  2  1  0  0  0  0  0  0  0  0999 V2000
M   bad line here
    1.4000    0.0000    0.0000 C   0  0
  1  2  1  0
M  END"""
    }
    
    for test_name, mol_content in test_mols.items():
        print(f"\n🧪 Test: {test_name}")
        print("-" * 30)
        
        try:
            result = backend.robust_mol_to_xyz(mol_content, f"test_{test_name}")
            print(f"✅ Succès: {len(result)} caractères XYZ")
            
            # Vérifier le format XYZ
            lines = result.strip().split('\n')
            if len(lines) >= 3:
                atom_count = int(lines[0])
                print(f"   📊 {atom_count} atomes dans le XYZ")
        except Exception as e:
            print(f"❌ Échec: {e}")
            print("   Debugging activé dans la fonction")
    
    # Test avec une molécule plus complexe typique de Ketcher
    complex_mol = """
  Ketcher 12152318552D 1   1.00000     0.00000     0

  6  6  0  0  0  0  0  0  0  0999 V2000
    1.4000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.7000    1.2124    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -0.7000    1.2124    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -1.4000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
   -0.7000   -1.2124    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.7000   -1.2124    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  2  0  0  0  0
  2  3  1  0  0  0  0
  3  4  2  0  0  0  0
  4  5  1  0  0  0  0
  5  6  2  0  0  0  0
  6  1  1  0  0  0  0
M  END
"""
    
    print(f"\n🧪 Test: Benzène Ketcher")
    print("-" * 30)
    try:
        result = backend.robust_mol_to_xyz(complex_mol, "benzene_test")
        print(f"✅ Benzène converti: {len(result)} caractères")
        lines = result.strip().split('\n')
        if len(lines) >= 3:
            atom_count = int(lines[0])
            print(f"   🔬 {atom_count} atomes (attendu: 6+ avec H)")
    except Exception as e:
        print(f"❌ Benzène échec: {e}")
    
    print("\n🎯 Debug terminé")
    print("🔍 Consultez les logs détaillés ci-dessus pour identifier les problèmes")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
