import pygame

# Design resolution (all game logic uses these)
TILE_SIZE = 60
DESIGN_WIDTH = 1920
DESIGN_HEIGHT = 1080 - TILE_SIZE
SCREEN_WIDTH = DESIGN_WIDTH
SCREEN_HEIGHT = DESIGN_HEIGHT
SCREENSIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
FPS = 60
SCROLL_THRESH = 200

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
RAIN_COLOR = (180, 215, 228, 255)

# Tile codes (used in world_data grid)
EMPTY = 0
BUSH_SMALL = 10
TREE = 11
BOX = 12
SCARECROW = 13
LOGS = 14
WELL = 15
MINOTAUR = 16
POWERUP_ARROW_REFILL = 17
POWERUP_TRIPLE_SHOT = 18
POWERUP_DAMAGE_X4 = 19
BUSH_MEDIUM = 20
OBSTACLE = 21
POLE = 22
LAMP = 23
WIZARD = 24
EYE = 25
BUSH_LARGE = 30
FLOWER_3 = 40
FLOWER = 50
GROUND = 60
CART = 70
WHEEL = 80
SURFACE = 90
SHOP = 95
GRANNY_HOUSE = 96
BARRIER = 97
SHOPKEEPER = 98
GRANNY_NPC = 99

# Game states
STATE_MENU = "menu"
STATE_MODE_SELECT = "mode_select"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_GAME_OVER = "game_over"
STATE_INVENTORY = "inventory"
STATE_SHOPPING = "shopping"
STATE_WIN = "win"

# Game modes
MODE_CLASSIC = "classic"
MODE_INFINITE = "infinite"

# Difficulty levels
DIFF_EASY = "easy"
DIFF_MEDIUM = "medium"
DIFF_HARD = "hard"

# Difficulty configs
# Spawn works on probability: every `spawn_interval` columns, there's a
# `spawn_chance` probability of spawning that enemy type.
# Higher chance + lower interval = more enemies.
DIFFICULTY_SETTINGS = {
    DIFF_EASY: {
        'damage_mult': 0.5,
        'flower_heal': 15,
        'potion_heal': 50,
        'inv_tick_rate': 0.1,       # enemies run at 10% speed while inventory open
        'spawn_wizards': False,
        'eye_chance': 0.15,
        'eye_interval': 25,
        'mino_chance': 0.15,
        'mino_interval': 25,
        'wiz_chance': 0.0,
        'wiz_interval': 25,
        'min_spacing': 8,
        'shop_interval': 60,       # check every 60 columns
        'shop_chance': 0.7,        # 70% chance at interval
        'shop_gold': (200, 400),
        'shop_potions': (5, 10),
        'shop_arrows': (15, 25),
    },
    DIFF_MEDIUM: {
        'damage_mult': 0.75,
        'flower_heal': 10,
        'potion_heal': 35,
        'inv_tick_rate': 0.5,       # enemies run at 50% speed
        'spawn_wizards': False,
        'eye_chance': 0.25,
        'eye_interval': 20,
        'mino_chance': 0.25,
        'mino_interval': 20,
        'wiz_chance': 0.0,
        'wiz_interval': 20,
        'min_spacing': 6,
        'shop_interval': 80,
        'shop_chance': 0.6,
        'shop_gold': (100, 250),
        'shop_potions': (3, 6),
        'shop_arrows': (8, 15),
    },
    DIFF_HARD: {
        'damage_mult': 1.0,
        'flower_heal': 5,
        'potion_heal': 25,
        'inv_tick_rate': 1.0,       # no slowdown
        'spawn_wizards': True,
        'eye_chance': 0.30,
        'eye_interval': 15,
        'mino_chance': 0.30,
        'mino_interval': 15,
        'wiz_chance': 0.25,
        'wiz_interval': 20,
        'min_spacing': 5,
        'shop_interval': 100,
        'shop_chance': 0.5,
        'shop_gold': (50, 150),
        'shop_potions': (1, 3),
        'shop_arrows': (3, 8),
    },
}

# Shop prices
SHOP_PRICES = {
    'hide_eye': 5,
    'hide_minotaur': 10,
    'hide_wizard': 20,
    'flower': 3,
    'health_potion': 15,
    'arrows_5': 8,         # 5 arrows for 8 gold
}

# Infinite mode
CHUNK_COLS = 80           # noise samples per chunk
TICK_DISTANCE = 2400      # pixels — entities beyond this don't update
