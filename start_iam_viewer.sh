#!/bin/bash
# Script de démarrage automatique pour IAM Molecule Viewer

echo "🚀 Démarrage IAM Molecule Viewer"
echo "================================"

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "IAM_GUI/backend.py" ]; then
    echo "❌ Erreur: Script doit être exécuté depuis le répertoire /home/lppou/IAM"
    echo "   Répertoire actuel: $(pwd)"
    exit 1
fi

# Activer l'environnement conda
echo "🔧 Activation de l'environnement chem-env..."
source ~/miniconda3/etc/profile.d/conda.sh
conda activate chem-env

# Vérifier les dépendances critiques
echo "🔍 Vérification des dépendances..."

# Vérifier Python et RDKit
python -c "
import rdkit
from rdkit import Chem
print('✅ RDKit disponible:', rdkit.__version__)
" || {
    echo "❌ Erreur: RDKit non disponible"
    exit 1
}

# Vérifier Flask
python -c "
import flask
print('✅ Flask disponible:', flask.__version__)
" || {
    echo "❌ Erreur: Flask non disponible" 
    exit 1
}

# Vérifier XTB (optionnel)
if command -v xtb >/dev/null 2>&1; then
    echo "✅ XTB disponible: $(xtb --version 2>&1 | head -1)"
else
    echo "⚠️  XTB non trouvé dans PATH - calculs XTB indisponibles"
fi

# Aller dans le répertoire GUI
cd IAM_GUI

# Afficher les informations de lancement
echo ""
echo "🌐 Interface web: http://localhost:5000"
echo "📝 Logs: Affichés ci-dessous"
echo "🛑 Arrêt: Ctrl+C"
echo ""
echo "================================"

# Démarrer le backend
echo "🔬 Démarrage du backend Flask..."
python backend.py
