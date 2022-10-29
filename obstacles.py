from pygame.sprite import Sprite

class Draw(Sprite):
    def __init__(self, image, pos, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)


class Block(Draw):
    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class Spike(Draw):
    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class End(Draw):
    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)
