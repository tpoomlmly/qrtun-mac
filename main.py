#!/usr/bin/env python3

import threading

from qr import QRDisplay, QRReader
from utun import Utun


def main():
    utun = Utun()
    print(f"Interface name: {utun.name}")
    qr_display = QRDisplay()

    transmit_thread = threading.Thread(target=transmit_loop, args=(utun, qr_display), daemon=True)
    receive_thread = threading.Thread(target=receive_loop, args=(utun,), daemon=True)
    transmit_thread.start()
    receive_thread.start()

    while True:
        qr_display.update_window()


def transmit_loop(utun: Utun, qr_display: QRDisplay) -> None:
    """
    Read data being sent into the utun device and set it to be displayed as a QR code.

    :param utun: the virtual network device to read from
    :param qr_display: the display to write the QR codes on
    """
    while True:
        message = utun.recv(utun.mtu)
        # print(message)
        # utun.send(message)
        qr_display.set_data(message)


def receive_loop(utun: Utun) -> None:
    """
    Read QR codes and make the data in them appear on the utun device.

    :param utun: the virtual network device receiving the QR data
    """
    qr_reader = QRReader()
    old_data = None

    while True:
        data = qr_reader.read()
        if data is None or data == old_data:  # in case of read failure or if the code is the same as last time
            continue

        old_data = data
        print(data)
        utun.send(data)


if __name__ == "__main__":
    main()
