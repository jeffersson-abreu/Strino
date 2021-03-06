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

from structures.uinput import UinputSetup, UinputAbsSetup
import constants.llevel
import ctypes

# ioctl
UINPUT_IOCTL_BASE   =   'U'
UI_DEV_CREATE       =   constants.llevel.io(UINPUT_IOCTL_BASE, 1)
UI_DEV_DESTROY      =   constants.llevel.io(UINPUT_IOCTL_BASE, 2)


# This function was adapted from C code. It's not 'pythonic' to
# use lambda to assign values so I had to adapt it to a function
#
# UI_DEV_SETUP - Set device parameters for setup
# This ioctl sets parameters for the input device to be created.  It
# supersedes the old "struct uinput_user_dev" method, which wrote this data
# via write(). To actually set the absolute axes UI_ABS_SETUP should be used.
UI_DEV_SETUP = constants.llevel.iow(UINPUT_IOCTL_BASE, 3, UinputSetup)


UI_ABS_SETUP = constants.llevel.iow(UINPUT_IOCTL_BASE, 4, UinputAbsSetup)


UI_SET_EVBIT    =   constants.llevel.iow(UINPUT_IOCTL_BASE, 100, ctypes.c_int)      # OK
UI_SET_KEYBIT   =   constants.llevel.iow(UINPUT_IOCTL_BASE, 101, ctypes.c_int)      # OK
UI_SET_RELBIT   =   constants.llevel.iow(UINPUT_IOCTL_BASE, 102, ctypes.c_int)      # OK
UI_SET_ABSBIT   =   constants.llevel.iow(UINPUT_IOCTL_BASE, 103, ctypes.c_int)      # OK
UI_SET_MSCBIT   =   constants.llevel.iow(UINPUT_IOCTL_BASE, 104, ctypes.c_int)      # OK
UI_SET_LEDBIT   =   constants.llevel.iow(UINPUT_IOCTL_BASE, 105, ctypes.c_int)      # OK
UI_SET_SNDBIT   =   constants.llevel.iow(UINPUT_IOCTL_BASE, 106, ctypes.c_int)      # NOT SUPPORTED
UI_SET_FFBIT    =   constants.llevel.iow(UINPUT_IOCTL_BASE, 107, ctypes.c_int)      # NOT SUPPORTED
UI_SET_PHYS     =   constants.llevel.iow(UINPUT_IOCTL_BASE, 108, ctypes.c_char_p)   # OK
UI_SET_SWBIT    =   constants.llevel.iow(UINPUT_IOCTL_BASE, 109, ctypes.c_int)      # OK
UI_SET_PROPBIT  =   constants.llevel.iow(UINPUT_IOCTL_BASE, 110, ctypes.c_int)      # OK
