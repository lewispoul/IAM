# 🔄 IAM Git Workflow - Raspberry Pi vs WSL

## Structure des branches

```
main                    ← Production stable
├── raspberry-pi-dev    ← Développement Raspberry Pi
└── wsl-dev            ← Développement WSL
```

## Workflow quotidien

### 🍓 Sur Raspberry Pi
```bash
git checkout raspberry-pi-dev
git add .
git commit -m "Pi: Interface fonctionnelle + backend optimisé"
git push origin raspberry-pi-dev
```

### 💻 Sur WSL
```bash
git checkout wsl-dev  
git add .
git commit -m "WSL: Tests + développement interface propre"
git push origin wsl-dev
```

## Échanger des fichiers entre environnements

### 1. Prendre un fichier du Pi vers WSL
```bash
# Sur WSL
git checkout wsl-dev
git checkout raspberry-pi-dev -- IAM_GUI/backend.py
git commit -m "Import backend.py from Pi version"
```

### 2. Prendre un fichier de WSL vers Pi
```bash
# Sur Pi
git checkout raspberry-pi-dev
git checkout wsl-dev -- IAM_GUI/templates/iam_clean.html
git commit -m "Import interface propre from WSL"
```

### 3. Merger des fonctionnalités spécifiques
```bash
# Cherry-pick un commit spécifique
git cherry-pick <commit-hash>
```

## Synchronisation périodique

### Merge vers main (quand stable)
```bash
git checkout main
git merge raspberry-pi-dev  # ou wsl-dev selon ce qui marche mieux
git push origin main
```

## Résolution de conflits
```bash
git status                    # Voir les conflits
git add <fichier-résolu>      # Après résolution manuelle
git commit -m "Resolve: ..."  # Finaliser
```

## Branches spécialisées
- `raspberry-pi-dev` : Interface Pi + backend optimisé ARM
- `wsl-dev` : Tests + développement + debugging
- `main` : Version stable qui marche partout

## Commandes utiles
```bash
git log --oneline --graph --all  # Visualiser l'arbre
git diff raspberry-pi-dev wsl-dev -- <fichier>  # Comparer
git stash                         # Sauver temporairement
git stash pop                     # Restaurer
```
