#!/bin/bash

echo "🔥 Choix d'agent IAM terminal 🔥"
echo "================================="
echo ""
echo "1. 🤖 Agent Chat simple        - python IAM_Agent.py --chat"
echo "2. ⚡ Agent GOD MODE complet   - python IAM_Agent.py --full-agent"  
echo "3. 🔥 Agent GOD MODE terminal  - python iam_god_terminal.py"
echo "4. 🔧 Assistant de codage      - python IAM_Agent.py --code"
echo ""

read -p "Votre choix (1-4): " choice

case $choice in
    1)
        echo "🚀 Lancement du chat simple..."
        python IAM_Agent.py --chat
        ;;
    2)
        echo "⚡ Lancement de l'agent GOD MODE complet..."
        python IAM_Agent.py --full-agent
        ;;
    3)
        echo "🔥 Lancement de l'agent GOD MODE terminal..."
        python iam_god_terminal.py
        ;;
    4)
        echo "🔧 Lancement de l'assistant de codage..."
        python IAM_Agent.py --code
        ;;
    *)
        echo "❌ Choix invalide"
        ;;
esac
