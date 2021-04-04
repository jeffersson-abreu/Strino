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


import structures.time
import ctypes


class InputId(ctypes.Structure):
    """
    Represents a C struct input_id defined in source file input.h
    """

    _fields_ = [
        ('bustype', ctypes.c_uint16),
        ('vendor', ctypes.c_uint16),
        ('product', ctypes.c_uint16),
        ('version', ctypes.c_uint16),
    ]


class ABSInfo(ctypes.Structure):
    """
    Struct ABSInfo - used by EVIOCGABS/EVIOCSABS ioctls

    Note that input core does not clamp reported values to the
    [minimum, maximum] limits, such task is left to userspace.

    Resolution for main axes (ABS_X, ABS_Y, ABS_Z) is reported in
    units per millimeter (units/mm), resolution for rotational axes
    (ABS_RX, ABS_RY, ABS_RZ) is reported in units per radian.
    """
    _fields_ = [
        ('value', ctypes.c_int32),          # latest reported value for the axis
        ('minimum', ctypes.c_int32),        # specifies minimum value for the axis
        ('maximum', ctypes.c_int32),        # specifies maximum value for the axis
        ('fuzz', ctypes.c_int32),           # specifies fuzz value that is used to filter noise from the event stream
        ('flat', ctypes.c_int32),           # values that are within this value will be discarded by joydev interface and reported as 0 instead
        ('resolution', ctypes.c_int32),     # specifies resolution for the values reported for the axis
    ]


class InputEvent(ctypes.Structure):
    """
    Struct input_event represents a device input
    """
    _fields_ = [
        ("time", structures.time.Timeval),  # Time of the event
        ("type", ctypes.c_uint16),          # Event type
        ("code", ctypes.c_uint16),          # Event code
        ("value", ctypes.c_int32),          # Event value
    ]


__all__ = [
    'InputEvent',
    'InputId',
    'ABSInfo'
]
