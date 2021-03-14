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

import constants.llevel
import structures.input
import ctypes


# Define the maximun name size of a device
MAX_NAME_SIZE = ctypes.create_string_buffer(256)

# Device id base generator
DEVICE_ID_BASE = ord('E')

# Get devices ID
EVIOCGID = constants.llevel.ior(DEVICE_ID_BASE, 0x02, structures.input.InputId)

# Get Devices name
EVIOCGNAME = constants.llevel.ior(DEVICE_ID_BASE, 0x06, MAX_NAME_SIZE)

# Get devices location
EVIOCGPHYS = constants.llevel.ior(DEVICE_ID_BASE, 0x07, MAX_NAME_SIZE)

# Get devices unique identifier
EVIOCGUNIQ = constants.llevel.ior(DEVICE_ID_BASE, 0x08, MAX_NAME_SIZE)


def EVIOCGBIT(ev_type, lenght) -> int:
    """
    Get events bits
    :param ev_type: Event code (0 retrieves all event handled)
    :param lenght: The length of string buffer (ctypes)
    :return: Ioctl read operation number
    """
    return constants.llevel.ioc(constants.llevel.IOC_READ, DEVICE_ID_BASE, 0x20 + ev_type, lenght)


def EVIOCGABS(code: int) -> int:
    """
    Get absolute value/limits
    :param code: ABS event code
    :return: Ioctl read operation number
    """
    return constants.llevel.ior(DEVICE_ID_BASE, 0x40 + code, structures.input.ABSInfo)
