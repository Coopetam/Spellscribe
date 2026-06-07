# main.py
# This is the entry point of the Spellscribe app.
# Run this file to start the application.

import pygame
import sys
import config
from services.spell_loader import load_spells
from screens.parchment_wake_screen import ParchmentWakeScreen
from screens.grimoire_screen import GrimoireScreen
from screens.spell_detail_screen import SpellDetailScreen

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
        # Pass all events to the active screen when awake
        if current_state in ("WAKE", "GRIMOIRE", "DETAIL"):
            active_screen.handle_event(event)

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
        if current_state in ("WAKE", "GRIMOIRE"):
            active_screen.handle_event(event)

   # --- 2. UPDATE ---
    if current_state in ("WAKE", "GRIMOIRE", "DETAIL"):
        dt = clock.get_time()
        active_screen.update(dt)

        # WAKE → GRIMOIRE when ripple finishes
        if current_state == "WAKE" and active_screen.is_done():
            print("Transitioning to grimoire screen")
            touch_pos  = (active_screen.ripple.x, active_screen.ripple.y)
            parchment  = active_screen.parchment
            current_state = "GRIMOIRE"
            active_screen = GrimoireScreen(screen, spells, parchment, touch_pos)

        # GRIMOIRE → DETAIL when a sigil is tapped
        elif current_state == "GRIMOIRE" and active_screen.is_done():
            spell        = active_screen.get_selected_spell()
            spell_index  = spells.index(spell)
            sigil_image  = active_screen.sigil_images[spell_index]
            parchment    = active_screen.parchment
            print(f"Opening detail screen for: {spell['name']}")
            current_state = "DETAIL"
            active_screen = SpellDetailScreen(screen, spell, parchment, sigil_image)

        # DETAIL → GRIMOIRE when Back is tapped
        elif current_state == "DETAIL" and active_screen.is_done():
            print("Returning to grimoire")
            current_state = "GRIMOIRE"
            active_screen = GrimoireScreen(
                screen, spells, parchment,
                (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
            )

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