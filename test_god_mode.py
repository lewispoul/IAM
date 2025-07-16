#!/usr/bin/env python3
"""
Test du mode GOD MODE pour IAM Agent
"""

import os
import sys
import subprocess
from pathlib import Path

def test_god_mode():
    """Test des fonctionnalités du mode GOD"""
    print("🔥 TEST DU MODE GOD MODE 🔥")
    print("=" * 50)
    
    # Vérifier les variables d'environnement
    print("📋 Variables d'environnement:")
    print(f"IAM_GOD_MODE: {os.getenv('IAM_GOD_MODE', 'NOT SET')}")
    print(f"IAM_UNLIMITED_ACCESS: {os.getenv('IAM_UNLIMITED_ACCESS', 'NOT SET')}")
    print(f"IAM_SYSTEM_COMMANDS: {os.getenv('IAM_SYSTEM_COMMANDS', 'NOT SET')}")
    
    # Test d'accès aux dossiers IAM
    print("\n📁 Test d'accès aux dossiers:")
    directories = [
        "IAM_Knowledge",
        "IAM_Logs", 
        "IAM_Modules",
        "IAM_GUI"
        "IAM"
    ]
    
    for directory in directories:
        path = Path(directory)
        if path.exists():
            print(f"✅ {directory} - Accessible")
        else:
            print(f"⚠️  {directory} - Non trouvé (sera créé si nécessaire)")
    
    # Test de l'agent en mode GOD
    print("\n🤖 Test du lancement de l'agent GOD MODE:")
    print("Commande: python3 IAM_Agent.py --full-agent")
    print("(Pour tester manuellement)")
    
    # Vérifier que les fichiers principaux existent
    print("\n📄 Vérification des fichiers principaux:")
    files = [
        "IAM_Agent.py",
        "IAM_ChatGPT_Integration.py", 
        "IAM_FileManager.py",
        "autonomous_interface.html",
        "agent_config.yaml"
    ]
    
    for file in files:
        path = Path(file)
        if path.exists():
            print(f"✅ {file} - Présent")
        else:
            print(f"❌ {file} - Manquant")
    
    print("\n⚡ RÉCAPITULATIF:")
    print("🔥 Le mode GOD MODE est prêt à être activé")
    print("🚀 Lancez: python3 IAM_Agent.py --full-agent")
    print("⚡ L'indicateur GOD MODE apparaîtra dans l'interface")

if __name__ == "__main__":
    test_god_mode()
