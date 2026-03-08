import pygame
import random
from constants import (TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, SCREENSIZE,
                       BUSH_SMALL, TREE, BOX, SCARECROW, LOGS, WELL,
                       MINOTAUR, POWERUP_ARROW_REFILL, POWERUP_TRIPLE_SHOT,
                       POWERUP_DAMAGE_X4, BUSH_MEDIUM, OBSTACLE, POLE, LAMP,
                       WIZARD, EYE, BUSH_LARGE, FLOWER_3, FLOWER, GROUND,
                       CART, WHEEL, SURFACE, SHOP, GRANNY_HOUSE, BARRIER,
                       SHOPKEEPER, GRANNY_NPC,
                       DIFF_HARD, DIFFICULTY_SETTINGS, SHOP_PRICES)
from enemies import Minotaur, Wizard as WizardEnemy, Eye as EyeEnemy
from npc import Shopkeeper, Granny


# Preloaded tile images (loaded once on first use)
_tile_images = {}


def _load_tile_images():
    if _tile_images:
        return
    _tile_images['ground'] = pygame.image.load("img/ground.png").convert_alpha()
    _tile_images['tree'] = pygame.image.load("img/tree.png").convert_alpha()
    _tile_images['box'] = pygame.image.load("img/box.png").convert_alpha()
    _tile_images['scarecrow'] = pygame.image.load("img/scarecrow.png").convert_alpha()
    _tile_images['logs'] = pygame.image.load("img/logs.png").convert_alpha()
    _tile_images['well'] = pygame.image.load("img/well.png").convert_alpha()
    _tile_images['surface'] = pygame.image.load("img/surface.png").convert_alpha()
    _tile_images['obstacle'] = pygame.image.load("img/obstacle.png").convert_alpha()
    _tile_images['cart'] = pygame.image.load("img/cart.png").convert_alpha()
    _tile_images['wheel'] = pygame.image.load("img/wheel.png").convert_alpha()
    _tile_images['bush1'] = pygame.image.load("img/bush1.png").convert_alpha()
    _tile_images['bush2'] = pygame.image.load("img/bush2.png").convert_alpha()
    _tile_images['bush3'] = pygame.image.load("img/bush3.png").convert_alpha()
    _tile_images['flower_3'] = pygame.image.load("img/3flowers.png").convert_alpha()
    _tile_images['lamp'] = pygame.image.load("img/lamp.png").convert_alpha()
    _tile_images['pole'] = pygame.image.load("img/pole.png").convert_alpha()


def _parse_tile(tile, row_count, col_count, tile_list, flower_group,
                minotaur_group, wizard_group, eye_group, powerup_group,
                sounds, damage_mult, shop_group=None, npc_group=None,
                difficulty=DIFF_HARD):
    """Parse a single tile code and create the appropriate game object."""
    _load_tile_images()

    if tile == BUSH_SMALL:
        img = pygame.transform.scale(_tile_images['bush1'], (TILE_SIZE, TILE_SIZE))
        img_rect = img.get_rect()
        img_rect.x = col_count * TILE_SIZE
        img_rect.y = row_count * TILE_SIZE + 2
        tile_list.append((img, img_rect, False, 0))
    if tile == BUSH_MEDIUM:
        img = pygame.transform.scale(_tile_images['bush2'], (int(TILE_SIZE * 1.5), int(TILE_SIZE * 1.5)))
        img_rect = img.get_rect()
        img_rect.x = col_count * TILE_SIZE
        img_rect.y = row_count * TILE_SIZE + 2 - int(TILE_SIZE * 0.5)
        tile_list.append((img, img_rect, False, 0))
    if tile == BUSH_LARGE:
        img = pygame.transform.scale(_tile_images['bush3'], (TILE_SIZE * 2, int(TILE_SIZE * 1.5)))
        img_rect = img.get_rect()
        img_rect.x = col_count * TILE_SIZE
        img_rect.y = row_count * TILE_SIZE + 2 - int(TILE_SIZE * 0.5)
        tile_list.append((img, img_rect, False, 0))
    if tile == FLOWER_3:
        img = pygame.transform.scale(_tile_images['flower_3'], (int(TILE_SIZE * 1.5), TILE_SIZE))
        img_rect = img.get_rect()
        img_rect.x = col_count * TILE_SIZE - 60
        img_rect.y = row_count * TILE_SIZE + 2
        tile_list.append((img, img_rect, False, 0))
    if tile == FLOWER:
        flower = Flower(col_count * TILE_SIZE, row_count * TILE_SIZE + 2)
        flower_group.add(flower)
    if tile == GROUND:
        img = pygame.transform.scale(_tile_images['ground'], (TILE_SIZE, TILE_SIZE))
        img_rect = img.get_rect()
        img_rect.x = col_count * TILE_SIZE
        img_rect.y = row_count * TILE_SIZE
        tile_list.append((img, img_rect, True, 0))
    if tile == CART:
        img = pygame.transform.scale(_tile_images['cart'], (TILE_SIZE * 3, int(TILE_SIZE * 1.5)))
        img_rect = img.get_rect()
        img_rect.x = col_count * TILE_SIZE
        img_rect.y = row_count * TILE_SIZE - int(TILE_SIZE * 0.5)
        tile_list.append((img, img_rect, False, 0))
    if tile == WHEEL:
        img = pygame.transform.scale(_tile_images['wheel'], (int(TILE_SIZE // 1.5), int(TILE_SIZE // 1.5)))
        img_rect = img.get_rect()
        img_rect.x = col_count * TILE_SIZE - 30
        img_rect.y = row_count * TILE_SIZE + 2 + 20
        tile_list.append((img, img_rect, False, 0))
    if tile == SURFACE:
        img = pygame.transform.scale(_tile_images['surface'], (TILE_SIZE, TILE_SIZE))
        img_rect = img.get_rect()
        img_rect.x = col_count * TILE_SIZE
        img_rect.y = row_count * TILE_SIZE
        tile_list.append((img, img_rect, True, 0))
    if tile == OBSTACLE:
        img = pygame.transform.scale(_tile_images['obstacle'], (TILE_SIZE, TILE_SIZE))
        img_rect = img.get_rect()
        img_rect.x = col_count * TILE_SIZE
        img_rect.y = row_count * TILE_SIZE
        tile_list.append((img, img_rect, True, 0))
    if tile == BOX:
        img = pygame.transform.scale(_tile_images['box'], (TILE_SIZE, TILE_SIZE))
        img_rect = img.get_rect()
        img_rect.x = col_count * TILE_SIZE
        img_rect.y = row_count * TILE_SIZE + 2
        tile_list.append((img, img_rect, True, 0))
    if tile == SCARECROW:
        img = pygame.transform.scale(_tile_images['scarecrow'], (TILE_SIZE, TILE_SIZE + 30))
        img_rect = img.get_rect()
        img_rect.x = col_count * TILE_SIZE
        img_rect.y = row_count * TILE_SIZE - 30 + 2
        tile_list.append((img, img_rect, False, 0))
    if tile == LOGS:
        img = pygame.transform.scale(_tile_images['logs'], (TILE_SIZE * 2, TILE_SIZE))
        img_rect = img.get_rect()
        img_rect.x = col_count * TILE_SIZE
        img_rect.y = row_count * TILE_SIZE + 2
        tile_list.append((img, img_rect, True, 0))
    if tile == WELL:
        img = pygame.transform.scale(_tile_images['well'], (TILE_SIZE * 2, TILE_SIZE * 2))
        img_rect = img.get_rect()
        img_rect.x = col_count * TILE_SIZE
        img_rect.y = row_count * TILE_SIZE - TILE_SIZE * 1 + 2
        tile_list.append((img, img_rect, True, 0))
    if tile == MINOTAUR:
        minotaur = Minotaur(col_count * TILE_SIZE, row_count * TILE_SIZE - 30,
                            sounds, damage_mult=damage_mult)
        minotaur_group.add(minotaur)
    if tile == POWERUP_ARROW_REFILL:
        powerup = ArrowPowerup(col_count * TILE_SIZE, row_count * TILE_SIZE, 1)
        powerup_group.add(powerup)
    if tile == POWERUP_TRIPLE_SHOT:
        powerup = ArrowPowerup(col_count * TILE_SIZE, row_count * TILE_SIZE, 2)
        powerup_group.add(powerup)
    if tile == POWERUP_DAMAGE_X4:
        powerup = ArrowPowerup(col_count * TILE_SIZE, row_count * TILE_SIZE, 3)
        powerup_group.add(powerup)
    if tile == POLE:
        img = pygame.transform.scale(_tile_images['pole'], (TILE_SIZE, TILE_SIZE * 2))
        img_rect = img.get_rect()
        img_rect.x = col_count * TILE_SIZE
        img_rect.y = row_count * TILE_SIZE - TILE_SIZE * 1 + 2
        tile_list.append((img, img_rect, False, 0))
    if tile == LAMP:
        img = pygame.transform.scale(_tile_images['lamp'], (TILE_SIZE // 2, TILE_SIZE // 2))
        img_rect = img.get_rect()
        img_rect.x = col_count * TILE_SIZE - 30
        img_rect.y = row_count * TILE_SIZE - TILE_SIZE * 1 + 35
        tile_list.append((img, img_rect, False, 1))
    if tile == TREE:
        tree_width = TILE_SIZE * 4
        tree_height = TILE_SIZE * 6
        img = pygame.transform.scale(_tile_images['tree'], (tree_width, tree_height))
        img_rect = img.get_rect()
        img_rect.x = col_count * TILE_SIZE - (tree_width // 2) + (TILE_SIZE // 2)
        img_rect.y = row_count * TILE_SIZE - TILE_SIZE * 5 + 2
        tile_list.append((img, img_rect, False, 0))
    if tile == WIZARD:
        wizard = WizardEnemy(col_count * TILE_SIZE, row_count * TILE_SIZE - 30,
                             sounds, damage_mult=damage_mult)
        wizard_group.add(wizard)
    if tile == EYE:
        eye = EyeEnemy(col_count * TILE_SIZE, row_count * TILE_SIZE - 30,
                       sounds, damage_mult=damage_mult)
        eye_group.add(eye)
    if tile == SHOP and shop_group is not None:
        shop = ShopBuilding(col_count * TILE_SIZE, row_count * TILE_SIZE, difficulty)
        shop_group.add(shop)
    if tile == GRANNY_HOUSE:
        img = pygame.image.load("img/Granny_home.png").convert_alpha()
        ow, oh = img.get_size()
        # 10 tiles wide, preserve aspect ratio
        house_w = TILE_SIZE * 10
        house_h = int(house_w * oh / ow)
        img = pygame.transform.scale(img, (house_w, house_h))
        img_rect = img.get_rect()
        img_rect.x = col_count * TILE_SIZE - TILE_SIZE * 2
        img_rect.y = row_count * TILE_SIZE - house_h + TILE_SIZE
        tile_list.append((img, img_rect, False, 0))
    if tile == BARRIER:
        # Invisible collidable wall — no image, just a collision rect
        img = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        img_rect = img.get_rect()
        img_rect.x = col_count * TILE_SIZE
        img_rect.y = row_count * TILE_SIZE
        tile_list.append((img, img_rect, True, 0))
    if tile == SHOPKEEPER and npc_group is not None:
        # Place at tile position, gravity will drop onto ground
        sk = Shopkeeper(col_count * TILE_SIZE,
                        row_count * TILE_SIZE - 60)
        npc_group.add(sk)
    if tile == GRANNY_NPC and npc_group is not None:
        granny = Granny(col_count * TILE_SIZE,
                        row_count * TILE_SIZE - 100)
        npc_group.add(granny)


class HealthBar:
    def draw(self, screen, health):
        pygame.draw.rect(screen, (255, 0, 0), (100, 10, 100 * 4, 20))
        pygame.draw.rect(screen, (0, 255, 0), (100, 10, health * 4, 20))


class World:
    def __init__(self, data, flower_group, minotaur_group, wizard_group,
                 eye_group, powerup_group, sounds, difficulty=DIFF_HARD,
                 shop_group=None, npc_group=None):
        self.tile_list = []
        self.sounds = sounds
        self.difficulty = difficulty
        self.flower_group = flower_group
        self.minotaur_group = minotaur_group
        self.wizard_group = wizard_group
        self.eye_group = eye_group
        self.powerup_group = powerup_group
        self.shop_group = shop_group
        self.npc_group = npc_group

        diff = DIFFICULTY_SETTINGS[difficulty]
        damage_mult = diff['damage_mult']

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                _parse_tile(tile, row_count, col_count, self.tile_list,
                            flower_group, minotaur_group, wizard_group,
                            eye_group, powerup_group, sounds, damage_mult,
                            shop_group=shop_group, npc_group=npc_group,
                            difficulty=difficulty)
                col_count += 1
            row_count += 1

    def add_chunk(self, chunk_data, col_offset):
        """Add new chunk tiles at a column offset (for infinite mode)."""
        diff = DIFFICULTY_SETTINGS[self.difficulty]
        damage_mult = diff['damage_mult']

        row_count = 0
        for row in chunk_data:
            col_count = 0
            for tile in row:
                _parse_tile(tile, row_count, col_count + col_offset,
                            self.tile_list, self.flower_group,
                            self.minotaur_group, self.wizard_group,
                            self.eye_group, self.powerup_group,
                            self.sounds, damage_mult,
                            shop_group=self.shop_group,
                            npc_group=self.npc_group,
                            difficulty=self.difficulty)
                col_count += 1
            row_count += 1

    def draw(self, screen, screen_scroll, y_scroll):
        for tile in self.tile_list:
            tile[1][0] += screen_scroll
            tile[1][1] += y_scroll
            if tile[3] == 1:
                circs = [17,17,17,17,17,16,16,16,17,17,17,15,14,13,12,11,11,10,10,9]
                for i in range(len(circs)):
                    pygame.draw.circle(
                        screen, (circs[i] * 15, circs[i] * 15, 0),
                        (tile[1][0] + 20, tile[1][1] + 17), i + 1, 1)
            screen.blit(tile[0], tile[1])


class Flower(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("img/1flower.png").convert_alpha()
        self.image = pygame.transform.scale(img, (TILE_SIZE // 2, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.consumed = False

    def update(self, screen_scroll, y_scroll, screen):
        self.rect.x += screen_scroll
        self.rect.y += y_scroll
        screen.blit(self.image, self.rect)


class Arrow(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("img/arrow.png").convert_alpha()
        self.image_right = pygame.transform.scale(img, (TILE_SIZE // 2, int(TILE_SIZE // 5)))
        self.image_left = pygame.transform.flip(self.image_right, True, False)
        self.direction = direction
        self.speed = 12
        self.dx = 0
        self.dy = 0
        self.stopped = False
        self.damage = 30
        self.image = self.image_right if direction == 1 else self.image_left
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self, screen_scroll, y_scroll, screen, world,
               minotaur_group, wizard_group, eye_group, arrow_group, sounds):
        screen.blit(self.image, self.rect)
        self.dx = self.speed * self.direction

        for tile in world.tile_list:
            if tile[2] and tile[1].colliderect(
                self.rect.x + self.dx, self.rect.y, self.width, self.height
            ):
                self.dx = 0
                sounds['arrow_hit'].play()
                arrow_group.remove(self)
                return

        for group in [minotaur_group, wizard_group, eye_group]:
            if pygame.sprite.spritecollide(self, group, False):
                for enemy in pygame.sprite.spritecollide(self, group, False):
                    enemy.health -= self.damage
                    sounds['arrow_hit'].play()
                arrow_group.remove(self)
                return

        self.rect.x += self.dx
        self.rect.x += screen_scroll
        self.rect.y += y_scroll


class ScoreFlower(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("img/1flower.png").convert_alpha()
        self.image = pygame.transform.scale(img, (TILE_SIZE // 3, int(TILE_SIZE // 1.5)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, screen):
        screen.blit(self.image, self.rect)


class ArrowCount(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load("img/arrow.png").convert_alpha()
        self.image = pygame.transform.scale(img, (TILE_SIZE // 2, int(TILE_SIZE // 5)))
        self.image = pygame.transform.rotozoom(self.image, 45, 1)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, screen):
        screen.blit(self.image, self.rect)


_powerup_images = {}

def _get_powerup_image(index):
    if index not in _powerup_images:
        paths = {1: "img/arrow_powerup.png", 2: "img/arrow_powerup2.png", 3: "img/arrow_powerup3.png"}
        img = pygame.image.load(paths[index]).convert_alpha()
        _powerup_images[index] = pygame.transform.scale(img, (int(TILE_SIZE // 1.5), int(TILE_SIZE // 1.5)))
    return _powerup_images[index]


class ArrowPowerup(pygame.sprite.Sprite):
    def __init__(self, x, y, index):
        pygame.sprite.Sprite.__init__(self)
        self.image = _get_powerup_image(index)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.consumed = False
        self.index = index

    def update(self, screen_scroll, y_scroll, screen):
        self.rect.x += screen_scroll
        self.rect.y += y_scroll
        screen.blit(self.image, self.rect)


class ActivePowerupIcon(pygame.sprite.Sprite):
    def __init__(self, x, y, index):
        pygame.sprite.Sprite.__init__(self)
        self.image = _get_powerup_image(index)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.consumed = False
        self.index = index

    def update(self, screen_scroll, y_scroll, screen):
        # HUD element — doesn't scroll, but matches ArrowPowerup signature
        pygame.draw.circle(screen, (0, 0, 0), (self.rect.centerx, self.rect.centery), 25)
        screen.blit(self.image, self.rect)


class ShopBuilding(pygame.sprite.Sprite):
    """A shop building the player can interact with."""
    def __init__(self, x, y, difficulty=DIFF_HARD):
        pygame.sprite.Sprite.__init__(self)
        diff = DIFFICULTY_SETTINGS[difficulty]
        img = pygame.image.load("img/Shop.png").convert_alpha()
        # 6 tiles wide, height preserves aspect ratio
        shop_w = TILE_SIZE * 6
        orig_w, orig_h = img.get_size()
        shop_h = int(shop_w * (orig_h / orig_w))
        self.image = pygame.transform.scale(img, (shop_w, shop_h))
        self.rect = self.image.get_rect()
        # Center on the spawn tile, bottom aligned to the ground
        self.rect.x = x - (shop_w // 2) + (TILE_SIZE // 2)
        self.rect.y = y - shop_h + TILE_SIZE

        # Shop stock — randomized per instance
        self.gold = random.randint(*diff['shop_gold'])
        self.stock = {
            'health_potion': random.randint(*diff['shop_potions']),
            'arrows_5': random.randint(*diff['shop_arrows']),
        }

        # Interaction hint font
        self.font = pygame.font.Font("AmaticSC-Bold.ttf", 26)

    def update(self, screen_scroll, y_scroll, screen):
        self.rect.x += screen_scroll
        self.rect.y += y_scroll
        screen.blit(self.image, self.rect)


class KillCounter:
    """HUD element showing small enemy icons with kill counts."""
    def __init__(self):
        icon_size = (36, 36)
        # Minotaur icon
        img = pygame.image.load("img/Mino_idle_list/idle1.png").convert_alpha()
        self.mino_icon = pygame.transform.scale(img, icon_size)
        # Wizard icon
        img = pygame.image.load("img/wizard_idle/Idle1.png").convert_alpha()
        self.wiz_icon = pygame.transform.scale(img, icon_size)
        # Eye icon
        img = pygame.image.load("img/eye/Flight1.png").convert_alpha()
        self.eye_icon = pygame.transform.scale(img, icon_size)

        self.font = pygame.font.Font("AmaticSC-Bold.ttf", 28)

    def draw(self, screen, kills):
        x = SCREEN_WIDTH - 130
        y = 80
        spacing = 42

        for icon, key in [(self.mino_icon, 'minotaur'),
                          (self.wiz_icon, 'wizard'),
                          (self.eye_icon, 'eye')]:
            screen.blit(icon, (x, y))
            count_text = self.font.render(f"x{kills.get(key, 0)}", True, (255, 255, 255))
            screen.blit(count_text, (x + 40, y + 8))
            y += spacing


# Inventory item definitions: (key, label, icon_path, col_span, row_span)
_INVENTORY_ITEMS = [
    ('coins',        'Gold',          'img/coin.png',               1, 1),
    ('health_potion','Health Potion',  'img/healing_potion.png',    1, 1),
    ('arrows',       'Arrows',        'img/arrow.png',              2, 1),
    ('flowers',      'Flowers',       'img/1flower.png',            1, 2),
    ('hide_minotaur','Minotaur Hide', 'img/mino_hide.PNG', 2, 2),
    ('hide_wizard',  'Wizard Hide',   'img/Wizard_hide.png',        3, 2),
    ('hide_eye',     'Eye Hide',      'img/eye_hide.PNG',     1, 1),
]

# Pre-computed grid positions: (grid_col, grid_row) for each item
# Layout (6 grid columns wide):
#  Row 0: [Gold 1x1] [Potion 1x1] [Arrows 2x1   ] [Eye 1x1] [ ]
#  Row 1: [Flower  ] [MinoHide  2x2  ] [WizardHide    3x2       ]
#  Row 2: [ 1x2    ] [           2x2  ] [              3x2       ]
_ITEM_POSITIONS = [
    (0, 0),  # coins
    (1, 0),  # health_potion
    (2, 0),  # arrows (2 wide)
    (0, 1),  # flowers (1x2)
    (1, 1),  # hide_minotaur (2x2)
    (3, 1),  # hide_wizard (3x2)
    (4, 0),  # hide_eye (1x1)
]


class Inventory:
    """Grid inventory overlay with variable-size cells."""
    CELL = 72
    GRID_COLS = 6
    GRID_ROWS = 3
    PAD = 8
    BG_COLOR = (20, 15, 10, 200)
    CELL_COLOR = (50, 40, 30)
    CELL_HIGHLIGHT = (80, 70, 50)
    BORDER_COLOR = (120, 100, 60)
    SELECT_COLOR = (255, 220, 80)

    def __init__(self):
        self.icons = {}
        self.items = _INVENTORY_ITEMS
        self.positions = _ITEM_POSITIONS
        self.selected = 0
        self.font = pygame.font.Font("AmaticSC-Bold.ttf", 22)
        self.font_label = pygame.font.Font("AmaticSC-Bold.ttf", 30)
        self.font_title = pygame.font.Font("AmaticSC-Bold.ttf", 50)
        self._icons_loaded = False

    def _load_icons(self):
        if self._icons_loaded:
            return
        for key, label, path, cw, ch in self.items:
            img = pygame.image.load(path).convert_alpha()
            # Scale icon to fit inside the cell span, with padding
            iw = cw * self.CELL + (cw - 1) * self.PAD - 24
            ih = ch * self.CELL + (ch - 1) * self.PAD - 24
            # Preserve aspect ratio within the available space
            orig_w, orig_h = img.get_size()
            scale = min(iw / orig_w, ih / orig_h)
            self.icons[key] = pygame.transform.scale(
                img, (int(orig_w * scale), int(orig_h * scale)))
        self._icons_loaded = True

    def _get_counts(self, player):
        return {
            'coins': player.coins,
            'health_potion': player.health_potions,
            'arrows': player.num_of_arrows,
            'flowers': player.flower_count,
            'hide_minotaur': player.hides['minotaur'],
            'hide_wizard': player.hides['wizard'],
            'hide_eye': player.hides['eye'],
        }

    def _cell_rect(self, idx, gx, gy):
        """Get pixel rect for an item's cell."""
        gcol, grow = self.positions[idx]
        _, _, _, cw, ch = self.items[idx]
        cx = gx + gcol * (self.CELL + self.PAD)
        cy = gy + grow * (self.CELL + self.PAD)
        w = cw * self.CELL + (cw - 1) * self.PAD
        h = ch * self.CELL + (ch - 1) * self.PAD
        return cx, cy, w, h

    def draw(self, screen, player):
        self._load_icons()
        counts = self._get_counts(player)

        grid_w = self.GRID_COLS * (self.CELL + self.PAD) + self.PAD
        grid_h = self.GRID_ROWS * (self.CELL + self.PAD) + self.PAD
        panel_w = grid_w + 40
        panel_h = grid_h + 100
        px = (SCREEN_WIDTH - panel_w) // 2
        py = (SCREEN_HEIGHT - panel_h) // 2

        # Dim background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        # Panel
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill(self.BG_COLOR)
        screen.blit(panel, (px, py))
        pygame.draw.rect(screen, self.BORDER_COLOR, (px, py, panel_w, panel_h), 3)

        # Title
        title = self.font_title.render("Inventory", True, (255, 220, 150))
        screen.blit(title, (px + (panel_w - title.get_width()) // 2, py + 10))

        gx = px + 20
        gy = py + 70

        for idx, (key, label, _, cw, ch) in enumerate(self.items):
            cx, cy, w, h = self._cell_rect(idx, gx, gy)

            # Cell background
            is_selected = (idx == self.selected)
            cell_col = self.CELL_HIGHLIGHT if is_selected else self.CELL_COLOR
            pygame.draw.rect(screen, cell_col, (cx, cy, w, h))

            if is_selected:
                pygame.draw.rect(screen, self.SELECT_COLOR, (cx, cy, w, h), 3)

            # Icon centered in cell
            icon = self.icons[key]
            ix = cx + (w - icon.get_width()) // 2
            iy = cy + (h - icon.get_height()) // 2 - 2
            screen.blit(icon, (ix, iy))

            # Count (bottom-right of cell)
            count = counts.get(key, 0)
            count_surf = self.font.render(str(count), True, (255, 255, 255))
            screen.blit(count_surf,
                        (cx + w - count_surf.get_width() - 4,
                         cy + h - count_surf.get_height() - 2))

        # Instructions
        sel_key = self.items[self.selected][0]
        hint = "Arrow keys to navigate"
        if sel_key == 'health_potion':
            hint = "ENTER to consume  |  Arrow keys to navigate"
        instr = self.font_label.render(hint, True, (200, 200, 180))
        screen.blit(instr,
                    (px + (panel_w - instr.get_width()) // 2,
                     py + panel_h - 35))

    def _find_neighbor(self, direction):
        """Find the nearest item index in a direction from current selection."""
        cur_col, cur_row = self.positions[self.selected]
        _, _, _, cur_cw, cur_ch = self.items[self.selected]
        # Center of current cell in grid units
        cx = cur_col + cur_cw / 2
        cy = cur_row + cur_ch / 2

        best = None
        best_dist = 9999
        for idx, (gcol, grow) in enumerate(self.positions):
            if idx == self.selected:
                continue
            _, _, _, iw, ih = self.items[idx]
            ix = gcol + iw / 2
            iy = grow + ih / 2

            if direction == 'left' and ix < cx:
                d = abs(iy - cy) * 2 + (cx - ix)
            elif direction == 'right' and ix > cx:
                d = abs(iy - cy) * 2 + (ix - cx)
            elif direction == 'up' and iy < cy:
                d = abs(ix - cx) * 2 + (cy - iy)
            elif direction == 'down' and iy > cy:
                d = abs(ix - cx) * 2 + (iy - cy)
            else:
                continue

            if d < best_dist:
                best_dist = d
                best = idx
        return best

    def handle_input(self, event, player):
        """Returns True if inventory should close."""
        if event.type != pygame.KEYDOWN:
            return False
        if event.key in (pygame.K_i, pygame.K_TAB, pygame.K_ESCAPE):
            return True
        if event.key == pygame.K_LEFT:
            n = self._find_neighbor('left')
            if n is not None:
                self.selected = n
        elif event.key == pygame.K_RIGHT:
            n = self._find_neighbor('right')
            if n is not None:
                self.selected = n
        elif event.key == pygame.K_UP:
            n = self._find_neighbor('up')
            if n is not None:
                self.selected = n
        elif event.key == pygame.K_DOWN:
            n = self._find_neighbor('down')
            if n is not None:
                self.selected = n
        elif event.key == pygame.K_RETURN:
            sel_key = self.items[self.selected][0]
            if sel_key == 'health_potion' and player.health_potions > 0:
                player.health_potions -= 1
                player.health = min(100, player.health + player.potion_heal)
        return False


# --- Shop trading UI ---

# Sellable items: (key, label, icon_path, price_key, cell_w, cell_h)
_SELL_ITEMS = [
    ('hide_minotaur', 'Minotaur Hide', 'img/mino_hide.PNG', 'hide_minotaur', 2, 2),
    ('hide_wizard',   'Wizard Hide',   'img/Wizard_hide.png',     'hide_wizard',   3, 2),
    ('hide_eye',      'Eye Hide',      'img/eye_hide.PNG',     'hide_eye',      1, 1),
    ('flower',        'Flowers',       'img/1flower.png',            'flower',         1, 1),
]

# Buyable items: (key, label, icon_path, price_key, cell_w, cell_h)
_BUY_ITEMS = [
    ('health_potion', 'Health Potion', 'img/healing_potion.png', 'health_potion', 1, 1),
    ('arrows_5',      '5 Arrows',     'img/arrow.png',          'arrows_5',       2, 1),
]


class ShopUI:
    """Full trading interface with buy/sell, variable-size cells, and amount prompt."""

    # Colors
    BG = (15, 12, 8, 230)
    PANEL_BG = (30, 25, 18)
    CELL_COL = (55, 45, 35)
    CELL_SEL = (100, 85, 60)
    BORDER = (120, 100, 60)
    DIVIDER = (90, 75, 50)
    GOLD_COL = (255, 220, 80)
    TEXT = (230, 220, 200)
    TEXT_DIM = (150, 140, 120)
    BTN_BUY = (40, 100, 50)
    BTN_BUY_H = (60, 140, 70)
    BTN_SELL = (130, 55, 40)
    BTN_SELL_H = (170, 75, 55)
    BTN_DISABLED = (60, 55, 50)

    C = 68  # base cell size
    PAD = 6

    def __init__(self):
        self.ft = pygame.font.Font("AmaticSC-Bold.ttf", 48)
        self.fl = pygame.font.Font("AmaticSC-Bold.ttf", 32)
        self.fi = pygame.font.Font("AmaticSC-Bold.ttf", 24)
        self.fc = pygame.font.Font("AmaticSC-Bold.ttf", 20)
        self.fb = pygame.font.Font("AmaticSC-Bold.ttf", 30)
        self.fp = pygame.font.Font("AmaticSC-Bold.ttf", 40)

        self.sell_items = _SELL_ITEMS
        self.buy_items = _BUY_ITEMS
        self.sell_icons = {}
        self.buy_icons = {}
        self._loaded = False

        self.selected_side = None
        self.selected_idx = -1
        self.shop = None

        self.prompt_active = False
        self.prompt_action = None
        self.prompt_amount = 1
        self.prompt_max = 0
        self.prompt_item_key = None
        self.prompt_label = ""

        self.sell_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.buy_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.confirm_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.cancel_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.plus_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.minus_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.sell_rects = []
        self.buy_rects = []
        self.coin_icon = None
        self._wscale_x = 1.0
        self._wscale_y = 1.0

    def _load(self):
        if self._loaded:
            return
        for items, icons in [(self.sell_items, self.sell_icons),
                             (self.buy_items, self.buy_icons)]:
            for key, label, path, _, cw, ch in items:
                img = pygame.image.load(path).convert_alpha()
                ow, oh = img.get_size()
                tw = cw * self.C + (cw - 1) * self.PAD - 16
                th = ch * self.C + (ch - 1) * self.PAD - 16
                s = min(tw / ow, th / oh)
                icons[key] = pygame.transform.scale(img, (int(ow * s), int(oh * s)))
        ci = pygame.image.load("img/coin.png").convert_alpha()
        self.coin_icon = pygame.transform.scale(ci, (20, 20))
        self._loaded = True

    def open(self, shop):
        self.shop = shop
        self.selected_side = None
        self.selected_idx = -1
        self.prompt_active = False

    def _pstock(self, player):
        return {
            'hide_minotaur': player.hides['minotaur'],
            'hide_wizard': player.hides['wizard'],
            'hide_eye': player.hides['eye'],
            'flower': player.flower_count,
        }

    def _smouse(self, mx, my):
        return int(mx * self._wscale_x), int(my * self._wscale_y)

    def _draw_btn(self, screen, rect, text, color, hover_color, enabled=True):
        mx, my = self._smouse(*pygame.mouse.get_pos())
        hovered = rect.collidepoint(mx, my) and enabled
        c = hover_color if hovered else (color if enabled else self.BTN_DISABLED)
        pygame.draw.rect(screen, c, rect, border_radius=6)
        pygame.draw.rect(screen, self.BORDER, rect, 2, border_radius=6)
        t = self.fb.render(text, True, self.TEXT if enabled else self.TEXT_DIM)
        screen.blit(t, (rect.centerx - t.get_width() // 2,
                        rect.centery - t.get_height() // 2))

    def _draw_cell(self, screen, x, y, w, h, icon, count, price, selected):
        col = self.CELL_SEL if selected else self.CELL_COL
        pygame.draw.rect(screen, col, (x, y, w, h))
        if selected:
            pygame.draw.rect(screen, self.GOLD_COL, (x, y, w, h), 2)
        # Icon centered
        ix = x + (w - icon.get_width()) // 2
        iy = y + (h - icon.get_height()) // 2 - 4
        screen.blit(icon, (ix, iy))
        # Count bottom-right
        ct = self.fc.render(str(count), True, (255, 255, 255))
        screen.blit(ct, (x + w - ct.get_width() - 3, y + h - ct.get_height() - 1))
        # Price bottom-left
        if self.coin_icon:
            screen.blit(self.coin_icon, (x + 2, y + h - 21))
        pt = self.fc.render(str(price), True, self.GOLD_COL)
        screen.blit(pt, (x + 23, y + h - pt.get_height() - 1))

    def _gold_row(self, screen, x, y, w, label, amount):
        t = self.fl.render(label, True, self.TEXT)
        screen.blit(t, (x + 8, y))
        a = self.fl.render(str(amount), True, self.GOLD_COL)
        ax = x + w - a.get_width() - 10
        screen.blit(a, (ax, y))
        if self.coin_icon:
            screen.blit(self.coin_icon, (ax - 24, y + 6))

    def draw(self, screen, player, window_w, window_h):
        self._load()
        self._wscale_x = SCREEN_WIDTH / window_w
        self._wscale_y = SCREEN_HEIGHT / window_h
        pstock = self._pstock(player)

        # Panel dimensions
        pw, ph = 920, 560
        px = (SCREEN_WIDTH - pw) // 2
        py = (SCREEN_HEIGHT - ph) // 2

        # Overlay
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        screen.blit(ov, (0, 0))

        # Main panel
        p = pygame.Surface((pw, ph), pygame.SRCALPHA)
        p.fill(self.BG)
        screen.blit(p, (px, py))
        pygame.draw.rect(screen, self.BORDER, (px, py, pw, ph), 3)

        # Title
        title = self.ft.render("Trading Post", True, self.GOLD_COL)
        screen.blit(title, (px + (pw - title.get_width()) // 2, py + 10))

        # Divider line down the middle
        mid_x = px + pw // 2
        pygame.draw.line(screen, self.DIVIDER, (mid_x, py + 55), (mid_x, py + ph - 55), 2)

        half = pw // 2 - 24
        lx = px + 16
        rx = mid_x + 8
        top = py + 60

        # ===== LEFT: Your Items (sell) =====
        lbl = self.fl.render("Your Items", True, self.TEXT)
        screen.blit(lbl, (lx, top))
        self._gold_row(screen, lx, top + 32, half, "Your Gold:", player.coins)

        self.sell_rects = []
        # Layout sell items with variable sizes using explicit positions
        # Row 0: Mino(2x2) + Wizard(3x2) = 5 cells wide
        # Row 2: Eye(1x1) + Flower(1x1) + empty
        sell_positions = [(0, 0), (2, 0), (0, 2), (1, 2)]
        gy = top + 72
        for i, (key, label, _, price_key, cw, ch) in enumerate(self.sell_items):
            gc, gr = sell_positions[i]
            cx = lx + gc * (self.C + self.PAD)
            cy = gy + gr * (self.C + self.PAD)
            w = cw * self.C + (cw - 1) * self.PAD
            h = ch * self.C + (ch - 1) * self.PAD
            r = pygame.Rect(cx, cy, w, h)
            self.sell_rects.append(r)
            sel = (self.selected_side == 'sell' and self.selected_idx == i)
            self._draw_cell(screen, cx, cy, w, h, self.sell_icons[key],
                            pstock.get(key, 0), SHOP_PRICES[price_key], sel)
            # Label below cell
            nm = self.fc.render(label, True, self.TEXT_DIM)
            screen.blit(nm, (cx + (w - nm.get_width()) // 2, cy + h + 2))

        # ===== RIGHT: Shop Items (buy) =====
        lbl2 = self.fl.render("Shop Items", True, self.TEXT)
        screen.blit(lbl2, (rx, top))
        if self.shop:
            self._gold_row(screen, rx, top + 32, half, "Shop Gold:", self.shop.gold)

        self.buy_rects = []
        gy2 = top + 72
        buy_positions = [(0, 0), (0, 1)]
        for i, (key, label, _, price_key, cw, ch) in enumerate(self.buy_items):
            gc, gr = buy_positions[i]
            cx = rx + gc * (self.C + self.PAD)
            cy = gy2 + gr * (self.C + self.PAD)
            w = cw * self.C + (cw - 1) * self.PAD
            h = ch * self.C + (ch - 1) * self.PAD
            r = pygame.Rect(cx, cy, w, h)
            self.buy_rects.append(r)
            sel = (self.selected_side == 'buy' and self.selected_idx == i)
            stock = self.shop.stock.get(key, 0) if self.shop else 0
            self._draw_cell(screen, cx, cy, w, h, self.buy_icons[key],
                            stock, SHOP_PRICES[price_key], sel)
            nm = self.fc.render(label, True, self.TEXT_DIM)
            screen.blit(nm, (cx + (w - nm.get_width()) // 2, cy + h + 2))

        # ===== Bottom bar: Sell + Buy buttons centered =====
        btn_y = py + ph - 50
        btn_w, btn_h = 130, 38
        gap = 30
        total_w = btn_w * 2 + gap
        bx = px + (pw - total_w) // 2

        # Sell button
        self.sell_btn_rect = pygame.Rect(bx, btn_y, btn_w, btn_h)
        can_sell = (self.selected_side == 'sell' and self.selected_idx >= 0 and
                    pstock.get(self.sell_items[self.selected_idx][0], 0) > 0 and
                    self.shop and self.shop.gold >= SHOP_PRICES[
                        self.sell_items[self.selected_idx][3]])
        self._draw_btn(screen, self.sell_btn_rect, "Sell", self.BTN_SELL,
                       self.BTN_SELL_H, enabled=can_sell)

        # Buy button
        self.buy_btn_rect = pygame.Rect(bx + btn_w + gap, btn_y, btn_w, btn_h)
        can_buy = (self.selected_side == 'buy' and self.selected_idx >= 0 and
                   self.shop and
                   self.shop.stock.get(self.buy_items[self.selected_idx][0], 0) > 0 and
                   player.coins >= SHOP_PRICES[self.buy_items[self.selected_idx][3]])
        self._draw_btn(screen, self.buy_btn_rect, "Buy", self.BTN_BUY,
                       self.BTN_BUY_H, enabled=can_buy)

        # Close hint
        hint = self.fc.render("ESC to close", True, self.TEXT_DIM)
        screen.blit(hint, (px + pw - hint.get_width() - 10, py + ph - 20))

        # Amount prompt overlay
        if self.prompt_active:
            self._draw_prompt(screen)

    def _draw_prompt(self, screen):
        pw, ph = 360, 210
        px = (SCREEN_WIDTH - pw) // 2
        py = (SCREEN_HEIGHT - ph) // 2

        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((20, 16, 10, 240))
        screen.blit(panel, (px, py))
        pygame.draw.rect(screen, self.GOLD_COL, (px, py, pw, ph), 2)

        action_lbl = "Buy" if self.prompt_action == 'buy' else "Sell"
        title = self.fl.render(f"{action_lbl}: {self.prompt_label}", True, self.TEXT)
        screen.blit(title, (px + (pw - title.get_width()) // 2, py + 15))

        price = SHOP_PRICES[self.prompt_item_key]
        total = price * self.prompt_amount
        ptext = self.fi.render(f"{price} each  |  Total: {total}", True, self.GOLD_COL)
        screen.blit(ptext, (px + (pw - ptext.get_width()) // 2, py + 52))

        # +/- and amount
        self.minus_btn_rect = pygame.Rect(px + 65, py + 88, 50, 40)
        self.plus_btn_rect = pygame.Rect(px + pw - 115, py + 88, 50, 40)
        self._draw_btn(screen, self.minus_btn_rect, "-", self.CELL_COL, self.CELL_SEL,
                       enabled=self.prompt_amount > 1)
        amt = self.fp.render(str(self.prompt_amount), True, (255, 255, 255))
        screen.blit(amt, (px + pw // 2 - amt.get_width() // 2, py + 90))
        self._draw_btn(screen, self.plus_btn_rect, "+", self.CELL_COL, self.CELL_SEL,
                       enabled=self.prompt_amount < self.prompt_max)

        mx = self.fc.render(f"(max {self.prompt_max})", True, self.TEXT_DIM)
        screen.blit(mx, (px + pw // 2 - mx.get_width() // 2, py + 133))

        # Confirm / Cancel
        self.confirm_btn_rect = pygame.Rect(px + 45, py + 160, 120, 36)
        self.cancel_btn_rect = pygame.Rect(px + pw - 165, py + 160, 120, 36)
        btn_col = self.BTN_BUY if self.prompt_action == 'buy' else self.BTN_SELL
        btn_hov = self.BTN_BUY_H if self.prompt_action == 'buy' else self.BTN_SELL_H
        self._draw_btn(screen, self.confirm_btn_rect, "Confirm", btn_col, btn_hov)
        self._draw_btn(screen, self.cancel_btn_rect, "Cancel", self.CELL_COL, self.CELL_SEL)

    def _open_prompt(self, action, item_key, label, max_amount):
        self.prompt_active = True
        self.prompt_action = action
        self.prompt_item_key = item_key
        self.prompt_label = label
        self.prompt_amount = 1
        self.prompt_max = max(1, max_amount)

    def _execute_trade(self, player):
        price = SHOP_PRICES[self.prompt_item_key]
        amount = self.prompt_amount
        total = price * amount

        if self.prompt_action == 'sell':
            key = self.prompt_item_key
            if key == 'hide_minotaur':
                player.hides['minotaur'] -= amount
            elif key == 'hide_wizard':
                player.hides['wizard'] -= amount
            elif key == 'hide_eye':
                player.hides['eye'] -= amount
            elif key == 'flower':
                player.flower_count -= amount
            player.coins += total
            self.shop.gold -= total
        elif self.prompt_action == 'buy':
            key = self.prompt_item_key
            if key == 'health_potion':
                player.health_potions += amount
            elif key == 'arrows_5':
                player.num_of_arrows += amount * 5
            player.coins -= total
            self.shop.gold += total
            self.shop.stock[key] -= amount

        self.prompt_active = False

    def handle_event(self, event, player, window_w, window_h):
        """Returns True if shop should close."""
        self._wscale_x = SCREEN_WIDTH / window_w
        self._wscale_y = SCREEN_HEIGHT / window_h

        if event.type == pygame.KEYDOWN:
            if self.prompt_active:
                if event.key == pygame.K_ESCAPE:
                    self.prompt_active = False
                elif event.key == pygame.K_LEFT and self.prompt_amount > 1:
                    self.prompt_amount -= 1
                elif event.key == pygame.K_RIGHT and self.prompt_amount < self.prompt_max:
                    self.prompt_amount += 1
                elif event.key == pygame.K_RETURN:
                    self._execute_trade(player)
                return False
            if event.key == pygame.K_ESCAPE:
                return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = self._smouse(*event.pos)

            if self.prompt_active:
                if self.minus_btn_rect.collidepoint(mx, my) and self.prompt_amount > 1:
                    self.prompt_amount -= 1
                elif self.plus_btn_rect.collidepoint(mx, my) and self.prompt_amount < self.prompt_max:
                    self.prompt_amount += 1
                elif self.confirm_btn_rect.collidepoint(mx, my):
                    self._execute_trade(player)
                elif self.cancel_btn_rect.collidepoint(mx, my):
                    self.prompt_active = False
                return False

            for i, r in enumerate(self.sell_rects):
                if r.collidepoint(mx, my):
                    self.selected_side = 'sell'
                    self.selected_idx = i
                    return False
            for i, r in enumerate(self.buy_rects):
                if r.collidepoint(mx, my):
                    self.selected_side = 'buy'
                    self.selected_idx = i
                    return False

            if self.sell_btn_rect.collidepoint(mx, my):
                if self.selected_side == 'sell' and self.selected_idx >= 0:
                    key, label, _, price_key, _, _ = self.sell_items[self.selected_idx]
                    pstock = self._pstock(player)
                    have = pstock.get(key, 0)
                    price = SHOP_PRICES[price_key]
                    max_sell = min(have, self.shop.gold // price) if price > 0 else have
                    if max_sell > 0:
                        self._open_prompt('sell', price_key, label, max_sell)
                return False

            if self.buy_btn_rect.collidepoint(mx, my):
                if self.selected_side == 'buy' and self.selected_idx >= 0:
                    key, label, _, price_key, _, _ = self.buy_items[self.selected_idx]
                    stock = self.shop.stock.get(key, 0)
                    price = SHOP_PRICES[price_key]
                    max_buy = min(stock, player.coins // price) if price > 0 else stock
                    if max_buy > 0:
                        self._open_prompt('buy', price_key, label, max_buy)
                return False

        return False
