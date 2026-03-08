import pygame
import random
from constants import TILE_SIZE, RED, GREEN
from physics import apply_gravity, check_tile_collisions


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, health, damage, sprite_size, detect_thresh=400,
                 atk_cooldown=10, idle_cooldown=5, move_speed=1, chase_speed=4,
                 dead_cooldown=5, corpse_timer=600, damage_mult=1.0):
        pygame.sprite.Sprite.__init__(self)
        self.health = health
        self.max_health = health
        self.damage = int(damage * damage_mult)
        self.sprite_size = sprite_size
        self.detect_thresh = detect_thresh
        self.atk_cooldown = atk_cooldown
        self._idle_cooldown = idle_cooldown
        self.move_speed = move_speed
        self.chase_speed = chase_speed
        self._dead_cooldown = dead_cooldown
        self.corpse_timer = corpse_timer

        self.images_right_idle = []
        self.images_left_idle = []
        self.images_right_run = []
        self.images_left_run = []
        self.images_right_atk1 = []
        self.images_left_atk1 = []
        self.images_right_ded = []
        self.images_left_ded = []

        self.index = 0
        self.counter = 0
        self.idle_index = 0
        self.idle_counter = 0
        self.direction = 1
        self.move_counter = 0
        self.move_direction = 1
        self.is_moving = False
        self.run_counter = 0
        self.iterations = 0
        self.detect_player = False
        self.atk1_index = 0
        self.atk1_counter = 0
        self.atk1_sequence = False
        self.atk1_music = False
        self.dead_counter = 0
        self.dead_index = 0
        self.alive = True
        self.ded_music = False
        self.jumped = False
        self.in_air = False
        self.t = corpse_timer

        self.vel_y = 0
        self.dx = 0
        self.dy = 0
        self.kill_counted = False
        self.hide_collected = False
        self.enemy_type = 'unknown'

        self._prompt_font = pygame.font.Font("AmaticSC-Bold.ttf", 32)

        self.image = None
        self.rect = None
        self.width = 0
        self.height = 0

    def load_sprites(self, idle_path, idle_count, run_path, run_count,
                     atk_path, atk_count, ded_path, ded_count):
        for num in range(1, idle_count + 1):
            img = pygame.image.load(idle_path.format(num)).convert_alpha()
            img = pygame.transform.scale(img, self.sprite_size)
            self.images_right_idle.append(img)
            self.images_left_idle.append(pygame.transform.flip(img, True, False))

        if run_path:
            for num in range(1, run_count + 1):
                img = pygame.image.load(run_path.format(num)).convert_alpha()
                img = pygame.transform.scale(img, self.sprite_size)
                self.images_right_run.append(img)
                self.images_left_run.append(pygame.transform.flip(img, True, False))

        for num in range(1, atk_count + 1):
            img = pygame.image.load(atk_path.format(num)).convert_alpha()
            img = pygame.transform.scale(img, self.sprite_size)
            self.images_right_atk1.append(img)
            self.images_left_atk1.append(pygame.transform.flip(img, True, False))

        for num in range(1, ded_count + 1):
            img = pygame.image.load(ded_path.format(num)).convert_alpha()
            img = pygame.transform.scale(img, self.sprite_size)
            self.images_right_ded.append(img)
            self.images_left_ded.append(pygame.transform.flip(img, True, False))

        self.image = self.images_right_idle[0]

    def _finish_init(self, x, y):
        self.image = self.images_right_idle[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self, screen_scroll, y_scroll, screen, world, player,
               enemy_group, damage_fx, frozen=False):
        self.dx = 0
        self.dy = 0
        if self.health <= 0:
            self._handle_death(screen_scroll, screen, enemy_group, damage_fx)
        else:
            if frozen:
                self._idle(screen_scroll, screen)
            elif self.atk1_sequence:
                self._handle_attack(screen_scroll, screen, player, damage_fx)
            else:
                if abs(player.rect.x - self.rect.x) <= self.detect_thresh:
                    self.detect_player = True
                    self._on_detect(player)
                if not self.detect_player:
                    if self.is_moving:
                        self._move(screen_scroll, screen, world)
                    else:
                        self._idle(screen_scroll, screen)
                else:
                    self._ai(screen_scroll, screen, world, player)

        self._apply_physics(screen_scroll, y_scroll, screen, world)

    def _handle_death(self, screen_scroll, screen, enemy_group, damage_fx):
        if not self.ded_music:
            damage_fx.play()
            self.ded_music = True
        if self.alive:
            self.dead_counter += 1
            if self.dead_counter > 10:
                self._ded_anim(screen_scroll, screen)
            else:
                screen.blit(self.image, self.rect)
        else:
            if self.t > 0:
                self.t -= 1
                if self.direction == 1:
                    self.image = self.images_right_ded[-1]
                else:
                    self.image = self.images_left_ded[-1]
                screen.blit(self.image, self.rect)
                # Show "E" prompt above the health bar
                if not self.hide_collected:
                    prompt = self._prompt_font.render("'E' to skin", True, (255, 255, 100))
                    screen.blit(prompt,
                                (self.rect.centerx - prompt.get_width() // 2,
                                 self.rect.top - 30))
            else:
                enemy_group.remove(self)

    def _handle_attack(self, screen_scroll, screen, player, damage_fx):
        self.iterations += 1
        self.atk1_counter += 1
        if self.atk1_counter > self.atk_cooldown:
            self.atk1_counter = 0
            self.atk1_index += 1
            if self.atk1_index >= len(self.images_right_atk1):
                self.atk1_sequence = False
                self.atk1_index = 0
                self.atk1_music = False
                self.iterations = 0

            if self._is_damage_frame():
                if self.rect.colliderect(player.rect):
                    player.health -= self.damage
                    if player.health <= 0:
                        damage_fx.play()

            if self.direction == 1:
                self.image = self.images_right_atk1[self.atk1_index]
            else:
                self.image = self.images_left_atk1[self.atk1_index]

        screen.blit(self.image, self.rect)

    def _is_damage_frame(self):
        mid = len(self.images_right_atk1) // 2
        return self.atk1_index >= mid and self.atk1_index <= mid

    def _on_detect(self, player):
        pass

    def _idle(self, screen_scroll, screen):
        self.idle_counter += 1
        if self.idle_counter > self._idle_cooldown:
            self.idle_counter = 0
            self.idle_index += 1
            if self.idle_index >= len(self.images_right_idle):
                self.idle_index = 0
                self.iterations += 1
                if self.iterations == 3:
                    self.is_moving = True
                    self.iterations = 0
            if self.direction == 1:
                self.image = self.images_right_idle[self.idle_index]
            else:
                self.image = self.images_left_idle[self.idle_index]
        screen.blit(self.image, self.rect)

    def _ded_anim(self, screen_scroll, screen):
        self.dead_counter += 1
        if self.dead_counter > self._dead_cooldown:
            self.dead_counter = 0
            self.dead_index += 1
            if self.dead_index >= len(self.images_right_ded):
                self.dead_index = 0
                self.dead_counter = 0
                self.alive = False
            if self.direction == 1:
                self.image = self.images_right_ded[self.dead_index]
            else:
                self.image = self.images_left_ded[self.dead_index]
        screen.blit(self.image, self.rect)

    def _move(self, screen_scroll, screen, world):
        self.dx += self.move_direction * self.move_speed
        self.direction = self.move_direction
        self.move_counter += 1
        self.run_counter += 1

        run_images = self.images_right_run or self.images_right_idle
        run_images_left = self.images_left_run or self.images_left_idle

        if self.run_counter > 5:
            self.run_counter = 0
            self.index += 1
            if self.index >= len(run_images):
                self.index = 0
            if self.direction == 1:
                self.image = run_images[self.index]
            else:
                self.image = run_images_left[self.index]

        self._obstacle_jump(world)
        screen.blit(self.image, self.rect)

        if abs(self.move_counter) > 120:
            self.is_moving = False
            self.move_direction *= -1
            self.move_counter *= -1

    def _ai(self, screen_scroll, screen, world, player):
        if self.rect.colliderect(player.rect):
            self.atk1_sequence = True
            if not self.atk1_music:
                self.iterations = 0
                self._play_attack_sound()
                self.atk1_music = True

        if self.detect_player and not self.atk1_sequence:
            if (player.rect.x - self.rect.x) < 0:
                self.direction = -1
                self.dx -= self.chase_speed
            else:
                self.direction = 1
                self.dx += self.chase_speed

        self.run_counter += 1
        run_images = self.images_right_run or self.images_right_idle
        run_images_left = self.images_left_run or self.images_left_idle

        if self.run_counter > 5:
            self.run_counter = 0
            self.index += 1
            if self.index >= len(run_images):
                self.index = 0
            if self.direction == 1:
                self.image = run_images[self.index]
            else:
                self.image = run_images_left[self.index]

        if not self.atk1_sequence:
            self._obstacle_jump(world)

        screen.blit(self.image, self.rect)

        if self.detect_player and abs(player.rect.x - self.rect.x) > self._disengage_range():
            self.detect_player = False

    def _obstacle_jump(self, world):
        for tile in world.tile_list:
            if (tile[2] and tile[1].colliderect(
                    self.rect.x + self.dx, self.rect.y,
                    self.width, self.height) and not self.jumped):
                self.vel_y -= 15
                self.jumped = True

    def _play_attack_sound(self):
        pass

    def _disengage_range(self):
        return 300

    def _apply_physics(self, screen_scroll, y_scroll, screen, world):
        apply_gravity(self)
        check_tile_collisions(self, world.tile_list)
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.rect.x += screen_scroll
        self.rect.y += y_scroll
        # Only show health bar while alive
        if self.health > 0:
            self._draw_healthbar(screen)

    def _draw_healthbar(self, screen):
        offset_x = 15 if self.direction == 1 else 40
        pygame.draw.rect(screen, RED,
                         (self.rect.x + offset_x, self.rect.y - 7,
                          int(self.max_health // 4), 10))
        pygame.draw.rect(screen, GREEN,
                         (self.rect.x + offset_x, self.rect.y - 7,
                          int(self.health // 4), 10))


class Minotaur(Enemy):
    def __init__(self, x, y, sounds, damage_mult=1.0):
        size = (TILE_SIZE + 48, 90)
        super().__init__(x, y, health=200, damage=20, sprite_size=size,
                         detect_thresh=400, atk_cooldown=10, idle_cooldown=5,
                         move_speed=1, chase_speed=4, damage_mult=damage_mult)
        self.sounds = sounds
        self.enemy_type = 'minotaur'

        self.images_right_taunt = []
        self.images_left_taunt = []
        self.taunt_counter = 0
        self.taunt_index = 0
        self.taunt_time = 0
        self.taunt_music = False
        self.taunt_sequence = False
        self.taunt_complete = False

        self.load_sprites(
            idle_path="img/Mino_idle_list/idle{}.png", idle_count=5,
            run_path="img/Mino_run_list/run{}.png", run_count=8,
            atk_path="img/Mino_atk_list/atk{}.png", atk_count=9,
            ded_path="img/Mino_ded_list/ded{}.png", ded_count=3,
        )

        for num in range(1, 6):
            img = pygame.image.load(f"img/mino_taunt/taunt{num}.png").convert_alpha()
            img = pygame.transform.scale(img, size)
            self.images_right_taunt.append(img)
            self.images_left_taunt.append(pygame.transform.flip(img, True, False))

        self._finish_init(x, y)

    def _on_detect(self, player):
        self.taunt_sequence = True

    def update(self, screen_scroll, y_scroll, screen, world, player,
               enemy_group, damage_fx, frozen=False):
        self.dx = 0
        self.dy = 0
        if self.health <= 0:
            self._handle_death(screen_scroll, screen, enemy_group, damage_fx)
        else:
            if frozen:
                self._idle(screen_scroll, screen)
            elif self.atk1_sequence:
                self._handle_attack(screen_scroll, screen, player, damage_fx)
            else:
                if abs(player.rect.x - self.rect.x) <= self.detect_thresh:
                    self.detect_player = True
                    self.taunt_sequence = True
                if self.taunt_sequence and not self.taunt_complete:
                    if not self.taunt_music:
                        self.sounds['growl'].play()
                        self.taunt_music = True
                    self._taunt(screen_scroll, screen, player)
                else:
                    if not self.detect_player:
                        if self.is_moving:
                            self._move(screen_scroll, screen, world)
                        else:
                            self._idle(screen_scroll, screen)
                    else:
                        self._ai(screen_scroll, screen, world, player)

        self._apply_physics(screen_scroll, y_scroll, screen, world)

    def _taunt(self, screen_scroll, screen, player):
        taunt_cooldown = 8
        self.taunt_counter += 1
        self.taunt_time += 1
        if self.taunt_counter > taunt_cooldown:
            self.taunt_counter = 0
            self.taunt_index += 1
            if self.taunt_index >= len(self.images_right_taunt):
                self.taunt_index = 0
            if (player.rect.x - self.rect.x) < 0:
                self.direction = -1
            else:
                self.direction = 1
            if self.direction == 1:
                self.image = self.images_right_taunt[self.taunt_index]
            else:
                self.image = self.images_left_taunt[self.taunt_index]
        if abs(self.taunt_time) > 120:
            self.taunt_time = 0
            self.taunt_sequence = False
            self.taunt_music = False
            self.taunt_complete = True
        screen.blit(self.image, self.rect)

    def _play_attack_sound(self):
        self.sounds['mino_atk'].play()


class Wizard(Enemy):
    def __init__(self, x, y, sounds, damage_mult=1.0):
        size = (int(TILE_SIZE * 2.5), TILE_SIZE * 4)
        super().__init__(x, y, health=300, damage=50, sprite_size=size,
                         detect_thresh=300, atk_cooldown=5, idle_cooldown=8,
                         move_speed=7, chase_speed=6, damage_mult=damage_mult)
        self.sounds = sounds
        self.enemy_type = 'wizard'

        self.load_sprites(
            idle_path="img/wizard_idle/Idle{}.png", idle_count=8,
            run_path="img/Run_idle/Run{}.png", run_count=8,
            atk_path="img/wiz_atk/Attack{}.png", atk_count=8,
            ded_path="img/wiz_ded/Death{}.png", ded_count=7,
        )
        self._finish_init(x, y)

    def _obstacle_jump(self, world):
        for tile in world.tile_list:
            if (tile[2] and tile[1].colliderect(
                    self.rect.x + self.dx, self.rect.y,
                    self.width, self.height) and not self.jumped):
                self.vel_y -= 20
                self.jumped = True

    def _play_attack_sound(self):
        self.sounds['wiz_atk'].play()

    def _ded_anim(self, screen_scroll, screen):
        self.dead_counter += 1
        if self.dead_counter > 7:
            self.dead_counter = 0
            self.dead_index += 1
            if self.dead_index >= len(self.images_right_ded):
                self.dead_index = 0
                self.dead_counter = 0
                self.alive = False
            if self.direction == 1:
                self.image = self.images_right_ded[self.dead_index]
            else:
                self.image = self.images_left_ded[self.dead_index]
        screen.blit(self.image, self.rect)


class Eye(Enemy):
    def __init__(self, x, y, sounds, damage_mult=1.0):
        size = (TILE_SIZE + 48, 90)
        super().__init__(x, y, health=60, damage=10, sprite_size=size,
                         detect_thresh=300, atk_cooldown=6, idle_cooldown=5,
                         move_speed=6, chase_speed=4, damage_mult=damage_mult)
        self.sounds = sounds
        self.enemy_type = 'eye'
        self.fly_counter = 0
        self.updown = random.choice([1, -1])

        self.load_sprites(
            idle_path="img/eye/Flight{}.png", idle_count=8,
            run_path=None, run_count=0,
            atk_path="img/eye_attack/Attack{}.png", atk_count=8,
            ded_path="img/eye_ded/Death{}.png", ded_count=4,
        )
        self._finish_init(x, y)

    def _is_damage_frame(self):
        return (self.atk1_index >= len(self.images_right_atk1) - 1 and
                self.atk1_index <= len(self.images_right_atk1))

    def _draw_healthbar(self, screen):
        offset_x = 57 if self.direction == 1 else 40
        pygame.draw.rect(screen, RED,
                         (self.rect.x + offset_x, self.rect.y - 7,
                          int(self.max_health // 4), 10))
        pygame.draw.rect(screen, GREEN,
                         (self.rect.x + offset_x, self.rect.y - 7,
                          int(self.health // 4), 10))

    def _obstacle_jump(self, world):
        for tile in world.tile_list:
            if (tile[2] and tile[1].colliderect(
                    self.rect.x + self.dx, self.rect.y,
                    self.width, self.height) and not self.jumped):
                self.dy = -3
                self.jumped = True

    def _ai(self, screen_scroll, screen, world, player):
        if self.rect.colliderect(player.rect):
            self.atk1_sequence = True
            if not self.atk1_music:
                self.iterations = 0
                self.sounds['screech'].play(0, 850)
                self.atk1_music = True

        if self.detect_player and not self.atk1_sequence:
            if (player.rect.x - self.rect.x) < 0:
                self.direction = -1
                self.dx = -4
            else:
                self.direction = 1
                self.dx = 4
            if (player.rect.y - self.rect.y) <= 0:
                self.dy = -2
            else:
                self.dy = 2

        self.run_counter += 1
        if self.run_counter > 5:
            self.run_counter = 0
            self.index += 1
            if self.index >= len(self.images_right_idle):
                self.index = 0
            if self.direction == 1:
                self.image = self.images_right_idle[self.index]
            else:
                self.image = self.images_left_idle[self.index]

        if not self.atk1_sequence:
            self._obstacle_jump(world)

        screen.blit(self.image, self.rect)

        if self.detect_player and abs(player.rect.x - self.rect.x) > 1000:
            self.detect_player = False

    def _apply_physics(self, screen_scroll, y_scroll, screen, world):
        if not self.alive:
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            self.dy += self.vel_y
        else:
            if self.fly_counter == 0:
                self.fly_counter = 100
                self.dy = self.updown
                self.updown *= -1
        self.fly_counter -= 1

        self.in_air = True
        for tile in world.tile_list:
            if tile[2] and tile[1].colliderect(
                self.rect.x + self.dx, self.rect.y,
                self.width, self.height
            ):
                self.dx = 0
            if tile[2] and tile[1].colliderect(
                self.rect.x, self.rect.y + self.dy,
                self.width, self.height
            ):
                if self.vel_y < 0:
                    self.dy = tile[1].bottom - self.rect.top
                    self.vel_y = 0
                elif self.vel_y >= 0:
                    self.dy = tile[1].top - self.rect.bottom
                    self.vel_y = 0
                    self.in_air = False
                    self.jumped = False
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.rect.x += screen_scroll
        self.rect.y += y_scroll
        if self.health > 0:
            self._draw_healthbar(screen)

    def _play_attack_sound(self):
        self.sounds['screech'].play(0, 850)

    def _disengage_range(self):
        return 1000
