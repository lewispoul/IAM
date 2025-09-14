#!/bin/bash
# Script de synchronisation WSL → Raspberry Pi pour IAM
# Usage: ./sync_wsl_to_pi.sh [user@pi-address]

echo "🔄 Synchronisation IAM: WSL → Raspberry Pi"
echo "=========================================="

# Variables par défaut (à modifier selon votre config)
WSL_USER=${WSL_USER:-"pouli"}
WSL_HOST=${WSL_HOST:-"wsl-hostname"}
PI_USER=${PI_USER:-"pi"}
PI_HOST=${PI_HOST:-"raspberry-pi"}
IAM_PATH=${IAM_PATH:-"/home/pi/IAM"}

# Si argument fourni, l'utiliser comme destination
if [ $# -eq 1 ]; then
    PI_DESTINATION=$1
else
    PI_DESTINATION="${PI_USER}@${PI_HOST}:${IAM_PATH}"
fi

echo "📁 Destination: $PI_DESTINATION"

# Fonction pour copier avec vérification
copy_file() {
    local source=$1
    local dest_path=$2
    local description=$3
    
    if [ -f "$source" ]; then
        echo "📋 Copie: $description"
        rsync -av "$source" "${PI_DESTINATION}/${dest_path}"
        if [ $? -eq 0 ]; then
            echo "✅ $description - OK"
        else
            echo "❌ $description - ÉCHEC"
        fi
    else
        echo "⚠️ Fichier manquant: $source"
    fi
}

# Fichiers critiques à synchroniser
echo -e "\n🔧 Synchronisation des fichiers corrigés..."

# Backend principal
copy_file "IAM_GUI/backend.py" "IAM_GUI/" "Backend Flask corrigé"

# Interface corrigée
copy_file "IAM_GUI/templates/interface_corrected.html" "IAM_GUI/templates/" "Interface HTML corrigée"

# JavaScript corrigé
copy_file "IAM_GUI/static/iam_fixed.js" "IAM_GUI/static/" "JavaScript corrigé"

# Documentation
copy_file "SOLUTION_MOL_TO_XYZ.md" "" "Documentation solution"

# Script de test
copy_file "test_mol_conversion_pi.sh" "" "Script de test"

# Copier les modules IAM_Knowledge si nécessaire
if [ -d "IAM_Knowledge" ]; then
    echo "📋 Copie: Modules IAM_Knowledge"
    rsync -av "IAM_Knowledge/" "${PI_DESTINATION}/IAM_Knowledge/"
    if [ $? -eq 0 ]; then
        echo "✅ Modules IAM_Knowledge - OK"
    else
        echo "❌ Modules IAM_Knowledge - ÉCHEC"
    fi
fi

echo -e "\n📋 Instructions pour le Raspberry Pi:"
echo "======================================"
echo "1. Se connecter au Pi:"
echo "   ssh $PI_DESTINATION"
echo ""
echo "2. Aller dans le dossier IAM:"
echo "   cd $IAM_PATH"
echo ""
echo "3. Rendre le script de test exécutable:"
echo "   chmod +x test_mol_conversion_pi.sh"
echo ""
echo "4. Lancer le test de validation:"
echo "   ./test_mol_conversion_pi.sh"
echo ""
echo "5. Si le test passe, démarrer l'interface:"
echo "   python3 IAM_GUI/backend.py"
echo ""
echo "6. Accéder à l'interface:"
echo "   http://raspberry-pi-ip:5000"
echo ""

# Créer un fichier de vérification des modifications
cat > "/tmp/iam_sync_$(date +%Y%m%d_%H%M%S).txt" << EOF
Synchronisation IAM effectuée le $(date)
========================================

Fichiers synchronisés:
- IAM_GUI/backend.py (Backend Flask avec gestion RDKit)
- IAM_GUI/templates/interface_corrected.html (Interface corrigée)  
- IAM_GUI/static/iam_fixed.js (JavaScript fonctionnel)
- SOLUTION_MOL_TO_XYZ.md (Documentation complète)
- test_mol_conversion_pi.sh (Script de validation)

Points clés de la correction:
✅ Gestion gracieuse RDKit (fallback si indisponible)
✅ Endpoint /molfile_to_xyz fonctionnel
✅ Endpoint /smiles_to_xyz fonctionnel  
✅ Communication Ketcher ↔ Backend
✅ Notifications Toast pour feedback utilisateur
✅ Port 5000 pour Pi (5006 pour WSL)

Test de validation:
1. ./test_mol_conversion_pi.sh
2. Vérifier tous les ✅ dans la sortie
3. Démarrer: python3 IAM_GUI/backend.py
4. Tester dans navigateur: http://localhost:5000

Si problèmes:
- Vérifier installation RDKit: python3 -c "import rdkit; print('OK')"
- Lire logs: tail -f logs ou sortie console
- Comparer avec documentation SOLUTION_MOL_TO_XYZ.md
EOF

echo "📄 Fichier de vérification créé: /tmp/iam_sync_$(date +%Y%m%d_%H%M%S).txt"
echo ""
echo "🎉 Synchronisation terminée!"
echo "   Votre ami peut maintenant tester la solution sur le Raspberry Pi."
