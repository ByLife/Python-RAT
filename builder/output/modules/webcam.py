import io
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

class WebcamCapture:
    def __init__(self):
        self.camera = None
        
    def take_photo(self):
        # prend une photo avec la webcam
        if not CV2_AVAILABLE:
            return None
            
        try:
            # ouvre la camera
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                return None
                
            # laisse le temps a la camera de s'initialiser
            import time
            time.sleep(1)
            
            # prend la photo
            ret, frame = self.camera.read()
            
            if ret:
                # encode en JPEG
                _, buffer = cv2.imencode('.jpg', frame)
                return buffer.tobytes()
            else:
                return None
                
        except Exception:
            return None
        finally:
            if self.camera:
                self.camera.release()
                self.camera = None