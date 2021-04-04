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

from structures.input import InputId, ABSInfo
import ctypes

UINPUT_MAX_NAME_SIZE = 80


class UinputSetup(ctypes.Structure):
    """
    Represents a uinput setup
    """
    _fields_ = [
        ("id", InputId),
        ("name", ctypes.c_char * UINPUT_MAX_NAME_SIZE),
        ("ff_effects_max", ctypes.c_uint32),
    ]


class UinputAbsSetup(ctypes.Structure):
    """ Used to set absolute events """
    _fields_ = [
        ('code',   ctypes.c_uint16),    # axis
        ('absinfo', ABSInfo),           # ABS info
    ]


__all__ = [
    'UinputAbsSetup',
    'UinputSetup'
]
