import pygame
from constants import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, SCROLL_THRESH
from physics import apply_gravity, check_tile_collisions


class Player:
    def __init__(self, x, y, sounds, flower_heal=5, potion_heal=25):
        self.sounds = sounds
        self.flower_heal = flower_heal
        self.potion_heal = potion_heal
        self.speed = 5
        self.coins = 0
        self.health_potions = 0
        self.hides = {'minotaur': 0, 'wizard': 0, 'eye': 0}
        self.images_right_idle = []
        self.images_left_idle = []
        self.images_right_run = []
        self.images_left_run = []
        self.images_right_jump = []
        self.images_left_jump = []
        self.images_right_latk = []
        self.images_left_latk = []
        self.images_right_shoot = []
        self.images_left_shoot = []
        self.images_right_ded = []
        self.images_left_ded = []
        self.index = 0
        self.counter = 0
        self.run_fx = False
        self.walk_music = 0
        self.jump_counter = 0
        self.jump_index = 0
        self.idle_counter = 0
        self.idle_index = 0
        self.flower_count = 0
        self.flower_counter = 0
        self.latk_index = 0
        self.latk_counter = 0
        self.latk_dmg = 50
        self.light_atk_sequence = False
        self.atk_music = False
        self.health = 100
        self.flower_cooler = 0
        self.shoot_index = 0
        self.shoot_counter = 0
        self.shoot_sequence = False
        self.shoot_music = False
        self.powerup_index = []

        self.ded_index = 0
        self.ded_counter = 0
        self.ded_sequence = False
        self.ded_music = False

        self.num_of_arrows = 12

        self._load_sprites()

        self.image = self.images_right_idle[self.idle_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 1
        self.in_air = True
        self.ground_level = self.rect.bottom
        self.dx = 0
        self.dy = 0

    def _load_sprites(self):
        for num in range(1, 4):
            img = pygame.image.load(f"img/idle{num}.png").convert_alpha()
            img = pygame.transform.scale(img, (40, 80))
            self.images_right_idle.append(img)
            self.images_left_idle.append(pygame.transform.flip(img, True, False))
        for num in range(1, 12):
            img = pygame.image.load(f"img/run{num}.png").convert_alpha()
            img = pygame.transform.scale(img, (40, 80))
            self.images_right_run.append(img)
            self.images_left_run.append(pygame.transform.flip(img, True, False))
        for num in range(1, 7):
            img = pygame.image.load(f"img/jump{num}.png").convert_alpha()
            img = pygame.transform.scale(img, (40, 80))
            self.images_right_jump.append(img)
            self.images_left_jump.append(pygame.transform.flip(img, True, False))
        for num in range(1, 9):
            img = pygame.image.load(f"img/lightatk/latk{num}.png").convert_alpha()
            img = pygame.transform.scale(img, (40, 80))
            self.images_right_latk.append(img)
            self.images_left_latk.append(pygame.transform.flip(img, True, False))
        for num in range(1, 13):
            img = pygame.image.load(f"img/shoot_list/shoot{num}.png").convert_alpha()
            img = pygame.transform.scale(img, (40, 80))
            img_right = pygame.transform.flip(img, True, False)
            self.images_right_shoot.append(img_right)
            self.images_left_shoot.append(img)
        for num in range(1, 7):
            img = pygame.image.load(f"img/ded_list/ded{num}.png").convert_alpha()
            img = pygame.transform.scale(img, (40, 80))
            img_right = pygame.transform.flip(img, True, False)
            self.images_right_ded.append(img_right)
            self.images_left_ded.append(img)

    def update(self, game_over, screen, world, flower_group, minotaur_group,
               wizard_group, eye_group, arrow_group, powerup_group, Arrow):
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.health = 0
        screen_scroll = 0
        y_scroll = 0
        self.dx = 0
        self.dy = 0
        walk_cooldown = 1
        idle_cooldown = 8
        flower_cooldown = 8

        if game_over == 0:
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and not self.jumped and not self.in_air:
                self.sounds['jump'].play()
                self.vel_y = -15
                self.jumped = True

            if not key[pygame.K_SPACE]:
                self.jumped = False

            if key[pygame.K_LEFT]:
                if not self.run_fx:
                    self.run_fx = True
                    self.sounds['walk'].play()
                self.dx -= self.speed
                self.counter += 1
                self.walk_music += 1
                self.direction = -1

            if key[pygame.K_RIGHT]:
                if not self.run_fx:
                    self.run_fx = True
                    self.sounds['walk'].play()
                self.dx += self.speed
                self.counter += 1
                self.walk_music += 1
                self.direction = 1

            if not key[pygame.K_LEFT] and not key[pygame.K_RIGHT]:
                self.sounds['walk'].stop()
                self.run_fx = False
                self.idle_counter += 1
                if self.idle_counter > idle_cooldown:
                    self.idle_counter = 0
                    self.idle_index += 1
                    if self.idle_index >= len(self.images_right_idle):
                        self.idle_index = 0
                    if self.direction == 1:
                        self.image = self.images_right_idle[self.idle_index]
                    else:
                        self.image = self.images_left_idle[self.idle_index]

            # plant flowers
            if key[pygame.K_f] and self.flower_cooler <= 0 and not self.in_air:
                self.flower_counter += 1
                if self.flower_count > 0:
                    if self.flower_counter > flower_cooldown:
                        self.flower_counter = 0
                        self.flower_count -= 1
                        from sprites import Flower
                        flower = Flower(self.rect.x, self.rect.y + 22)
                        flower.consumed = True
                        flower_group.add(flower)
                        self.sounds['plant'].play()
                        self.flower_cooler = 50

            # light attack
            if key[pygame.K_q]:
                if not self.atk_music:
                    self.sounds['atk1'].play()
                    self.atk_music = True
                self.light_atk_sequence = True

            # shoot arrows
            if key[pygame.K_w] and self.num_of_arrows > 0:
                if not self.shoot_music:
                    self.sounds['arrow_release'].play()
                    self.shoot_music = True
                    self.num_of_arrows -= 1
                self.shoot_sequence = True

            # run animation
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right_run):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right_run[self.index]
                else:
                    self.image = self.images_left_run[self.index]

            # jump animation
            if self.in_air:
                self.walk_music = 0
                self.sounds['walk'].stop()
                self.run_fx = False
                self.jump_index = 0
                self.jump_index += 1
                if self.jump_index >= len(self.images_right_jump):
                    self.jump_index = 0
                if self.direction == 1:
                    self.image = self.images_right_jump[self.jump_index]
                else:
                    self.image = self.images_left_jump[self.jump_index]

            # gravity
            apply_gravity(self)

            # collision
            self.in_air = True
            for tile in world.tile_list:
                if tile[2]:
                    if tile[1].colliderect(
                        self.rect.x + self.dx, self.rect.y,
                        self.width, self.height
                    ):
                        self.dx = 0
                    if tile[1].colliderect(
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
                            self.ground_level = self.rect.y

            # powerup collision
            if pygame.sprite.spritecollide(self, powerup_group, False):
                powerup_list = pygame.sprite.spritecollide(self, powerup_group, True)
                for powerup in powerup_list:
                    if powerup.index == 1:
                        powerup_group.remove(powerup)
                        self.sounds['flower'].play()
                        self.num_of_arrows += 5
                    elif powerup.index == 2:
                        powerup_group.remove(powerup)
                        self.sounds['flower'].play()
                        self.powerup_index.append(list([2, True]))
                    elif powerup.index == 3:
                        powerup_group.remove(powerup)
                        self.sounds['flower'].play()
                        self.powerup_index.append(list([3, True]))

            self.rect.x += self.dx
            self.rect.y += self.dy

            # scroll
            if ((self.rect.right > (SCREEN_WIDTH - SCROLL_THRESH) and self.direction == 1) or
                    (self.rect.left < SCROLL_THRESH and self.direction == -1)):
                self.rect.x -= self.dx
                screen_scroll = -self.dx

            if ((self.rect.top < 200) or
                    ((self.rect.bottom > (SCREEN_HEIGHT - 400)) and
                     (self.rect.bottom < (SCREEN_HEIGHT - 300))) or
                    (self.rect.bottom < (SCREEN_HEIGHT - 150))):
                self.rect.y -= self.dy
                y_scroll = -self.dy

            # draw
            if self.light_atk_sequence:
                self._latk(screen, minotaur_group, wizard_group, eye_group)
            elif self.shoot_sequence:
                self._shoot_arrow(screen, arrow_group, Arrow)
            else:
                screen.blit(self.image, self.rect)
            self.flower_cooler -= 1
            if self.flower_cooler < 0:
                self.flower_cooler = 0

        elif game_over == -1:
            if not self.ded_sequence:
                self._ded(screen)
                if self.ded_music:
                    self.sounds['damage'].play()
                    self.ded_music = False
            else:
                self.image = self.images_left_ded[5]
                screen.blit(self.image, self.rect)

            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            self.dy += self.vel_y
            self.in_air = True
            for tile in world.tile_list:
                if tile[2]:
                    if tile[1].colliderect(
                        self.rect.x + self.dx, self.rect.y,
                        self.width, self.height
                    ):
                        self.dx = 0
                    if tile[1].colliderect(
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

        return screen_scroll, y_scroll

    def _latk(self, screen, minotaur_group, wizard_group, eye_group):
        latk_cooldown = 2
        self.latk_counter += 1
        if self.latk_counter > latk_cooldown:
            self.latk_counter = 0
            self.latk_index += 1
            if self.latk_index >= len(self.images_right_latk):
                self.light_atk_sequence = False
                self.latk_index = 0
                if pygame.sprite.spritecollide(self, minotaur_group, False):
                    for m in pygame.sprite.spritecollide(self, minotaur_group, False):
                        m.health -= self.latk_dmg
                if pygame.sprite.spritecollide(self, wizard_group, False):
                    for w in pygame.sprite.spritecollide(self, wizard_group, False):
                        w.health -= self.latk_dmg
                if pygame.sprite.spritecollide(self, eye_group, False):
                    for e in pygame.sprite.spritecollide(self, eye_group, False):
                        e.health -= self.latk_dmg
                self.atk_music = False
            if self.direction == 1:
                self.image = self.images_right_latk[self.latk_index]
            else:
                self.image = self.images_left_latk[self.latk_index]
            screen.blit(self.image, self.rect)
        else:
            screen.blit(self.image, self.rect)

    def _shoot_arrow(self, screen, arrow_group, Arrow):
        shoot_cooldown = 1
        self.shoot_counter += 1
        if self.shoot_counter > shoot_cooldown:
            self.shoot_counter = 0
            self.shoot_index += 1
            if self.shoot_index >= len(self.images_right_shoot):
                self.shoot_sequence = False
                self.shoot_index = 0

            if self.shoot_index == 5:
                i = 1
                j = 1
                cond = 0
                for powerup in self.powerup_index:
                    cond = 1
                    if powerup[0] == 2:
                        arrow_group.add(Arrow(self.rect.centerx, self.rect.centery, self.direction))
                        arrow_group.add(Arrow(self.rect.centerx, self.rect.centery - (7 * i), self.direction))
                        arrow_group.add(Arrow(self.rect.centerx, self.rect.centery + (7 * i), self.direction))
                        i += 1
                    elif powerup[0] == 3:
                        arrow = Arrow(self.rect.centerx, self.rect.centery, self.direction)
                        arrow.damage *= 4 * j
                        arrow_group.add(arrow)
                        j += 1
                if cond == 0:
                    arrow_group.add(Arrow(self.rect.centerx, self.rect.centery, self.direction))
                self.shoot_music = False

            if self.direction == 1:
                self.image = self.images_right_shoot[self.shoot_index]
            else:
                self.image = self.images_left_shoot[self.shoot_index]

        screen.blit(self.image, self.rect)

    def _ded(self, screen):
        ded_cooldown = 2
        self.ded_counter += 1
        if self.ded_counter > ded_cooldown:
            self.ded_counter = 0
            self.ded_index += 1
            if self.ded_index >= len(self.images_right_ded):
                self.ded_sequence = True
                self.ded_index = 0
            if self.direction == 1:
                self.image = self.images_right_ded[self.ded_index]
            else:
                self.image = self.images_left_ded[self.ded_index]
        screen.blit(self.image, self.rect)
