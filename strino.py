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
import functions.utils
import functions.system
import constants
import argparse
import logging
import sys
import os


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Share your IO in unix like operating systems with Strino.')
    parser.add_argument('--list', help='List of available devices to share.', action="store_true")
    parser.add_argument('--verbose', help='Increase the output verbosity', action="store_true")
    args = parser.parse_args()

    # print(args)
    # Project name. Yes I know it can be set in a string... anyway ;)
    PROJECT_NAME = os.path.dirname(os.path.abspath(__file__))

    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), PROJECT_NAME)

    # Add Strino to PYTHONPATH
    if BASE_DIR not in sys.path:
        sys.path.append(BASE_DIR)

    if args.verbose:
        # Add a handler and set the default output to stdout
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)

        constants.glob.logger.addHandler(handler)
        constants.glob.logger.error('Verbose output is set to true')

    if args.list:
        devices = functions.system.get_all_devices_info()
        print(constants.glob.list_header)

        devices = functions.utils.natural_sort(devices, keyword='handler')
        print(f"{'ID':<5} {'Handler':<10} {'Device name'}")

        for pos, device in enumerate(devices):
            print(f"{pos:<5} {os.path.basename(device.get('handler')):<10} {device.get('name')}")
