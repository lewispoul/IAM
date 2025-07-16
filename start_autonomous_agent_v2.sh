#!/bin/bash

# Script de configuration pour IAM Autonomous Agent
echo "🔧 Configuration de IAM Autonomous Agent"
echo ""

# Vérifier si la clé API est déjà définie
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Variable OPENAI_API_KEY non définie"
    echo ""
    echo "Pour utiliser les fonctionnalités IA, vous devez configurer votre clé API OpenAI:"
    echo ""
    echo "1. Option temporaire (session actuelle):"
    echo "   export OPENAI_API_KEY='votre-clé-api-ici'"
    echo ""
    echo "2. Option permanente (ajouter au ~/.bashrc):"
    echo "   echo 'export OPENAI_API_KEY=\"votre-clé-api-ici\"' >> ~/.bashrc"
    echo "   source ~/.bashrc"
    echo ""
    echo "3. Lancer le script avec la clé:"
    echo "   OPENAI_API_KEY='votre-clé' python IAM_AutonomousAgent_v2.py"
    echo ""
else
    echo "✅ OPENAI_API_KEY configurée"
fi

echo "🚀 Démarrage de la plateforme..."
echo "📡 Interface disponible sur: http://localhost:5001"

# Lancer l'agent
python IAM_AutonomousAgent_v2.py
