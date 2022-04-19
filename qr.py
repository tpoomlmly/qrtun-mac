import math

import pygame
import qrcode
import sys


class QRDisplay:
    """
    A window that shows QR codes.
    """

    def __init__(self) -> None:
        pygame.init()
        monitor_height = pygame.display.get_desktop_sizes()[0][1]
        surface_height = math.floor(monitor_height * 3/5)
        size = surface_height, surface_height
        print(size)
        background_colour = 255, 255, 255
        surface = pygame.display.set_mode(size)
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
            surface.fill(background_colour)
            pygame.display.flip()


if __name__ == "__main__":
    QRDisplay()
