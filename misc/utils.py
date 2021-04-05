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

import constants.globals
import subprocess
import random
import string
import re
import os


def to_int(obj: str):
    """
    Convert a string to integer if possible
    and if not possible make it lowercase
    :param obj: Any string digit
    :return: Undefined
    """
    if obj.isdigit():
        return int(obj)
    return obj.lower()


def order_by_alphanum(item, keyword=None) -> list:
    """
    Return a list of ordered by alphanumeric string. By
    passing a keyword to sort and if no keyword is given
    the primary key in dicts elements will be used to sort

    :param item: The item can be a alphanumeric string or a dict
    :param keyword: In case of item is a dict the we can set a key to sort
    :return: Sorted in alphanumeric list
    """

    if isinstance(item, str):
        # If the item is a string we extract the integers and
        # convert it to the real type (int) to help sorting
        return [to_int(c) for c in re.split('([0-9]+)', item)]

    if isinstance(item, dict):
        # If the item is a dict we extract and no keyword was
        # given we try to get the first key value to sort.
        if keyword is None:
            keys = list(item.keys())
            keyword = keys[0]

        # Otherwise the dict key value gonna be used to sort
        return [to_int(c) for c in re.split('([0-9]+)', str(item[keyword]))]


def natural_sort(_list: list, keyword=None) -> list:
    """
    Sort a list by natural keys. This functions can also
    sort a list of dict by passing a keyword to sort and
    if no keyword is given the primary key in dicts elements
    will be used to sort

    :param _list: A list containing string elements or dicts
    :param keyword: A key of dict if the list elements are dicts
    :return: A list sorted.
    """
    return sorted(_list, key=lambda key: order_by_alphanum(key, keyword=keyword))


def generate_random_id(size=20, chars=string.ascii_uppercase + string.digits):
    """ Generate a random id to make clean clients server space """
    return ''.join(random.choice(chars) for _ in range(size))


def is_in_bitmask(bitmask: bytes, bit: int) -> int:
    """
    Check an int in a bitmask
    :param bitmask: Bytes
    :param bit: integer to check in the bitmask
    :return: Operation product
    """
    return bitmask[bit//8] & (1 << (bit % 8))


def detect_system_type():
    """
    This function is responsible to detect
    witch kind of system we are running
    """
    command = 'ps --no-headers -o comm 1'
    system_encoded = subprocess.check_output(command.split())
    system_not_scape = system_encoded.decode()
    system = system_not_scape.strip('\n')
    return system


def disable_strino_service(system) -> bool:
    """
    Disable strino from start at boot time as a service

    :param system:  The system running type (E.g: systemd)
    :return: True if no errors and False if some error occurs
    """

    commands = {
        'systemd': [
            "systemctl disable strino",
            "rm /etc/systemd/system/strino.service"

        ]
    }

    if system in list(commands.keys()):
        # Execute all commands
        for command in commands.get(system):
            try:
                output = subprocess.check_output(command.split(), stderr=subprocess.DEVNULL)
                continue
            except subprocess.CalledProcessError:
                constants.globals.logger.error(f"Error while disabling strino {system} service")
        return True
    else:
        constants.globals.logger.error(f"Unknown {system} system type")
        constants.globals.logger.error(f"System {system} not supported")
        return False


def enable_strino_service(system) -> bool:
    """
    Enable strino to start at boot time as a service

    :param system:  The system running type (E.g: systemd)
    :return: True if no errors and False if some error occurs
    """

    # Build the relative path to the service based on system
    relative_path = os.path.join('etc/services', system)

    # Build a full path to the service
    file_path = os.path.join(
        constants.globals.BASE_DIR,
        relative_path
    )

    commands = {
        'systemd': [
            f"cp {file_path} /etc/systemd/system/strino.service",
            'systemctl enable strino'
        ]
    }

    # Save a result reference
    result = None

    if os.path.isfile(file_path):
        if system in commands.keys():

            # Execute all commands
            for command in commands.get(system):
                try:

                    output = subprocess.check_output(command.split(), stderr=subprocess.DEVNULL)
                    result = True
                    continue

                except subprocess.CalledProcessError:
                    constants.globals.logger.error(f"Fail to enable strino {system} service")
                    result = False
                    break
        else:
            constants.globals.logger.error(f"Unknown {system} system type")
            constants.globals.logger.error(f"System {system} not supported")
            result = False

    return result


__all__ = [
    'natural_sort',
    'order_by_alphanum',
    'generate_random_id',
    'is_in_bitmask',
    'to_int'
]
