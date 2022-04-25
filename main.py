#!/usr/bin/env python3

import threading

from qr import QRDisplay, QRReader
from utun import Utun


def main():
    utun = Utun()
    print(f"Interface name: {utun.name}")
    qr_display = QRDisplay()
    qr_reader = QRReader()

    transmit_thread = threading.Thread(target=transmit_loop, args=(utun, qr_display))
    receive_thread = threading.Thread(target=receive_loop, args=(utun, qr_reader))

    transmit_thread.start()
    receive_thread.start()
    transmit_thread.join()
    # while True:
    #     message = utun.recv(utun.mtu)
    #     print(message)
    #     utun.send(message)


def transmit_loop(utun: Utun, qr_display: QRDisplay) -> None:
    """
    Read data being sent into the utun device and display it as a QR code.

    :param utun: the virtual network device to read from
    :param qr_display: the display to write the QR codes on
    """
    while True:
        message = utun.recv(utun.mtu)
        print(message)
        utun.send(message)
        qr_display.show(message)


def receive_loop(utun: Utun, qr_reader: QRReader) -> None:
    """
    Read QR codes and make the data in them appear on the utun device.

    :param utun: the virtual network device receiving the QR data
    :param qr_reader: the device reading QR codes
    """


if __name__ == "__main__":
    main()
