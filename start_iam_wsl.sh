#!/bin/bash

# 🚀 Script de démarrage IAM WSL
# Utilisation: ./start_iam_wsl.sh

echo "🔄 IAM WSL Startup Script"
echo "========================="

# Vérifier si on est dans le bon répertoire
if [ ! -d "IAM_GUI" ]; then
    echo "❌ Erreur: Lancez depuis le répertoire /home/pouli/IAM"
    exit 1
fi

# Vérifier la branche Git
current_branch=$(git branch --show-current)
echo "📂 Branche actuelle: $current_branch"

if [ "$current_branch" != "wsl-dev" ]; then
    echo "⚠️  Pas sur la branche wsl-dev. Changement..."
    git checkout wsl-dev
fi

# Vérifier si le port 5005 est libre
if lsof -Pi :5005 -sTCP:LISTEN -t >/dev/null ; then
    echo "❌ Port 5005 déjà utilisé!"
    echo "🔧 Arrêt du processus existant..."
    pkill -f "server_clean.py"
    sleep 2
fi

# Pull dernières mises à jour
echo "📥 Pull des dernières mises à jour..."
git pull origin wsl-dev

# Démarrer le serveur
echo "🚀 Démarrage du serveur IAM WSL sur port 5005..."
echo "📍 Interface: http://localhost:5005"
echo "⏸️  Arrêt avec Ctrl+C"
echo ""

python3 IAM_GUI/server_clean.py
