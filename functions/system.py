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
def get_device_info(dev_handler: str) -> dict:
    """
    Get Device information by a given file descriptor
    :param dev_handler: A file opened with built-in open function
    :return: Dict containing information about device handled by file
    """

    with open(dev_handler, 'wb') as handler:
        constants.glob.logger.info(f'Trying to get {handler.name} information')

        # Create the string buffer to make future ioctl calls
        name = ctypes.create_string_buffer(constants.input.MAX_NAME_SIZE)
        phys = ctypes.create_string_buffer(constants.input.MAX_NAME_SIZE)
        uniq = ctypes.create_string_buffer(constants.input.MAX_NAME_SIZE)

        prop = ctypes.create_string_buffer(constants.input.INPUT_PROP_CNT // 8)
        fcntl.ioctl(handler, constants.input.EVIOCGPROP(prop), prop)

        # Instantiate a struct input_id and and
        # clean (fill 0) memory of it's address
        iid = structures.input.InputId()
        ctypes.memset(ctypes.addressof(iid), 0, ctypes.sizeof(iid))

        # Get the file ID (type, vendor, product, version)
        fcntl.ioctl(handler, constants.input.EVIOCGID, iid)

        # Get the device name
        fcntl.ioctl(handler, constants.input.EVIOCGNAME, name)

        # Some devices do not have a physical topology associated with them
        fcntl.ioctl(handler, constants.input.EVIOCGPHYS, phys)

        try:
            # Some kernels have started reporting bluetooth controller MACs as phys.
            # This lets us get the real physical address. As with phys, it may be blank.
            fcntl.ioctl(handler, constants.input.EVIOCGUNIQ, uniq)
        except IOError:
            pass

        constants.glob.logger.info(f'Device name is "{name.value.decode()}"')

        return {
            'bustype': iid.bustype,
            'vendor': iid.vendor,
            'product': iid.product,
            'version': iid.version,
            'name': name.value.decode(),
            'phys': phys.value.decode(),
            'unique': uniq.value.decode(),
            'handler': handler.name,
            'prop': prop.raw,
            'events': get_device_capabilities(dev_handler)
        }


# noinspection PyTypeChecker
def get_handlers_by_devices_name(names: list):
    """
    Get device handler by a giving device name
    :param: names: A list containing device names
    :return: A list containing valid device handlers
    """

    # Create the string buffer to make future ioctl calls
    name = ctypes.create_string_buffer(constants.input.MAX_NAME_SIZE)
    handlers = list()

    for handler in get_all_devices_handlers():
        # Get the device name
        with open(handler, 'rb') as hd:
            fcntl.ioctl(hd, constants.input.EVIOCGNAME, name)
            decoded_name = name.value.decode()
            if decoded_name in names:
                handlers.append(os.path.basename(handler))
                continue
            else:
                constants.glob.logger.error(f"Device {decoded_name} not exists")

    return handlers


def get_all_devices_handlers(basename=False) -> list:
    """
    Get all devices file handlers living in linux /dev/input folder
    :param: basename: Boolean value to control if file returns as a full path
    :return: A set of event handlers filename
    """
    file_handlers = set()

    for _, _, files in os.walk(constants.glob.DEVICES_PATH):
        for file in files:
            # Filter only files that name starts with "event"
            if file.startswith('event'):
                path = os.path.join(
                    constants.glob.DEVICES_PATH,
                    file
                )

                # Depending on basename append a file name or a full path
                file_handlers.add(file if basename else path)

    return list(file_handlers)


def get_all_devices_info() -> list:
    """
    Get a list of all devices handled by files living in /dev/input
    :return: A list of dictionary devices info
    """

    all_devices = list()
    constants.glob.logger.info(f'Trying to get information about all devices found in {constants.glob.DEVICES_PATH}')

    for file in get_all_devices_handlers():
        file_path = os.path.join(constants.glob.DEVICES_PATH, file)
        device_info = get_device_info(file_path)
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
def get_device_capabilities(dev_handler: str) -> dict:
    """
    Return all device events supported and keys related
    :param dev_handler: A file opened with built-in open function
    :return: Dict with device capabilities
    """

    with open(dev_handler, 'wb') as handler:
        constants.glob.logger.info(f'Trying to get {handler.name} information')

        # Create char arrays to be filed in ioctl calls. This char's
        # array a will handle events and key codes related to event
        cd_bits = ctypes.create_string_buffer(constants.ecodes.KEY_MAX // 8 + 1)
        ev_bits = ctypes.create_string_buffer(constants.ecodes.EV_MAX // 8 + 1)

        capabilities = dict()

        # Fill 0 (clean) the memory space of ev_bits and call ioctl to get bits of
        # all event codes supported by device so we can build the device capabilities
        constants.glob.logger.info(f'Trying to get all events supported by the device')
        ctypes.memset(ctypes.addressof(ev_bits), 0, ctypes.sizeof(ev_bits))
        fcntl.ioctl(handler, constants.input.EVIOCGBIT(0, ev_bits), ev_bits)

        # Build a dictionary of the device's capabilities
        for ev_type in range(0, constants.ecodes.EV_MAX):
            if test_bit(ev_bits.raw, ev_type):

                try:
                    # Fill 0 (clean) the memory space of cd_bits and call ioctl to get all
                    # related event codes so we can build a list of codes handled by event
                    ctypes.memset(ctypes.addressof(cd_bits), 0, ctypes.sizeof(cd_bits))
                    fcntl.ioctl(handler, constants.input.EVIOCGBIT(ev_type, cd_bits), cd_bits)
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
                            fcntl.ioctl(handler, constants.input.EVIOCGABS(ev_code), abs_info)

                            _abs = {
                                'value': abs_info.value,
                                'minimum': abs_info.minimum,
                                'maximum': abs_info.maximum,
                                'fuzz': abs_info.fuzz,
                                'flat': abs_info.flat,
                                'resolution': abs_info.resolution
                            }

                            # Get the event list and save the ABS
                            # dict in a tuple numbered by event...
                            # Eg: (00, _abs)
                            event = capabilities[keyname]
                            event.append((ev_code, _abs))

                        else:
                            # Just append the event code to event type key
                            capabilities[keyname].append(ev_code)

        constants.glob.logger.info(f'Success getting device supported events')

        for key in capabilities.keys():
            for name, code in constants.ecodes.event_types.items():
                if key == code:
                    constants.glob.logger.info(f'Found event {name}')

        constants.glob.logger.info(f'End device event reports\n')
        return capabilities
