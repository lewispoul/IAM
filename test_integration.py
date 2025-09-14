#!/usr/bin/env python3
"""
Test des nouvelles fonctionnalités d'intégration backend
"""

import requests
import json

BASE_URL = "http://localhost:5002"

def test_integration_features():
    """Test des fonctionnalités d'intégration"""
    print("🔧 Test des fonctionnalités d'intégration backend")
    print("=" * 60)
    
    # Test avec le module density_calculator existant
    module_name = "density_calculator"
    
    print(f"📦 Test d'intégration pour le module: {module_name}")
    
    # Test 1: Génération de l'intégration
    print("\n1. 🔧 Test génération d'intégration...")
    try:
        response = requests.post(f"{BASE_URL}/integrate_module", 
                               json={"module_name": module_name}, 
                               timeout=30)
        result = response.json()
        
        if result.get('success'):
            print("✅ Intégration générée avec succès")
            print(f"📁 Répertoire: {result.get('integration_dir')}")
            print(f"🔗 Endpoints: {result.get('endpoints_file')}")
            print(f"🖥️  Interface: {result.get('interface_file')}")
            print(f"📋 Instructions: {result.get('instructions_file')}")
        else:
            print(f"❌ Erreur: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur requête: {e}")
        return False
    
    # Test 2: Application de l'intégration
    print("\n2. ✅ Test application d'intégration...")
    try:
        response = requests.post(f"{BASE_URL}/apply_integration", 
                               json={"module_name": module_name}, 
                               timeout=10)
        result = response.json()
        
        if result.get('success'):
            print("✅ Application réussie")
            print(f"📝 Message: {result.get('message')}")
            if result.get('routes_found'):
                print(f"🔗 Routes trouvées: {len(result.get('routes_found'))}")
        else:
            print(f"❌ Erreur: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Erreur requête: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Test d'intégration terminé")
    
    return True

if __name__ == "__main__":
    test_integration_features()
