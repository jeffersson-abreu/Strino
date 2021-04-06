# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.
#
# Author: Jeffersson Abreu (ctw6av)

from structures.ifaddrs import Ifaddrs, Sockaddr
import constants.input
import ctypes
import socket
import fcntl
import os


def get_all_devices_handlers(basename=False) -> list:
    """
    Get all devices file handlers living in linux /dev/input folder
    :param: basename: Boolean value to control if file returns as a full path
    :return: A set of event handlers filename
    """
    file_handlers = set()

    for _, _, files in os.walk('/dev/input'):
        for file in files:
            # Filter only files that name starts with "event"
            if file.startswith('event'):
                path = os.path.join(
                    '/dev/input',
                    file
                )

                # Depending on basename append a file name or a full path
                file_handlers.add(file if basename else path)

    return list(file_handlers)


# noinspection PyTypeChecker
def get_handlers_by_devices_name(names: list):
    """
    Get device handler by a giving device name
    :param: names: A list containing device names
    :return: A list containing valid device handlers
    """

    # Create the string buffer to make future ioctl calls
    name = ctypes.create_string_buffer(constants.input.MAX_NAME_SIZE)
    handlers = list()

    for handler in get_all_devices_handlers():
        # Get the device name
        with open(handler, 'rb') as hd:
            fcntl.ioctl(hd, constants.input.EVIOCGNAME, name)
            decoded_name = name.value.decode()
            if decoded_name in names:
                handlers.append(os.path.basename(handler))
                continue

            constants.globals.logger.warning(f"Device {decoded_name} not exists")

    return handlers


def get_network_interfaces() -> dict:
    """
    Get all network interfaces in the system
    The data comes with address and broadcast

    :returns: Dict with interfaces information
    """

    # Load library and prepare ifaddrs to
    # be filled by getifaddrs call
    libc = ctypes.CDLL('libc.so.6')
    ifaddrs = Ifaddrs()
    libc.getifaddrs(ctypes.byref(ifaddrs))

    # This is the IPv4 address and broadcast of the interface
    ipv4 = ctypes.create_string_buffer(socket.NI_MAXHOST)

    # Keep a reference of all interfaces and
    # save ifaddrs head to be free later
    interfaces = {}
    ifa = ifaddrs

    while ifa.ifa_next:
        ifa = ifa.ifa_next.contents
        ifname = ifa.ifa_name.decode()

        # When we have the info we need,
        # so we can stop the loop
        if ifname in interfaces.keys():
            element = interfaces[ifname]
            if 'address' in element.keys():
                if 'broadcast' in element.keys():
                    break

        interfaces[ifname] = {}

        if ifa.ifa_addr:
            # Get the interface local address
            family = ifa.ifa_addr.contents.sa_family

            if family == socket.AF_INET:
                s = libc.getnameinfo(ifa.ifa_addr, ctypes.sizeof(Sockaddr), ipv4, ctypes.sizeof(ipv4), None, 0, socket.NI_NUMERICHOST)

                if s != 0:
                    constants.globals.logger.error("Cold not retrieve interface address")
                    interfaces[ifname]['address'] = ''
                    continue

                interfaces[ifname]['address'] = ipv4.value.decode()

        if ifa.ifu_broaddr:
            # Get the interface local broadcast address
            family = ifa.ifu_broaddr.contents.sa_family

            if family == socket.AF_INET:
                s = libc.getnameinfo(ifa.ifu_broaddr, ctypes.sizeof(Sockaddr), ipv4, ctypes.sizeof(ipv4), None, 0, socket.NI_NUMERICHOST)

                if s != 0:
                    constants.globals.logger.error("Cold not retrieve interface broadcast")
                    interfaces[ifname]['broadcast'] = ''
                    continue

                interfaces[ifname]['broadcast'] = ipv4.value.decode()

    return interfaces
