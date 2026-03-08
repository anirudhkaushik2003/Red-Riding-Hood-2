import json
import os
import pygame
import time
import random
from pygame import mixer
from constants import (TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT,
                       DESIGN_WIDTH, DESIGN_HEIGHT, FPS,
                       WHITE, BLACK, CYAN, STATE_MENU, STATE_PLAYING,
                       STATE_PAUSED, STATE_GAME_OVER, STATE_MODE_SELECT,
                       STATE_INVENTORY, STATE_SHOPPING, STATE_WIN,
                       MODE_CLASSIC, MODE_INFINITE,
                       DIFF_EASY, DIFF_MEDIUM, DIFF_HARD,
                       DIFFICULTY_SETTINGS, TICK_DISTANCE)
from player import Player
from sprites import (World, HealthBar, ScoreFlower, ArrowCount,
                     Arrow, ActivePowerupIcon, KillCounter, ShopBuilding,
                     Inventory, ShopUI)
from npc import Shopkeeper, Granny
from rain import Rain
import worldgen

SAVE_FILE = "savegame.json"

YELLOW = (255, 255, 100)
MODES = [MODE_CLASSIC, MODE_INFINITE]
DIFFICULTIES = [DIFF_EASY, DIFF_MEDIUM, DIFF_HARD]
DIFF_LABELS = {DIFF_EASY: "Easy", DIFF_MEDIUM: "Medium", DIFF_HARD: "Hard"}
MODE_LABELS = {MODE_CLASSIC: "Classic", MODE_INFINITE: "Infinite"}


class Game:
    def __init__(self):
        try:
            import ctypes
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass

        pygame.mixer.pre_init(44100, -16, 2, 512)
        mixer.init()
        pygame.init()
        self.clock = pygame.time.Clock()

        info = pygame.display.Info()
        display_w, display_h = info.current_w, info.current_h
        max_w = int(display_w * 0.9)
        max_h = int(display_h * 0.85)
        scale = min(max_w / DESIGN_WIDTH, max_h / DESIGN_HEIGHT)
        self.window_width = int(DESIGN_WIDTH * scale)
        self.window_height = int(DESIGN_HEIGHT * scale)

        self.window = pygame.display.set_mode(
            (self.window_width, self.window_height), pygame.RESIZABLE
        )
        pygame.display.set_caption("Red Riding Hood")
        pygame.mixer.set_num_channels(100)

        self.screen = pygame.Surface((DESIGN_WIDTH, DESIGN_HEIGHT))

        self.font = pygame.font.Font("AmaticSC-Bold.ttf", 35)
        self.font_health = pygame.font.Font("AmaticSC-Bold.ttf", 30)
        self.font_large = pygame.font.Font("AmaticSC-Bold.ttf", 80)
        self.font_medium = pygame.font.Font("AmaticSC-Bold.ttf", 50)
        self.font_small = pygame.font.Font("AmaticSC-Bold.ttf", 28)

        bg_img = pygame.image.load("img/dark-forest-background-hd-1080p-90357.jpg").convert()
        self.background = pygame.transform.scale(bg_img, (DESIGN_WIDTH, DESIGN_HEIGHT))

        self._load_sounds()
        self._start_music()

        self.state = STATE_MENU
        self.rain = Rain(self.screen)

        # Mode/difficulty selection state
        self.selected_mode = 0       # index into MODES
        self.selected_diff = 2       # index into DIFFICULTIES (default Hard)
        self.mode_select_row = 0     # 0=mode, 1=difficulty, 2=start

        self.game_mode = MODE_CLASSIC
        self.difficulty = DIFF_HARD
        self._init_game()

    def _load_sounds(self):
        self.sounds = {
            'walk': pygame.mixer.Sound("music/walk.wav"),
            'jump': pygame.mixer.Sound("music/jump.wav"),
            'flower': pygame.mixer.Sound("music/flower_collect.wav"),
            'plant': pygame.mixer.Sound("music/plant.wav"),
            'atk1': pygame.mixer.Sound("music/atk.wav"),
            'wiz_atk': pygame.mixer.Sound("music/wiz_atk_fx.wav"),
            'thunder': pygame.mixer.Sound("music/thunder.wav"),
            'mino_atk': pygame.mixer.Sound("music/atk2.wav"),
            'damage': pygame.mixer.Sound("music/damage.wav"),
            'arrow_release': pygame.mixer.Sound("music/arrow_release.wav"),
            'arrow_hit': pygame.mixer.Sound("music/arrow_hit.wav"),
            'growl': pygame.mixer.Sound("music/mino_growl.wav"),
            'screech': pygame.mixer.Sound("music/GIRLS.wav"),
        }
        self.sounds['flower'].set_volume(0.7)
        self.sounds['screech'].set_volume(0.3)

    def _start_music(self):
        bg1 = pygame.mixer.Sound("music/kaze.wav")
        bg1.set_volume(0.3)
        bg2 = pygame.mixer.Sound("music/davyjones.wav")
        bg2.set_volume(0.5)
        bg3 = pygame.mixer.Sound("music/rain.wav")
        bg3.set_volume(0.3)
        self.channel0 = pygame.mixer.Channel(0)
        self.channel1 = pygame.mixer.Channel(1)
        self.channel2 = pygame.mixer.Channel(2)
        self.channel0.play(bg1, -1)
        self.channel1.play(bg2, -1)
        self.channel2.play(bg3, -1)

    def _init_game(self):
        self.game_over = 0
        self.screen_scroll = 0
        self.y_scroll = 0

        self.flower_group = pygame.sprite.Group()
        self.minotaur_group = pygame.sprite.Group()
        self.wizard_group = pygame.sprite.Group()
        self.eye_group = pygame.sprite.Group()
        self.arrow_group = pygame.sprite.Group()
        self.powerup_group = pygame.sprite.Group()
        self.shop_group = pygame.sprite.Group()
        self.npc_group = pygame.sprite.Group()

        diff = DIFFICULTY_SETTINGS[self.difficulty]

        world_data, self.last_terrain_y = worldgen.gen_new_world(self.difficulty)
        world_data = worldgen.base_connect(world_data)
        world_data = worldgen.place_items(world_data, self.difficulty)

        # For infinite mode, add start barrier
        if self.game_mode == MODE_INFINITE:
            from constants import BARRIER
            for r in range(17):
                if world_data[r][0] == 0:
                    world_data[r][0] = BARRIER

        # Find granny house column for classic mode interaction
        self.granny_house_col = -1
        if self.game_mode == MODE_CLASSIC:
            from constants import GRANNY_HOUSE
            for r in range(17):
                for c in range(len(world_data[r])):
                    if world_data[r][c] == GRANNY_HOUSE:
                        self.granny_house_col = c
                        break
                if self.granny_house_col >= 0:
                    break
        # Track granny house screen-x (will be updated by scroll)
        self.granny_house_x = self.granny_house_col * TILE_SIZE if self.granny_house_col >= 0 else -1
        self.at_granny = False

        # Track total world width in columns for infinite mode
        self.world_total_cols = len(world_data[0])
        # The rightmost pixel of the generated world
        self.world_right_edge = self.world_total_cols * TILE_SIZE
        # Cumulative scroll to track player's absolute world position
        self.total_scroll_x = 0
        self.total_scroll_y = 0

        self.player = Player(TILE_SIZE + 10, SCREEN_HEIGHT - 260 + 2,
                             self.sounds, flower_heal=diff['flower_heal'],
                             potion_heal=diff['potion_heal'])
        self.world = World(world_data, self.flower_group, self.minotaur_group,
                           self.wizard_group, self.eye_group, self.powerup_group,
                           self.sounds, difficulty=self.difficulty,
                           shop_group=self.shop_group, npc_group=self.npc_group)

        # Link shopkeepers to their nearest shop
        for npc in self.npc_group:
            if isinstance(npc, Shopkeeper):
                best_shop = None
                best_dist = 9999
                for shop in self.shop_group:
                    d = abs(npc.rect.x - shop.rect.centerx)
                    if d < best_dist:
                        best_dist = d
                        best_shop = shop
                npc.shop = best_shop
        self.health_bar = HealthBar()

        self.dummy_flower = ScoreFlower(20, TILE_SIZE)
        self.dummy_arrow = ArrowCount(20, TILE_SIZE + 40)

        self.text_x = TILE_SIZE
        self.text_y = 180

        self.powerup_iterations = []
        self.set_iterations = []
        self.dummy_arrow2 = []
        self.c_list = []
        self.active_p = 0

        self.thunder = False
        self.thunder2 = False
        self.co = 0

        self.rain = Rain(self.screen)
        self.pause_selection = 0

        self.kills = {'minotaur': 0, 'wizard': 0, 'eye': 0}
        self.kill_counter = KillCounter()
        self.inventory = Inventory()
        self.shop_ui = ShopUI()
        self.inv_tick_counter = 0

        # Distance traveled display for infinite mode
        self.distance_traveled = 0

    def restart(self):
        self._init_game()
        self.state = STATE_PLAYING

    def save_game(self):
        data = {
            'player_x': self.player.rect.x,
            'player_y': self.player.rect.y,
            'player_health': self.player.health,
            'player_flower_count': self.player.flower_count,
            'player_num_of_arrows': self.player.num_of_arrows,
            'player_direction': self.player.direction,
            'player_powerups': self.player.powerup_index,
            'game_mode': self.game_mode,
            'difficulty': self.difficulty,
        }
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f)

    def load_game(self):
        if not os.path.exists(SAVE_FILE):
            return False
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
        self.game_mode = data.get('game_mode', MODE_CLASSIC)
        self.difficulty = data.get('difficulty', DIFF_HARD)
        self._init_game()
        self.player.rect.x = data['player_x']
        self.player.rect.y = data['player_y']
        self.player.health = data['player_health']
        self.player.flower_count = data['player_flower_count']
        self.player.num_of_arrows = data['player_num_of_arrows']
        self.player.direction = data['player_direction']
        self.player.powerup_index = data['player_powerups']
        return True

    def _draw_text(self, text, font, color, x, y):
        img = font.render(text, True, color)
        self.screen.blit(img, (x, y))

    def _draw_text_centered(self, text, font, color, y):
        img = font.render(text, True, color)
        x = (SCREEN_WIDTH - img.get_width()) // 2
        self.screen.blit(img, (x, y))

    # ---- MENU ----

    def _draw_menu(self):
        self.screen.blit(self.background, (0, 0))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        self._draw_text_centered("Red Riding Hood", self.font_large, WHITE, 200)
        self._draw_text_centered("Press ENTER to Start", self.font_medium, WHITE, 400)

        if os.path.exists(SAVE_FILE):
            self._draw_text_centered("Press L to Load Game", self.font_medium, WHITE, 470)

        self._draw_text_centered("Press ESC to Quit", self.font_medium, WHITE, 540)
        self.rain.timer(time.time())

    def _handle_menu_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                self._handle_resize(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.mode_select_row = 0
                    self.state = STATE_MODE_SELECT
                elif event.key == pygame.K_l and os.path.exists(SAVE_FILE):
                    self.load_game()
                    self.state = STATE_PLAYING
                elif event.key == pygame.K_ESCAPE:
                    return False
        return True

    # ---- MODE SELECT ----

    def _draw_mode_select(self):
        self.screen.blit(self.background, (0, 0))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        self._draw_text_centered("Game Setup", self.font_large, WHITE, 150)

        # Row 0: Mode
        row0_color = CYAN if self.mode_select_row == 0 else WHITE
        mode_text = f"Mode:  < {MODE_LABELS[MODES[self.selected_mode]]} >"
        self._draw_text_centered(mode_text, self.font_medium, row0_color, 320)

        # Row 1: Difficulty
        row1_color = CYAN if self.mode_select_row == 1 else WHITE
        diff_text = f"Difficulty:  < {DIFF_LABELS[DIFFICULTIES[self.selected_diff]]} >"
        self._draw_text_centered(diff_text, self.font_medium, row1_color, 400)

        # Difficulty description
        desc = {
            DIFF_EASY: "Fewer enemies, lower damage, higher healing. No wizards.",
            DIFF_MEDIUM: "Moderate enemies and damage. No wizards.",
            DIFF_HARD: "Full enemies, full damage, low healing. Wizards spawn!",
        }
        self._draw_text_centered(
            desc[DIFFICULTIES[self.selected_diff]],
            self.font_small, YELLOW, 460
        )

        # Mode description
        mode_desc = {
            MODE_CLASSIC: "Fixed world - reach the end alive.",
            MODE_INFINITE: "Endless world - survive as long as you can!",
        }
        self._draw_text_centered(
            mode_desc[MODES[self.selected_mode]],
            self.font_small, YELLOW, 500
        )

        # Row 2: Start
        row2_color = CYAN if self.mode_select_row == 2 else WHITE
        self._draw_text_centered("> Start Game <", self.font_medium, row2_color, 580)

        self.rain.timer(time.time())

    def _handle_mode_select_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                self._handle_resize(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = STATE_MENU
                elif event.key == pygame.K_UP:
                    self.mode_select_row = (self.mode_select_row - 1) % 3
                elif event.key == pygame.K_DOWN:
                    self.mode_select_row = (self.mode_select_row + 1) % 3
                elif event.key == pygame.K_LEFT:
                    if self.mode_select_row == 0:
                        self.selected_mode = (self.selected_mode - 1) % len(MODES)
                    elif self.mode_select_row == 1:
                        self.selected_diff = (self.selected_diff - 1) % len(DIFFICULTIES)
                elif event.key == pygame.K_RIGHT:
                    if self.mode_select_row == 0:
                        self.selected_mode = (self.selected_mode + 1) % len(MODES)
                    elif self.mode_select_row == 1:
                        self.selected_diff = (self.selected_diff + 1) % len(DIFFICULTIES)
                elif event.key == pygame.K_RETURN:
                    if self.mode_select_row == 2:
                        self.game_mode = MODES[self.selected_mode]
                        self.difficulty = DIFFICULTIES[self.selected_diff]
                        self._init_game()
                        self.state = STATE_PLAYING
        return True

    # ---- PAUSE ----

    def _draw_pause(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        self._draw_text_centered("PAUSED", self.font_large, WHITE, 200)

        options = ["Resume", "Save Game", "Restart", "Quit to Menu"]
        for i, option in enumerate(options):
            color = CYAN if i == self.pause_selection else WHITE
            prefix = "> " if i == self.pause_selection else "  "
            self._draw_text_centered(prefix + option, self.font_medium, color, 350 + i * 60)

    def _handle_pause_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                self._handle_resize(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    self.state = STATE_PLAYING
                elif event.key == pygame.K_UP:
                    self.pause_selection = (self.pause_selection - 1) % 4
                elif event.key == pygame.K_DOWN:
                    self.pause_selection = (self.pause_selection + 1) % 4
                elif event.key == pygame.K_RETURN:
                    if self.pause_selection == 0:
                        self.state = STATE_PLAYING
                    elif self.pause_selection == 1:
                        self.save_game()
                        self._draw_text_centered("Game Saved!", self.font_medium, CYAN, 650)
                        self._present()
                        pygame.time.wait(800)
                        self.state = STATE_PLAYING
                    elif self.pause_selection == 2:
                        self.restart()
                    elif self.pause_selection == 3:
                        self.state = STATE_MENU
        return True

    # ---- GAME OVER ----

    def _draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        self._draw_text_centered("GAME OVER", self.font_large, (255, 50, 50), 200)
        self._draw_text_centered(
            f"Flowers collected: {self.player.flower_count}",
            self.font_medium, WHITE, 320
        )
        total_kills = sum(self.kills.values())
        self._draw_text_centered(
            f"Enemies slain: {total_kills}",
            self.font_medium, WHITE, 380
        )
        if self.game_mode == MODE_INFINITE:
            dist = int(self.distance_traveled / TILE_SIZE)
            self._draw_text_centered(
                f"Distance: {dist} tiles",
                self.font_medium, WHITE, 440
            )
        self._draw_text_centered("Press R to Restart", self.font_medium, WHITE, 520)
        self._draw_text_centered("Press ESC for Menu", self.font_medium, WHITE, 580)

    def _handle_game_over_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                self._handle_resize(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.restart()
                elif event.key == pygame.K_ESCAPE:
                    self.state = STATE_MENU
        return True

    # ---- WIN ----

    def _draw_win(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        self._draw_text_centered("You Made It!", self.font_large, (100, 255, 100), 160)
        self._draw_text_centered(
            "Red Riding Hood reached Granny's home safely",
            self.font_medium, WHITE, 260
        )
        self._draw_text_centered(
            f"Flowers for Granny: {self.player.flower_count}",
            self.font_medium, YELLOW, 340
        )
        total_kills = sum(self.kills.values())
        self._draw_text_centered(
            f"Enemies slain: {total_kills}",
            self.font_medium, WHITE, 400
        )
        self._draw_text_centered(
            f"Gold earned: {self.player.coins}",
            self.font_medium, YELLOW, 460
        )
        self._draw_text_centered("Press R to Play Again", self.font_medium, WHITE, 540)
        self._draw_text_centered("Press ESC for Menu", self.font_medium, WHITE, 600)

    def _handle_win_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                self._handle_resize(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.restart()
                elif event.key == pygame.K_ESCAPE:
                    self.state = STATE_MENU
        return True

    # ---- PLAYING ----

    def _handle_playing_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                self._handle_resize(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    self.pause_selection = 0
                    self.state = STATE_PAUSED
                elif event.key in (pygame.K_i, pygame.K_TAB):
                    self.inventory.selected = 0
                    self.state = STATE_INVENTORY
                elif event.key == pygame.K_e:
                    self._handle_e_interact()
        return True

    def _handle_e_interact(self):
        """Handle E key press with priority: flowers > hides > buildings."""
        px = self.player.rect.centerx

        # Priority 1: Pick up a nearby flower (one at a time)
        for flower in self.flower_group:
            if abs(px - flower.rect.centerx) < 60:
                self.sounds['flower'].play()
                if not flower.consumed:
                    self.player.flower_count += 1
                else:
                    self.player.health += self.player.flower_heal
                self.flower_group.remove(flower)
                return

        # Priority 2: Skin a nearby corpse (one at a time)
        for group in [self.minotaur_group, self.wizard_group, self.eye_group]:
            for enemy in group:
                if (enemy.health <= 0 and not enemy.alive and
                        not enemy.hide_collected and enemy.t > 0 and
                        abs(px - enemy.rect.centerx) < 80):
                    enemy.hide_collected = True
                    enemy.t = 0
                    self.player.hides[enemy.enemy_type] += 1
                    self.sounds['flower'].play()
                    return

        # Priority 3: NPCs (granny win, shopkeeper trade)
        for npc in self.npc_group:
            if abs(px - npc.rect.centerx) < 120:
                if isinstance(npc, Granny) and self.game_mode == MODE_CLASSIC:
                    self.state = STATE_WIN
                    return
                if isinstance(npc, Shopkeeper) and npc.shop:
                    self.shop_ui.open(npc.shop)
                    self.state = STATE_SHOPPING
                    return

    def _handle_inventory_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                self._handle_resize(event)
            if self.inventory.handle_input(event, self.player):
                self.inv_tick_counter = 0
                self.state = STATE_PLAYING
        return True

    def _handle_shopping_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                self._handle_resize(event)
            if self.shop_ui.handle_event(event, self.player,
                                         self.window_width, self.window_height):
                self.inv_tick_counter = 0
                self.state = STATE_PLAYING
        return True

    def _is_in_tick_range(self, entity):
        """Check if an entity is within tick distance of the player."""
        return abs(entity.rect.x - self.player.rect.x) <= TICK_DISTANCE

    def _extend_world_if_needed(self):
        """For infinite mode, generate a new chunk when approaching the edge."""
        # The player's absolute x in world space
        player_world_x = self.player.rect.x - self.total_scroll_x

        # Generate when within 2 screens of the right edge
        if self.world_right_edge - player_world_x < SCREEN_WIDTH * 2:
            chunk_data, self.last_terrain_y, num_cols = worldgen.gen_chunk(
                self.last_terrain_y, self.difficulty
            )
            chunk_data = worldgen.place_items(chunk_data, self.difficulty)

            # Snapshot what exists before adding the chunk
            old_tile_count = len(self.world.tile_list)
            old_entities = set()
            for group in [self.flower_group, self.minotaur_group,
                          self.wizard_group, self.eye_group,
                          self.powerup_group, self.shop_group,
                          self.npc_group]:
                old_entities.update(group.sprites())

            # add_chunk places tiles at absolute world coords
            # (col + world_total_cols) * TILE_SIZE
            self.world.add_chunk(chunk_data, self.world_total_cols)

            # Existing tiles have been shifted by total_scroll each frame.
            # New tiles are at absolute world positions — shift them to match.
            sx = int(self.total_scroll_x)
            sy = int(self.total_scroll_y)

            for tile in self.world.tile_list[old_tile_count:]:
                tile[1].x += sx
                tile[1].y += sy

            for group in [self.flower_group, self.minotaur_group,
                          self.wizard_group, self.eye_group,
                          self.powerup_group, self.shop_group,
                          self.npc_group]:
                for entity in group:
                    if entity not in old_entities:
                        entity.rect.x += sx
                        entity.rect.y += sy

            self.world_total_cols += num_cols
            self.world_right_edge = self.world_total_cols * TILE_SIZE

            # Link new shopkeepers to their nearest shop
            for npc in self.npc_group:
                if isinstance(npc, Shopkeeper) and npc.shop is None:
                    best_shop = None
                    best_dist = 9999
                    for shop in self.shop_group:
                        d = abs(npc.rect.x - shop.rect.centerx)
                        if d < best_dist:
                            best_dist = d
                            best_shop = shop
                    npc.shop = best_shop

    def _update_playing(self, enemy_tick_rate=1.0):
        self.screen.blit(self.background, (0, 0))

        # Determine if enemies should tick this frame (for inventory slowdown)
        self.inv_tick_counter += enemy_tick_rate
        enemies_tick = self.inv_tick_counter >= 1.0
        if enemies_tick:
            self.inv_tick_counter -= 1.0

        # --- LAYER 1: World backdrop (ground, trees, bushes, decorations) ---
        self.world.draw(self.screen, self.screen_scroll, self.y_scroll)

        # --- LAYER 2: Shops (behind player/enemies, on top of ground) ---
        for shop in self.shop_group:
            shop.update(self.screen_scroll, self.y_scroll, self.screen)

        # Tutorial text (world-space, scrolls with terrain)
        self.text_x += self.screen_scroll
        self.text_y += self.y_scroll
        self._draw_text("Collect flowers for granny", self.font, WHITE, self.text_x, self.text_y)
        self._draw_text("Collect flowers using E", self.font, WHITE, self.text_x, self.text_y + 40)
        self._draw_text(
            "Plant flowers using F and consume them again to heal",
            self.font, WHITE, self.text_x, self.text_y + 80
        )

        # --- LAYER 3: Ground items (flowers, powerups) ---
        for flower in self.flower_group:
            flower.update(self.screen_scroll, self.y_scroll, self.screen)
        for p in self.powerup_group:
            p.update(self.screen_scroll, self.y_scroll, self.screen)

        # --- LAYER 4: Active entities (player, enemies, arrows) ---
        if self.state in (STATE_INVENTORY, STATE_SHOPPING):
            # Freeze player movement, just draw at current position
            self.screen.blit(self.player.image, self.player.rect)
            self.screen_scroll = 0
            self.y_scroll = 0
            # Make sure walk sound isn't stuck
            self.sounds['walk'].stop()
            self.player.run_fx = False
        else:
            # Player (draws itself inside update)
            (self.screen_scroll, self.y_scroll) = self.player.update(
                self.game_over, self.screen, self.world, self.flower_group,
                self.minotaur_group, self.wizard_group, self.eye_group,
                self.arrow_group, self.powerup_group, Arrow
            )

        # Track scroll for infinite mode
        self.total_scroll_x += self.screen_scroll
        self.total_scroll_y += self.y_scroll
        if self.screen_scroll < 0:
            self.distance_traveled -= self.screen_scroll

        # Track granny house screen position
        if self.granny_house_x >= 0:
            self.granny_house_x += self.screen_scroll

        # Enemies — always update for rendering/physics/death,
        # but freeze AI on non-tick frames (inventory slowdown)
        frozen = not enemies_tick
        for m in self.minotaur_group:
            if self._is_in_tick_range(m):
                m.update(self.screen_scroll, self.y_scroll, self.screen,
                         self.world, self.player, self.minotaur_group,
                         self.sounds['damage'], frozen=frozen)
            else:
                m.rect.x += self.screen_scroll
                m.rect.y += self.y_scroll
                self.screen.blit(m.image, m.rect)

        for w in self.wizard_group:
            if self._is_in_tick_range(w):
                w.update(self.screen_scroll, self.y_scroll, self.screen,
                         self.world, self.player, self.wizard_group,
                         self.sounds['damage'], frozen=frozen)
            else:
                w.rect.x += self.screen_scroll
                w.rect.y += self.y_scroll
                self.screen.blit(w.image, w.rect)

        for e in self.eye_group:
            if self._is_in_tick_range(e):
                e.update(self.screen_scroll, self.y_scroll, self.screen,
                         self.world, self.player, self.eye_group,
                         self.sounds['damage'], frozen=frozen)
            else:
                e.rect.x += self.screen_scroll
                e.rect.y += self.y_scroll
                self.screen.blit(e.image, e.rect)

        # Arrows
        for a in list(self.arrow_group):
            a.update(self.screen_scroll, self.y_scroll, self.screen,
                     self.world, self.minotaur_group, self.wizard_group,
                     self.eye_group, self.arrow_group, self.sounds)

        # NPCs
        for npc in self.npc_group:
            npc.update(self.screen_scroll, self.y_scroll, self.screen,
                       self.world, self.player.rect)

        # Granny arrival detection (classic mode)
        self.at_granny = False
        if self.game_mode == MODE_CLASSIC:
            for npc in self.npc_group:
                if isinstance(npc, Granny):
                    if abs(self.player.rect.centerx - npc.rect.centerx) < 300:
                        self.at_granny = True
                        msg = self.font_large.render("You've reached Granny's home!", True, (255, 220, 100))
                        self.screen.blit(msg, ((SCREEN_WIDTH - msg.get_width()) // 2, 200))
                        hint = self.font_medium.render("Press E to end your journey", True, WHITE)
                        self.screen.blit(hint, ((SCREEN_WIDTH - hint.get_width()) // 2, 280))
                    break

        # --- LAYER 5: HUD (always on top) ---
        self._draw_text("HEALTH", self.font_health, WHITE, 0, 10)
        self._draw_text(
            "X" + str(self.player.flower_count),
            self.font_health, WHITE, 40, TILE_SIZE - 10
        )
        self._draw_text(
            "X" + str(self.player.num_of_arrows),
            self.font_health, WHITE, 50, TILE_SIZE + 40 - 10
        )

        mode_label = MODE_LABELS[self.game_mode]
        diff_label = DIFF_LABELS[self.difficulty]
        self._draw_text(f"{mode_label} | {diff_label}",
                        self.font_small, YELLOW, SCREEN_WIDTH - 280, 10)

        if self.game_mode == MODE_INFINITE:
            dist = int(self.distance_traveled / TILE_SIZE)
            self._draw_text(f"Distance: {dist}",
                            self.font_small, WHITE, SCREEN_WIDTH - 200, 40)

        self.health_bar.draw(self.screen, self.player.health)
        self.dummy_flower.update(self.screen)
        self.dummy_arrow.update(self.screen)

        # Kill tracking
        for m in self.minotaur_group:
            if m.health <= 0 and not m.kill_counted:
                m.kill_counted = True
                self.kills['minotaur'] += 1
        for w in self.wizard_group:
            if w.health <= 0 and not w.kill_counted:
                w.kill_counted = True
                self.kills['wizard'] += 1
        for e in self.eye_group:
            if e.health <= 0 and not e.kill_counted:
                e.kill_counted = True
                self.kills['eye'] += 1
        self.kill_counter.draw(self.screen, self.kills)

        # check death
        if self.player.health <= 0:
            self.game_over = -1

        # active powerup management
        self._update_powerups()

        # rain
        self.rain.timer(time.time())

        # thunder
        self._update_thunder()

        # infinite mode: extend world
        if self.game_mode == MODE_INFINITE:
            self._extend_world_if_needed()

        # transition to game over screen after death animation
        if self.game_over == -1 and self.player.ded_sequence:
            self.state = STATE_GAME_OVER

    def _update_powerups(self):
        for p in range(len(self.player.powerup_index)):
            if self.player.powerup_index[p][1]:
                self.powerup_iterations.append(1000)
                self.set_iterations.append(True)
                icon = ActivePowerupIcon(25, 150 + (60 * self.active_p),
                                         self.player.powerup_index[p][0])
                self.dummy_arrow2.append(icon)
                self.c_list.append(150 + (60 * self.active_p))
                self.powerup_group.add(self.dummy_arrow2[self.active_p])
                self.player.powerup_index[p][1] = False
                self.active_p += 1

        for inte in range(len(self.powerup_iterations)):
            if inte >= len(self.powerup_iterations):
                break
            if self.set_iterations[inte]:
                pygame.draw.rect(
                    self.screen, CYAN,
                    (55, self.c_list[inte], self.powerup_iterations[inte] / 10, 15)
                )
            if self.powerup_iterations[inte] > 0:
                self.powerup_iterations[inte] -= 1
            if self.powerup_iterations[inte] == 0:
                if self.set_iterations[inte]:
                    self.sounds['plant'].play()
                self.powerup_group.remove(self.dummy_arrow2[inte])
                self.dummy_arrow2.remove(self.dummy_arrow2[inte])
                self.set_iterations.remove(self.set_iterations[inte])
                self.player.powerup_index.remove(self.player.powerup_index[inte])
                self.c_list.remove(self.c_list[inte])
                self.powerup_iterations.remove(self.powerup_iterations[inte])
                self.active_p -= 1

    def _update_thunder(self):
        if random.randint(0, 200) == 7 and not self.thunder and not self.thunder2:
            self.thunder = True
        if self.thunder and self.co < 25:
            self.co += 1
        if self.co == 20:
            self.screen.fill(WHITE)
            self.thunder2 = True
        if self.co == 25 and self.thunder2:
            self.screen.fill(WHITE)
            self.co = 0
            self.thunder = False
            self.thunder2 = False
            self.sounds['thunder'].play()

    def _handle_resize(self, event):
        self.window_width = event.w
        self.window_height = event.h
        self.window = pygame.display.set_mode(
            (self.window_width, self.window_height), pygame.RESIZABLE
        )

    def _present(self):
        pygame.transform.scale(self.screen, (self.window_width, self.window_height), self.window)
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)

            if self.state == STATE_MENU:
                self._draw_menu()
                running = self._handle_menu_events()

            elif self.state == STATE_MODE_SELECT:
                self._draw_mode_select()
                running = self._handle_mode_select_events()

            elif self.state == STATE_PLAYING:
                self._update_playing()
                running = self._handle_playing_events()

            elif self.state == STATE_PAUSED:
                self._draw_pause()
                running = self._handle_pause_events()

            elif self.state == STATE_INVENTORY:
                diff = DIFFICULTY_SETTINGS[self.difficulty]
                self._update_playing(enemy_tick_rate=diff['inv_tick_rate'])
                self.inventory.draw(self.screen, self.player)
                running = self._handle_inventory_events()

            elif self.state == STATE_SHOPPING:
                diff = DIFFICULTY_SETTINGS[self.difficulty]
                self._update_playing(enemy_tick_rate=diff['inv_tick_rate'])
                self.shop_ui.draw(self.screen, self.player,
                                  self.window_width, self.window_height)
                running = self._handle_shopping_events()

            elif self.state == STATE_GAME_OVER:
                self._update_playing()
                self._draw_game_over()
                running = self._handle_game_over_events()

            elif self.state == STATE_WIN:
                self._update_playing()
                self._draw_win()
                running = self._handle_win_events()

            self._present()

        pygame.quit()
