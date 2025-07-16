#!/usr/bin/env python3
"""
Script de correction automatique des problèmes IAM
"""
import os
import sys
import subprocess
from pathlib import Path

def fix_requirements():
    """Nettoie et corrige le fichier requirements.txt"""
    print("🔧 Correction de requirements.txt...")
    
    clean_requirements = """flask>=2.0.0
flask-cors>=3.0.0
rdkit>=2022.9.0
numpy>=1.20.0
scipy>=1.7.0
pandas>=1.3.0
matplotlib>=3.4.0
jupyterlab>=3.0.0
requests>=2.25.0
python-dotenv>=0.19.0
py3Dmol>=2.0.0
openai>=1.0.0
scikit-learn>=1.0.0
torch>=1.9.0
transformers>=4.15.0"""

    try:
        with open("/home/lppou/IAM/requirements.txt", "w") as f:
            f.write(clean_requirements)
        print("✅ requirements.txt corrigé")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def create_startup_script():
    """Crée un script de démarrage robuste"""
    print("🔧 Création du script de démarrage...")
    
    startup_content = """#!/bin/bash
# Script de démarrage IAM

echo "🚀 Démarrage IAM..."

# Activation de l'environnement conda
source ~/miniconda3/etc/profile.d/conda.sh
conda activate chem-env

# Vérification et installation de XTB si nécessaire
if ! command -v xtb &> /dev/null; then
    echo "📦 Installation de XTB..."
    conda install -c conda-forge xtb -y
fi

# Installation des dépendances manquantes
echo "📦 Vérification des dépendances..."
pip install -r requirements.txt --quiet

# Vérification des ports
PORT=5002
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port $PORT occupé, utilisation du port 5003"
    PORT=5003
fi

# Démarrage du serveur
cd /home/lppou/IAM
echo "🌐 Démarrage sur http://localhost:$PORT"
python IAM_AutonomousAgent_Final.py --port $PORT
"""

    try:
        script_path = Path("/home/lppou/IAM/start_iam.sh")
        with open(script_path, "w") as f:
            f.write(startup_content)
        
        # Rendre exécutable
        os.chmod(script_path, 0o755)
        print("✅ Script de démarrage créé: start_iam.sh")
        return True
    except Exception as e:
        print(f"❌ Erreur création script: {e}")
        return False

def fix_backend_config():
    """Corrige la configuration du backend"""
    print("🔧 Correction de la configuration backend...")
    
    backend_path = Path("/home/lppou/IAM/IAM_GUI/backend.py")
    if not backend_path.exists():
        print("⚠️  backend.py non trouvé")
        return False
    
    try:
        # Lire le contenu actuel
        with open(backend_path, "r") as f:
            content = f.read()
        
        # Ajouter la gestion d'erreur améliorée si pas présente
        error_handler = '''
# Configuration du port dynamique
def get_available_port(start_port=5000):
    import socket
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return start_port

'''
        
        if "get_available_port" not in content:
            # Ajouter la fonction au début du fichier après les imports
            lines = content.split('\n')
            import_end = 0
            for i, line in enumerate(lines):
                if line.startswith('from ') or line.startswith('import '):
                    import_end = i
            
            lines.insert(import_end + 1, error_handler)
            content = '\n'.join(lines)
            
            with open(backend_path, "w") as f:
                f.write(content)
            
            print("✅ Configuration backend améliorée")
        else:
            print("✅ Configuration backend déjà optimisée")
        
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def create_env_file():
    """Crée un fichier .env avec les variables par défaut"""
    print("🔧 Création du fichier .env...")
    
    env_content = """# Configuration IAM
OPENAI_API_KEY=your_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
IAM_PORT=5002
IAM_HOST=0.0.0.0

# XTB Configuration
XTB_PATH=/home/lppou/miniconda3/envs/chem-env/bin/xtb

# Logging
LOG_LEVEL=INFO
LOG_FILE=/home/lppou/IAM/logs/iam.log
"""

    try:
        env_path = Path("/home/lppou/IAM/.env")
        if not env_path.exists():
            with open(env_path, "w") as f:
                f.write(env_content)
            print("✅ Fichier .env créé")
        else:
            print("✅ Fichier .env existe déjà")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def create_test_script():
    """Crée un script de test simple"""
    print("🔧 Création du script de test...")
    
    test_content = """#!/usr/bin/env python3
\"\"\"
Script de test rapide pour IAM
\"\"\"
import sys
import os
sys.path.append('/home/lppou/IAM')

def test_imports():
    print("🧪 Test des imports...")
    try:
        import flask
        print("✅ Flask")
        import rdkit
        print("✅ RDKit")
        import numpy
        print("✅ NumPy")
        import pandas
        print("✅ Pandas")
        return True
    except Exception as e:
        print(f"❌ Erreur import: {e}")
        return False

def test_xtb():
    print("🧪 Test XTB...")
    import subprocess
    try:
        result = subprocess.run(['xtb', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ XTB fonctionnel")
            return True
        else:
            print("❌ XTB erreur")
            return False
    except:
        print("❌ XTB non trouvé")
        return False

def test_backend():
    print("🧪 Test backend...")
    try:
        from IAM_GUI.backend import app
        print("✅ Backend importable")
        return True
    except Exception as e:
        print(f"❌ Backend erreur: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTS IAM")
    print("="*40)
    
    tests = [test_imports, test_xtb, test_backend]
    passed = 0
    
    for test in tests:
        if test():
            passed += 1
    
    print("="*40)
    print(f"📊 Résultats: {passed}/{len(tests)} tests réussis")
    
    if passed == len(tests):
        print("🎉 Tous les tests sont OK!")
        print("   Vous pouvez démarrer IAM avec: ./start_iam.sh")
    else:
        print("⚠️  Certains tests ont échoué")
        print("   Vérifiez l'installation des dépendances")
"""

    try:
        test_path = Path("/home/lppou/IAM/test_iam.py")
        with open(test_path, "w") as f:
            f.write(test_content)
        
        os.chmod(test_path, 0o755)
        print("✅ Script de test créé: test_iam.py")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    print("🔧 CORRECTION AUTOMATIQUE IAM")
    print("="*50)
    
    corrections = [
        ("Requirements.txt", fix_requirements),
        ("Script de démarrage", create_startup_script), 
        ("Configuration backend", fix_backend_config),
        ("Fichier .env", create_env_file),
        ("Script de test", create_test_script)
    ]
    
    success_count = 0
    for name, func in corrections:
        if func():
            success_count += 1
    
    print("="*50)
    print(f"📊 Corrections appliquées: {success_count}/{len(corrections)}")
    
    if success_count == len(corrections):
        print("🎉 Toutes les corrections ont été appliquées!")
        print("\n🚀 PROCHAINES ÉTAPES:")
        print("   1. Installer XTB: conda install -c conda-forge xtb")
        print("   2. Tester: python test_iam.py")
        print("   3. Démarrer: ./start_iam.sh")
    else:
        print("⚠️  Certaines corrections ont échoué")

if __name__ == "__main__":
    main()
