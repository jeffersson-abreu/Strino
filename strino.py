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
import constants.globals
import devices.physical
import misc.functions
import configparser
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

    settings = os.path.join(constants.globals.BASE_DIR, 'etc/settings.ini')

    # Get the default server from settings
    config = configparser.ConfigParser()
    config.read(settings)
    keys = config['STRINO_DEFAULTS']

    verbose = keys.getboolean('verbose')
    port = keys.getint('port')
    addr = keys.get('addr')
    tp = keys.get('type')

    # Get default devices in settings
    dev_section = config['STRINO_DEVICES']

    # Check if devices has handlers and pass it as default
    names = [dev_section.get(device) for device in dev_section]
    handlers = misc.functions.get_handlers_by_devices_name(names)

    parser = argparse.ArgumentParser(description='Share your IO in unix like operating systems with Strino.')
    parser.add_argument('-d', '--devices', help='List devices handlers to share', nargs='*', type=str, default=handlers)
    parser.add_argument('-v', '--verbose', help='Increase the output verbosity', action="store_true", default=verbose)
    parser.add_argument('-a', '--addr', help='Enter the server address to connect', type=str, default=addr)
    parser.add_argument('-p', '--port', help='Enter the server port to connect', type=int, default=port)
    parser.add_argument('-l', '--list', help='List of available devices to share', action="store_true")
    parser.add_argument('-t', '--type', help='Enter the type (server or client)', type=str, default=tp)

    args = parser.parse_args()

    if args.verbose:
        # Add a handler and set the default output to stdout
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(constants.globals.format_string, datefmt=constants.globals.format_date)
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)

        constants.globals.logger.addHandler(handler)
        constants.globals.logger.info('Verbose output is set to true')

    if args.list:
        handlers_mixed = misc.functions.get_all_devices_handlers()
        handlers_sorted = misc.utils.natural_sort(handlers_mixed)
        devices_list = [devices.physical.PhysicalDevice(handler) for handler in handlers_sorted]

        print(
            """
            \rBellow a list of all devices found on the system, if your pretended device 
            \rwas not in the list so verify if the device is really connected in a working 
            \rUSB port. If your device is not USB may it's not recognized by the system. 
            """
        )

        print(f"{'Handler':<10} {'Device name'}")

        for handler, device in zip(handlers_sorted, devices_list):
            print(f"{os.path.basename(handler):<10} {device.name}")
        sys.exit(0)

    if args.type:

        if args.type == 'server':

            # Get a list of all available events handlers in system
            handlers = misc.functions.get_all_devices_handlers(basename=True)

            # Filter devices to accept only valid devices.
            # This devices should exists in handlers
            filtered_devices = []
            for device in args.devices:
                if device not in handlers:
                    constants.globals.logger.info(f"{device} is not a valid device handler")
                    continue

                filtered_devices.append(
                    os.path.join('/dev/input', device)
                )

            start_server(args.addr, args.port, filtered_devices)

        if args.type == 'client':
            connect_to(addr=args.addr, port=args.port)
