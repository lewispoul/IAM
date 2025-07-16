#!/usr/bin/env python3
"""
Script de correction avancée pour le backend IAM
"""
import os
import sys
from pathlib import Path

def fix_backend_error_handling():
    """Améliore la gestion d'erreur du backend"""
    backend_path = "/home/lppou/IAM/IAM_GUI/backend.py"
    
    try:
        with open(backend_path, 'r') as f:
            content = f.read()
        
        # Ajouter une configuration plus robuste pour le serveur
        server_config = '''
# Configuration du serveur améliorée
def configure_app():
    """Configure l'application Flask avec les meilleures pratiques"""
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = '/tmp/iam_uploads'
    app.config['SECRET_KEY'] = 'iam-secret-key-change-in-production'
    
    # Créer le dossier de upload s'il n'existe pas
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app

# Ajouter la configuration d'erreur améliorée
@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "error": "Internal server error"}), 500

'''
        
        # Insérer la configuration après les imports s'il n'y est pas déjà
        if "configure_app" not in content:
            # Trouver la ligne où on déclare app = Flask()
            lines = content.split('\n')
            app_line = None
            for i, line in enumerate(lines):
                if "app = Flask(" in line:
                    app_line = i
                    break
            
            if app_line:
                lines.insert(app_line + 2, server_config)
                lines.insert(app_line + 3, "configure_app()")
                
                content = '\n'.join(lines)
                
                with open(backend_path, 'w') as f:
                    f.write(content)
                
                print("✅ Configuration backend améliorée")
                return True
        
        print("✅ Backend déjà configuré")
        return True
        
    except Exception as e:
        print(f"❌ Erreur correction backend: {e}")
        return False

def create_logging_config():
    """Crée une configuration de logging robuste"""
    log_config = '''
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    """Configure le système de logging"""
    log_dir = "/home/lppou/IAM/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Configuration du logger principal
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                os.path.join(log_dir, 'iam.log'),
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

logger = setup_logging()
'''
    
    try:
        log_path = "/home/lppou/IAM/IAM_config/logging_config.py"
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        
        with open(log_path, 'w') as f:
            f.write(log_config)
        
        print("✅ Configuration logging créée")
        return True
    except Exception as e:
        print(f"❌ Erreur création logging: {e}")
        return False

def create_docker_config():
    """Crée les fichiers Docker pour déploiement"""
    dockerfile_content = '''FROM python:3.12-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
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
'''

    docker_compose_content = '''version: '3.8'

services:
  iam:
    build: .
    ports:
      - "5002:5002"
    environment:
      - FLASK_ENV=production
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - iam
    restart: unless-stopped
'''

    try:
        # Dockerfile
        with open("/home/lppou/IAM/Dockerfile", 'w') as f:
            f.write(dockerfile_content)
        
        # Docker Compose
        with open("/home/lppou/IAM/docker-compose.yml", 'w') as f:
            f.write(docker_compose_content)
        
        print("✅ Configuration Docker créée")
        return True
    except Exception as e:
        print(f"❌ Erreur création Docker: {e}")
        return False

def create_monitoring_script():
    """Crée un script de monitoring"""
    monitoring_content = '''#!/usr/bin/env python3
"""
Script de monitoring IAM
"""
import psutil
import requests
import time
import logging
from datetime import datetime

def check_service_health():
    """Vérifie la santé du service IAM"""
    try:
        response = requests.get("http://localhost:5002/", timeout=5)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

def check_system_resources():
    """Vérifie les ressources système"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_percent = psutil.virtual_memory().percent
    disk_percent = psutil.disk_usage('/').percent
    
    return {
        'cpu': cpu_percent,
        'memory': memory_percent,
        'disk': disk_percent
    }

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('/home/lppou/IAM/logs/monitoring.log'),
            logging.StreamHandler()
        ]
    )
    
    while True:
        try:
            # Vérifier la santé du service
            service_ok = check_service_health()
            resources = check_system_resources()
            
            status = "🟢 OK" if service_ok else "🔴 DOWN"
            
            logging.info(f"IAM Service: {status}")
            logging.info(f"CPU: {resources['cpu']:.1f}% | "
                        f"Memory: {resources['memory']:.1f}% | "
                        f"Disk: {resources['disk']:.1f}%")
            
            # Alertes
            if not service_ok:
                logging.error("🚨 Service IAM inaccessible!")
            
            if resources['cpu'] > 80:
                logging.warning(f"⚠️  CPU élevé: {resources['cpu']:.1f}%")
            
            if resources['memory'] > 80:
                logging.warning(f"⚠️  Mémoire élevée: {resources['memory']:.1f}%")
            
            time.sleep(60)  # Vérification toutes les minutes
            
        except KeyboardInterrupt:
            logging.info("Arrêt du monitoring")
            break
        except Exception as e:
            logging.error(f"Erreur monitoring: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
'''

    try:
        with open("/home/lppou/IAM/monitor_iam.py", 'w') as f:
            f.write(monitoring_content)
        
        os.chmod("/home/lppou/IAM/monitor_iam.py", 0o755)
        print("✅ Script de monitoring créé")
        return True
    except Exception as e:
        print(f"❌ Erreur création monitoring: {e}")
        return False

def main():
    print("🔧 CORRECTIONS AVANCÉES IAM")
    print("="*40)
    
    corrections = [
        ("Gestion d'erreur backend", fix_backend_error_handling),
        ("Configuration logging", create_logging_config),
        ("Configuration Docker", create_docker_config),
        ("Script de monitoring", create_monitoring_script)
    ]
    
    success_count = 0
    for name, func in corrections:
        print(f"\n📝 {name}...")
        if func():
            success_count += 1
    
    print("\n" + "="*40)
    print(f"📊 Corrections avancées: {success_count}/{len(corrections)}")
    
    if success_count == len(corrections):
        print("🎉 Toutes les corrections avancées appliquées!")
        print("\n🚀 NOUVEAUX OUTILS DISPONIBLES:")
        print("   • monitor_iam.py - Monitoring en temps réel")
        print("   • Docker support - Déploiement containerisé")
        print("   • Logging avancé - Traçabilité complète")
    
    print("\n📋 FICHIERS CRÉÉS/MODIFIÉS:")
    files = [
        "✅ IAM_GUI/backend.py (amélioré)",
        "✅ IAM_config/logging_config.py",
        "✅ Dockerfile",
        "✅ docker-compose.yml", 
        "✅ monitor_iam.py"
    ]
    for f in files:
        print(f"   {f}")

if __name__ == "__main__":
    main()
