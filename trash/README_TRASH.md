# Dossier Trash - Fichiers Obsolètes du Projet IAM

Date de nettoyage: 14 Juillet 2025

## Fichiers déplacés et raisons

### Versions de sauvegarde obsolètes
- `IAM_Agent_backup.py` - Ancienne version de sauvegarde d'IAM_Agent.py
- `IAM_Agent_fixed.py` - Version "corrigée" très similaire à IAM_Agent.py (doublon)
- `IAM_FileManager_backup.py` - Ancienne version de sauvegarde du FileManager
- `IAM_FileManager_clean.py` - Version intermédiaire nettoyée
- `IAM_FileManager_fixed.py` - Version corrigée remplacée par la version finale
- `IAM_FileManager_old.py` - Ancienne version du FileManager

### Anciens fichiers de test
- `test.py` - Ancien fichier de test général
- `test_gpt.py` - Test GPT obsolète
- `test_rapide.py` - Test rapide remplacé par test_final.py
- `test_simple.py` - Test simple remplacé par test_final.py
- `test_xtb.py` - Test XTB obsolète

### Scripts obsolètes
- `main.py` - Ancien point d'entrée remplacé par IAM_Agent.py
- `setup.sh` - Script de setup obsolète
- `start.sh` - Script de démarrage obsolète
- `check_config.py` - Vérification de config intégrée dans les modules

### Fichiers temporaires XTB
- `xtbopt.log` - Log d'optimisation XTB temporaire
- `xtbopt.xyz` - Géométrie optimisée temporaire
- `xtbout.json` - Sortie JSON temporaire XTB
- `xtbrestart` - Fichier de redémarrage XTB
- `xtbtopo.mol` - Topologie moléculaire temporaire
- `wbo` - Wiberg Bond Orders temporaires
- `charges` - Charges atomiques temporaires
- `.xtboptok` - Flag d'optimisation XTB

### Fichiers Zone.Identifier (Windows)
- `iam_update_db.py:Zone.Identifier`
- `iam.sh:Zone.Identifier`
- `reset_iam_env.sh:Zone.Identifier`
- `test_methane_xtb.py:Zone.Identifier`

### Dossiers obsolètes
- `Molecule_Engine/` - Doublon de IAM_Molecule_Engine/
- `webui/` - Interface web obsolète remplacée par IAM_GUI/

## Fichiers conservés (versions actuelles)
- `IAM_Agent.py` - Point d'entrée principal
- `IAM_FileManager.py` - Gestionnaire de fichiers final
- `IAM_CodeExecutor.py` - Exécuteur de code
- `IAM_ChatGPT_Integration.py` - Intégration ChatGPT
- `test_final.py` - Suite de tests complète
- `test_chatgpt_agent.py` - Test spécifique agent ChatGPT

## Actions recommandées
1. Ces fichiers peuvent être supprimés définitivement après vérification
2. Garder ce dossier trash pendant quelques semaines pour sécurité
3. Supprimer le contenu si aucun problème n'est détecté

## Nettoyage effectué par
GitHub Copilot - 14 Juillet 2025
