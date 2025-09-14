#!/usr/bin/env python3

"""
Test simple pour vérifier si README.md existe et peut être lu
"""

import os

def test_readme():
    print("🧪 Test simple de lecture README.md")
    print("=" * 40)
    
    # Vérifier si le fichier existe
    readme_path = "/home/lppou/IAM/README.md"
    print(f"📁 Chemin testé: {readme_path}")
    
    if os.path.exists(readme_path):
        print("✅ Le fichier README.md existe")
        
        # Lire le fichier
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"✅ Fichier lu avec succès!")
            print(f"📊 Taille: {len(content)} caractères")
            print(f"📄 Premières lignes:")
            print("-" * 30)
            lines = content.split('\n')[:5]
            for line in lines:
                print(f"  {line}")
            print("-" * 30)
            
        except Exception as e:
            print(f"❌ Erreur de lecture: {e}")
    else:
        print("❌ Le fichier README.md n'existe pas")
        
        # Lister le contenu du répertoire
        print("\n📂 Contenu du répertoire /home/lppou/IAM:")
        for item in os.listdir("/home/lppou/IAM")[:10]:
            print(f"  - {item}")

if __name__ == "__main__":
    test_readme()
