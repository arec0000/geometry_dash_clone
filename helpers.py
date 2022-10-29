from pygame.transform import smoothscale

def resize_img(img, size=(32, 32)):
        return smoothscale(img, size)
