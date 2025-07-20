import unittest
import sys
import os

# ajoute le path du projet
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.config import Config
from shared.protocol import Protocol, Message

class TestCrypto(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.protocol = Protocol(self.config.get_cipher())
        
    def test_message_creation(self):
        # teste la creation d'un message
        msg = Message("test", {"data": "hello"})
        self.assertEqual(msg.type, "test")
        self.assertEqual(msg.data["data"], "hello")
        
    def test_message_serialization(self):
        # teste la serialisation/deserialisation
        msg = Message("test_cmd", {"key": "value"})
        
        # serialize
        packed = self.protocol.pack_message(msg)
        self.assertIsInstance(packed, bytes)
        
        # deserialize (sans la taille)
        unpacked = self.protocol.unpack_message(packed[4:])  # skip size header
        self.assertEqual(unpacked.type, "test_cmd")
        self.assertEqual(unpacked.data["key"], "value")
        
    def test_encryption(self):
        # teste que le chiffrement fonctionne
        msg = Message("secret", {"password": "123456"})
        packed = self.protocol.pack_message(msg)
        
        # verifie que le message est bien chiffré
        self.assertNotIn(b"secret", packed)
        self.assertNotIn(b"123456", packed)

if __name__ == "__main__":
    unittest.main()