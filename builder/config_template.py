CLIENT_TEMPLATE = '''#!/usr/bin/env python3
# {filename}
# Generated RAT Client
import socket
import time
import threading
import platform
import subprocess
import os
import base64
import getpass
import sys
from cryptography.fernet import Fernet
import json
import struct

# Configuration generee par le builder
SERVER_HOST = "{server_host}"
SERVER_PORT = {server_port}
ENCRYPTION_KEY = b"{encryption_key}"

# Code du client complet seria ici...
# Pour le moment c'est juste un template

class GeneratedRatClient:
    def __init__(self):
        self.host = SERVER_HOST
        self.port = SERVER_PORT
        self.key = ENCRYPTION_KEY
        self.running = False
        
    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            print(f"[+] Connecte a {{self.host}}:{{self.port}}")
            return True
        except Exception as e:
            print(f"[-] Erreur connexion: {{e}}")
            return False
            
    def start(self):
        if self.connect():
            self.running = True
            print("[*] Client demarre")
            
            # boucle principale simplifiee
            while self.running:
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    break
                    
        self.disconnect()
        
    def disconnect(self):
        self.running = False
        if hasattr(self, 'sock'):
            try:
                self.sock.close()
            except:
                pass

if __name__ == "__main__":
    client = GeneratedRatClient()
    client.start()
'''

def generate_client(server_host, server_port, encryption_key, filename="client.py"):
    # genere le code du client avec la config
    return CLIENT_TEMPLATE.format(
        filename=filename,
        server_host=server_host,
        server_port=server_port,
        encryption_key=encryption_key.decode() if isinstance(encryption_key, bytes) else encryption_key
    )