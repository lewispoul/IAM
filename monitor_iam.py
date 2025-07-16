#!/usr/bin/env python3
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
