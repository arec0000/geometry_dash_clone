import pygame as pg
from pygame.math import Vector2
import csv
from random import randint
import config
from player import Player
from obstacles import Block, Spike, End
from helpers import resize_img

class Game:
    def __init__(self):
        pg.init()
        pg.display.set_caption(' geometry dash clone')
        self.sc = pg.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        self.alpha_surf = pg.Surface(self.sc.get_size(), pg.SRCALPHA)
        self.player_sprite = pg.sprite.Group()
        self.elements = pg.sprite.Group()
        self.clock = pg.time.Clock()

        self.bg = pg.image.load(config.BACKGROUND)
        self.avatar = pg.image.load(config.AVATAR)
        self.block = resize_img(pg.image.load(config.BLOCK))
        self.spike = resize_img(pg.image.load(config.SPIKE))
        self.end_block = resize_img(pg.image.load(config.END_BLOCK))
        self.font = pg.font.Font('Montserrat-Medium.ttf', config.FONT_SIZE)

        self.game_over_sound = pg.mixer.Sound('sound/death.mp3')
        self.music = config.MUSIC
        self.music_track = randint(0, len(self.music) - 1)
        self.music_end_event = pg.USEREVENT + 1
        pg.mixer.music.set_endevent(self.music_end_event)
        self.next_song()

        self.started = False
        self.level = config.START_LEVEL - 1
        self.gravity = Vector2(0, 0.86)
        self.camera_x = 0
        self.bg_x = 0
        self.player = Player(
            self.avatar, 
            self.elements, 
            (150, 150), 
            self.alpha_surf, 
            self.gravity, 
            self.player_sprite
        )
        pg.display.set_icon(resize_img(self.avatar))

    def next_song(self):
        pg.mixer.music.load(self.music[self.music_track])
        pg.mixer.music.play()
        self.music_track = self.music_track + 1 if self.music_track < len(self.music) - 1 else 0

    def move_camera(self):
        for sprite in self.elements:
            sprite.rect.x -= self.camera_x
        self.bg_x -= 0.1

    def render_screen(self, *text, color=config.WHITE, bg=config.BLACK):
        self.sc.fill(bg)
        offset = (len(text) - 1) * config.LINE_HEIGHT
        for i, line in enumerate(text):
            line_text = self.font.render(line, 1, color)
            rect = line_text.get_rect(center=(
                config.WINDOW_WIDTH / 2,
                config.WINDOW_HEIGHT / 2 - offset + i * config.LINE_HEIGHT
            ))
            self.sc.blit(line_text, rect)
        pg.display.update()

    def start_screen(self):
        self.render_screen('Нажмите пробел, чтобы начать')

    def won_screen(self):
        self.render_screen(
            f'{self.level + 1} уровень пройден',
            'нажмите пробел, чтобы продолжить',
            bg=config.DARK_GREEN
        )

    def death_screen(self):
        self.render_screen('Поражение..', 'нажмите пробел, чтобы продолжить', bg=config.PURPLE)

    def start(self):
        self.start_screen()
        self.wait_for_key()
        self.reset()
        self.started = True

    def win(self):
        self.player_sprite.clear(self.player.image, self.sc)
        self.won_screen()
        self.level += 1
        self.wait_for_key()
        self.reset()

    def death(self):
        self.game_over_sound.play()
        self.player_sprite.clear(self.player.image, self.sc)
        self.death_screen()
        self.wait_for_key()
        self.reset()

    def wait_for_key(self):
        wait = True
        while wait:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        wait = False
                    elif event.key == pg.K_ESCAPE:
                        wait = False
                        pg.quit()
                elif event.type == self.music_end_event:
                    self.next_song()
                elif event.type == pg.QUIT:
                    wait = False
                    pg.quit()
            self.clock.tick(60)

    def check_game_over(self):
        if self.player.win:
            self.win()
        elif self.player.died:
            self.death()

    def rotate(self, surf, img, pos, orig_pos, angle):
        w, h = img.get_size()
        box = [Vector2(p) for p in [(0, 0), (w, 0), (w, -h), (0, -h)]]
        box_rotate = [p.rotate(angle) for p in box]
        min_box = (min(box_rotate, key=lambda p: p[0])[0], min(box_rotate, key=lambda p: p[1])[1])
        max_box = (max(box_rotate, key=lambda p: p[0])[0], max(box_rotate, key=lambda p: p[1])[1])
        pivot = Vector2(orig_pos[0], -orig_pos[1])
        pivot_rotate = pivot.rotate(angle)
        pivot_move = pivot_rotate - pivot
        origin = (
            pos[0] - orig_pos[0] + min_box[0] - pivot_move[0],
            pos[1] - orig_pos[1] - max_box[1] + pivot_move[1]
        )
        rotated_image = pg.transform.rotozoom(img, angle, 1)
        surf.blit(rotated_image, origin)

    def generate_level(self, map):
        x, y = config.MAP_OFFSET, 0
        for row in map:
            for col in row:
                if col == '1':
                    Block(self.block, (x, y), self.elements)
                if col == 's':
                    Spike(self.spike, (x, y), self.elements)
                if col == 'end':
                    End(self.end_block, (x, y), self.elements)
                x += 32
            y += 32
            x = config.MAP_OFFSET

    def read_map(self, level_path):
        with open(level_path) as file:
            return tuple(csv.reader(file, delimiter=',', quotechar='"'))

    def check_events(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_UP] or keys[pg.K_SPACE]:
            self.player.isjump = True
        for event in pg.event.get():
            if event.type == self.music_end_event:
                self.next_song()
            elif event.type == pg.QUIT:
                exit()

    def render_player(self):
        if self.player.isjump:
            self.player.angle -= 7.1712
            self.rotate(self.sc, self.player.image, self.player.rect.center, (16, 16), self.player.angle)
        else:
            if self.player.overturn:
                self.rotate(self.sc, self.player.image, self.player.rect.center, (16, 16), 180)
            else:
                self.player_sprite.draw(self.sc)

    def reset(self):
        self.player_sprite = pg.sprite.Group()
        self.elements = pg.sprite.Group()
        self.player = Player(
            self.avatar, 
            self.elements, 
            (150, 150), 
            self.alpha_surf, 
            self.gravity, 
            self.player_sprite
        )
        self.bg_x = 0
        map = self.read_map(config.LEVELS[self.level])
        self.generate_level(map)

    def run(self):
        while True:
            if not self.started:
                self.start()
            self.check_events()
            self.player.vel.x = 6
            self.check_game_over()
            self.alpha_surf.fill((255, 255, 255, 1), special_flags=pg.BLEND_RGBA_MULT)
            self.player_sprite.update()
            self.camera_x = self.player.vel.x
            self.move_camera()
            self.sc.blit(self.bg, (self.bg_x, 0))
            self.player.draw_particle_trail(
                self.player.rect.left - 1, 
                self.player.rect.bottom + 2, 
                config.WHITE
            )
            self.sc.blit(self.alpha_surf, (0, 0))
            self.render_player()
            self.elements.draw(self.sc)
            pg.display.flip()
            self.clock.tick(60)
            