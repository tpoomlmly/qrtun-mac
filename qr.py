import io
import math
import sys
from typing import Optional

import cv2
import pygame
import qrcode


class QRDisplay:
    """
    A window that shows QR codes.
    """

    def __init__(self, title: str = "IP over QR") -> None:
        pygame.init()
        monitor_height = pygame.display.get_desktop_sizes()[0][1]
        surface_height = math.floor(monitor_height * 3/5)
        self.surface = pygame.display.set_mode((surface_height, surface_height))
        self.title = title

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

    def set_data(self, data: bytes) -> None:
        """
        Convert the specified data to a QR code and set it to be the next one displayed on the screen.

        :param data: the data to show
        """
        self.qr_code = QRDisplay.make_qrcode(data)

    def show_image(self, image_surface: pygame.Surface) -> None:
        """
        Display an image in the centre of the window.

        :param image_surface: the image to display
        """
        screen_width, screen_height = self.surface.get_size()
        image_rect = image_surface.get_rect()
        image_rect.update(
            screen_width / 2 - image_rect.width / 2,
            screen_height / 2 - image_rect.height / 2,
            image_rect.width,
            image_rect.height,
        )
        self.surface.blit(image_surface, image_rect)

    def update_window(self) -> None:
        """
        Update the window where the QR code is displayed.

        This should be run at least as often as the monitor's refresh rate.
        """
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


class QRReader:
    """
    A camera input that reads QR codes.

    Uses the first camera it finds.
    """

    def __init__(self) -> None:
        self.capture_device = cv2.VideoCapture(0)
        self.detector = cv2.QRCodeDetector()

    def read(self) -> Optional[str]:
        """
        Try to read a QR code from the camera.
        """
        success, frame = self.capture_device.read()
        if not success:
            raise OSError("Couldn't read from camera")

        try:
            data, bounding_box, _ = self.detector.detectAndDecode(frame)
            if bounding_box is None or len(data) == 0:
                return None
            return data
        except cv2.error:
            return None

    def finish(self) -> None:
        self.capture_device.release()


if __name__ == "__main__":
    screen = QRDisplay()
    reader = QRReader()
    old_qr = None

    while True:
        qr = reader.read()
        if qr != old_qr and qr is not None and qr != b"":
            print(qr)
            old_qr = qr
        screen.update_window()
