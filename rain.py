import pygame
import random
from constants import SCREENSIZE, RAIN_COLOR


class Rain:
    def __init__(self, screen, height=160, speed=3, color=RAIN_COLOR, numdrops=10):
        self.screen = screen
        self.drops = []
        self.height = height
        self.speed = speed
        self.color = color
        self.numdrops = numdrops

        for i in range(self.numdrops):
            raindropscale = random.randint(40, 100) / 100.0
            w, h = 3, int(raindropscale * self.height)
            velocity = raindropscale * self.speed / 10.0
            pic = pygame.Surface((w, h), pygame.SRCALPHA, 32).convert_alpha()
            colorinterval = float(self.color[3] * raindropscale) / h
            r, g, b = self.color[:3]
            for j in range(h):
                a = int(colorinterval * j)
                pic.fill((r, g, b, a), (1, j, w - 2, 1))
                pygame.draw.circle(pic, (r, g, b, a), (1, h - 2), 2)
            drop = Rain.Drop(self.speed, velocity, pic)
            self.drops.append(drop)

    def timer(self, now):
        dirtyrects = []
        for drop in self.drops:
            r = drop.render(self.screen, now)
            if r:
                i = r.collidelist(dirtyrects)
                if i > -1:
                    dirtyrects[i].union_ip(r)
                else:
                    dirtyrects.append(r)
        return dirtyrects

    class Drop:
        nexttime = 0
        interval = 0.01

        def __init__(self, speed, scale, pic):
            self.speed = speed
            self.scale = scale
            self.pic = pic
            self.size = pic.get_size()
            self.set_speed(speed)
            self.pos = [
                random.random() * SCREENSIZE[0],
                -random.randint(-SCREENSIZE[1], SCREENSIZE[1]),
            ]
            self.currentspeed = speed

        def set_speed(self, speed):
            self.speed = speed
            self.velocity = self.scale * self.speed / 10.0

        def reset(self):
            self.pos = [
                random.random() * SCREENSIZE[0],
                -random.random() * self.size[1] - self.size[1],
            ]
            self.currentspeed = self.speed

        def render(self, screen, now):
            if now < self.nexttime:
                return None
            self.nexttime = now + self.interval
            oldrect = pygame.Rect(
                self.pos[0], self.pos[1],
                self.size[0], self.size[1] + self.currentspeed
            )
            self.pos[1] += self.currentspeed
            newrect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
            r = oldrect.union(newrect)
            screen.blit(self.pic, self.pos)
            self.currentspeed += self.velocity
            if self.pos[1] > SCREENSIZE[1]:
                self.reset()
            return r
