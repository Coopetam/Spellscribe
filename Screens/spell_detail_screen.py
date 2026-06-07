# screens/spell_detail_screen.py
# This screen shows the full details of a spell when a sigil is tapped.
# Layout (top to bottom):
#   - Large sigil image
#   - Sphere level as Roman numerals
#   - Spell name
#   - Valid target
#   - Description (word wrapped)
#   - Crafting cost
#   - Back button (bottom left) / Cast button (bottom right)

import pygame
import config

# Roman numeral lookup for sphere levels
ROMAN = {1: "I", 2: "II", 3: "III"}

# Button dimensions
BUTTON_WIDTH  = 160
BUTTON_HEIGHT = 55
BUTTON_MARGIN = 20  # distance from screen edges

class SpellDetailScreen:
    """
    Displays the full details of a single spell.
    Tapping Cast transitions to the cast screen.
    Tapping Back returns to the grimoire.
    """

    def __init__(self, screen, spell, parchment, sigil_image):
        """
        screen       — the Pygame display surface
        spell        — the spell dictionary from spells.json
        parchment    — the loaded parchment surface (reused for continuity)
        sigil_image  — the already-loaded sigil image for this spell
        """
        self.screen      = screen
        self.spell       = spell
        self.parchment   = parchment
        self.sigil_image = sigil_image

        # --- OUTCOME ---
        # Set to "cast" or "back" when a button is tapped
        self.outcome = None

        # --- SIGIL ---
        # Scale sigil to fill the top portion of the screen
        self.sigil_display_size = 180
        self.sigil_scaled = pygame.transform.scale(
            sigil_image,
            (self.sigil_display_size, self.sigil_display_size)
        )
        # Centre the sigil horizontally at the top
        self.sigil_x = (config.SCREEN_WIDTH - self.sigil_display_size) // 2
        self.sigil_y = 30

        # --- FONTS ---
        try:
            self.font_large  = pygame.font.Font(config.FONT_PATH, 26)
            self.font_medium = pygame.font.Font(config.FONT_PATH, 19)
            self.font_small  = pygame.font.Font(config.FONT_PATH, 16)
            self.font_button = pygame.font.Font(config.FONT_PATH, 20)
        except FileNotFoundError:
            print("WARNING: Font not found — using default font")
            self.font_large  = pygame.font.Font(None, 30)
            self.font_medium = pygame.font.Font(None, 24)
            self.font_small  = pygame.font.Font(None, 20)
            self.font_button = pygame.font.Font(None, 24)

        # --- PRE-RENDER TEXT ---
        # We render all the text surfaces once here rather than
        # every frame — much more efficient
        sphere = ROMAN.get(spell.get("sphere_level", 1), "I")
        self.sphere_surface = self.font_large.render(
            f"Sphere {sphere}", True, config.DEEP_INDIGO
        )
        self.name_surface = self.font_large.render(
            spell["name"], True, config.INK_DARK
        )
        self.target_label  = self.font_small.render(
            "Target:", True, config.DEEP_INDIGO
        )
        self.target_surface = self.font_small.render(
            spell.get("valid_target", ""), True, config.INK_DARK
        )
        self.cost_label   = self.font_small.render(
            "Cost:", True, config.DEEP_INDIGO
        )
        self.cost_surface = self.font_small.render(
            spell.get("crafting_cost", ""), True, config.INK_DARK
        )

        # Word-wrap the description into multiple lines
        self.desc_lines = self._wrap_text(
            spell.get("description", ""),
            self.font_small,
            config.SCREEN_WIDTH - 40    # 20px margin each side
        )

        # --- BUTTONS ---
        # Back button — bottom left
        self.back_rect = pygame.Rect(
            BUTTON_MARGIN,
            config.SCREEN_HEIGHT - BUTTON_HEIGHT - BUTTON_MARGIN,
            BUTTON_WIDTH,
            BUTTON_HEIGHT
        )

        # Cast button — bottom right
        self.cast_rect = pygame.Rect(
            config.SCREEN_WIDTH - BUTTON_WIDTH - BUTTON_MARGIN,
            config.SCREEN_HEIGHT - BUTTON_HEIGHT - BUTTON_MARGIN,
            BUTTON_WIDTH,
            BUTTON_HEIGHT
        )

        self.back_label = self.font_button.render("Back", True, config.WHITE)
        self.cast_label = self.font_button.render("Cast", True, config.WHITE)

        # Button press visual feedback
        self.back_pressed = False
        self.cast_pressed = False

    def _wrap_text(self, text, font, max_width):
        """
        Splits a long string into a list of lines that each
        fit within max_width pixels when rendered with font.

        This is what handles long spell descriptions automatically —
        no manual line breaks needed in the JSON.
        """
        words  = text.split(" ")
        lines  = []
        current_line = ""

        for word in words:
            # Try adding the next word to the current line
            test_line = current_line + (" " if current_line else "") + word
            width, _ = font.size(test_line)

            if width <= max_width:
                current_line = test_line
            else:
                # This word doesn't fit — save current line, start new one
                if current_line:
                    lines.append(current_line)
                current_line = word

        # Don't forget the last line
        if current_line:
            lines.append(current_line)

        return lines

    def handle_event(self, event):
        """
        Detects taps on the Cast and Back buttons.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.cast_rect.collidepoint(event.pos):
                self.cast_pressed = True
            if self.back_rect.collidepoint(event.pos):
                self.back_pressed = True

        if event.type == pygame.MOUSEBUTTONUP:
            if self.cast_pressed and self.cast_rect.collidepoint(event.pos):
                self.outcome = "cast"
                print(f"Casting: {self.spell['name']}")
            if self.back_pressed and self.back_rect.collidepoint(event.pos):
                self.outcome = "back"
                print("Returning to grimoire")
            self.cast_pressed = False
            self.back_pressed = False

    def update(self, dt):
        """
        Nothing to animate on this screen — placeholder for consistency.
        """
        pass

    def draw(self):
        """
        Draws the full spell detail screen.
        """
        # --- BACKGROUND ---
        self.screen.blit(self.parchment, (0, 0))

        # Subtle dark overlay to make text more readable
        overlay = pygame.Surface(config.SCREEN_SIZE, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 40))
        self.screen.blit(overlay, (0, 0))

        # --- SIGIL ---
        self.screen.blit(self.sigil_scaled, (self.sigil_x, self.sigil_y))

        # --- TEXT LAYOUT ---
        # Start drawing text just below the sigil
        text_x  = 20
        text_y  = self.sigil_y + self.sigil_display_size + 16

        # Sphere level
        self.screen.blit(self.sphere_surface,
            ((config.SCREEN_WIDTH - self.sphere_surface.get_width()) // 2, text_y))
        text_y += self.sphere_surface.get_height() + 6

        # Spell name — centred
        self.screen.blit(self.name_surface,
            ((config.SCREEN_WIDTH - self.name_surface.get_width()) // 2, text_y))
        text_y += self.name_surface.get_height() + 14

        # Divider line
        pygame.draw.line(self.screen, config.INK_DARK,
                         (20, text_y), (config.SCREEN_WIDTH - 20, text_y), 1)
        text_y += 10

        # Valid target
        self.screen.blit(self.target_label, (text_x, text_y))
        self.screen.blit(self.target_surface,
                         (text_x + self.target_label.get_width() + 8, text_y))
        text_y += self.target_surface.get_height() + 8

        # Description — word wrapped lines
        for line in self.desc_lines:
            line_surface = self.font_small.render(line, True, config.INK_DARK)
            self.screen.blit(line_surface, (text_x, text_y))
            text_y += line_surface.get_height() + 4

        text_y += 8

        # Crafting cost
        self.screen.blit(self.cost_label, (text_x, text_y))
        self.screen.blit(self.cost_surface,
                         (text_x + self.cost_label.get_width() + 8, text_y))

        # --- BUTTONS ---
        # Back button — dark indigo, bottom left
        back_color = config.DARK_VIOLET if self.back_pressed else config.DEEP_INDIGO
        pygame.draw.rect(self.screen, back_color, self.back_rect, border_radius=10)
        self.screen.blit(self.back_label, (
            self.back_rect.centerx - self.back_label.get_width() // 2,
            self.back_rect.centery - self.back_label.get_height() // 2
        ))

        # Cast button — gold, bottom right
        cast_color = config.PARCHMENT if self.cast_pressed else config.GOLD
        pygame.draw.rect(self.screen, cast_color, self.cast_rect, border_radius=10)
        self.screen.blit(self.cast_label, (
            self.cast_rect.centerx - self.cast_label.get_width() // 2,
            self.cast_rect.centery - self.cast_label.get_height() // 2
        ))

    def is_done(self):
        """
        Returns True when the player has tapped Cast or Back.
        """
        return self.outcome is not None

    def get_outcome(self):
        """
        Returns "cast" or "back" depending on what was tapped.
        """
        return self.outcome