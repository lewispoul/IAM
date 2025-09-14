#!/usr/bin/env python3

"""
Test rapide du IAMFileManager pour vérifier la lecture de fichiers
"""

from IAM_FileManager import IAMFileManager

def test_file_manager():
    """Test des fonctions du gestionnaire de fichiers"""
    print("🧪 Test du IAMFileManager")
    print("=" * 50)
    
    # Créer une instance avec le bon chemin
    fm = IAMFileManager(base_path="/home/lppou/IAM")
    fm.enable_god_mode()
    
    print("1. Test de lecture du fichier README.md")
    result = fm.read_file("README.md")
    
    if result.get("success"):
        content = result.get("content", "")
        print(f"✅ Fichier lu avec succès!")
        print(f"📊 Taille: {len(content)} caractères")
        print(f"📄 Début du contenu:")
        print("-" * 30)
        print(content[:200] + "..." if len(content) > 200 else content)
        print("-" * 30)
    else:
        print(f"❌ Erreur: {result.get('error')}")
    
    print("\n2. Test de listage du répertoire")
    list_result = fm.list_directory("")
    
    if list_result.get("success"):
        items = list_result.get("items", [])
        print(f"✅ Répertoire listé: {len(items)} éléments")
        print("📁 Premiers fichiers:")
        for item in items[:5]:
            print(f"  - {item['name']} ({item['type']})")
    else:
        print(f"❌ Erreur: {list_result.get('error')}")

if __name__ == "__main__":
    test_file_manager()
