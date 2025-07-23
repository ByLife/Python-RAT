"""
Script de lancement du builder RAT depuis la racine
Usage: python run_builder.py
"""

import sys
import os

# s'assure qu'on est dans le bon dossier
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# import et lancement
from builder.builder import main

if __name__ == "__main__":
    main()