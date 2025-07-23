import socket
import time
import threading
import json
import struct
from cryptography.fernet import Fernet

# config de test
HOST = "127.0.0.1"
PORT = 4444
KEY = b'ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg='

def test_server():
    """Lance un serveur de test minimaliste"""
    cipher = Fernet(KEY)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(1)
    
    print(f"[*] Test server listening on {HOST}:{PORT}")
    
    try:
        while True:
            client_sock, addr = sock.accept()
            print(f"[+] Connection from {addr}")
            
            # thread pour gérer le client
            client_thread = threading.Thread(
                target=handle_test_client, 
                args=(client_sock, cipher),
                daemon=True
            )
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\n[*] Stopping test server")
    finally:
        sock.close()

def handle_test_client(client_sock, cipher):
    """Gère un client de test"""
    try:
        while True:
            # recoit la taille
            size_data = recv_exact(client_sock, 4)
            if not size_data:
                break
                
            size = struct.unpack('!I', size_data)[0]
            print(f"[*] Receiving {size} bytes")
            
            # recoit le message
            message_data = recv_exact(client_sock, size)
            if not message_data:
                break
                
            # dechiffre
            try:
                decrypted = cipher.decrypt(message_data)
                message = json.loads(decrypted.decode())
                print(f"[*] Received: {message}")
                
                # repond selon le type
                if message.get("type") == "heartbeat":
                    response = {"type": "heartbeat_ack", "data": {}, "status": "ok"}
                else:
                    response = {"type": "response", "data": {"output": "Test OK"}, "status": "ok"}
                    
                # envoie la reponse
                response_json = json.dumps(response).encode()
                encrypted_response = cipher.encrypt(response_json)
                size = struct.pack('!I', len(encrypted_response))
                client_sock.sendall(size + encrypted_response)
                
            except Exception as e:
                print(f"[!] Error processing message: {e}")
                
    except Exception as e:
        print(f"[!] Client error: {e}")
    finally:
        client_sock.close()
        print("[*] Client disconnected")

def recv_exact(sock, length):
    """Recoit exactement length bytes"""
    data = b''
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            return None
        data += chunk
    return data

def test_client():
    """Lance un client de test minimaliste"""
    cipher = Fernet(KEY)
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        print(f"[+] Connected to {HOST}:{PORT}")
        
        # envoie un message de test
        test_message = {
            "type": "client_info",
            "data": {"os": "Test", "user": "TestUser"},
            "status": "ok"
        }
        
        message_json = json.dumps(test_message).encode()
        encrypted = cipher.encrypt(message_json)
        size = struct.pack('!I', len(encrypted))
        
        sock.sendall(size + encrypted)
        print("[*] Sent test message")
        
        # envoie des heartbeats
        for i in range(3):
            time.sleep(2)
            
            heartbeat = {
                "type": "heartbeat",
                "data": {},
                "status": "ok"
            }
            
            hb_json = json.dumps(heartbeat).encode()
            hb_encrypted = cipher.encrypt(hb_json)
            hb_size = struct.pack('!I', len(hb_encrypted))
            
            sock.sendall(hb_size + hb_encrypted)
            print(f"[*] Sent heartbeat {i+1}")
            
        sock.close()
        print("[*] Test client finished")
        
    except Exception as e:
        print(f"[!] Client error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "client":
        test_client()
    else:
        print("Usage:")
        print("  python test_connection.py          # Start test server")
        print("  python test_connection.py client   # Start test client")
        print()
        
        if len(sys.argv) == 1:
            test_server()