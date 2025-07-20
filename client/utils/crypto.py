from cryptography.fernet import Fernet
import base64

class CryptoHelper:
    def __init__(self, key=None):
        if key:
            self.cipher = Fernet(key)
        else:
            # cle par defaut (sera remplacee par le builder)
            default_key = b'ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg='
            self.cipher = Fernet(default_key)
            
    def encrypt_string(self, text):
        # chiffre un string
        return self.cipher.encrypt(text.encode()).decode()
        
    def decrypt_string(self, encrypted_text):
        # dechiffre un string
        return self.cipher.decrypt(encrypted_text.encode()).decode()
        
    def encrypt_bytes(self, data):
        # chiffre des bytes
        return self.cipher.encrypt(data)
        
    def decrypt_bytes(self, encrypted_data):
        # dechiffre des bytes
        return self.cipher.decrypt(encrypted_data)