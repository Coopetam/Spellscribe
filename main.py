# main.py
# This is the entry point of the Spellscribe app.
# Run this file to start the application.

import pygame
import sys
import config
from services.spell_loader import load_spells

# -------------------------------------------------------
# INITIALISE PYGAME
# -------------------------------------------------------
# This wakes up all of Pygame's systems — display, audio,
# fonts, and input. Always the first thing in a Pygame app.
pygame.init()

# -------------------------------------------------------
# CREATE THE SCREEN
# -------------------------------------------------------
# This opens the window at the size defined in config.py
# pygame.FULLSCREEN makes it fill the entire screen (important on the RPi)
# For now on your PC it will open as a normal window instead
screen = pygame.display.set_mode(config.SCREEN_SIZE)
pygame.display.set_caption("Spellscribe — Lipika's Grimoire")

# -------------------------------------------------------
# CLOCK
# -------------------------------------------------------
# The clock controls how fast the game loop runs.
# We use it to lock the app to 60 frames per second (FPS).
clock = pygame.time.Clock()

# -------------------------------------------------------
# SCREEN STATE
# -------------------------------------------------------
# This variable tracks which screen the app is currently showing.
# We'll add more states as we build each screen.
# For now "WAKE" is the only state — it means the book was just opened.
# Load spell data at startup
spells = load_spells()

current_state = "WAKE"

# -------------------------------------------------------
# MAIN GAME LOOP
# -------------------------------------------------------
# This loop runs 60 times per second forever until the app closes.
# Every frame it does three things:
#   1. Handle events (taps, keypresses, reed switch)
#   2. Update the app state (animations, timers)
#   3. Draw everything to the screen

running = True

while running:

    # --- 1. HANDLE EVENTS ---
    # Pygame collects all input events into a queue each frame.
    # We loop through them and decide what to do with each one.
    for event in pygame.event.get():

        # If the user closes the window (clicks the X), stop the loop
        if event.type == pygame.QUIT:
            running = False

        # KEYBOARD SIMULATION OF REED SWITCH
        # On your PC we use the SPACEBAR to simulate opening/closing the book.
        # When the RPi arrives this will be replaced by the GPIO signal.
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Toggle between WAKE (book open) and SLEEP (book closed)
                if current_state == "SLEEP":
                    current_state = "WAKE"
                    print("Book opened — waking screen")
                else:
                    current_state = "SLEEP"
                    print("Book closed — sleeping screen")

    # --- 2. UPDATE ---
    # This is where we'll update animations and timers.
    # We'll fill this in as we build each screen.

    # --- 3. DRAW ---
    # Fill the screen with black every frame before drawing anything.
    # This prevents the previous frame from showing through.
    if current_state == "SLEEP":
        screen.fill(config.BLACK)
    else:
        # Temporary placeholder — deep indigo while we build the wake screen
        screen.fill(config.DEEP_INDIGO)

    # This pushes everything we just drew to the actual screen.
    # Without this line nothing would appear.
    pygame.display.flip()

    # --- LOCK TO 60 FPS ---
    # This makes the loop wait if it's running faster than 60fps.
    # Keeps animations smooth and consistent.
    clock.tick(config.FPS)

# -------------------------------------------------------
# SHUTDOWN
# -------------------------------------------------------
# When the loop ends, cleanly shut down Pygame and exit.
pygame.quit()
sys.exit()