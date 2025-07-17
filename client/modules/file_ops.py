import os
import glob
import shutil

class FileOperations:
    def __init__(self):
        pass
        
    def read_file(self, filepath):
        # lit un fichier et retourne ses donnees
        try:
            with open(filepath, "rb") as f:
                return f.read()
        except Exception:
            return None
            
    def write_file(self, filepath, data):
        # ecrit des donnees dans un fichier
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "wb") as f:
                f.write(data)
            return True
        except Exception:
            return False
            
    def search_files(self, pattern, max_results=100):
        # cherche des fichiers selon un pattern
        results = []
        try:
            # cherche dans le repertoire courant et sous-dossiers
            for root, dirs, files in os.walk("."):
                for file in files:
                    if pattern.lower() in file.lower():
                        full_path = os.path.join(root, file)
                        results.append(full_path)
                        if len(results) >= max_results:
                            break
                if len(results) >= max_results:
                    break
                    
            # cherche aussi avec glob dans certains dossiers communs
            common_dirs = []
            if os.name == "nt":  # windows
                common_dirs = [
                    os.path.expanduser("~\\Desktop"),
                    os.path.expanduser("~\\Documents"),
                    os.path.expanduser("~\\Downloads")
                ]
            else:  # linux/mac
                common_dirs = [
                    os.path.expanduser("~/Desktop"),
                    os.path.expanduser("~/Documents"),
                    os.path.expanduser("~/Downloads")
                ]
                
            for dir_path in common_dirs:
                if os.path.exists(dir_path) and len(results) < max_results:
                    try:
                        glob_pattern = os.path.join(dir_path, f"*{pattern}*")
                        matches = glob.glob(glob_pattern, recursive=True)
                        for match in matches[:max_results - len(results)]:
                            if match not in results:
                                results.append(match)
                    except:
                        continue
                        
        except Exception:
            pass
            
        return results[:max_results]