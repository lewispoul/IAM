FROM python:3.12-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Variables d'environnement
ENV FLASK_APP=IAM_AutonomousAgent_Final.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Port d'exposition
EXPOSE 5002

# Commande de démarrage
CMD ["python", "IAM_AutonomousAgent_Final.py"]
