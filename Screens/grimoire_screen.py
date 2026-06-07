# screens/grimoire_screen.py
# This screen displays the 3-column sigil grid.
# Sigils bloom into view as the ripple wave passes them,
# then pulse gently while waiting for the player to tap one.

import pygame
import math
import random
import config

class GrimoireScreen:
    """
    Displays all 12 spells as a pulsing sigil grid on parchment.
    Sigils reveal themselves radially from the ripple touch point.
    """

    def __init__(self, screen, spells, parchment, touch_pos):
        """
        screen      — the Pygame display surface
        spells      — list of spell dictionaries from spells.json
        parchment   — the already-loaded parchment surface (we reuse it
                      so the background looks continuous, not reset)
        touch_pos   — (x, y) where the player touched the parchment
                      used to calculate sigil reveal order
        """
        self.screen = screen
        self.spells = spells
        self.parchment = parchment
        self.touch_pos = touch_pos

        # --- GRID LAYOUT ---
        # Work out where each sigil card sits on the screen
        self.columns = config.GRIMOIRE_COLUMNS
        self.card_width  = config.SCREEN_WIDTH // self.columns
        self.card_height = self.card_width  # square cards

        # How much padding around each sigil image inside its card
        self.sigil_padding = 20

        # The actual sigil image size inside the card
        self.sigil_size = self.card_width - (self.sigil_padding * 2)

        # Top margin before the first row of sigils
        self.top_margin = 40

        # --- SCROLL ---
        self.scroll_y = 0       # how many pixels we've scrolled down
        self.scroll_speed = 20
        self.drag_start = None  # tracks swipe gestures

        # --- LOAD SIGIL IMAGES ---
        self.sigil_images = self._load_sigils()

        # --- BUILD CARD POSITIONS ---
        # Calculate the centre (x, y) of every sigil card
        self.card_positions = self._build_positions()

        # --- REVEAL STATE ---
        # Each sigil starts invisible (alpha 0) and blooms in when
        # the ripple wave reaches it
        self.reveal_alphas = [0] * len(self.spells)

        # Calculate each sigil's distance from the touch point
        # so we know when the ripple wave reaches it
        self.reveal_distances = self._calc_distances()

        # Track total time elapsed for reveal and pulse animations
        self.elapsed = 0
        self.reveal_complete = False

        # --- PULSE ---
        # Random phase offset per sigil so they don't pulse in unison
        self.pulse_phases = [random.uniform(0, 2 * math.pi)
                             for _ in self.spells]

        # --- FONT ---
        try:
            self.font = pygame.font.Font(config.FONT_PATH, 16)
        except FileNotFoundError:
            print("WARNING: Font not found — using default font")
            self.font = pygame.font.Font(None, 20)

        # --- SELECTED SPELL ---
        self.selected_spell = None  # set when player taps a sigil

    def _load_sigils(self):
        """
        Loads each spell's sigil image, scaled to sigil_size.
        Falls back to placeholder if the file is missing.
        """
        images = []
        placeholder = self._load_placeholder()

        for spell in self.spells:
            path = f"assets/images/sigils/{spell['sigil']}"
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (self.sigil_size, self.sigil_size))
                images.append(img)
            except FileNotFoundError:
                print(f"WARNING: Sigil not found for {spell['name']} — using placeholder")
                images.append(placeholder)

        return images

    def _load_placeholder(self):
        """
        Loads the placeholder sigil image.
        If even that is missing, draws a simple circle as fallback.
        """
        try:
            img = pygame.image.load(config.PLACEHOLDER_SIGIL).convert_alpha()
            return pygame.transform.scale(img, (self.sigil_size, self.sigil_size))
        except FileNotFoundError:
            print("WARNING: Placeholder sigil not found — using drawn fallback")
            surface = pygame.Surface((self.sigil_size, self.sigil_size), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*config.DEEP_INDIGO, 180),
                               (self.sigil_size // 2, self.sigil_size // 2),
                               self.sigil_size // 2 - 4, 3)
            return surface

    def _build_positions(self):
        """
        Calculates the top-left (x, y) position of each sigil card.
        """
        positions = []
        for i, _ in enumerate(self.spells):
            col = i % self.columns
            row = i // self.columns
            x = col * self.card_width
            y = self.top_margin + row * self.card_height
            positions.append((x, y))
        return positions

    def _card_centre(self, index):
        """
        Returns the centre (x, y) of a card, accounting for scroll.
        """
        x, y = self.card_positions[index]
        cx = x + self.card_width // 2
        cy = y + self.card_height // 2 - self.scroll_y
        return cx, cy

    def _calc_distances(self):
        """
        Calculates each sigil's distance from the touch point.
        Used to stagger the reveal so closer sigils appear first.
        """
        tx, ty = self.touch_pos
        distances = []
        for i in range(len(self.spells)):
            cx, cy = self._card_centre(i)
            dist = math.sqrt((cx - tx) ** 2 + (cy - ty) ** 2)
            distances.append(dist)
        return distances

    def handle_event(self, event):
        """
        Handles touch/click events on the grimoire grid.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.drag_start = event.pos

        if event.type == pygame.MOUSEBUTTONUP:
            if self.drag_start:
                dx = event.pos[0] - self.drag_start[0]
                dy = event.pos[1] - self.drag_start[1]
                dist = math.sqrt(dx**2 + dy**2)

                # Only register as a tap if the finger barely moved
                # Otherwise it was a scroll gesture
                if dist < 15 and self.reveal_complete:
                    self._check_tap(event.pos)

            self.drag_start = None

        # Scroll with mouse drag
        if event.type == pygame.MOUSEMOTION:
            if self.drag_start:
                dy = event.pos[1] - self.drag_start[1]
                self.scroll_y -= dy
                self.scroll_y = max(0, self.scroll_y)
                self.drag_start = event.pos

    def _check_tap(self, pos):
        """
        Checks if the tap landed on a sigil card.
        """
        tx, ty = pos
        for i, spell in enumerate(self.spells):
            x, y = self.card_positions[i]
            # Adjust y for scroll position
            adjusted_y = y - self.scroll_y
            if (x <= tx <= x + self.card_width and
                    adjusted_y <= ty <= adjusted_y + self.card_height):
                self.selected_spell = spell
                print(f"Sigil tapped: {spell['name']}")
                break

    def update(self, dt):
        """Fades all sigils in together at the same rate. No radial order — all reveal simultaneously."""
        self.elapsed += dt

        # Progress goes from 0.0 to 1.0 over RIPPLE_DURATION
        progress = min(self.elapsed / config.RIPPLE_DURATION, 1.0)

        # All sigils fade in together
        alpha = int(255 * progress)
        self.reveal_alphas = [alpha] * len(self.spells)

        if progress >= 1.0 and not self.reveal_complete:
            self.reveal_complete = True
            print("All sigils revealed — grimoire ready")

        # Clamp all alphas to 255
        self.reveal_alphas = [min(255, a) for a in self.reveal_alphas]

    def draw(self):
        """
        Draws the grimoire screen — parchment, sigils, and spell names.
        """
        # Draw parchment background
        self.screen.blit(self.parchment, (0, 0))

        for i, spell in enumerate(self.spells):
            x, y = self.card_positions[i]
            draw_y = y - self.scroll_y

            # Skip cards that are off screen
            if draw_y + self.card_height < 0 or draw_y > config.SCREEN_HEIGHT:
                continue

            # --- PULSE ---
            # No pulse — sigils stay solid once revealed
            final_alpha = int(self.reveal_alphas[i])

            # Combine reveal alpha and pulse alpha
            # Reveal alpha goes 0→255, pulse modulates on top of that
            final_alpha = int(self.reveal_alphas[i])

            # --- DRAW SIGIL ---
            sigil = self.sigil_images[i].copy()
            sigil.set_alpha(final_alpha)
            sigil_x = x + self.sigil_padding
            sigil_y = draw_y + self.sigil_padding
            self.screen.blit(sigil, (sigil_x, sigil_y))

            # --- DRAW SPELL NAME ---
            name_surface = self.font.render(spell["name"], True, config.INK_DARK)
            name_surface.set_alpha(final_alpha)
            name_x = x + (self.card_width - name_surface.get_width()) // 2
            name_y = draw_y + self.sigil_padding + self.sigil_size + 6
            self.screen.blit(name_surface, (name_x, name_y))

    def is_done(self):
        """
        Returns True when the player has tapped a sigil.
        """
        return self.selected_spell is not None

    def get_selected_spell(self):
        """
        Returns the spell the player tapped.
        """
        return self.selected_spell