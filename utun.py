#!/usr/local/bin/python3

# Adapted from https://gist.github.com/whiler/295113850bd55ed4f4bf898124abe4a8

import socket
from fcntl import ioctl
import struct

CTLIOCGINFO = 3227799043
STRUCT_FORMAT = "<I96s"


# Get file descriptor for socket
utun_socket = socket.socket(socket.PF_SYSTEM, socket.SOCK_DGRAM, socket.SYSPROTO_CONTROL)
file_descriptor = utun_socket.fileno()

# Make struct ctl_info
ctl_info = struct.pack(STRUCT_FORMAT, 0, "com.apple.net.utun_control".encode())
# Exchange controller name for ID + name
ctl_info = ioctl(utun_socket, CTLIOCGINFO, ctl_info)
controller_id, controller_name = struct.unpack(STRUCT_FORMAT, ctl_info)

# Connect + activate (requires sudo)
utun_socket.connect((controller_id, 0))  # 0 means pick the next convenient one

while True:
    # infinite loop to keep the interface open
    message = utun_socket.recv(1500)
    print(message)
    utun_socket.send(message)
