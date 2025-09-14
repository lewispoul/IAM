#!/bin/bash
# launch_autonomous_agent.sh - Lancement de la plateforme IAM autonome

echo "🚀 Lancement de la Plateforme IAM Autonome"
echo "=========================================="
echo ""
echo "🧠 Capacités de l'agent autonome:"
echo "   • Génération automatique de modules Python"
echo "   • Tests automatiques avec correction IA"  
echo "   • Intégration dynamique dans l'interface web"
echo "   • Sauvegarde intelligente"
echo "   • Feedback utilisateur en temps réel"
echo ""

cd /home/lppou/IAM

# Vérifier les dépendances
echo "🔍 Vérification des dépendances..."
python3 -c "import openai, yaml, pandas, fitz, flask, flask_cors" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Installation des dépendances manquantes..."
    pip3 install flask flask-cors
fi

# Vérifier la configuration
if [ ! -f "agent_config.yaml" ]; then
    echo "❌ Fichier agent_config.yaml manquant!"
    echo "Création d'un template..."
    cat > agent_config.yaml << EOF
gpt4_api_key: "VOTRE_CLE_API_ICI"
gpt4_model: "gpt-4o"
EOF
    echo "⚠️  Veuillez éditer agent_config.yaml avec votre clé API OpenAI"
    exit 1
fi

echo "✅ Configuration validée"
echo ""

# Créer les dossiers nécessaires
mkdir -p GeneratedScripts IAM_Logs

echo "🌐 Démarrage du serveur autonome sur le port 5001..."
echo "📡 Interface web disponible via l'endpoint Flask principal"
echo ""
echo "🔧 Endpoints disponibles:"
echo "   POST /generate_module - Générer un module automatiquement"
echo "   POST /test_module - Tester un module"
echo "   GET  /list_modules - Lister tous les modules"
echo "   POST /run_shell - Exécuter une commande shell"
echo "   POST /write_file - Créer/modifier un fichier"
echo "   POST /log_feedback - Enregistrer un feedback"
echo "   POST /run_backup - Lancer une sauvegarde"
echo "   GET  /health - Statut de santé du système"
echo ""

# Lancer l'agent autonome
python3 IAM_AutonomousAgent.py
