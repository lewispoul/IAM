#!/bin/bash

# 🚀 Script de Test Backend IAM Corrigé
echo "=== Test du Backend IAM Corrigé ==="

# Vérifier Python et environnement
echo "📋 Vérification environnement..."
python3 --version
which python3

# Vérifier les imports critiques
echo "🔍 Test imports RDKit..."
python3 -c "
try:
    from rdkit import Chem
    print('✅ RDKit OK')
except ImportError as e:
    print(f'❌ RDKit ERROR: {e}')

try:
    import flask
    print('✅ Flask OK')
except ImportError as e:
    print(f'❌ Flask ERROR: {e}')
"

# Test syntaxe backend
echo "🔧 Test syntaxe backend..."
python3 -m py_compile backend.py && echo "✅ Syntaxe OK" || echo "❌ Erreur syntaxe"

# Démarrer backend en mode test
echo "🚀 Démarrage backend en mode test..."
timeout 10 python3 backend.py &
BACKEND_PID=$!

# Attendre le démarrage
sleep 3

# Test endpoints de base
echo "🌐 Test endpoints..."

# Test endpoint racine
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/ && echo "✅ Endpoint / OK" || echo "❌ Endpoint / FAIL"

# Test endpoint health check basique
curl -s -X POST http://localhost:5000/smiles_to_xyz \
     -H "Content-Type: application/json" \
     -d '{"smiles":"CCO"}' \
     -w "Status: %{http_code}\n" || echo "❌ Test SMILES FAIL"

# Arrêter le backend
kill $BACKEND_PID 2>/dev/null

echo "=== Test Backend Terminé ==="
