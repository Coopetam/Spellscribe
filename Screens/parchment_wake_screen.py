# screens/parchment_wake_screen.py
# This screen handles the transition from black to parchment
# when the book is opened.
#
# Think of it like slowly opening your eyes in a candlelit room —
# the world fades in gradually rather than snapping on all at once.

import pygame
import config

class ParchmentWakeScreen:
    """
    Fades the screen from black to a parchment background over
    PARCHMENT_FADE_DURATION milliseconds (set in config.py).

    When the fade is complete, the screen waits for a touch/click
    to trigger the ink ripple and sigil reveal.
    """

    def __init__(self, screen, spells):
        """
        Sets up the screen. This runs once when we switch to this screen.

        screen — the Pygame display surface (the window itself)
        spells — the list of spells loaded from spells.json
        """
        self.screen = screen
        self.spells = spells

        # --- LOAD PARCHMENT IMAGE ---
        # We try to load the image — if it's missing we fall back
        # to a solid parchment-coloured rectangle instead of crashing
        try:
            raw = pygame.image.load(config.PARCHMENT_IMAGE)
            self.parchment = pygame.transform.scale(raw, config.SCREEN_SIZE)
            print("Parchment image loaded successfully.")
        except FileNotFoundError:
            print(f"WARNING: Parchment image not found at {config.PARCHMENT_IMAGE}")
            print("Using solid color fallback.")
            self.parchment = pygame.Surface(config.SCREEN_SIZE)
            self.parchment.fill(config.PARCHMENT)

        # --- FADE STATE ---
        # alpha goes from 255 (fully black) down to 0 (fully visible)
        # We use a black overlay surface that we make more transparent over time
        self.overlay = pygame.Surface(config.SCREEN_SIZE)
        self.overlay.fill(config.BLACK)
        self.alpha = 255        # Start fully black
        self.fade_complete = False

        # --- TIMING ---
        # We track how long the fade has been running using Pygame's clock
        self.fade_elapsed = 0   # milliseconds elapsed since fade started

        # --- TOUCH STATE ---
        # Once the fade is done, we wait for the first touch
        self.touched = False

    def handle_event(self, event):
        """
        Listens for input events.
        Once the fade is complete, any touch or mouse click triggers
        the transition to the grimoire screen.
        """
        if self.fade_complete and not self.touched:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.touched = True
                print("Parchment touched — transitioning to grimoire")

    def update(self, dt):
        """
        Updates the fade animation.

        dt — delta time in milliseconds (how long since the last frame)
             This keeps the animation speed consistent regardless of FPS
        """
        if not self.fade_complete:
            # Add the time since last frame to our elapsed counter
            self.fade_elapsed += dt

            # Calculate how far through the fade we are as a value 0.0 to 1.0
            # e.g. halfway through = 0.5
            progress = self.fade_elapsed / config.PARCHMENT_FADE_DURATION

            # Clamp progress to 1.0 maximum so we don't overshoot
            progress = min(progress, 1.0)

            # Alpha goes from 255 (black) to 0 (transparent) as progress goes 0 to 1
            self.alpha = int(255 * (1.0 - progress))

            # When progress reaches 1.0 the fade is done
            if progress >= 1.0:
                self.fade_complete = True
                self.alpha = 0
                print("Parchment fade complete — waiting for touch")

    def draw(self):
        """
        Draws the current frame to the screen.
        Called 60 times per second by the main loop.
        """
        # Draw the parchment texture as the base layer
        self.screen.blit(self.parchment, (0, 0))

        # Draw the black overlay on top with the current alpha
        # As alpha decreases the overlay becomes transparent revealing parchment
        self.overlay.set_alpha(self.alpha)
        self.screen.blit(self.overlay, (0, 0))

    def is_done(self):
        """
        Returns True when the player has touched the screen after the fade.
        main.py uses this to know when to switch to the grimoire screen.
        """
        return self.touched