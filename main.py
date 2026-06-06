# main.py
# This is the entry point of the Spellscribe app.
# Run this file to start the application.

import pygame
import sys
import config
from services.spell_loader import load_spells
from screens.parchment_wake_screen import ParchmentWakeScreen

# -------------------------------------------------------
# INITIALISE PYGAME
# -------------------------------------------------------
pygame.init()
pygame.mixer.init()  # Needed for all audio — touch sounds, ambient, cast sounds

# -------------------------------------------------------
# CREATE THE SCREEN
# -------------------------------------------------------
screen = pygame.display.set_mode(config.SCREEN_SIZE)
pygame.display.set_caption("Spellscribe — Lipika's Grimoire")

# -------------------------------------------------------
# CLOCK
# -------------------------------------------------------
clock = pygame.time.Clock()

# -------------------------------------------------------
# LOAD SPELL DATA
# -------------------------------------------------------
spells = load_spells()

# -------------------------------------------------------
# SCREEN MANAGER
# -------------------------------------------------------
# current_state tracks which state the app is in
# active_screen holds the screen object that is currently running
current_state = "WAKE"
active_screen = ParchmentWakeScreen(screen, spells)

# -------------------------------------------------------
# MAIN GAME LOOP
# -------------------------------------------------------
running = True

while running:

    # --- 1. HANDLE EVENTS ---
    for event in pygame.event.get():

        # Close the window
        if event.type == pygame.QUIT:
            running = False

        # Spacebar simulates the reed switch (book open/close)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if current_state == "SLEEP":
                    current_state = "WAKE"
                    active_screen = ParchmentWakeScreen(screen, spells)
                    print("Book opened — waking screen")
                else:
                    current_state = "SLEEP"
                    print("Book closed — sleeping screen")

        # Pass all events to the active screen when awake
        if current_state == "WAKE":
            active_screen.handle_event(event)

    # --- 2. UPDATE ---
    # This runs every frame regardless of whether an event happened
    if current_state == "WAKE":
        dt = clock.get_time()   # milliseconds since last frame
        active_screen.update(dt)

    # --- 3. DRAW ---
    if current_state == "SLEEP":
        screen.fill(config.BLACK)
    else:
        active_screen.draw()

    # Push the frame to the screen
    pygame.display.flip()

    # Lock to 60 FPS
    clock.tick(config.FPS)

# -------------------------------------------------------
# SHUTDOWN
# -------------------------------------------------------
pygame.quit()
sys.exit()