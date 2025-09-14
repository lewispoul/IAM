# 🚀 IAM Plateforme Autonome - Mode d'emploi

## 🎯 Vue d'ensemble

La plateforme IAM Autonome transforme votre projet en un système intelligent capable de générer, tester et intégrer automatiquement des modules Python par simple demande textuelle.

## 🚀 Démarrage rapide

### 1. Lancer la plateforme autonome



```bash
./launch_autonomous_agent.sh
```



### 2. Lancer l'interface web (dans un autre terminal)
```bash
cd IAM_GUI
python3 backend.py

```


### 3. Tester la plateforme
```bash
python3 test_autonomous_platform.py
```


## 🧠 Fonctionnalités principales


### Génération automatique de modules
L'agent peut créer des modules Python complets à partir d'une simple description :


**Via interface web :**
- Cliquer sur "🧠 Générer Module"
- Entrer le nom et la description
- Le module est généré, testé et intégré automatiquement


**Via API :**
```bash
curl -X POST http://localhost:5001/generate_module \\
  -H "Content-Type: application/json" \\
  -d '{

    "name": "vod_predictor",
    "description": "Prédit la vitesse de détonation à partir d un fichier XYZ",
    "output": "json"
  }'
```



### Tests automatiques
- Chaque module généré a son script de test
- Tests exécutés automatiquement
- Correction IA en cas d'échec (jusqu'à 3 tentatives)


### Intégration dynamique
- Modules automatiquement disponibles dans l'interface
- Boutons générés dynamiquement
- Résultats affichés en temps réel

## 📡 Endpoints API

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/generate_module` | POST | Génère un module Python automatiquement |
| `/test_module` | POST | Teste un module spécifique |
| `/list_modules` | GET | Liste tous les modules générés |
| `/run_shell` | POST | Exécute une commande shell |
| `/write_file` | POST | Crée/modifie un fichier |
| `/log_feedback` | POST | Enregistre un feedback utilisateur |
| `/run_backup` | POST | Lance une sauvegarde complète |
| `/health` | GET | Statut de santé du système |

## 🎮 Interface web intégrée

L'interface IAM Viewer inclut maintenant une section "🤖 Agent Autonome" avec :

- **🧠 Générer Module** : Créer un nouveau module
- **📋 Liste Modules** : Voir tous les modules générés
- **💾 Backup** : Sauvegarder le travail
- **🖥️ ls -la** : Exécuter des commandes shell
- **📝 Test Script** : Créer des scripts de test
- **📤 Feedback** : Envoyer des retours

## 📁 Structure des fichiers

```
IAM/
├── IAM_AutonomousAgent.py          # 🧠 Cœur de la plateforme autonome
├── launch_autonomous_agent.sh      # 🚀 Script de lancement
├── test_autonomous_platform.py     # 🧪 Tests de validation
├── GeneratedScripts/               # 📁 Modules générés automatiquement
│   ├── vod_predictor.py
│   ├── molecular_analyzer.py
│   └── [autres modules]
├── IAM_Logs/                       # 📊 Logs et historique

│   ├── agent_log.txt
│   ├── module_history.json
│   └── feedback_log.txt
└── [fichiers existants]
```


## 💬 Exemples d'usage


### 1. Générer un prédicteur VoD

```
Description: "Module qui prédit la vitesse de détonation d'un explosif à partir de sa formule chimique et de sa densité"
```


### 2. Créer un analyseur moléculaire
```

Description: "Analyse un fichier XYZ et calcule les distances de liaison, angles et propriétés géométriques"
```


### 3. Développer un convertisseur de formats

```
Description: "Convertit entre les formats MOL, XYZ, SMILES et PDB automatiquement"
```

## 🔧 Configuration avancée



### Variables d'environnement
- `IAM_AUTONOMOUS_PORT` : Port du serveur (défaut: 5001)
- `IAM_LOG_LEVEL` : Niveau de logging (DEBUG, INFO, WARNING, ERROR)

- `IAM_MAX_RETRIES` : Tentatives de correction IA (défaut: 3)


### Personnalisation des prompts
Éditez `IAM_AutonomousAgent.py` pour modifier les prompts de génération de code selon vos besoins spécifiques.


## 🚨 Résolution de problèmes


### Le serveur ne démarre pas
1. Vérifiez que le port 5001 est libre : `netstat -tulpn | grep 5001`
2. Vérifiez votre clé API OpenAI dans `agent_config.yaml`

3. Installez les dépendances : `pip install flask flask-cors openai`


### Les modules ne se génèrent pas
1. Vérifiez votre connexion internet

2. Vérifiez les quotas de votre API OpenAI
3. Consultez les logs : `tail -f IAM_Logs/agent_log.txt`


### L'interface web ne communique pas
1. Vérifiez que le serveur autonome tourne sur le port 5001
2. Vérifiez la configuration CORS
3. Ouvrez la console web pour voir les erreurs JavaScript

## 📈 Métriques et monitoring


### Logs automatiques
- Toutes les opérations sont loggées avec timestamp
- Historique JSON des modules générés
- Feedback utilisateur tracé


### Fichiers de monitoring
- `IAM_Logs/agent_log.txt` : Log principal
- `IAM_Logs/module_history.json` : Historique des modules
- `IAM_Logs/feedback_log.txt` : Retours utilisateurs

## 🔮 Fonctionnalités futures

- [ ] Base de données SQLite pour persistance
- [ ] Interface de monitoring en temps réel
- [ ] Templates de modules prédéfinis
- [ ] Génération de documentation automatique
- [ ] Intégration CI/CD pour les modules générés
- [ ] Support multi-langage (R, Julia, etc.)

## 🤝 Contribution


Pour ajouter de nouvelles fonctionnalités :
1. Étendre `IAM_AutonomousAgent.py` avec de nouveaux endpoints
2. Mettre à jour `script.js` pour les fonctions client
3. Ajouter les boutons dans `iam_viewer_connected.html`
4. Documenter dans ce README

---

**🎉 Félicitations ! Votre projet IAM est maintenant une plateforme autonome intelligente !**
