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
import configparser
import functions
import constants
import argparse
import logging
import sys
import os


if __name__ == '__main__':

    # Check if user has root access.
    # All operations need root
    if os.geteuid():
        print('We need root access!')
        sys.exit(1)

    # Get the default server from settings
    config = configparser.ConfigParser()
    config.read('settings.ini')
    keys = config['STRINO_DEFAULTS']

    verbose = keys.getboolean('verbose')
    port = keys.getint('port')
    addr = keys.get('addr')

    parser = argparse.ArgumentParser(description='Share your IO in unix like operating systems with Strino.')
    parser.add_argument('-v', '--verbose', help='Increase the output verbosity', action="store_true", default=verbose)
    parser.add_argument('-a', '--addr', help='Enter the server address to connect', type=str, default=addr)
    parser.add_argument('-p', '--port', help='Enter the server port to connect', type=int, default=port)
    parser.add_argument('-d', '--devices', help='List devices handlers to share', nargs='*', type=str, default=[])
    parser.add_argument('-l', '--list', help='List of available devices to share', action="store_true")
    parser.add_argument('-t', '--type', help='Enter the type (server or client)', type=str)

    args = parser.parse_args()

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

            # Get a list of all available events handlers in system
            handlers = functions.system.get_all_devices_handlers(basename=True)

            # Filter devices to accept only valid devices.
            # This devices should exists in handlers
            filtered_devices = []
            for device in args.devices:
                if device not in handlers:
                    constants.glob.logger.info(f"{device} is not a valid device handler")
                    continue
                filtered_devices.append(device)

            start_server(args.addr, args.port, args.devices)

        if args.type == 'client':
            connect_to(addr=args.addr, port=args.port)
