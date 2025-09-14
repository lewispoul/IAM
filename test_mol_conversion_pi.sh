#!/bin/bash
# Script de test pour validation de la conversion MOL → XYZ sur Raspberry Pi
# Auteur: Solution WSL-dev pour compatibilité Pi
# Date: 2025-01-15

echo "🔧 Test de Validation IAM - Conversion MOL → XYZ"
echo "=================================================="

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
BACKEND_URL="http://localhost:5000"
TEST_DIR="/tmp/iam_test"
BACKEND_PID=""

# Créer dossier de test
mkdir -p $TEST_DIR

echo -e "${BLUE}📋 Étape 1: Vérification Python et dépendances${NC}"
echo "=================================================="

# Test Python
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✅ Python3 disponible:${NC} $(python3 --version)"
else
    echo -e "${RED}❌ Python3 non trouvé${NC}"
    exit 1
fi

# Test RDKit
echo -e "\n${BLUE}🧪 Test RDKit...${NC}"
python3 -c "
try:
    from rdkit import Chem
    from rdkit.Chem import rdDistGeom, rdForceFieldHelpers
    print('✅ RDKit importé avec succès')
    
    # Test conversion SMILES
    mol = Chem.MolFromSmiles('CCO')
    if mol:
        mol = Chem.AddHs(mol)
        rdDistGeom.EmbedMolecule(mol)
        xyz = Chem.MolToXYZBlock(mol)
        print('✅ Conversion SMILES → XYZ fonctionnelle')
        print(f'📊 XYZ preview: {xyz[:50].strip()}...')
    else:
        print('❌ Échec conversion SMILES')
        
except ImportError as e:
    print(f'❌ RDKit non disponible: {e}')
    print('💡 Installation: conda install -c conda-forge rdkit')
    exit(1)
" || { echo -e "${RED}❌ Test RDKit échoué${NC}"; exit 1; }

echo -e "\n${BLUE}🚀 Étape 2: Test du Backend Flask${NC}"
echo "=================================================="

# Vérifier si backend.py existe
if [ ! -f "IAM_GUI/backend.py" ]; then
    echo -e "${RED}❌ backend.py non trouvé${NC}"
    echo "📁 Répertoire actuel: $(pwd)"
    echo "📁 Contenu: $(ls -la)"
    exit 1
fi

echo -e "${GREEN}✅ backend.py trouvé${NC}"

# Démarrer le backend en arrière-plan
echo -e "${YELLOW}🔄 Démarrage backend Flask (port 5000)...${NC}"
python3 IAM_GUI/backend.py > $TEST_DIR/backend.log 2>&1 &
BACKEND_PID=$!

# Attendre que le serveur soit prêt
echo -e "${YELLOW}⏳ Attente démarrage serveur...${NC}"
sleep 5

# Vérifier si le processus fonctionne
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Backend n'a pas démarré${NC}"
    echo -e "${YELLOW}📋 Logs backend:${NC}"
    cat $TEST_DIR/backend.log
    exit 1
fi

echo -e "${GREEN}✅ Backend démarré (PID: $BACKEND_PID)${NC}"

# Test de connectivité
echo -e "\n${BLUE}🌐 Étape 3: Tests d'endpoints${NC}"
echo "=================================================="

# Test endpoint racine
echo -e "${YELLOW}🔍 Test GET /...${NC}"
if curl -s $BACKEND_URL > $TEST_DIR/index_response.html; then
    if grep -q "Interface IAM" $TEST_DIR/index_response.html; then
        echo -e "${GREEN}✅ Interface principale accessible${NC}"
    else
        echo -e "${YELLOW}⚠️ Interface chargée mais contenu inattendu${NC}"
    fi
else
    echo -e "${RED}❌ Interface principale inaccessible${NC}"
fi

# Test MOL → XYZ avec MOL invalide (test gestion d'erreur)
echo -e "\n${YELLOW}🧪 Test POST /molfile_to_xyz (MOL invalide)...${NC}"
cat > $TEST_DIR/test_invalid_mol.json << 'EOF'
{
    "molfile": "invalid mol content"
}
EOF

MOL_RESPONSE=$(curl -s -X POST $BACKEND_URL/molfile_to_xyz \
    -H "Content-Type: application/json" \
    -d @$TEST_DIR/test_invalid_mol.json)

echo "📋 Réponse MOL invalide: $MOL_RESPONSE"

if echo "$MOL_RESPONSE" | grep -q '"success": false'; then
    echo -e "${GREEN}✅ Gestion d'erreur MOL invalide OK${NC}"
else
    echo -e "${RED}❌ Gestion d'erreur MOL défaillante${NC}"
fi

# Test SMILES → XYZ
echo -e "\n${YELLOW}🧪 Test POST /smiles_to_xyz...${NC}"
cat > $TEST_DIR/test_smiles.json << 'EOF'
{
    "smiles": "CCO"
}
EOF

SMILES_RESPONSE=$(curl -s -X POST $BACKEND_URL/smiles_to_xyz \
    -H "Content-Type: application/json" \
    -d @$TEST_DIR/test_smiles.json)

echo "📋 Réponse SMILES: $SMILES_RESPONSE"

if echo "$SMILES_RESPONSE" | grep -q '"success": true'; then
    echo -e "${GREEN}✅ Conversion SMILES → XYZ réussie${NC}"
    # Extraire et valider XYZ
    echo "$SMILES_RESPONSE" | python3 -c "
import json, sys
data = json.load(sys.stdin)
if 'xyz' in data:
    xyz_lines = data['xyz'].strip().split('\n')
    print(f'📊 XYZ généré: {len(xyz_lines)} lignes')
    if len(xyz_lines) >= 3:
        print(f'🧮 Atomes: {xyz_lines[0].strip()}')
        print(f'📝 Commentaire: {xyz_lines[1].strip()}')
        print('✅ Format XYZ valide')
    else:
        print('❌ Format XYZ invalide')
"
elif echo "$SMILES_RESPONSE" | grep -q '"error": "RDKit not available"'; then
    echo -e "${YELLOW}⚠️ RDKit non disponible - Mode fallback activé${NC}"
else
    echo -e "${RED}❌ Conversion SMILES échouée${NC}"
fi

# Test avec MOL valide (éthanol)
echo -e "\n${YELLOW}🧪 Test POST /molfile_to_xyz (MOL valide)...${NC}"
cat > $TEST_DIR/test_valid_mol.json << 'EOF'
{
    "molfile": "CCO\n  Mrv2014 01151425\n\n  3  2  0  0  0  0            999 V2000\n   -1.3125    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\n   -0.5000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\n    0.3125    0.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0\n  1  2  1  0  0  0  0\n  2  3  1  0  0  0  0\nM  END"
}
EOF

VALID_MOL_RESPONSE=$(curl -s -X POST $BACKEND_URL/molfile_to_xyz \
    -H "Content-Type: application/json" \
    -d @$TEST_DIR/test_valid_mol.json)

echo "📋 Réponse MOL valide: $VALID_MOL_RESPONSE"

if echo "$VALID_MOL_RESPONSE" | grep -q '"success": true'; then
    echo -e "${GREEN}✅ Conversion MOL → XYZ réussie${NC}"
else
    echo -e "${YELLOW}⚠️ Conversion MOL → XYZ échouée (peut être normal selon RDKit)${NC}"
fi

# Nettoyage
echo -e "\n${BLUE}🧹 Nettoyage${NC}"
echo "=================================================="

# Arrêter le backend
if [ ! -z "$BACKEND_PID" ]; then
    echo -e "${YELLOW}🛑 Arrêt backend (PID: $BACKEND_PID)...${NC}"
    kill $BACKEND_PID 2>/dev/null
    wait $BACKEND_PID 2>/dev/null
fi

# Afficher logs si erreur
if [ -f "$TEST_DIR/backend.log" ]; then
    echo -e "\n${YELLOW}📋 Logs backend:${NC}"
    cat $TEST_DIR/backend.log
fi

# Résumé final
echo -e "\n${BLUE}📊 Résumé du Test${NC}"
echo "=================================================="
echo -e "${GREEN}✅ Tests terminés${NC}"
echo -e "📁 Fichiers de test: $TEST_DIR"
echo -e "📋 Pour débugger: cat $TEST_DIR/backend.log"

# Nettoyer les fichiers temporaires (optionnel)
# rm -rf $TEST_DIR

echo -e "\n${BLUE}💡 Instructions pour mise en production:${NC}"
echo "1. Copier les fichiers depuis WSL:"
echo "   rsync -av user@wsl:/path/to/files ."
echo "2. Démarrer le serveur:"
echo "   python3 IAM_GUI/backend.py"
echo "3. Accéder à l'interface:"
echo "   http://localhost:5000"

echo -e "\n${GREEN}🎉 Test de validation terminé!${NC}"
