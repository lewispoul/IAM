#!/bin/bash

VENV_DIR="venv"

function activate_venv {
    source "$VENV_DIR/bin/activate"
}

function run_iam {
    activate_venv
    python3 core/runner.py
}

function run_chem_mode {
    activate_venv
    echo "🔬 Lancement d'IAM en mode chimie..."
    python3 core/runner.py --chem  # à personnaliser plus tard
}

function update_env {
    activate_venv
    echo "📦 Mise à jour de l'environnement..."
    git pull
    pip install -r requirements.txt
}

function push_changes {
    echo "🚀 Commit et push en cours..."
    git add .
    git commit -m "Auto-push via setup.sh"
    git push
}

function clean_temp {
    echo "🧹 Nettoyage des fichiers temporaires..."
    find . -name '*.pyc' -delete
    find . -name '__pycache__' -type d -exec rm -r {} +
    find . -name '.DS_Store' -delete
}

function reset_env {
    echo "♻️ Réinitialisation de l'environnement..."
    rm -rf "$VENV_DIR"
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install -r requirements.txt
}

# ------- Choix de l'option -------
case "$1" in
    --run)
        run_iam
        ;;
    --chem)
        run_chem_mode
        ;;
    --update)
        update_env
        ;;
    --push)
        push_changes
        ;;
    --clean)
        clean_temp
        ;;
    --reset)
        reset_env
        ;;
    *)
        echo "❌ Option invalide : $1"
        echo "Utilisation : ./setup.sh [--run | --chem | --update | --push | --clean | --reset]"
        ;;
esac

