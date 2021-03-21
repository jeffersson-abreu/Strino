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

import logging

# Linux living devices handler files
DEVICES_PATH = '/dev/input'

UINPUT_MAX_NAME_SIZE = 80


logger = logging.getLogger()

format_string = '[%(asctime)s][%(levelname)s] - %(message)s'
format_date = '%d-%m-%y %H:%M:%S'

logging.basicConfig(
    filename='/home/jeffersson/strino.log',
    format=format_string,
    datefmt=format_date,
    level=logging.INFO,
    filemode='w'
)


list_header = """
    \rBellow a list of all devices found on the system, if your pretended device 
    \rwas not in the list so verify if the device is really connected in a working 
    \rUSB port. If your device is not USB may it's not recognized by the system. 
"""