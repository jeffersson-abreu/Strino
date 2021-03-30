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


# Define the Maximum name size of a device
MAX_NAME_BUFFER = ctypes.create_string_buffer(256)
MAX_NAME_SIZE = ctypes.sizeof(MAX_NAME_BUFFER)


# Device id base generator
DEVICE_ID_BASE = 'E'

# Get devices ID
EVIOCGID = constants.llevel.ior(DEVICE_ID_BASE, 0x02, structures.input.InputId)

# Get Devices name
EVIOCGNAME = constants.llevel.ior(DEVICE_ID_BASE, 0x06, MAX_NAME_BUFFER)

# Get devices location
EVIOCGPHYS = constants.llevel.ior(DEVICE_ID_BASE, 0x07, MAX_NAME_BUFFER)

# Get devices unique identifier
EVIOCGUNIQ = constants.llevel.ior(DEVICE_ID_BASE, 0x08, MAX_NAME_BUFFER)

# Max number of device properties
INPUT_PROP_MAX = 0x1f
INPUT_PROP_CNT = (INPUT_PROP_MAX + 1)

# Grab device access
EVIOCGRAB = constants.llevel.iow('E', 0x90, ctypes.c_int)

# Revoke device access
EVIOCREVOKE = constants.llevel.iow('E', 0x91, ctypes.c_int)

# Virtual bus
BUS_VIRTUAL = 0x06


# Get device properties
def EVIOCGPROP(length):
    return constants.llevel.ior(DEVICE_ID_BASE, 0x09, length)


def EVIOCGBIT(ev_type, length) -> int:
    """
    Get events bits
    :param ev_type: Event code (0 retrieves all event handled)
    :param length: The length of string buffer (ctypes)
    :return: Ioctl read operation number
    """
    return constants.llevel.ior(DEVICE_ID_BASE, 0x20 + ev_type, length)


def EVIOCGABS(code: int) -> int:
    """
    Get absolute value/limits
    :param code: ABS event code
    :return: Ioctl read operation number
    """
    return constants.llevel.ior(DEVICE_ID_BASE, 0x40 + code, structures.input.ABSInfo)


def EVIOCSABS(code: int) -> int:
    """
    Set absolute value/limits
    :param code: ABS event code
    :return: Ioctl write operation number
    """
    return constants.llevel.iow(DEVICE_ID_BASE, 0xc0 + code, structures.input.ABSInfo)
