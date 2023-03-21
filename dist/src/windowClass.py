import pygame, sys, os, time
from random import choice
from pygame.locals import *
pygame.init()

class Window:
    def __init__(self, title, size, icon, tag = pygame.RESIZABLE, vsync = False, FPS = 60, spriteDraw = True):
        self.title = title
        self.size = size
        self.tag = tag
        self.icon = icon
        self.FPS = FPS
        self.clock = pygame.time.Clock()
        self.fullscreen = False
        self.spriteDraw = spriteDraw
        self.last_time = time.time()
        self.dt = 0
        self.vsync = vsync
        self.monitor = [pygame.display.Info().current_w, pygame.display.Info().current_h]

        # Sprite & Main Display
        # Draw things on the sprite layer if using pixel art, otherwiise use the normal layer
        self.spriteLayer = pygame.Surface((self.size[0]//2, self.size[1]//2))
        self.displayLayer = pygame.display.set_mode(self.size, self.tag, self.vsync)
        pygame.display.set_caption(self.title)
        if self.icon != None:
            pygame.display.set_icon(self.icon)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, newSize):
        self._size = newSize

    def resize(self, newSize):
        self.size = newSize
        self.displayLayer = pygame.display.set_mode(self.size, self.tag)

    def drawImage(self, img, coords, collision = False):
        self.spriteLayer.blit(img, coords)
        self.displayLayer.blit(img, coords)

    def update(self):
        pygame.display.update()
        self.clock.tick(self.FPS)
        self.spriteLayer = pygame.Surface((self.size[0]//2, self.size[1]//2))

    def toggleFullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.tag = pygame.FULLSCREEN
            self.display = pygame.display.set_mode(self.monitor, self.tag)
        else:
            self.tag = pygame.RESIZABLE
            self.dispaly = pygame.display.set_mode(self.size, self.tag)

    def drawSpriteLayer(self):
        temp = pygame.transform.scale(self.spriteLayer, self.size)
        self.displayLayer.blit(temp, (0, 0))

    def updateWindow(self, newIcon, newTitle):
        self.icon = newIcon
        self.title = newTitle
        pygame.display.set_caption(self.title)
        pygame.display.set_icon(self.icon)

    def deltaTime(self, dt):
        self.dt = time.time() - self.last_time
        self.dt *= 60
        self.last_time = time.time()

    def close(self):
    	pygame.quit()
    	sys.exit()
