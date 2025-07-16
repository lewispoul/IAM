#!/usr/bin/env python3

from openai import OpenAI
import os

def test_openai_connection():
    """Test de connexion OpenAI"""
    try:
        print("🔍 Test de la connexion OpenAI...")
        
        # Vérifier la clé
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY non définie")
            return False
        
        print(f"✅ Clé API trouvée: {api_key[:20]}...")
        
        # Initialiser le client
        client = OpenAI()
        print("✅ Client OpenAI initialisé")
        
        # Test simple
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": "Réponds juste: Test réussi"}
            ],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ Test API réussi: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    success = test_openai_connection()
    print("\n" + "="*50)
    if success:
        print("🎉 OpenAI API fonctionne parfaitement !")
        print("✅ Vous pouvez maintenant utiliser toutes les fonctionnalités IA")
    else:
        print("❌ Problème avec l'API OpenAI")
    print("="*50)
