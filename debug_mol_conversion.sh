#!/bin/bash

# 🔍 SCRIPT DE DEBUG - Conversion MOL Problématique
# Ce script aide à identifier pourquoi certains fichiers MOL échouent

echo "🔍 IAM - Debug Conversion MOL"
echo "=================================="

# Tester avec différents échantillons MOL
echo ""
echo "📋 Test 1: MOL basique (Méthane)"
cat > /tmp/test_methane.mol << 'EOF'
  Mrv2014 07150000002D          

  1  0  0  0  0  0            999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
M  END
EOF

echo "🧪 Contenu MOL méthane:"
cat /tmp/test_methane.mol
echo ""

echo "🔬 Test conversion..."
MOL_CONTENT=$(cat /tmp/test_methane.mol | sed 's/$/\\n/' | tr -d '\n' | sed 's/\\n$//')
curl -X POST -H "Content-Type: application/json" \
  -d "{\"mol\": \"$MOL_CONTENT\"}" \
  http://127.0.0.1:5000/molfile_to_xyz 2>/dev/null | \
  python3 -m json.tool 2>/dev/null || echo "❌ Échec JSON"

echo ""
echo "=================================="
echo "📋 Test 2: MOL avec hydrogènes (Éthanol)"

cat > /tmp/test_ethanol.mol << 'EOF'
  Mrv2014 07150000002D          

  9  8  0  0  0  0            999 V2000
   -1.2500    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.2500    0.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
   -1.8660    0.8660    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   -1.8660   -0.8660    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
   -0.6340    0.8660    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
    0.6160    0.8660    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
    0.6160   -0.8660    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
    1.8660    0.0000    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  2  3  1  0  0  0  0
  1  4  1  0  0  0  0
  1  5  1  0  0  0  0
  1  6  1  0  0  0  0
  2  7  1  0  0  0  0
  2  8  1  0  0  0  0
  3  9  1  0  0  0  0
M  END
EOF

echo "🧪 Contenu MOL éthanol:"
cat /tmp/test_ethanol.mol | head -5
echo "[...tronqué...]"
echo ""

echo "🔬 Test conversion..."
MOL_CONTENT2=$(cat /tmp/test_ethanol.mol | sed 's/$/\\n/' | tr -d '\n' | sed 's/\\n$//')
curl -X POST -H "Content-Type: application/json" \
  -d "{\"mol\": \"$MOL_CONTENT2\"}" \
  http://127.0.0.1:5000/molfile_to_xyz 2>/dev/null | \
  python3 -m json.tool 2>/dev/null || echo "❌ Échec JSON"

echo ""
echo "=================================="
echo "📋 Test 3: Comparaison avec SMILES (référence)"

echo "🔬 Test SMILES éthanol (CCO)..."
curl -X POST -H "Content-Type: application/json" \
  -d '{"smiles": "CCO"}' \
  http://127.0.0.1:5000/smiles_to_xyz 2>/dev/null | \
  python3 -c "import json, sys; data=json.load(sys.stdin); print('✅ SMILES OK' if data.get('success') else '❌ SMILES Fail')" 2>/dev/null

echo ""
echo "=================================="
echo "📋 Résumé Debug"
echo "- MOL basique (méthane): Test effectué"
echo "- MOL complexe (éthanol): Test effectué" 
echo "- SMILES référence: Test effectué"
echo ""
echo "📝 Actions recommandées:"
echo "1. Analyser logs Flask: tail -20 flask.log"
echo "2. Vérifier format MOL dans patch_molblock()"
echo "3. Comparer avec sorties SMILES fonctionnelles"
echo "4. Identifier pattern d'échec spécifique"

# Nettoyer fichiers temporaires
rm -f /tmp/test_*.mol

echo ""
echo "🎯 Debug terminé. Analysez les résultats ci-dessus."
