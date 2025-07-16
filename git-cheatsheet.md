# 🚀 Aide-mémoire Git Pi/WSL

## Navigation rapide
```bash
git checkout raspberry-pi-dev  # Aller sur branche Pi
git checkout wsl-dev          # Aller sur branche WSL
```

## Prendre un fichier d'une autre branche
```bash
# Du Pi vers WSL
git checkout wsl-dev
git checkout raspberry-pi-dev -- IAM_GUI/backend.py

# De WSL vers Pi  
git checkout raspberry-pi-dev
git checkout wsl-dev -- IAM_GUI/templates/iam_clean.html
```

## Comparer les versions
```bash
git diff wsl-dev raspberry-pi-dev -- IAM_GUI/backend.py
```

## Workflow quotidien
```bash
git fetch origin              # Récupérer les dernières versions
git add .                     # Ajouter modifications
git commit -m "WSL: ..."      # Commit avec préfixe
git push origin wsl-dev       # Push vers GitHub
```

---
**Référence complète :** `Guide-Git-Pi-WSL.md`
