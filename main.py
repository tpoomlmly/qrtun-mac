#!/usr/bin/env python3

import base64
import threading

from qr import QRDisplay, QRReader
from utun import Utun


def main():
    utun = Utun(mtu=820)
    print(f"Interface name: {utun.name.decode('utf-8')}")
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
        message_encoded = base64.b32encode(message).replace(b'=', b':')
        qr_display.set_data(message_encoded)


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
        data_decoded = base64.b32decode(data.replace(':', '='))
        utun.send(data_decoded)


if __name__ == "__main__":
    main()
