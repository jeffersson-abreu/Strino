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

from ctypes import *

# The original linux ioctl numbering scheme was just a general
# "anything goes" setup, where more or less random numbers were
# assigned.  Sorry, I was clueless when I started out on this.
#
# On the alpha, we'll try to clean it up a bit, using a more sane
# ioctl numbering, and also trying to be compatible with OSF/1 in
# the process. I'd like to clean it up for the i386 as well, but
# it's so painful recognizing both the new and the old numbers..
_IOC_NRBITS = 8
_IOC_TYPEBITS = 8

_IOC_NRSHIFT = 0
_IOC_TYPESHIFT = _IOC_NRSHIFT + _IOC_NRBITS
_IOC_SIZESHIFT = _IOC_TYPESHIFT + _IOC_TYPEBITS


_IOC_NONE = 0
_IOC_WRITE = 1
_IOC_READ  = 2
_IOC_SIZEBITS = 14
_IOC_DIRBITS = 2

_IOC_DIRSHIFT = _IOC_SIZESHIFT + _IOC_SIZEBITS


def _IOC(dir_, type_, nr, size):
    return (
        c_int32(dir_ << _IOC_DIRSHIFT).value |
        c_int32(ord(type_) << _IOC_TYPESHIFT).value |
        c_int32(nr << _IOC_NRSHIFT).value |
        c_int32(size << _IOC_SIZESHIFT).value)


def _IOC_TYPECHECK(t):
    return sizeof(t)


def _IO(type_, nr):
    return _IOC(_IOC_NONE, type_, nr, 0)


def _IOW(type_, nr, size):
    return _IOC(_IOC_WRITE, type_, nr, _IOC_TYPECHECK(size))


def _IOR(type_, nr, size):
    return _IOC(_IOC_READ, type_, nr, _IOC_TYPECHECK(size))


def _IOWR(type_, nr, size):
    return _IOC(_IOC_READ | _IOC_WRITE, type_, nr, _IOC_TYPECHECK(size))


def io(type_, nr):
    return _IO(type_, nr)


def ioc(dir_, type_, nr, size):
    return _IOC(dir_, type_, nr, size)


def ior(type_, nr, size):
    return _IOR(type_, nr, size)


def iow(type_, nr, size):
    return _IOW(type_, nr, size)


def iowr(type_, nr, size):
    return _IOWR(type_, nr, size)


