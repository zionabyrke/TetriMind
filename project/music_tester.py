import pygame
import os

pygame.init()
pygame.mixer.init()

# change directory if needed
music_file = "C:\\Python Projects\\TetriMind\\project\\assets\\music\\Tetris Theme.mp3"

print(f"File exists: {os.path.exists(music_file)}")
print(f"Current directory: {os.getcwd()}")

if os.path.exists(music_file):
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.set_volume(0.7)
    pygame.mixer.music.play(-1)
    print("Music should be playing...")
    input("Press Enter to stop...")
else:
    print("File not found!")