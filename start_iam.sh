#!/bin/bash
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
