# 🔄 Guide de Gestion Git : Raspberry Pi vs WSL

## 📋 Vue d'ensemble

Ce guide explique comment gérer le développement IAM entre deux environnements différents sans conflits de merge.

### **Structure des branches**
```
main                    ← Version stable de production
├── raspberry-pi-dev    ← Développement Raspberry Pi (optimisé ARM)
└── wsl-dev            ← Développement WSL (tests et expérimentation)
```

---

## 🏗️ Configuration initiale

### Premier setup sur Raspberry Pi
```bash
git checkout -b raspberry-pi-dev
git add .
git commit -m "Pi: Configuration initiale Raspberry Pi"
git push origin raspberry-pi-dev
```

### Premier setup sur WSL
```bash
git checkout -b wsl-dev
git add .
git commit -m "WSL: Configuration initiale WSL"
git push origin wsl-dev
```

---

## 🔄 Workflow quotidien

### 🍓 Développement sur Raspberry Pi
```bash
# Travailler sur la branche Pi
git checkout raspberry-pi-dev
git pull origin raspberry-pi-dev

# Faire vos modifications...
# Tester l'interface, optimiser pour ARM, etc.

git add .
git commit -m "Pi: [description des changements]"
git push origin raspberry-pi-dev
```

### 💻 Développement sur WSL
```bash
# Travailler sur la branche WSL
git checkout wsl-dev
git pull origin wsl-dev

# Faire vos modifications...
# Développer nouvelles features, tester interfaces, etc.

git add .
git commit -m "WSL: [description des changements]"
git push origin wsl-dev
```

---

## 🔄 Échanger des fichiers entre environnements

### 1. Prendre un fichier du Pi vers WSL
```bash
# Sur WSL
git checkout wsl-dev
git fetch origin                                    # Récupérer les dernières versions
git checkout raspberry-pi-dev -- chemin/vers/fichier.py
git commit -m "Import: [nom fichier] depuis version Pi"
```

**Exemple concret :**
```bash
git checkout wsl-dev
git checkout raspberry-pi-dev -- IAM_GUI/backend.py
git commit -m "Import: backend.py optimisé Pi vers WSL"
```

### 2. Prendre un fichier de WSL vers Pi
```bash
# Sur Raspberry Pi
git checkout raspberry-pi-dev
git fetch origin                                    # Récupérer les dernières versions
git checkout wsl-dev -- chemin/vers/fichier.html
git commit -m "Import: [nom fichier] depuis version WSL"
```

**Exemple concret :**
```bash
git checkout raspberry-pi-dev
git checkout wsl-dev -- IAM_GUI/templates/iam_clean.html
git commit -m "Import: interface propre sans boîtes blanches depuis WSL"
```

### 3. Prendre plusieurs fichiers d'un coup
```bash
# Prendre tout un dossier
git checkout wsl-dev -- IAM_Knowledge/
git commit -m "Import: tous les modules prédiction depuis WSL"

# Prendre des fichiers spécifiques
git checkout raspberry-pi-dev -- IAM_GUI/backend.py IAM_GUI/static/style.css
git commit -m "Import: backend + styles depuis Pi"
```

---

## 🔍 Comparer les versions

### Voir les différences entre branches
```bash
# Comparer un fichier spécifique
git diff wsl-dev raspberry-pi-dev -- IAM_GUI/templates/iam_viewer_connected.html

# Comparer tous les fichiers d'un dossier
git diff wsl-dev raspberry-pi-dev -- IAM_GUI/

# Voir la liste des fichiers différents
git diff --name-only wsl-dev raspberry-pi-dev
```

### Voir l'historique des branches
```bash
# Vue graphique de l'arbre Git
git log --oneline --graph --all

# Voir les commits récents de chaque branche
git log --oneline raspberry-pi-dev -10
git log --oneline wsl-dev -10
```

---

## 🚀 Synchronisation et merges

### Merger une branche vers main (quand stable)
```bash
git checkout main
git pull origin main

# Merger la version qui marche le mieux
git merge raspberry-pi-dev    # OU git merge wsl-dev
git push origin main
```

### Cherry-pick un commit spécifique
```bash
# Prendre juste un commit précis d'une autre branche
git cherry-pick <hash-du-commit>
git commit -m "Cherry-pick: [description]"
```

---

## 🛠️ Résolution de problèmes

### En cas de conflits de merge
```bash
git status                              # Voir les fichiers en conflit
# Éditer manuellement les fichiers pour résoudre les conflits
git add <fichier-résolu>
git commit -m "Resolve: conflit entre Pi et WSL versions"
```

### Annuler des changements
```bash
# Annuler le dernier commit (garde les fichiers modifiés)
git reset --soft HEAD~1

# Revenir à l'état du dernier commit (perd les modifications)
git reset --hard HEAD

# Sauvegarder temporairement des modifications
git stash                    # Sauver
git stash pop               # Restaurer
```

### Voir ce qui a changé
```bash
git status                   # État actuel
git diff                     # Différences non commitées
git diff --cached            # Différences en staging
```

---

## 📋 Stratégie par environnement

### 🍓 Raspberry Pi (`raspberry-pi-dev`)
**Objectif :** Version stable et optimisée
- Interface fonctionnelle et testée
- Backend optimisé pour ARM
- Performance et stabilité
- Configuration spécifique Pi

### 💻 WSL (`wsl-dev`)
**Objectif :** Développement et expérimentation
- Nouvelles fonctionnalités
- Tests d'interface (résolution problèmes CSS)
- Modules de prédiction
- Debugging et optimisation

### 🌟 Main (`main`)
**Objectif :** Version de production
- Code stable validé sur les deux environnements
- Documentation à jour
- Prêt pour déploiement

---

## 🎯 Exemples pratiques

### Scénario 1: Interface marche mieux sur WSL
```bash
# Sur Pi, récupérer l'interface WSL
git checkout raspberry-pi-dev
git checkout wsl-dev -- IAM_GUI/templates/iam_clean.html
git commit -m "Fix: interface propre sans boîtes blanches depuis WSL"
```

### Scénario 2: Backend marche mieux sur Pi
```bash
# Sur WSL, récupérer le backend Pi
git checkout wsl-dev  
git checkout raspberry-pi-dev -- IAM_GUI/backend.py
git commit -m "Fix: backend optimisé ARM depuis Pi"
```

### Scénario 3: Nouveau module développé sur WSL
```bash
# Sur Pi, récupérer le nouveau module
git checkout raspberry-pi-dev
git checkout wsl-dev -- IAM_Knowledge/IAM_NewModule.py
git commit -m "Add: nouveau module depuis WSL"
```

---

## 📞 Commandes de référence rapide

```bash
# Navigation entre branches
git checkout raspberry-pi-dev
git checkout wsl-dev
git checkout main

# Synchronisation
git fetch origin                    # Récupérer sans merger
git pull origin <branche>          # Récupérer et merger

# Import de fichiers
git checkout <branche-source> -- <fichier>

# Comparaison
git diff wsl-dev raspberry-pi-dev -- <fichier>

# Historique
git log --oneline --graph --all
```

---

## 💡 Bonnes pratiques

1. **Toujours fetch avant de travailler** : `git fetch origin`
2. **Commits descriptifs** : `"Pi: fix interface"` ou `"WSL: add module"`
3. **Test avant merge vers main** : Valider sur les deux environnements
4. **Backup régulier** : Push vers origin fréquemment
5. **Documentation** : Noter les changements importants

---

*Guide créé le 15 juillet 2025 pour la gestion du projet IAM*
