import unittest
import sys
import os

# ajoute le path du projet
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from client.modules.system_info import SystemInfo
from client.modules.file_ops import FileOperations
from shared.protocol import Message

class TestClientModules(unittest.TestCase):
    def setUp(self):
        self.sysinfo = SystemInfo()
        self.fileops = FileOperations()
        
    def test_system_info(self):
        # teste la recuperation d'infos systeme
        info = self.sysinfo.get_system_info()
        
        self.assertIn("os", info)
        self.assertIn("user", info)
        self.assertIn("hostname", info)
        
    def test_network_info(self):
        # teste la recuperation d'infos reseau
        network_info = self.sysinfo.get_network_info()
        self.assertIsInstance(network_info, str)
        self.assertGreater(len(network_info), 0)
        
    def test_file_operations(self):
        # teste les operations fichier
        test_data = b"test data for file operations"
        test_file = "/tmp/test_rat_file.txt"
        
        # teste l'ecriture
        success = self.fileops.write_file(test_file, test_data)
        self.assertTrue(success)
        
        # teste la lecture
        read_data = self.fileops.read_file(test_file)
        self.assertEqual(read_data, test_data)
        
        # nettoie
        try:
            os.remove(test_file)
        except:
            pass
            
    def test_file_search(self):
        # teste la recherche de fichiers
        results = self.fileops.search_files("test", max_results=5)
        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 5)

if __name__ == "__main__":
    unittest.main()