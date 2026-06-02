# config.py
# This file holds all the global settings for the Spellscribe app.
# Other files will import from here so settings only need to change in one place.

import pygame

# --- SCREEN ---
# The resolution of the Raspberry Pi 7" touchscreen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

# How many times per second the screen redraws itself (frames per second)
# 60 is smooth and standard for most apps
FPS = 60

# --- COLORS ---
# Colors in Pygame are written as (Red, Green, Blue) values
# Each value goes from 0 (none) to 255 (full)
BLACK       = (0,   0,   0)
WHITE       = (255, 255, 255)
DEEP_INDIGO = (43,  0,   82)
DARK_VIOLET = (60,  0,   100)
PARCHMENT   = (210, 190, 150)
INK_DARK    = (20,  10,  40)
GOLD        = (200, 170, 80)

# --- FONTS ---
# We'll add custom font file paths here later once we have font files
# For now we'll use None which tells Pygame to use its built-in default font
FONT_MAIN   = None
FONT_TITLE  = None

# --- TIMING ---
# How long the parchment takes to fade in when the book opens (in milliseconds)
# 1000 milliseconds = 1 second
PARCHMENT_FADE_DURATION = 3000

# How long the cast animation plays before returning to the grimoire
CAST_DURATION = 60000

# How long the ripple takes to expand across the screen
RIPPLE_DURATION = 3000

# --- GRIMOIRE ---
# How many sigil columns appear on the grimoire screen
GRIMOIRE_COLUMNS = 3

# How fast each sigil pulses (lower = slower, higher = faster)
PULSE_SPEED = 0.8

# The dimmest a sigil gets during its pulse (0.0 = invisible, 1.0 = full brightness)
PULSE_MIN_ALPHA = 0.4

# --- GPIO ---
# The GPIO pin number the reed switch is wired to on the Raspberry Pi
# We'll use this when we get to the hardware setup
GPIO_PIN = 17