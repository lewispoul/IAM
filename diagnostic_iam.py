#!/usr/bin/env python3
"""
Script de diagnostic IAM - Vérifie et résout les problèmes du projet
"""
import sys
import os
import subprocess
import importlib
import json
from pathlib import Path

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def check_python_version():
    print_header("VERSION PYTHON")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    if version.major != 3 or version.minor < 8:
        print("❌ Python 3.8+ requis")
        return False
    else:
        print("✅ Version Python compatible")
        return True

def check_conda_env():
    print_header("ENVIRONNEMENT CONDA")
    conda_env = os.environ.get('CONDA_DEFAULT_ENV', 'Aucun')
    print(f"Environnement actuel: {conda_env}")
    
    if conda_env == 'chem-env':
        print("✅ Environnement chem-env activé")
        return True
    else:
        print("⚠️  Environnement chem-env non activé")
        return False

def check_dependencies():
    print_header("DÉPENDANCES PYTHON")
    
    required_packages = [
        'flask', 'flask_cors', 'numpy', 'pandas', 'matplotlib',
        'requests', 'rdkit', 'scipy', 'jupyterlab'
    ]
    
    optional_packages = [
        'openai', 'torch', 'transformers', 'scikit-learn'
    ]
    
    problems = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package} - {e}")
            problems.append(package)
    
    print("\nPaquets optionnels:")
    for package in optional_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"⚠️  {package} - optionnel")
    
    return problems

def check_file_structure():
    print_header("STRUCTURE DES FICHIERS")
    
    base_dir = Path("/home/lppou/IAM")
    critical_files = [
        "IAM_AutonomousAgent_Final.py",
        "requirements.txt",
        "IAM_GUI/backend.py",
        "IAM_Molecule_Engine/",
        "webui/app.py"
    ]
    
    problems = []
    for file_path in critical_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - manquant")
            problems.append(file_path)
    
    return problems

def check_xtb_installation():
    print_header("INSTALLATION XTB")
    try:
        result = subprocess.run(['xtb', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ XTB installé et fonctionnel")
            print(f"Version: {result.stdout.strip()}")
            return True
        else:
            print("❌ XTB installé mais ne fonctionne pas")
            print(f"Erreur: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ XTB non trouvé")
        return False
    except subprocess.TimeoutExpired:
        print("❌ XTB timeout")
        return False

def check_ports():
    print_header("PORTS RÉSEAU")
    import socket
    
    ports_to_check = [5000, 5001, 5002, 8888]
    port_status = {}
    
    for port in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        if result == 0:
            print(f"⚠️  Port {port} déjà utilisé")
            port_status[port] = "occupé"
        else:
            print(f"✅ Port {port} disponible")
            port_status[port] = "libre"
        sock.close()
    
    return port_status

def fix_requirements():
    print_header("CORRECTION REQUIREMENTS.TXT")
    
    # Nettoyer requirements.txt
    requirements_path = Path("/home/lppou/IAM/requirements.txt")
    
    clean_requirements = [
        "flask>=2.0.0",
        "flask-cors>=3.0.0",
        "rdkit>=2022.9.0",
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "jupyterlab>=3.0.0",
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
        "py3Dmol>=2.0.0",
        "# Optional packages",
        "openai>=1.0.0",
        "scikit-learn>=1.0.0",
        "torch>=1.9.0",
        "transformers>=4.15.0"
    ]
    
    try:
        with open(requirements_path, 'w') as f:
            f.write('\n'.join(clean_requirements))
        print("✅ requirements.txt nettoyé")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la correction: {e}")
        return False

def install_missing_packages(missing_packages):
    print_header("INSTALLATION DES PAQUETS MANQUANTS")
    
    for package in missing_packages:
        print(f"Installation de {package}...")
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', package],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {package} installé")
            else:
                print(f"❌ Échec installation {package}: {result.stderr}")
        except Exception as e:
            print(f"❌ Erreur {package}: {e}")

def check_config_files():
    print_header("FICHIERS DE CONFIGURATION")
    
    config_files = {
        "/home/lppou/IAM/agent_config.yaml": "Configuration agent",
        "/home/lppou/IAM/chem-env.yaml": "Configuration environnement chimie",
        "/home/lppou/IAM/.env": "Variables d'environnement"
    }
    
    problems = []
    for file_path, description in config_files.items():
        if Path(file_path).exists():
            print(f"✅ {description}")
        else:
            print(f"⚠️  {description} - manquant (optionnel)")
            problems.append(file_path)
    
    return problems

def create_startup_script():
    print_header("CRÉATION SCRIPT DE DÉMARRAGE")
    
    startup_script = """#!/bin/bash
# Script de démarrage IAM

echo "🚀 Démarrage IAM..."

# Activation de l'environnement conda
source ~/miniconda3/etc/profile.d/conda.sh
conda activate chem-env

# Vérification XTB
if ! command -v xtb &> /dev/null; then
    echo "❌ XTB non trouvé - installation..."
    conda install -c conda-forge xtb -y
fi

# Démarrage du serveur principal
cd /home/lppou/IAM
python IAM_AutonomousAgent_Final.py

echo "✅ IAM démarré sur http://localhost:5002"
"""
    
    script_path = Path("/home/lppou/IAM/start_iam.sh")
    try:
        with open(script_path, 'w') as f:
            f.write(startup_script)
        
        # Rendre exécutable
        os.chmod(script_path, 0o755)
        print("✅ Script de démarrage créé: start_iam.sh")
        return True
    except Exception as e:
        print(f"❌ Erreur création script: {e}")
        return False

def generate_fix_report():
    print_header("RAPPORT DE DIAGNOSTIC ET CORRECTIONS")
    
    # Exécuter tous les checks
    python_ok = check_python_version()
    conda_ok = check_conda_env()
    missing_deps = check_dependencies()
    missing_files = check_file_structure()
    xtb_ok = check_xtb_installation()
    ports = check_ports()
    missing_configs = check_config_files()
    
    # Corrections automatiques
    req_fixed = fix_requirements()
    script_created = create_startup_script()
    
    if missing_deps:
        install_missing_packages(missing_deps)
    
    print_header("RÉSUMÉ FINAL")
    
    issues = []
    fixes = []
    
    if not python_ok:
        issues.append("Version Python incompatible")
    if not conda_ok:
        issues.append("Environnement conda non activé")
    if missing_deps:
        issues.append(f"Dépendances manquantes: {', '.join(missing_deps)}")
    if missing_files:
        issues.append(f"Fichiers manquants: {', '.join(missing_files)}")
    if not xtb_ok:
        issues.append("XTB non fonctionnel")
    
    if req_fixed:
        fixes.append("requirements.txt nettoyé")
    if script_created:
        fixes.append("Script de démarrage créé")
    
    print(f"\n📊 STATUT:")
    print(f"   Problèmes détectés: {len(issues)}")
    print(f"   Corrections appliquées: {len(fixes)}")
    
    if issues:
        print(f"\n❌ PROBLÈMES RESTANTS:")
        for issue in issues:
            print(f"   • {issue}")
    
    if fixes:
        print(f"\n✅ CORRECTIONS APPLIQUÉES:")
        for fix in fixes:
            print(f"   • {fix}")
    
    print(f"\n🔧 PROCHAINES ÉTAPES:")
    if not conda_ok:
        print("   1. Activer l'environnement: conda activate chem-env")
    if not xtb_ok:
        print("   2. Installer XTB: conda install -c conda-forge xtb")
    if missing_deps:
        print("   3. Installer dépendances: pip install -r requirements.txt")
    
    print("   4. Démarrer IAM: ./start_iam.sh")
    print("   5. Ouvrir http://localhost:5002")

if __name__ == "__main__":
    print("🔧 DIAGNOSTIC IAM - Analyse et correction des problèmes")
    generate_fix_report()
