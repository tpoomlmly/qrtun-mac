#!/usr/bin/env python3

import asyncio

from qr import QRDisplay, QRReader
from utun import Utun


async def main():
    utun = Utun()
    print(f"Interface name: {utun.name}")
    qr_display = QRDisplay()
    qr_reader = QRReader()

    await asyncio.gather(
        transmit_loop(utun, qr_display),
        receive_loop(utun, qr_reader),
    )
    # while True:
    #     message = utun.recv(utun.mtu)
    #     print(message)
    #     utun.send(message)


async def transmit_loop(utun: Utun, qr_display: QRDisplay) -> None:
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


async def receive_loop(utun: Utun, qr_reader: QRReader) -> None:
    """
    Read QR codes and make the data in them appear on the utun device.

    :param utun: the virtual network device receiving the QR data
    :param qr_reader: the device reading QR codes
    """


if __name__ == "__main__":
    asyncio.run(main())
