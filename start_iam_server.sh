#!/bin/bash

cd ~/IAM/IAM_GUI
echo "?? Démarrage du serveur Flask IAM..."
pkill -f backend.py 2>/dev/null
nohup python3 backend.py > ~/IAM/flask.log 2>&1 &
echo "✅ Serveur IAM lancé sur http://$(hostname -I | awk '{print $1}'):5000"
