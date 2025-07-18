# RAT Project - Remote Administration Tool

Projet académique de développement d'un outil d'administration à distance en Python.

## ⚠️ Avertissement

Ce projet est développé uniquement dans un contexte éducatif pour apprendre les concepts de sécurité informatique. L'utilisation malveillante de cet outil est strictement interdite.

## Structure du projet

```
rat_project/
├── server/          # Code du serveur
├── client/          # Code du client
├── shared/          # Code partagé (protocole, config)
├── builder/         # Builder pour générer le client
├── tests/           # Tests unitaires
└── docs/           # Documentation
```

## Installation

### Avec Poetry (recommandé)

```bash
# Installation des dépendances
poetry install

# Activation de l'environnement virtuel
poetry shell
```

### Avec pip

```bash
pip install -r requirements.txt
```

## Utilisation

### 1. Lancement du serveur

```bash
cd server/
python main.py
```

Le serveur écoute par défaut sur le port 4444.

### 2. Génération du client

```bash
cd builder/
python builder.py
```

Suivez les instructions pour configurer l'IP et le port du serveur.

### 3. Déploiement du client

Copiez le client généré sur la machine cible et exécutez-le.

## Fonctionnalités

### Serveur
- Interface interactive multi-clients
- Gestion des sessions
- Commandes de base (help, sessions, interact)

### Client
- Communication chiffrée TCP
- Fonctionnalités système :
  - `ipconfig` - Configuration réseau
  - `screenshot` - Capture d'écran
  - `shell` - Exécution de commandes
  - `download/upload` - Transfert de fichiers
  - `search` - Recherche de fichiers
  - `hashdump` - Extraction de hashes
  - `keylogger` - Enregistrement de frappes
  - `webcam_snapshot` - Photo webcam
  - `record_audio` - Enregistrement audio

## Sécurité

- Communication chiffrée avec cryptography (Fernet)
- Gestion d'erreurs robuste
- Timeout des connexions

## Tests

```bash
pytest tests/
```

## Développement

### Pre-commit hooks

```bash
pre-commit install
```

### Formatage du code

```bash
black .
flake8 .
```

## Auteurs

Projet réalisé dans le cadre du cours de sécurité informatique.

## Licence

Ce projet est strictement à des fins éducatives.