import pygame as pg
import random
import config
from helpers import resize_img
from obstacles import Block, Spike, End

class Player(pg.sprite.Sprite):
    def __init__(self, image, elements, pos, alpha_surf, gravity, *groups):
        super().__init__(*groups)
        self.image = resize_img(image)
        self.elements = elements
        self.rect = self.image.get_rect(center=pos)
        self.alpha_surf = alpha_surf
        self.gravity = gravity
        self.win = False
        self.died = False
        self.jump_amount = config.JUMP_AMOUNT
        self.angle = 0
        self.overturn = False
        self.onGround = False
        self.isjump = False
        self.particles = []
        self.vel = pg.math.Vector2(0, 0)

    def draw_particle_trail(self, x, y, color=(255, 255, 255)):
        self.particles.append([
            [x - 5, y - 8],
            [random.randint(0, 25) / 10 - 1, random.choice([0, 0])],
            random.randint(5, 8)
        ])
        for particle in self.particles:
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            particle[2] -= 0.5
            particle[1][0] -= 0.4
            pos = ((int(particle[0][0]), int(particle[0][1])), (int(particle[2]), int(particle[2])))
            pg.draw.rect(self.alpha_surf, color, pos)
            if particle[2] <= 0:
                self.particles.remove(particle)

    def jump(self):
        self.vel.y = -self.jump_amount
        if self.overturn:
            self.angle = 180
        else:
            self.angle = 0
        self.overturn = not self.overturn

    def collide(self, yvel, elements):
        for el in elements:
            if pg.sprite.collide_rect(self, el):
                if isinstance(el, Block):
                    if yvel > 0:
                        self.rect.bottom = el.rect.top
                        self.vel.y = 0
                        self.onGround = True
                        self.isjump = False
                    elif yvel < 0:
                        self.rect.top = el.rect.bottom
                    else:
                        self.vel.x = 0
                        self.rect.right = el.rect.left
                        self.died = True
                elif isinstance(el, Spike):
                    self.died = True
                elif isinstance(el, End):
                    self.win = True
        if self.rect.y > config.DEADLY_HEIGHT:
            self.died = True

    def update(self):
        if self.isjump and self.onGround:
            self.jump()
        if not self.onGround:
            self.vel += self.gravity
            if self.vel.y > 100: 
                self.vel.y = 100
        self.collide(0, self.elements)
        self.rect.top += self.vel.y
        self.onGround = False
        self.collide(self.vel.y, self.elements)
