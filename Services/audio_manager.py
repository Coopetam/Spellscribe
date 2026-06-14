# services/audio_manager.py
# Handles all audio for the Spellscribe app.
# Manages the ambient background loop and sound effects.

import pygame
import config

def start_ambient():
    """
    Starts the ambient background music looping.
    Called as soon as the book opens.
    -1 means loop forever.
    """
    try:
        pygame.mixer.music.load(config.AMBIENT_SOUND)
        pygame.mixer.music.set_volume(0.5)  # 50% volume — adjust to taste
        pygame.mixer.music.play(-1)         # -1 = loop forever
        print("Ambient music started.")
    except FileNotFoundError:
        print(f"WARNING: Ambient sound not found at {config.AMBIENT_SOUND}")

def stop_ambient():
    """
    Stops the ambient music immediately.
    Called when the book closes.
    """
    pygame.mixer.music.stop()
    print("Ambient music stopped.")

def fade_out_ambient(duration_ms=500):
    """
    Fades the ambient music out over duration_ms milliseconds.
    Smoother than stopping abruptly.
    """
    pygame.mixer.music.fadeout(duration_ms)
    print("Ambient music fading out.")