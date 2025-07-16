#!/bin/bash

# 🔄 Script de synchronisation WSL -> Pi
# Utilisation: ./sync_to_pi.sh

echo "🔄 IAM WSL -> Pi Sync Script"  
echo "============================="

# Vérifier si on est sur wsl-dev
current_branch=$(git branch --show-current)
if [ "$current_branch" != "wsl-dev" ]; then
    echo "❌ Erreur: Pas sur la branche wsl-dev"
    echo "🔧 Changement vers wsl-dev..."
    git checkout wsl-dev
fi

# Vérifier s'il y a des changements non commitées
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Changements non commitées détectés"
    echo "📝 Commit automatique..."
    
    read -p "💬 Message de commit (Enter pour défaut): " commit_msg
    if [ -z "$commit_msg" ]; then
        commit_msg="WSL: Auto-sync $(date '+%Y-%m-%d %H:%M')"
    fi
    
    git add .
    git commit -m "$commit_msg"
fi

# Push vers origin
echo "📤 Push vers origin/wsl-dev..."
git push origin wsl-dev

echo ""
echo "✅ Synchronisation WSL terminée!"
echo ""
echo "🥧 Prochaines étapes sur le Pi SSH:"
echo "   1. git checkout raspberry-pi-dev"
echo "   2. git pull origin wsl-dev"  
echo "   3. git merge wsl-dev"
echo "   4. Tester interface Pi"
echo "   5. git push origin raspberry-pi-dev"
echo ""
echo "📋 Ou copiez-coller:"
echo "git checkout raspberry-pi-dev && git pull origin wsl-dev && git merge wsl-dev"
