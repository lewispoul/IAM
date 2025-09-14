#!/bin/bash

echo "🔧 Configuration de l'API OpenAI pour IAM"
echo "========================================"
echo ""
echo "Pour obtenir votre clé API OpenAI :"
echo "1. Allez sur https://platform.openai.com/account/api-keys"
echo "2. Créez une nouvelle clé API"
echo "3. Copiez la clé qui commence par 'sk-'"
echo ""

read -p "Entrez votre clé API OpenAI (sk-...): " OPENAI_KEY

if [[ $OPENAI_KEY == sk-* ]]; then
    echo ""
    echo "✅ Configuration de la clé API..."
    
    # Exporter la variable d'environnement
    export OPENAI_API_KEY="$OPENAI_KEY"
    
    # Ajouter au fichier .env si il existe, sinon le créer
    echo "OPENAI_API_KEY=$OPENAI_KEY" > .env
    
    echo "✅ Clé API configurée avec succès !"
    echo "🔄 Redémarrage de l'agent en cours..."
    
    # Arrêter l'ancien processus
    pkill -f "IAM_AutonomousAgent_Final.py" 2>/dev/null
    
    # Attendre un peu
    sleep 2
    
    # Relancer avec la nouvelle clé
    echo "🚀 Lancement de l'agent avec la nouvelle API..."
    OPENAI_API_KEY="$OPENAI_KEY" IAM_GOD_MODE=TRUE python IAM_AutonomousAgent_Final.py &
    
    echo "✅ Agent relancé avec la nouvelle clé API !"
    echo "📡 Interface disponible sur http://localhost:5002"
    
else
    echo "❌ Erreur: La clé API doit commencer par 'sk-'"
    echo "Veuillez relancer le script avec une clé valide."
fi
