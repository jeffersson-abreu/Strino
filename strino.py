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

import virtualize.devices
import functions.system
from time import sleep
import argparse
import sys
import os


def get_handler_position(path):
    basename = os.path.basename(path)
    position = basename.strip('event')
    return int(position)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Share your IO in unix like operating systems.')
    parser.add_argument('list', type=bool, help='List of available devices to share.')
    args = parser.parse_args()

    # Project name. Yes I know it can be set in a string... anyway ;)
    PROJECT_NAME = os.path.dirname(os.path.abspath(__file__))

    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), PROJECT_NAME)

    # Add Strino to PYTHONPATH
    if BASE_DIR not in sys.path:
        sys.path.append(BASE_DIR)

    if args.list:
        import constants.ecodes
        with open('/dev/input/event7', 'rb') as handler:
            device_info = functions.system.get_device_info(handler)
            print(device_info)
            device = virtualize.devices.VirtualDevice(device_info)

            try:
                with open('/home/jeffersson/data.txt', 'r') as datafile:
                    for line in datafile.readlines():
                        cd, tp, vl = line.split(',')
                        device.write(int(cd), int(tp), int(vl))
                        sleep(0.001)
                device.destroy()
                # sleep(1000)
            except KeyboardInterrupt:
                device.destroy()
