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

        self.background_colour = 255, 255, 255
        self.surface.fill(self.background_colour)

        pygame.event.set_allowed(None)
        pygame.event.set_allowed(pygame.QUIT)

        self.qr_code = QRDisplay.make_qrcode(b"")

    @property
    def title(self) -> str:
        return pygame.display.get_caption()[0]

    @title.setter
    def title(self, title) -> None:
        pygame.display.set_caption(title, title)

    def run_display_loop(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            self.surface.fill(self.background_colour)
            qr_surface = pygame.image.load_basic(self.qr_code)
            qr_rect = qr_surface.get_rect()
            self.surface.blit(qr_surface, qr_rect)

            pygame.display.flip()

    @staticmethod
    def make_qrcode(data: bytes) -> io.BytesIO:
        """
        Make a QR code that can be displayed by pygame.

        :param data: the data to put in the QR code
        :return: a file-like BytesIO object containing a BMP of the QR code
        """
        qr_image = qrcode.make(data)
        qr_bytes = io.BytesIO()
        qr_image.save(qr_bytes, "BMP")
        return qr_bytes


if __name__ == "__main__":
    screen = QRDisplay()
    screen.title = "IP over QR"

    print(QRDisplay.make_qrcode(b"hellooo").getvalue())

    screen.run_display_loop()
