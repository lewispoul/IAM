#!/usr/bin/env python3
"""
Test GOD MODE Chat Integration
Vérification que le chat IA reconnaît et utilise le mode GOD
"""

import requests
import json
import time
import os

def test_god_mode_chat():
    print("🔥 TEST GOD MODE CHAT INTEGRATION 🔥")
    print("=" * 50)
    
    # URL de base
    base_url = "http://localhost:5002"
    
    try:
        # 1. Vérifier le statut GOD MODE
        print("1️⃣ Vérification du statut GOD MODE...")
        response = requests.get(f"{base_url}/god_mode_status")
        status = response.json()
        
        print(f"   GOD MODE: {status.get('god_mode', False)}")
        print(f"   Accès illimité: {status.get('unlimited_access', False)}")
        print(f"   OpenAI configuré: {status.get('openai_configured', False)}")
        
        # 2. Activer GOD MODE si pas activé
        if not status.get('god_mode', False):
            print("\n2️⃣ Activation du GOD MODE...")
            response = requests.post(f"{base_url}/activate_god_mode", json={})
            result = response.json()
            
            if result.get('success', False):
                print("   ✅ GOD MODE activé avec succès!")
            else:
                print(f"   ❌ Erreur activation: {result.get('error', 'Inconnue')}")
                return False
        
        # 3. Test du chat avec GOD MODE
        print("\n3️⃣ Test du chat IA avec GOD MODE...")
        
        chat_messages = [
            "Salut ! Peux-tu me dire si tu as accès aux fichiers ?",
            "Lis-moi le fichier README.md s'il te plaît",
            "Peux-tu lister les fichiers du dossier IAM_Knowledge ?",
            "Exécute la commande 'ls -la' pour moi"
        ]
        
        for i, message in enumerate(chat_messages, 1):
            print(f"\n   📩 Message {i}: {message}")
            
            chat_data = {
                "message": message,
                "image": None,
                "history": []
            }
            
            response = requests.post(f"{base_url}/chat", json=chat_data)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success', False):
                    chat_response = result.get('data', {}).get('response', '')
                    god_mode = result.get('data', {}).get('god_mode', False)
                    function_calling = result.get('data', {}).get('function_calling', False)
                    
                    print(f"   🔥 GOD MODE: {'✅' if god_mode else '❌'}")
                    print(f"   ⚡ Function Calling: {'✅' if function_calling else '❌'}")
                    print(f"   💬 Réponse: {chat_response[:100]}...")
                    
                    # Vérifier si la réponse contient des indications d'accès aux fichiers
                    if any(keyword in chat_response.lower() for keyword in [
                        'accès', 'fichier', 'dossier', 'commande', 'exécuter', 'lire'
                    ]):
                        print("   ✅ Réponse semble avoir accès aux fichiers")
                    else:
                        print("   ⚠️ Réponse générique - possiblement pas d'accès fichiers")
                        
                else:
                    print(f"   ❌ Erreur chat: {result.get('error', 'Inconnue')}")
                    
            else:
                print(f"   ❌ Erreur HTTP {response.status_code}: {response.text}")
            
            time.sleep(1)  # Pause entre les messages
        
        print("\n4️⃣ Test terminé!")
        print("=" * 50)
        print("🔍 Analyse des résultats:")
        print("- Si GOD MODE = ✅ et Function Calling = ✅ → Chat complet avec accès fichiers")
        print("- Si GOD MODE = ✅ et Function Calling = ❌ → Chat basique avec indication GOD")
        print("- Si GOD MODE = ❌ → Chat standard sans accès spécial")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Erreur: Impossible de se connecter au serveur")
        print("💡 Lancez d'abord: python IAM_AutonomousAgent_Final.py")
        return False
        
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    test_god_mode_chat()
