import io
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
        self.surface = pygame.display.set_mode(size)

        self.surface.fill(self.background_colour)

        pygame.event.set_allowed(None)
        pygame.event.set_allowed(pygame.QUIT)

        self.qr_code = QRDisplay.make_qrcode(b"")

    @property
    def background_colour(self) -> (int, int, int):
        return 255, 255, 255

    @property
    def title(self) -> str:
        return pygame.display.get_caption()[0]

    @title.setter
    def title(self, title: str) -> None:
        pygame.display.set_caption(title, title)

    def show_image(self, image_surface: pygame.Surface) -> None:
        """
        Display an image in the centre of the window.

        :param image_surface: the image to display
        """
        image_rect = image_surface.get_rect()
        self.surface.blit(image_surface, image_rect)

    def run_display_loop(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            self.surface.fill(self.background_colour)
            self.show_image(self.qr_code)

            pygame.display.flip()

    @staticmethod
    def make_qrcode(data: bytes) -> pygame.Surface:
        """
        Make a QR code that can be displayed by pygame.

        :param data: the data to put in the QR code
        :return: a file-like BytesIO object containing a BMP of the QR code
        """
        qr_image = qrcode.make(data)
        qr_bytes = io.BytesIO()
        qr_image.save(qr_bytes, "PNG")
        qr_bytes.seek(0)
        return pygame.image.load(qr_bytes)


if __name__ == "__main__":
    screen = QRDisplay()
    screen.title = "IP over QR"

    screen.run_display_loop()
