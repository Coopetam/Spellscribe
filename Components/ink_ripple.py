# components/ink_ripple.py
# This component draws the ink ripple animation that plays when
# the player first touches the parchment.
#
# Think of it like dropping a stone into still water — multiple
# rings expand outward from the point of contact, each one
# slightly behind the last.

import pygame
import math
import config

# How many rings expand outward from the touch point
RING_COUNT = 4

# How far apart each ring is from the next (in milliseconds)
# e.g. the second ring starts 150ms after the first
RING_DELAY = 150

# How thick each ring is in pixels
RING_WIDTH = 3

# The color of the rings — dark ink on parchment
RING_COLOR = (30, 10, 50)

class InkRipple:
    """
    Draws multiple expanding ink rings from a touch point.
    Each ring starts slightly after the previous one,
    creating a water-drop ripple effect.
    """

    def __init__(self, x, y):
        """
        x, y — the coordinates where the player touched the screen
        """
        self.x = x
        self.y = y
        self.elapsed = 0        # total time since ripple started
        self.finished = False   # True when all rings have fully expanded

        # How far the ripple needs to expand to cover the whole screen
        # We use the diagonal distance from touch point to furthest corner
        self.max_radius = self._max_radius()

        # Load and play the touch sound
        try:
            self.sound = pygame.mixer.Sound(config.TOUCH_SOUND)
            self.sound.play()
            print("Touch sound played.")
        except FileNotFoundError:
            print(f"WARNING: Touch sound not found at {config.TOUCH_SOUND}")
            self.sound = None

    def _max_radius(self):
        """
        Calculates the furthest distance from the touch point
        to any corner of the screen. This ensures the ripple
        always fully covers the screen no matter where you tap.
        """
        corners = [
            (0, 0),
            (config.SCREEN_WIDTH, 0),
            (0, config.SCREEN_HEIGHT),
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        ]
        distances = [
            math.sqrt((self.x - cx) ** 2 + (self.y - cy) ** 2)
            for cx, cy in corners
        ]
        return max(distances)

    def update(self, dt):
        """
        Advances the animation by dt milliseconds.
        """
        self.elapsed += dt

        # Check if the last ring has fully expanded
        last_ring_start = RING_DELAY * (RING_COUNT - 1)
        if self.elapsed >= last_ring_start + config.RIPPLE_DURATION:
            self.finished = True

    def draw(self, surface):
        """
        Draws all active rings onto the surface.
        Each ring starts after a delay and expands outward.
        """
        for i in range(RING_COUNT):

            # How long ago this ring started (can be negative if not started yet)
            ring_elapsed = self.elapsed - (i * RING_DELAY)

            # Skip this ring if it hasn't started yet
            if ring_elapsed <= 0:
                continue

            # How far through its animation is this ring (0.0 to 1.0)
            progress = ring_elapsed / config.RIPPLE_DURATION
            progress = min(progress, 1.0)

            # Current radius grows from 0 to max_radius
            radius = int(self.max_radius * progress)

            # Alpha fades from fully visible to invisible as the ring expands
            # Early rings fade faster so they don't linger too long
            alpha = int(200 * (1.0 - progress))

            # Skip drawing if the ring is fully transparent
            if alpha <= 0 or radius <= 0:
                continue

            # Draw the ring onto a temporary transparent surface
            # We need this because Pygame circles don't support alpha directly
            ring_surface = pygame.Surface(config.SCREEN_SIZE, pygame.SRCALPHA)

            pygame.draw.circle(
                ring_surface,
                (*RING_COLOR, alpha),   # color with alpha
                (self.x, self.y),       # centre point
                radius,                 # radius
                RING_WIDTH              # thickness — 0 would fill the circle
            )

            surface.blit(ring_surface, (0, 0))

    def is_finished(self):
        """
        Returns True when all rings have fully expanded.
        The grimoire screen uses this to know when to show the sigils.
        """
        return self.finished

    def get_radius(self):
        """
        Returns the current radius of the FIRST ring.
        The sigil reveal uses this to know when the wave
        has reached each sigil's position.
        """
        progress = min(self.elapsed / config.RIPPLE_DURATION, 1.0)
        return self.max_radius * progress