import io
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

class ScreenCapture:
    def __init__(self):
        self.method = self._detect_method()
        
    def _detect_method(self):
        # detecte la meilleure methode disponible
        if PIL_AVAILABLE:
            return "pil"
        elif MSS_AVAILABLE:
            return "mss"
        else:
            return None
            
    def take_screenshot(self):
        # prend une capture d'ecran
        try:
            if self.method == "pil":
                return self._screenshot_pil()
            elif self.method == "mss":
                return self._screenshot_mss()
            else:
                return None
        except Exception:
            return None
            
    def _screenshot_pil(self):
        # capture avec PIL
        try:
            screenshot = ImageGrab.grab()
            buffer = io.BytesIO()
            screenshot.save(buffer, format="PNG")
            return buffer.getvalue()
        except:
            return None
            
    def _screenshot_mss(self):
        # capture avec mss
        try:
            with mss.mss() as sct:
                # capture l'ecran principal
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                
                # convertit en PNG
                return mss.tools.to_png(screenshot.rgb, screenshot.size)
        except:
            return None