from panda3d.core import AudioSound

class SoundManager:
    def __init__(self, base):
        self.base = base
        self.music = None
        self.sound_effects = {}
        
    def play_music(self, file_path, loop=True, volume=0.5):
        try:
            self.music = self.base.loader.loadSfx(file_path)
            if self.music:
                self.music.setLoop(loop)
                self.music.setVolume(volume)
                self.music.play()
                print(f"✅ Música cargada: {file_path}")
            else:
                print(f"❌ No se pudo cargar la música: {file_path}")
        except Exception as e:
            print(f"❌ Error al cargar música: {e}")
    
    def stop_music(self):
        if self.music:
            self.music.stop()
    
    def set_music_volume(self, volume):
        if self.music:
            self.music.setVolume(volume)
    
    def play_sound(self, name, file_path=None, volume=1.0):
        """Reproduce un efecto de sonido. Si no tiene archivo, intenta usar uno precargado"""
        try:
            # Si el sonido no está cargado y se proporciona ruta, cargarlo
            if name not in self.sound_effects and file_path:
                sound = self.base.loader.loadSfx(file_path)
                if sound:
                    self.sound_effects[name] = sound
            
            # Reproducir el sonido si existe
            if name in self.sound_effects:
                sound = self.sound_effects[name]
                if sound:
                    sound.setVolume(volume)
                    sound.play()
        except Exception as e:
            print(f"❌ Error al reproducir sonido {name}: {e}")
    
    def preload_sound(self, name, file_path):
        """Precarga un sonido para uso posterior"""
        try:
            if name not in self.sound_effects:
                sound = self.base.loader.loadSfx(file_path)
                if sound:
                    self.sound_effects[name] = sound
                    print(f"✅ Sonido precargado: {name}")
                    return True
        except Exception as e:
            print(f"⚠️ No se pudo precargar sonido {name}: {e}")
        return False
    
    def cleanup(self):
        if self.music:
            self.music.stop()
        for sound in self.sound_effects.values():
            if sound:
                sound.stop()
                
    def setVolume(self, volume):
        if self.music:
            self.music.setVolume(volume)
            