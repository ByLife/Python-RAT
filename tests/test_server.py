import unittest
import threading
import time
import socket
import sys
import os

# ajoute le path du projet
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from server.rat_server import RatServer
from shared.config import Config
from shared.protocol import Protocol, Message

class TestServer(unittest.TestCase):
    def setUp(self):
        self.server = RatServer("127.0.0.1", 9999)  # port de test
        
    def test_server_creation(self):
        # teste la creation du serveur
        self.assertEqual(self.server.host, "127.0.0.1")
        self.assertEqual(self.server.port, 9999)
        self.assertFalse(self.server.running)
        
    def test_client_list(self):
        # teste la liste des clients
        clients = self.server.list_clients()
        self.assertEqual(len(clients), 0)
        
    def test_server_start_stop(self):
        # teste demarrage/arret serveur
        server_thread = threading.Thread(target=self.server.start, daemon=True)
        server_thread.start()
        
        time.sleep(0.5)  # laisse le temps de demarrer
        self.assertTrue(self.server.running)
        
        self.server.stop()
        time.sleep(0.5)
        self.assertFalse(self.server.running)

if __name__ == "__main__":
    unittest.main()