import pygame
import random
from constants import TILE_SIZE
from physics import apply_gravity, check_tile_collisions


_SHOPKEEPER_DIALOGUES = [
    "Care to trade?",
    "Fresh potions, just in!",
    "Got hides? I'll pay well.",
    "Arrows, cheap today!",
    "What'll it be?",
    "Best deals in the forest!",
]

_GRANNY_DIALOGUES = [
    "Welcome home, kiddo!",
    "Got my flowers?",
    "You made it safe!",
    "Come in, come in!",
    "My brave girl!",
    "I baked cookies!",
]


class NPC(pygame.sprite.Sprite):
    """Base NPC with idle animation, gravity, facing player, and dialogue."""

    def __init__(self, x, y, idle_path, frame_count, size, dialogues,
                 idle_cooldown=8, detect_range=250):
        pygame.sprite.Sprite.__init__(self)
        self.images_right = []
        self.images_left = []
        self.dialogues = dialogues
        self.detect_range = detect_range
        self._idle_cooldown = idle_cooldown
        self.idle_index = 0
        self.idle_counter = 0
        self.direction = 1
        self.current_dialogue = ""
        self._was_near = False

        for num in range(1, frame_count + 1):
            img = pygame.image.load(idle_path.format(num)).convert_alpha()
            img = pygame.transform.scale(img, size)
            self.images_right.append(img)
            self.images_left.append(pygame.transform.flip(img, True, False))

        self.image = self.images_right[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.dx = 0
        self.dy = 0
        self.in_air = True

        self.font = pygame.font.Font("AmaticSC-Bold.ttf", 28)

    def update(self, screen_scroll, y_scroll, screen, world, player_rect):
        self.dx = 0
        self.dy = 0

        # Face the player when nearby
        near = abs(player_rect.centerx - self.rect.centerx) < self.detect_range
        if near:
            if player_rect.centerx < self.rect.centerx:
                self.direction = -1
            else:
                self.direction = 1

            # Pick new dialogue on each new approach
            if not self._was_near:
                self.current_dialogue = random.choice(self.dialogues)
            self._was_near = True
        else:
            self._was_near = False

        # Idle animation
        self.idle_counter += 1
        if self.idle_counter > self._idle_cooldown:
            self.idle_counter = 0
            self.idle_index += 1
            if self.idle_index >= len(self.images_right):
                self.idle_index = 0

        if self.direction == 1:
            self.image = self.images_right[self.idle_index]
        else:
            self.image = self.images_left[self.idle_index]

        # Gravity + collision
        apply_gravity(self)
        check_tile_collisions(self, world.tile_list)
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.rect.x += screen_scroll
        self.rect.y += y_scroll

        # Draw
        screen.blit(self.image, self.rect)

        # Dialogue bubble when near
        if near and self.current_dialogue:
            text = self.font.render(self.current_dialogue, True, (255, 255, 255))
            # Background bubble
            bw = text.get_width() + 16
            bh = text.get_height() + 8
            bx = self.rect.centerx - bw // 2
            by = self.rect.top - bh - 8
            bubble = pygame.Surface((bw, bh), pygame.SRCALPHA)
            bubble.fill((0, 0, 0, 160))
            screen.blit(bubble, (bx, by))
            screen.blit(text, (bx + 8, by + 4))


class Shopkeeper(NPC):
    def __init__(self, x, y):
        super().__init__(
            x, y,
            idle_path="img/shopkeeper_idle/idle{}.PNG",
            frame_count=8,
            size=(45, 60),
            dialogues=_SHOPKEEPER_DIALOGUES,
            detect_range=200,
        )
        # Link to the shop building this shopkeeper belongs to
        self.shop = None


class Granny(NPC):
    def __init__(self, x, y):
        super().__init__(
            x, y,
            idle_path="img/Granny_idle/idle{}.PNG",
            frame_count=8,
            size=(90, 120),  # 1.5 blocks wide, 2 blocks tall
            dialogues=_GRANNY_DIALOGUES,
            detect_range=300,
        )
