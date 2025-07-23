import os
import base64
import hashlib
from datetime import datetime

class FileHandler:
    def __init__(self, base_dir="./downloads"):
        self.base_dir = base_dir
        self.max_file_size = 50 * 1024 * 1024  # 50MB max
        
        # cree le dossier de telechargement
        os.makedirs(self.base_dir, exist_ok=True)
        
    def save_file(self, filename, data, client_id):
        # sauvegarde un fichier telecharge
        try:
            # cree un nom unique
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = self._sanitize_filename(filename)
            final_filename = f"client_{client_id}_{timestamp}_{safe_filename}"
            
            filepath = os.path.join(self.base_dir, final_filename)
            
            # verifie la taille
            if len(data) > self.max_file_size:
                return None, "File too large"
                
            # sauvegarde
            with open(filepath, "wb") as f:
                f.write(data)
                
            # calcule le hash
            file_hash = hashlib.md5(data).hexdigest()
            
            return filepath, file_hash
            
        except Exception as e:
            return None, str(e)
            
    def load_file_for_upload(self, filepath):
        # charge un fichier pour l'upload
        try:
            if not os.path.exists(filepath):
                return None, "File not found"
                
            file_size = os.path.getsize(filepath)
            if file_size > self.max_file_size:
                return None, "File too large"
                
            with open(filepath, "rb") as f:
                data = f.read()
                
            return data, None
            
        except Exception as e:
            return None, str(e)
            
    def _sanitize_filename(self, filename):
        # nettoie le nom de fichier
        # supprime les caracteres dangereux
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"
        safe_name = "".join(c for c in filename if c in safe_chars)
        
        # limite la longueur
        if len(safe_name) > 100:
            safe_name = safe_name[:100]
            
        return safe_name or "unknown_file"
        
    def get_file_info(self, filepath):
        # retourne les infos d'un fichier
        try:
            if not os.path.exists(filepath):
                return None
                
            stat = os.stat(filepath)
            return {
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
            }
        except:
            return None