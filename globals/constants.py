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

import structures.input
import ctypes


# Linux living devices handler files
DEVICES_PATH = '/dev/input'

#
# ioctl.h
#
# The original linux ioctl numbering scheme was just a general
# "anything goes" setup, where more or less random numbers were
# assigned.  Sorry, I was clueless when I started out on this.
#
# On the alpha, we'll try to clean it up a bit, using a more sane
# ioctl numbering, and also trying to be compatible with OSF/1 in
# the process. I'd like to clean it up for the i386 as well, but
# it's so painful recognizing both the new and the old numbers..
_IOC_NRBITS     =   8
_IOC_TYPEBITS   =   8
_IOC_SIZEBITS   =   14
_IOC_DIRBITS    =   2

_IOC_NRMASK     =   (1 << _IOC_NRBITS) - 1
_IOC_TYPEMASK   =   (1 << _IOC_TYPEBITS) - 1
_IOC_SIZEMASK   =   (1 << _IOC_SIZEBITS) - 1
_IOC_DIRMASK    =   (1 << _IOC_DIRBITS) - 1

_IOC_NRSHIFT    =   0
_IOC_TYPESHIFT  =   _IOC_NRSHIFT + _IOC_NRBITS
_IOC_SIZESHIFT  =   _IOC_TYPESHIFT + _IOC_TYPEBITS
_IOC_DIRSHIFT   =   _IOC_SIZESHIFT + _IOC_SIZEBITS

# Direction bits _IOC_NONE could be 0, but OSF/1 gives it a bit.
# And this turns out useful to catch old ioctl numbers in header
# files for us.
IOC_NONE    =   0
IOC_WRITE   =   1
IOC_READ    =   2


def ioc(dr, tp, nr, size):
    assert dr <= _IOC_DIRMASK, dr
    assert tp <= _IOC_TYPEMASK, tp
    assert nr <= _IOC_NRMASK, nr
    assert size <= _IOC_SIZEMASK, size
    return (dr << _IOC_DIRSHIFT) | (tp << _IOC_TYPESHIFT) | (nr << _IOC_NRSHIFT) | (size << _IOC_SIZESHIFT)


def ioc_typecheck(t):
    result = ctypes.sizeof(t)
    assert result <= _IOC_SIZEMASK, result
    return result


# Used to create numbers
def io(t, nr):
    return ioc(IOC_NONE, t, nr, 0)


# Used to decode then
def iow(t, nr, size):
    return ioc(IOC_WRITE, t, nr, ioc_typecheck(size))


def ior(t, nr, size):
    return ioc(IOC_READ, t, nr, ioc_typecheck(size))


def iowr(t, nr, size):
    return ioc(IOC_READ | IOC_WRITE, t, nr, ioc_typecheck(size))


#
# input.h
#

# Define the maximun name size of a device
MAX_NAME_SIZE = ctypes.create_string_buffer(256)

# Device id base generator
DEVICE_ID_BASE = ord('E')

# Get devices ID
EVIOCGID = ior(DEVICE_ID_BASE, 0x02, structures.input.InputId)

# Get Devices name
EVIOCGNAME = ior(DEVICE_ID_BASE, 0x06, MAX_NAME_SIZE)

# Get devices location
EVIOCGPHYS = ior(DEVICE_ID_BASE, 0x07, MAX_NAME_SIZE)

# Get devices unique identifier
EVIOCGUNIQ = ior(DEVICE_ID_BASE, 0x08, MAX_NAME_SIZE)


def EVIOCGBIT(ev_type, lenght) -> int:
    """
    Get events bits
    :param ev_type: Event code (0 retrieves all event handled)
    :param lenght: The length of string buffer (ctypes)
    :return: Ioctl read operation number
    """
    return ioc(IOC_READ, DEVICE_ID_BASE, 0x20 + ev_type, lenght)


def EVIOCGABS(code: int) -> int:
    """
    Get absolute value/limits
    :param code: ABS event code
    :return: Ioctl read operation number
    """
    return ior(DEVICE_ID_BASE, 0x40 + code, structures.input.ABSInfo)


#
# Linux input-event-codes.h
#

# Event types
EV_ABS  =   int(0x03)


KEY_MAX =   int(0x2ff)
EV_MAX  =   int(0x1f)
