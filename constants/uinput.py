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
import ctypes

UINPUT_MAX_NAME_SIZE = 80

# ioctl
UINPUT_IOCTL_BASE   =   ord('U')
UI_DEV_CREATE       =   constants.llevel.io(UINPUT_IOCTL_BASE, 1)
UI_DEV_DESTROY      =   constants.llevel.io(UINPUT_IOCTL_BASE, 2)


def UI_DEV_SETUP(struct):
    """
    This function was adapted from C code. It's not 'pythonic' to
    use lambda to assign values so I had to adapt it to a function

    UI_DEV_SETUP - Set device parameters for setup
    This ioctl sets parameters for the input device to be created.  It
    supersedes the old "struct uinput_user_dev" method, which wrote this data
    via write(). To actually set the absolute axes UI_ABS_SETUP should be used.
    """
    return constants.llevel.iow(UINPUT_IOCTL_BASE, 3, struct)


UI_SET_EVBIT    =   constants.llevel.iow(UINPUT_IOCTL_BASE, 100, ctypes.c_int)
UI_SET_KEYBIT   =   constants.llevel.iow(UINPUT_IOCTL_BASE, 101, ctypes.c_int)
UI_SET_RELBIT   =   constants.llevel.iow(UINPUT_IOCTL_BASE, 102, ctypes.c_int)
UI_SET_ABSBIT   =   constants.llevel.iow(UINPUT_IOCTL_BASE, 103, ctypes.c_int)
UI_SET_MSCBIT   =   constants.llevel.iow(UINPUT_IOCTL_BASE, 104, ctypes.c_int)
UI_SET_LEDBIT   =   constants.llevel.iow(UINPUT_IOCTL_BASE, 105, ctypes.c_int)
UI_SET_SNDBIT   =   constants.llevel.iow(UINPUT_IOCTL_BASE, 106, ctypes.c_int)
UI_SET_FFBIT    =   constants.llevel.iow(UINPUT_IOCTL_BASE, 107, ctypes.c_int)
UI_SET_PHYS     =   constants.llevel.iow(UINPUT_IOCTL_BASE, 108, ctypes.c_char_p)
UI_SET_SWBIT    =   constants.llevel.iow(UINPUT_IOCTL_BASE, 109, ctypes.c_int)
UI_SET_PROPBIT  =   constants.llevel.iow(UINPUT_IOCTL_BASE, 110, ctypes.c_int)

uinput_sets = {
    'EV_SYN':		UI_SET_EVBIT,
    'EV_KEY':		UI_SET_KEYBIT,
    'EV_REL':		UI_SET_RELBIT,
    'EV_ABS':		UI_SET_ABSBIT,
    'EV_MSC':		UI_SET_MSCBIT,
    'EV_SW':		UI_SET_SWBIT,
    'EV_LED':		UI_SET_LEDBIT,
    'EV_SND':		UI_SET_SNDBIT,
    'EV_REP':		None,               # Todo: Figure out what code is this
    'EV_FF':		UI_SET_FFBIT,
    'EV_PWR':		None,
    'EV_FF_STATUS': None,
}