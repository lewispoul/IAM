#!/bin/bash
# 📊 Script de diagnostic complet IAM
# Vérifie tous les composants essentiels du projet

echo "🔍 DIAGNOSTIC COMPLET IAM"
echo "=========================="

# 1. Structure des dossiers
echo "📁 Structure des dossiers:"
for dir in "IAM_Molecule_Engine" "IAM_GUI" "IAM_Knowledge" "IAM_Results" "IAM_EmpiricalPredictor"; do
    if [ -d "/home/lppou/IAM/$dir" ]; then
        echo "✅ $dir exists"
        ls -la "/home/lppou/IAM/$dir" | head -5
    else
        echo "❌ $dir MISSING"
    fi
done

# 2. Fichiers Python principaux
echo -e "\n🐍 Fichiers Python principaux:"
for file in "IAM_MoleculeEngine.py" "IAM_Agent.py" "start_all.sh" "IAM_PerformancePredictor.py"; do
    if [ -f "/home/lppou/IAM/$file" ]; then
        echo "✅ $file exists ($(wc -l < /home/lppou/IAM/$file) lines)"
    else
        echo "❌ $file MISSING"
    fi
done

# 3. Backend Flask
echo -e "\n🌐 Backend Flask:"
if [ -f "/home/lppou/IAM/IAM_GUI/backend.py" ]; then
    echo "✅ backend.py exists ($(wc -l < /home/lppou/IAM/IAM_GUI/backend.py) lines)"
else
    echo "❌ backend.py MISSING"
fi

# 4. Interface Web
echo -e "\n🖥️ Interface Web:"
if [ -f "/home/lppou/IAM/IAM_GUI/templates/iam_viewer_connected.html" ]; then
    echo "✅ Interface HTML exists ($(wc -l < /home/lppou/IAM/IAM_GUI/templates/iam_viewer_connected.html) lines)"
else
    echo "❌ Interface HTML MISSING"
fi

# 5. Base de données moléculaires
echo -e "\n📊 Base de données:"
if [ -f "/home/lppou/IAM/IAM_Master_Energetics.csv" ]; then
    echo "✅ IAM_Master_Energetics.csv exists ($(wc -l < /home/lppou/IAM/IAM_Master_Energetics.csv) lines)"
else
    echo "❌ IAM_Master_Energetics.csv MISSING"
fi

# 6. Outils XTB
echo -e "\n⚗️ Outils XTB:"
if command -v xtb &> /dev/null; then
    echo "✅ XTB installed: $(xtb --version 2>&1 | head -1)"
else
    echo "❌ XTB not found in PATH"
fi

# 7. Python packages
echo -e "\n📦 Python packages:"
python -c "
import sys
packages = ['rdkit', 'flask', 'flask_cors', 'pandas', 'numpy', 'sklearn']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg} available')
    except ImportError:
        print(f'❌ {pkg} MISSING')
"

echo -e "\n🏁 Diagnostic terminé"
