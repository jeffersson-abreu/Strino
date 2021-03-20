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


import structures.input

import constants.ecodes
import constants.input
import constants.glob

import ctypes
import fcntl
import os


# noinspection PyTypeChecker
def get_device_info(file: open) -> dict:
    """
    Get Device informations by a given file descriptor
    :param file: A file opened with built-in open function
    :return: Dict containing informations about device handled by file
    """

    # Create the string buffer to make future ioctl calls
    max_name_size = ctypes.sizeof(constants.input.MAX_NAME_SIZE)
    name = ctypes.create_string_buffer(max_name_size)
    phys = ctypes.create_string_buffer(max_name_size)
    uniq = ctypes.create_string_buffer(max_name_size)

    # Instantiate a struct input_id and and
    # clean (fill 0) memory of it's address
    iid = structures.input.InputId()
    ctypes.memset(ctypes.addressof(iid), 0, ctypes.sizeof(iid))

    # Get the file ID (type, vendor, product, version)
    fcntl.ioctl(file, constants.input.EVIOCGID, iid)

    # Get the device name
    fcntl.ioctl(file, constants.input.EVIOCGNAME, name)

    # Some devices do not have a physical topology associated with them
    fcntl.ioctl(file, constants.input.EVIOCGPHYS, phys)

    try:
        # Some kernels have started reporting bluetooth controller MACs as phys.
        # This lets us get the real physical address. As with phys, it may be blank.
        fcntl.ioctl(file, constants.input.EVIOCGUNIQ, uniq)
    except IOError:
        pass

    return {
        'bustype': iid.bustype,
        'vendor': iid.vendor,
        'product': iid.product,
        'version': iid.version,
        'name': name.value.decode(),
        'phys': phys.value.decode(),
        'unique': uniq.value.decode(),
        'handler': file.name,
        'events': get_device_capabilities(file)
    }


def get_all_devices_handlers() -> set:
    """
    Get all devices file handlers living in linux /dev/input folder
    :return: A set of event handlers filename
    """
    file_handlers = set()

    for _, _, files in os.walk(constants.glob.DEVICES_PATH):
        for file in files:
            # Filter only files that name starts with "event"
            if file.startswith('event'):
                file_handlers.add(
                    os.path.join(
                        constants.glob.DEVICES_PATH,
                        file
                    )
                )

    return file_handlers


def get_all_devices_info() -> list:
    """
    Get a list of all devices handled by files living in /dev/input
    :return: A list of dicionary devices info
    """

    all_devices = list()

    for file in get_all_devices_handlers():
        file_path = os.path.join(constants.glob.DEVICES_PATH, file)
        with open(file_path, 'r') as handler:
            device_info = get_device_info(handler)
            all_devices.append(device_info)

    return all_devices


def test_bit(bitmask: bytes, bit: int) -> int:
    """
    Check an int in a bitmask
    :param bitmask: Bytes
    :param bit: integer to check in the bitmask
    :return: Operation product
    """
    return bitmask[bit//8] & (1 << (bit % 8))


# noinspection PyTypeChecker
def get_device_capabilities(file: open) -> dict:
    """
    Return all device events supported and keys related
    :param file: A file opened with built-in open function
    :return: Dict with device capabilities
    """

    # Create char arrays to be filed in ioctl calls. This char's
    # array a will handle events and key codes related to event
    cd_bits = ctypes.create_string_buffer(constants.ecodes.KEY_MAX // 8 + 1)
    ev_bits = ctypes.create_string_buffer(constants.ecodes.EV_MAX // 8 + 1)

    capabilities = dict()

    # Fill 0 (clean) the memory space of ev_bits and call ioctl to get bits of
    # all event codes suported by device so we can build the device capabilities
    ctypes.memset(ctypes.addressof(ev_bits), 0, ctypes.sizeof(ev_bits))
    fcntl.ioctl(file, constants.input.EVIOCGBIT(0, ev_bits), ev_bits)

    # Build a dictionary of the device's capabilities
    for ev_type in range(0, constants.ecodes.EV_MAX):
        if test_bit(ev_bits.raw, ev_type):

            try:
                # Fill 0 (clean) the momory space of cd_bits and call ioctl to get all
                # related event codes so we can build a list of codes handled by event
                ctypes.memset(ctypes.addressof(cd_bits), 0, ctypes.sizeof(cd_bits))
                fcntl.ioctl(file, constants.input.EVIOCGBIT(ev_type, cd_bits), cd_bits)
            except OSError:
                # Sometime an argument error occurs we
                # just break the loop and keep going
                break

            keyname = ev_type

            # if no error occurs so add the event key
            capabilities[keyname] = []

            for ev_code in range(0, constants.ecodes.KEY_MAX):
                if test_bit(cd_bits.raw, ev_code):

                    if ev_type == constants.ecodes.event_types['EV_ABS']:
                        abs_info = structures.input.ABSInfo()

                        # At this point we just check if event type is EV_ABS so clean the memory
                        # space of the instance of ABSInfo defined above and call the kernel to
                        # give us info about ABS device capabilities
                        ctypes.memset(ctypes.addressof(abs_info), 0, ctypes.sizeof(abs_info))
                        fcntl.ioctl(file, constants.input.EVIOCGABS(ev_code), abs_info)

                        _abs = {
                            'value': abs_info.value,
                            'minimum': abs_info.minimum,
                            'maximum': abs_info.maximum,
                            'fuzz': abs_info.fuzz,
                            'flat': abs_info.flat,
                            'resolution': abs_info.resolution
                        }

                        # Get the event list and save the ABS
                        # dict in a tuple numered by event...
                        # Eg: (00, _abs)
                        event = capabilities[keyname]
                        event.append((ev_code, _abs))

                    else:
                        # Just append the event code to event type key
                        capabilities[keyname].append(ev_code)

    return capabilities
