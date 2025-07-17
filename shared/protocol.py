import json
import struct
import base64
from cryptography.fernet import Fernet

class Message:
    def __init__(self, cmd_type, data=None, status="ok"):
        self.type = cmd_type
        self.data = data or {}
        self.status = status
        
    def to_dict(self):
        return {
            "type": self.type,
            "data": self.data,
            "status": self.status
        }
        
    @classmethod
    def from_dict(cls, data):
        return cls(data["type"], data.get("data"), data.get("status", "ok"))

class Protocol:
    def __init__(self, cipher):
        self.cipher = cipher
        
    def pack_message(self, message):
        # serialize le message en json puis chiffre
        json_data = json.dumps(message.to_dict()).encode()
        encrypted = self.cipher.encrypt(json_data)
        
        # ajoute la taille au debut
        size = struct.pack('!I', len(encrypted))
        return size + encrypted
        
    def unpack_message(self, data):
        # dechiffre et deserialize
        try:
            decrypted = self.cipher.decrypt(data)
            json_data = json.loads(decrypted.decode())
            return Message.from_dict(json_data)
        except Exception as e:
            return None
            
    def receive_full_message(self, sock):
        # recoit un message complet
        try:
            # lit la taille d'abord
            size_data = self._recv_exact(sock, 4)
            if not size_data:
                return None
                
            size = struct.unpack('!I', size_data)[0]
            
            # puis lit le message
            message_data = self._recv_exact(sock, size)
            if not message_data:
                return None
                
            return self.unpack_message(message_data)
        except:
            return None
            
    def _recv_exact(self, sock, length):
        # recoit exactement length bytes
        data = b''
        while len(data) < length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                return None
            data += chunk
        return data