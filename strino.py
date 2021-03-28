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

from server.server import start_server
from client.client import connect_to
import functions.utils
import constants
import argparse
import logging
import sys
import os


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Share your IO in unix like operating systems with Strino.')
    parser.add_argument('-a', '--addr', help='Enter the server address to connect', type=str, default='127.0.0.1')
    parser.add_argument('-p', '--port', help='Enter the server port to connect', type=int, default=4000)
    parser.add_argument('-l', '--list', help='List of available devices to share', action="store_true")
    parser.add_argument('-v', '--verbose', help='Increase the output verbosity', action="store_true")
    parser.add_argument('-t', '--type', help='Enter the type (server or client)', type=str)
    parser.add_argument('-d', '--devices', help='List devices to share', nargs='*')

    args = parser.parse_args()

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
        formatrer = logging.Formatter(constants.glob.format_string, datefmt=constants.glob.format_date)
        handler.setFormatter(formatrer)
        handler.setLevel(logging.INFO)

        constants.glob.logger.addHandler(handler)
        constants.glob.logger.info('Verbose output is set to true')

    if args.list:
        devices = functions.system.get_all_devices_info()
        print(constants.glob.list_header)

        devices = functions.utils.natural_sort(devices, keyword='handler')
        print(f"{'Handler':<10} {'Device name'}")

        for device in devices:
            print(f"{os.path.basename(device.get('handler')):<10} {device.get('name')}")

    if args.type:

        if args.type == 'server':

            devices = []

            for device in args.devices:
                path = os.path.join(constants.glob.DEVICES_PATH, device)
                devices.append(path)

            start_server(args.addr, args.port, devices)

        if args.type == 'client':
            connect_to(addr=args.addr, port=args.port)
            # pass


