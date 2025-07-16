#!/bin/bash
"""
🚀 Script de démarrage IAM Molecule Viewer - Version Corrigée
Démarre le backend avec toutes les corrections appliquées
"""

echo "🔬 IAM Molecule Viewer - Démarrage"
echo "=================================="

# Vérifier l'environnement
cd /home/lppou/IAM/IAM_GUI

echo "📋 Vérification de l'environnement..."

# Vérifier Python
if ! command -v python &> /dev/null; then
    echo "❌ Python non trouvé"
    exit 1
fi

# Vérifier RDKit
if ! python -c "import rdkit" 2>/dev/null; then
    echo "❌ RDKit non installé"
    echo "💡 Installer avec: conda install rdkit"
    exit 1
fi

# Vérifier Flask
if ! python -c "import flask" 2>/dev/null; then
    echo "❌ Flask non installé"
    echo "💡 Installer avec: pip install flask flask-cors"
    exit 1
fi

echo "✅ Environnement OK"

# Vérifier que le port 5000 est libre
if netstat -tuln | grep -q ":5000 "; then
    echo "⚠️  Port 5000 déjà utilisé"
    echo "🔧 Arrêt du processus existant..."
    pkill -f "python.*backend.py" 2>/dev/null || true
    sleep 2
fi

# Démarrer le backend
echo "🚀 Démarrage du backend IAM..."
echo "📡 Interface disponible sur: http://localhost:5000"
echo "🔬 Fonctionnalités disponibles:"
echo "   ✅ SMILES → 3D Visualization"
echo "   ✅ Ketcher Integration"
echo "   ✅ XTB Calculations"
echo "   ✅ File Upload (XYZ/MOL)"
echo "   ✅ VoD Prediction"
echo "   ✅ Dark Mode"
echo ""
echo "🛑 Appuyer Ctrl+C pour arrêter"
echo ""

# Lancer avec gestion d'erreur
python backend.py
