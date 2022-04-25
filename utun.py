#!/usr/bin/env python3


import socket
import subprocess
from fcntl import ioctl
import struct

CTLIOCGINFO = 3227799043  # _IOWR('N', 3, struct ctl_info)
CTL_INFO_FORMAT = "<I96s"  # little-endian uint32_t, then a char[96]
UTUN_OPT_IFNAME = 2  # from net/if_utun.h
IF_NAMESIZE = 16  # from net/if.h


class Utun(socket.socket):
    """
    A connection for controlling a utun device.

    Use send() and recv() to communicate with programs sending via this virtual NIC.
    Anything sent via the utun device can be received for processing by calling recv().
    Anything sent from this socket with send() is heard by those listening on the utun device.
    """

    def __init__(self, mtu: int = 1500) -> None:
        """
        Create a new utun device and a socket connection to its controller.

        Calling this requires root privileges. This function will crash if not run on macOS,
        since PF_SYSTEM and SYSPROTO_CONTROL are only defined on Darwin.

        :param mtu: the Maximum Transmission Unit for the virtual interface
        """
        super().__init__(socket.PF_SYSTEM, socket.SOCK_DGRAM, socket.SYSPROTO_CONTROL)

        self._mtu = mtu

        # Make struct ctl_info
        ctl_info = struct.pack(CTL_INFO_FORMAT, 0, "com.apple.net.utun_control".encode())
        # Exchange controller name for ID + name
        ctl_info = ioctl(self, CTLIOCGINFO, ctl_info)
        controller_id, controller_name = struct.unpack(CTL_INFO_FORMAT, ctl_info)

        # Connect + activate (requires sudo)
        self.connect((controller_id, 0))  # 0 means pick the next convenient number

        # Generate IPv6 address
        subprocess.run(["ifconfig", self.name, "inet6", "fe80::1111"], check=True)

    @property
    def mtu(self) -> int:
        """The Maximum Transmission Unit of this utun device."""
        return self._mtu

    @property
    def name(self) -> bytes:
        """
        Get the name of a utun device.

        :return: the name of the utun device as a bytestring
        """
        return self.getsockopt(
            socket.SYSPROTO_CONTROL,
            UTUN_OPT_IFNAME,
            IF_NAMESIZE,
        )[:-1]  # take off the null terminator


if __name__ == "__main__":
    utun = Utun()
    print(utun.name)
    while True:
        # infinite loop to keep the interface open
        message = utun.recv(utun.mtu)
        print(message)
        utun.send(message)
