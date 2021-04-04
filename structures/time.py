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

import ctypes


class Timeval(ctypes.Structure):
    """ Struct timeval represents an elapsed time """
    _fields_ = [
        ("tv_sec", ctypes.c_int),
        ("tv_usec", ctypes.c_long)
    ]


__all__ = [
    'Timeval'
]
