#!/usr/bin/env python3


import socket
from fcntl import ioctl
import struct

CTLIOCGINFO = 3227799043  # _IOWR('N', 3, struct ctl_info)
CTL_INFO_FORMAT = "<I96s"  # little-endian uint32_t, then a char[96]
UTUN_OPT_IFNAME = 2  # from net/if_utun.h
IF_NAMESIZE = 16  # from net/if.h

SIOCAIFADDR = 2151704858  # _IOW('i', 26, struct ifaliasreq) 2166384921
IN6_ADDR_FORMAT = "16s"  # 16-long unsigned char array
SOCKADDR_IN6_FORMAT = f"HHI{IN6_ADDR_FORMAT}I"  # address family, port no., flow info, v6 address, scope ID
# interface name, address, broadcast address, subnet mask
IFALIASREQ_FORMAT = f"{IF_NAMESIZE}s{SOCKADDR_IN6_FORMAT}{SOCKADDR_IN6_FORMAT}{SOCKADDR_IN6_FORMAT}"


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

        # Force-generate IPv6 address
        self.add_ipv6(b"\xfe\x80" + b"\x00"*12 + b"\x11\x11")  # fe80::1111

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

    def add_ipv6(self, address: bytes) -> None:
        """
        Give this interface an IPv6 address.
        :param address: the address to give
        """
        ifaliasreq = struct.pack(
            IFALIASREQ_FORMAT,
            self.name,
            socket.AF_INET6, 0, 0, address, 0,
            socket.AF_INET6, 0, 0, b"\x00"*16, 0,
            socket.AF_INET6, 0, 0, b"\x00"*16, 0,
        )
        ioctl(self, SIOCAIFADDR, ifaliasreq)

    def delete_ipv6(self, address: bytes) -> None:
        """
        Delete one of this interface's IPv6 addresses.
        :param address: the address to remove
        """


if __name__ == "__main__":
    utun = Utun()
    print(utun.name)
    while True:
        # infinite loop to keep the interface open
        message = utun.recv(utun.mtu)
        print(message)
        utun.send(message)
