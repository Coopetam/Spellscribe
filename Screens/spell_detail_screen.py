# screens/spell_detail_screen.py
# Shows the full details of a spell when a sigil is tapped.
# Layout (top to bottom):
#   - Large sigil (~half screen width)
#   - Sphere level as Roman numerals
#   - Spell name
#   - Valid target
#   - Description (word wrapped)
#   - Crafting cost
#   - Back button image (bottom left)

import pygame
import config

# Roman numeral lookup for sphere levels
ROMAN = {1: "I", 2: "II", 3: "III"}

# Back button size and position
BACK_BUTTON_SIZE   = 60
BACK_BUTTON_MARGIN = 20

class SpellDetailScreen:
    """
    Displays the full details of a single spell.
    No cast button or timer — stays until the player taps Back.
    """

    def __init__(self, screen, spell, parchment, sigil_image):
        """
        screen       — the Pygame display surface
        spell        — the spell dictionary from spells.json
        parchment    — the loaded parchment surface
        sigil_image  — the already-loaded sigil image for this spell
        """
        self.screen      = screen
        self.spell       = spell
        self.parchment   = parchment
        self.sigil_image = sigil_image

        # --- OUTCOME ---
        self.outcome = None  # set to "back" when Back is tapped

        # --- SIGIL ---
        # About half the screen width
        self.sigil_display_size = int(config.SCREEN_WIDTH * 0.75)
        self.sigil_scaled = pygame.transform.scale(
            sigil_image,
            (self.sigil_display_size, self.sigil_display_size)
        )
        # Centre the sigil horizontally at the top
        self.sigil_x = (config.SCREEN_WIDTH - self.sigil_display_size) // 2
        self.sigil_y = 24

        # --- FONTS ---
        try:
            self.font_large  = pygame.font.Font(config.FONT_PATH, 32)
            self.font_medium = pygame.font.Font(config.FONT_PATH, 24)
            self.font_small  = pygame.font.Font(config.FONT_PATH, 20)
        except FileNotFoundError:
            print("WARNING: Font not found — using default font")
            self.font_large  = pygame.font.Font(None, 36)
            self.font_medium = pygame.font.Font(None, 28)
            self.font_small  = pygame.font.Font(None, 24)

        # --- PRE-RENDER TEXT ---
        sphere = ROMAN.get(spell.get("sphere_level", 1), "I")
        self.sphere_surface = self.font_medium.render(
            f"Sphere {sphere}", True, config.DEEP_INDIGO
        )
        self.name_surface = self.font_large.render(
            spell["name"], True, config.INK_DARK
        )
        self.target_label   = self.font_small.render(
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

        # Word wrap the description
        self.desc_lines = self._wrap_text(
            spell.get("description", ""),
            self.font_small,
            config.SCREEN_WIDTH - 40
        )

        # --- BACK BUTTON ---
        try:
            raw = pygame.image.load(config.BACK_BUTTON_IMAGE).convert_alpha()
            self.back_image = pygame.transform.scale(
                raw, (BACK_BUTTON_SIZE, BACK_BUTTON_SIZE)
            )
            print("Back button image loaded.")
        except FileNotFoundError:
            print(f"WARNING: Back button image not found — using text fallback")
            self.back_image = None

        # Hit area for the back button — bottom left corner
        self.back_rect = pygame.Rect(
            BACK_BUTTON_MARGIN,
            config.SCREEN_HEIGHT - BACK_BUTTON_SIZE - BACK_BUTTON_MARGIN,
            BACK_BUTTON_SIZE,
            BACK_BUTTON_SIZE
        )

        self.back_pressed = False

    def _wrap_text(self, text, font, max_width):
        """
        Splits a long string into lines that fit within max_width.
        """
        words        = text.split(" ")
        lines        = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            width, _  = font.size(test_line)
            if width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def handle_event(self, event):
        """
        Detects taps on the Back button.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_rect.collidepoint(event.pos):
                self.back_pressed = True

        if event.type == pygame.MOUSEBUTTONUP:
            if self.back_pressed and self.back_rect.collidepoint(event.pos):
                self.outcome = "back"
                print("Returning to grimoire")
            self.back_pressed = False

    def update(self, dt):
        """
        Nothing to animate — placeholder for consistency.
        """
        pass

    def draw(self):
        """
        Draws the full spell detail screen.
        """
        # --- BACKGROUND ---
        self.screen.blit(self.parchment, (0, 0))

        # Subtle overlay to improve text readability
        overlay = pygame.Surface(config.SCREEN_SIZE, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 40))
        self.screen.blit(overlay, (0, 0))

        # --- SIGIL ---
        self.screen.blit(self.sigil_scaled, (self.sigil_x, self.sigil_y))

        # --- TEXT ---
        text_x = 20
        text_y = self.sigil_y + self.sigil_display_size + 12

        # Sphere level — centred
        self.screen.blit(self.sphere_surface,
            ((config.SCREEN_WIDTH - self.sphere_surface.get_width()) // 2,
             text_y))
        text_y += self.sphere_surface.get_height() + 4

        # Spell name — centred
        self.screen.blit(self.name_surface,
            ((config.SCREEN_WIDTH - self.name_surface.get_width()) // 2,
             text_y))
        text_y += self.name_surface.get_height() + 10

        # Divider line
        pygame.draw.line(self.screen, config.INK_DARK,
                         (20, text_y),
                         (config.SCREEN_WIDTH - 20, text_y), 1)
        text_y += 10

        # Valid target
        self.screen.blit(self.target_label, (text_x, text_y))
        self.screen.blit(self.target_surface,
                         (text_x + self.target_label.get_width() + 8, text_y))
        text_y += self.target_surface.get_height() + 8

        # Description lines
        for line in self.desc_lines:
            line_surf = self.font_small.render(line, True, config.INK_DARK)
            self.screen.blit(line_surf, (text_x, text_y))
            text_y += line_surf.get_height() + 4

        text_y += 6

        # Crafting cost
        self.screen.blit(self.cost_label, (text_x, text_y))
        self.screen.blit(self.cost_surface,
                         (text_x + self.cost_label.get_width() + 8, text_y))

        # --- BACK BUTTON ---
        if self.back_image:
            # Dim slightly when pressed for visual feedback
            if self.back_pressed:
                dimmed = self.back_image.copy()
                dimmed.set_alpha(160)
                self.screen.blit(dimmed, self.back_rect.topleft)
            else:
                self.screen.blit(self.back_image, self.back_rect.topleft)
        else:
            # Text fallback if image is missing
            font = pygame.font.Font(None, 28)
            label = font.render("← Back", True, config.DEEP_INDIGO)
            self.screen.blit(label, self.back_rect.topleft)

    def is_done(self):
        return self.outcome is not None

    def get_outcome(self):
        return self.outcome