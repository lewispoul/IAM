#!/bin/bash

cd ~/IAM || exit
source ~/miniconda3/etc/profile.d/conda.sh
conda activate chem-env

# Lancer Flask en arrière-plan
nohup python3 IAM_GUI/backend.py > flask.log 2>&1 &

# Attente pour que le serveur démarre
sleep 3

# Lancer l’agent IA en arrière-plan
nohup python3 IAM_Agent.py > agent.log 2>&1 &

# Ouvrir l'interface dans un navigateur local (si interface GUI)
if command -v xdg-open &> /dev/null; then
  xdg-open http://localhost:5000
fi

echo "✅ IAM Agent + Interface Flask lancés."
