#!/bin/bash
# 🔥 Script de Lancement GOD MODE + Interface Flask 🔥

echo "⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡"
echo "🔥🔥🔥🔥🔥 ACTIVATION GOD MODE + INTERFACE FLASK 🔥🔥🔥🔥🔥"
echo "⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡"
echo ""
echo "🚀 IAM - Plateforme Autonome Intelligente v2.0"
echo "⚡ GOD MODE + Interface Flask Combinés"
echo ""

# Activer l'environnement conda
echo "🔧 Activation de l'environnement conda..."
source ~/miniconda3/etc/profile.d/conda.sh
conda activate chem-env

# Définir les variables d'environnement GOD MODE
export IAM_GOD_MODE=TRUE
export IAM_UNLIMITED_ACCESS=TRUE
export IAM_SYSTEM_COMMANDS=TRUE

# Aller dans le répertoire IAM
cd /home/lppou/IAM

echo "✅ Variables GOD MODE définies"
echo "✅ Environnement conda activé"
echo ""

# Fonction pour démarrer l'interface Flask en arrière-plan
start_flask_interface() {
    echo "🌐 Démarrage de l'interface Flask..."
    cd IAM_GUI
    python backend.py &
    FLASK_PID=$!
    echo "✅ Interface Flask démarrée (PID: $FLASK_PID)"
    echo "🌐 Interface disponible sur: http://localhost:5000"
    cd ..
}

# Fonction pour démarrer le GOD MODE
start_god_mode() {
    echo "⚡ Lancement de l'agent en mode GOD..."
    python3 IAM_Agent.py --full-agent
}

# Fonction de nettoyage
cleanup() {
    echo ""
    echo "🧹 Nettoyage en cours..."
    if [ ! -z "$FLASK_PID" ]; then
        kill $FLASK_PID 2>/dev/null
        echo "✅ Interface Flask fermée"
    fi
    echo "👋 Au revoir!"
    exit 0
}

# Intercepter Ctrl+C pour le nettoyage
trap cleanup SIGINT

# Menu de sélection
echo "🎯 Options disponibles:"
echo "1) GOD MODE seul"
echo "2) Interface Flask seule" 
echo "3) GOD MODE + Interface Flask (recommandé)"
echo "4) Quitter"
echo ""
read -p "⚡ Choisissez une option (1-4): " choice

case $choice in
    1)
        echo "🔥 Lancement GOD MODE seul..."
        start_god_mode
        ;;
    2)
        echo "🌐 Lancement Interface Flask seule..."
        start_flask_interface
        echo "⌨️  Appuyez sur Ctrl+C pour arrêter"
        wait
        ;;
    3)
        echo "🔥🌐 Lancement GOD MODE + Interface Flask..."
        start_flask_interface
        sleep 3
        echo ""
        echo "🎯 CONFIGURATION COMPLÈTE ACTIVÉE:"
        echo "  🔥 GOD MODE: Agent autonome avec permissions étendues"
        echo "  🌐 FLASK: Interface web sur http://localhost:5000"
        echo "  ⚡ ACCÈS: Système complet + modification illimitée"
        echo ""
        echo "🚀 Lancement du GOD MODE (interface Flask en arrière-plan)..."
        start_god_mode
        ;;
    4)
        echo "👋 Au revoir!"
        exit 0
        ;;
    *)
        echo "❌ Option invalide"
        exit 1
        ;;
esac

# Nettoyage à la fin
cleanup
