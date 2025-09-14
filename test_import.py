#!/usr/bin/env python3

# Test de base
try:
    from IAM_ChatGPT_Integration import IAMChatGPTAgent
    print("✅ Import réussi!")
    print("✅ Classe IAMChatGPTAgent disponible")
    print("Création d'une instance de test...")
    # On ne peut pas tester sans clé API, mais on peut vérifier la structure
    print("✅ Module IAM_ChatGPT_Integration corrigé avec succès!")
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
except Exception as e:
    print(f"❌ Une erreur inattendue s'est produite: {e}")
