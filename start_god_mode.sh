#!/bin/bash
# Script de démarrage du mode GOD MODE pour IAM

echo "⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡"
echo "🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 ACTIVATION MODE GOD 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥"
echo "⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡"
echo ""
echo "🚀 IAM - Plateforme Autonome Intelligente v2.0"
echo "⚡ GOD MODE - Permissions étendues activées"
echo ""
echo "✅ Accès illimité au système de fichiers"
echo "✅ Exécution libre de commandes shell" 
echo "✅ Modification complète du code source"
echo "✅ Permissions étendues sur tous les dossiers IAM"
echo "✅ Pas de limitations de sécurité"
echo ""
echo "⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡"

# Activer l'environnement conda
source ~/miniconda3/etc/profile.d/conda.sh
conda activate chem-env

# Définir les variables d'environnement GOD MODE
export IAM_GOD_MODE=TRUE
export IAM_UNLIMITED_ACCESS=TRUE
export IAM_SYSTEM_COMMANDS=TRUE

# Aller dans le répertoire IAM
cd /home/lppou/IAM

echo "🔥 Lancement de l'agent en mode GOD..."
echo ""

# Lancer l'agent en mode GOD
python3 IAM_Agent.py --full-agent
