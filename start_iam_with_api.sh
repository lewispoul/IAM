#!/bin/bash
# Configuration environnement IAM avec clé API OpenAI

echo "🔧 Configuration de l'environnement IAM..."

# Configuration de la clé API OpenAI
export OPENAI_API_KEY="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"

echo "✅ OPENAI_API_KEY configurée"
echo "🚀 Lancement de la plateforme IAM avec IA complète..."

# Lancer la plateforme
python IAM_AutonomousAgent_v2.py
