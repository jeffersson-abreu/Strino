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