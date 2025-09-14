#!/bin/bash
# launch_chatgpt_agent.sh - Script de lancement de l'agent ChatGPT avec accès complet

echo "🤖 Lancement de l'agent ChatGPT IAM avec accès complet au système"
echo "=============================================================="
echo ""
echo "Fonctionnalités disponibles:"
echo "📁 Gestion complète des fichiers"
echo "🐍 Exécution de code Python"
echo "🖥️  Exécution de commandes shell"
echo "📦 Installation de packages"
echo "🧪 Calculs XTB"
echo ""

cd /home/lppou/IAM

# Vérifier que les dépendances sont installées
echo "🔍 Vérification des dépendances..."

python3 -c "import openai, yaml, pandas, fitz" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Certaines dépendances manquent. Installation en cours..."
    pip3 install openai pyyaml pandas pymupdf
fi

# Vérifier la configuration
if [ ! -f "agent_config.yaml" ]; then
    echo "❌ Fichier de configuration agent_config.yaml manquant!"
    echo "Création d'un fichier template..."
    cat > agent_config.yaml << EOF
gpt4_api_key: "VOTRE_CLE_API_ICI"
gpt4_model: "gpt-4o"
EOF
    echo "⚠️  Veuillez éditer agent_config.yaml avec votre clé API OpenAI"
    exit 1
fi

echo "✅ Configuration OK"
echo ""

# Lancer l'agent
python3 IAM_Agent.py --full-agent
