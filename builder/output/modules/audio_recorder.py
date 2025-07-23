import io
import wave
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

class AudioRecorder:
    def __init__(self):
        self.format = pyaudio.paInt16 if PYAUDIO_AVAILABLE else None
        self.channels = 2
        self.rate = 44100
        self.chunk = 1024
        
    def record(self, duration=5):
        # enregistre l'audio pendant duration secondes
        if not PYAUDIO_AVAILABLE:
            return None
            
        try:
            audio = pyaudio.PyAudio()
            
            # ouvre le stream
            stream = audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            frames = []
            
            # enregistre
            for _ in range(0, int(self.rate / self.chunk * duration)):
                data = stream.read(self.chunk)
                frames.append(data)
                
            # ferme le stream
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # cree le fichier WAV en memoire
            buffer = io.BytesIO()
            wf = wave.open(buffer, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            return buffer.getvalue()
            
        except Exception:
            return None