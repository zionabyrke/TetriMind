import pygame
import os

class MusicManager:
    def __init__(self):
        pygame.mixer.init()
        self.is_playing = False
        self.volume = 0.3  # Default volume (0.0 to 1.0)
        
    def load_music(self, music_file):
        try:
            if os.path.exists(music_file):
                pygame.mixer.music.load(music_file)
                return True
            else:
                print(f"Music file not found: {music_file}")
                return False
        except pygame.error as e:
            print(f"Error loading music: {e}")
            return False
    
    def play(self, loops=-1, fade_ms=0):
        try:
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play(loops, fade_ms=fade_ms)
            self.is_playing = True
        except pygame.error as e:
            print(f"Error playing music: {e}")
    
    def stop(self, fade_ms=0):
        if fade_ms > 0:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()
        self.is_playing = False
    
    def pause(self):
        pygame.mixer.music.pause()
        self.is_playing = False
    
    def unpause(self):
        pygame.mixer.music.unpause()
        self.is_playing = True
    
    # Set the music volume to: 0.0 to 1.0
    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))  # Clamp between 0 and 1
        pygame.mixer.music.set_volume(self.volume)
    
    def get_volume(self):
        return self.volume
    
    def is_music_playing(self):
        return pygame.mixer.music.get_busy()


# Global music manager instance
music_manager = MusicManager()

# Change directory to your preference, Supported formats: MP3, OGG, WAV
def play_menu_music(music_file="project/assets/music/Tetris Theme.mp3"):
    if music_manager.load_music(music_file):
        music_manager.play(loops=-1, fade_ms=1000)  
        return True
    return False

def stop_menu_music(fade_ms=1000):
    music_manager.stop(fade_ms)