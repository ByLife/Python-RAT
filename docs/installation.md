# Installation du projet RAT

## Prérequis

- Python 3.8+
- Poetry (optionnel mais recommandé)
- Git

## Installation avec Poetry

```bash
# Clone du projet
git clone <repo_url>
cd rat_project

# Installation des dépendances
poetry install

# Activation de l'environnement
poetry shell
```

## Installation avec pip

```bash
# Clone du projet
git clone <repo_url>
cd rat_project

# Creation environnement virtuel
python -m venv venv

# Activation (Linux/Mac)
source venv/bin/activate

# Activation (Windows)
venv\Scripts\activate

# Installation dépendances
pip install -r requirements.txt
```

## Dependances systeme

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3-dev portaudio19-dev
```

### Windows
- Installer Microsoft Visual C++ Build Tools
- Les autres dépendances s'installent automatiquement

### macOS
```bash
brew install portaudio
```

## Configuration pre-commit

```bash
pre-commit install
```

## Tests

```bash
# Avec Poetry
poetry run pytest

# Avec pip
pytest
```