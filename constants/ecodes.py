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

# Maximum synchronization events
KEY_MAX = int(0x2ff)

# Maximum abs events
ABS_MAX = int(0x3f)

# Maximum SYN events
SYN_MAX = int(0xf)

EV_SYN      = 0x00
EV_KEY      = 0x01
EV_REL      = 0x02
EV_ABS      = 0x03
EV_MSC      = 0x04
EV_SW       = 0x05
EV_LED      = 0x11
EV_SND      = 0x12
EV_REP      = 0x14
EV_FF       = 0x15
EV_PWR      = 0x16
EV_FF_STATUS = 0x17
EV_MAX      = 0x1f

# Dict to help in loops
event_types = {
    'EV_SYN':		   EV_SYN,
    'EV_KEY':		   EV_KEY,
    'EV_REL':		   EV_REL,
    'EV_ABS':		   EV_ABS,
    'EV_MSC':		   EV_MSC,
    'EV_SW':		   EV_SW,
    'EV_LED':		   EV_LED,
    'EV_SND':		   EV_SND,
    'EV_REP':		   EV_REP,
    'EV_FF':		   EV_FF,
    'EV_PWR':		   EV_PWR,
    'EV_FF_STATUS':    EV_FF_STATUS,
    'EV_MAX':		   EV_MAX,
}
