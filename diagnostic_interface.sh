#!/bin/bash
echo "🔧 Script de diagnostic IAM Interface"
echo "====================================="
echo ""

echo "1. Vérification du backend..."
ps aux | grep python | grep backend | head -1
echo ""

echo "2. Test de l'interface..."
curl -s http://localhost:5000 | head -10
echo ""

echo "3. Vérification des templates..."
ls -la /home/lppou/IAM/IAM_GUI/templates/
echo ""

echo "4. Vérification Bootstrap..."
curl -s http://localhost:5000 | grep -o "Bootstrap" | head -1
echo ""

echo "✅ Si vous voyez 'Bootstrap' ci-dessus, l'interface fonctionne."
echo "🔄 Forcez le refresh de votre navigateur : Ctrl+F5"
echo "🌐 Ou essayez en mode incognito : http://localhost:5000"
