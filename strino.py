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

import argparse
import sys
import os


def list_devices():
    print("Listing devices...")


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
        list_devices()

