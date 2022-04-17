#!/usr/bin/env python3

# Adapted from https://gist.github.com/whiler/295113850bd55ed4f4bf898124abe4a8

import socket
from fcntl import ioctl
import struct

CTLIOCGINFO = 3227799043  # _IOWR('N', 3, struct ctl_info)
CTL_INFO_FORMAT = "<I96s"  # little-endian uint32_t, then a char[96]
UTUN_OPT_IFNAME = 2  # from net/if_utun.h


def get_utun() -> socket.socket:
    """
    Create a utun device and get a socket connection to its controller.

    Anything sent via the newly created utun device is received on this socket.
    Anything sent from this socket is received by those listening on the utun device.
    This function will crash if not run on macOS, since PF_SYSTEM and SYSPROTO_CONTROL
    only exist on macOS.

    :return: a socket.socket() instance corresponding to a newly created utun adapter
    """
    # Get file descriptor for socket
    utun_socket = socket.socket(socket.PF_SYSTEM, socket.SOCK_DGRAM, socket.SYSPROTO_CONTROL)

    # Make struct ctl_info
    ctl_info = struct.pack(CTL_INFO_FORMAT, 0, "com.apple.net.utun_control".encode())
    # Exchange controller name for ID + name
    ctl_info = ioctl(utun_socket, CTLIOCGINFO, ctl_info)
    controller_id, controller_name = struct.unpack(CTL_INFO_FORMAT, ctl_info)

    # Connect + activate (requires sudo)
    utun_socket.connect((controller_id, 0))  # 0 means pick the next convenient number

    return utun_socket


def utun_name(sock: socket.socket) -> bytes:
    """
    Get the name of a utun device.

    :param sock: the socket controlling a utun device as returned from get_utun()
    :return: the name of the utun device as a bytestring
    """
    return sock.getsockopt(socket.SYSPROTO_CONTROL, UTUN_OPT_IFNAME, 20)[:-1]  # take off the null terminator


if __name__ == "__main__":
    utun = get_utun()
    print(utun_name(utun))
    while True:
        # infinite loop to keep the interface open
        message = utun.recv(1500)
        print(message)
        utun.send(message)
