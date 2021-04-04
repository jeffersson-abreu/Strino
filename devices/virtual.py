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
import structures.input
import structures.uinput
import constants.uinput
import misc.utils
import ctypes
import fcntl
import os


# noinspection PyTypeChecker
class VirtualDevice(object):
    def __init__(self, device_info):

        try:
            self.fd = os.open('/dev/uinput', os.O_RDWR | os.O_NONBLOCK)
        except Exception as err:
            constants.globals.logger.error('Error when opening uinput file')
            raise err

        self.events = device_info.pop('events')
        self.name = device_info.get('name')
        self.info = device_info

        constants.globals.logger.info(f'Emulating {self.name}')

        # Prepare the setup and clean the memory space
        self.usetup = structures.uinput.UinputSetup()
        ctypes.memset(ctypes.addressof(self.usetup), 0, ctypes.sizeof(self.usetup))

        # Set the device phys
        fcntl.ioctl(self.fd, constants.uinput.UI_SET_PHYS, self.info.get('phys'))

        # Fill the struct with our virtual device information
        self.usetup.name = self.info['name'].encode()
        self.usetup.id.product = self.info['product']
        self.usetup.id.vendor = self.info['vendor']

        # Set our bus different from the original info because now
        # we are emulating the device so set bus as virtual
        self.usetup.id.bustype = constants.input.BUS_VIRTUAL

        # TODO: set FF bits

        # For each event and codes [0, [1, 2, 3...]]
        for event, codes in self.events.items():

            # Set the event code bit
            fcntl.ioctl(self.fd, constants.uinput.UI_SET_EVBIT, event)

            if event == constants.ecodes.event_types.get("EV_SYN"):
                constants.globals.logger.info('Setting up event EV_SYN')

            if event == constants.ecodes.event_types.get("EV_MSC"):
                constants.globals.logger.info('Setting up event EV_MSC')
                for key in codes:
                    fcntl.ioctl(self.fd, constants.uinput.UI_SET_MSCBIT, key)
                continue

            if event == constants.ecodes.event_types.get("EV_LED"):
                constants.globals.logger.info('Setting up event EV_LED')
                for key in codes:
                    fcntl.ioctl(self.fd, constants.uinput.UI_SET_LEDBIT, key)
                continue

            if event == constants.ecodes.event_types.get("EV_KEY"):
                constants.globals.logger.info('Setting up event EV_KEY')
                for key in codes:
                    fcntl.ioctl(self.fd, constants.uinput.UI_SET_KEYBIT, key)
                continue

            if event == constants.ecodes.event_types.get("EV_SND"):
                constants.globals.logger.info('Not supported EV_SND yet!')
                continue

            if event == constants.ecodes.event_types.get("EV_SW"):
                constants.globals.logger.info('Setting up event EV_SW')
                for key in codes:
                    fcntl.ioctl(self.fd, constants.uinput.UI_SET_SWBIT, key)
                continue

            if event == constants.ecodes.event_types.get("EV_REL"):
                constants.globals.logger.info('Setting up event EV_REL')

                for key in codes:
                    fcntl.ioctl(self.fd, constants.uinput.UI_SET_RELBIT, key)
                continue

            if event == constants.ecodes.event_types.get("EV_ABS"):
                constants.globals.logger.info('Setting up event EV_ABS')

                # Define all structures we gonna use below
                uinput_abs_setup = structures.input.UinputAbsSetup()
                abs_info = structures.input.ABSInfo()

                for key in codes:
                    # (0 {value: 0, minimum: 0, maximum: 0, flat: 0, fuzz: 0, resolution: 0})
                    _axis, _abs = key

                    # Every single loop we fill 0 our structures to prevent memory trash in our structure
                    ctypes.memset(ctypes.addressof(uinput_abs_setup), 0, ctypes.sizeof(uinput_abs_setup))
                    ctypes.memset(ctypes.addressof(abs_info), 0, ctypes.sizeof(abs_info))

                    # Activate the absolute movements for the axis
                    fcntl.ioctl(self.fd, constants.uinput.UI_SET_ABSBIT, _axis)

                    abs_info.value = _abs.get('value')
                    abs_info.minimum = _abs.get('minimum')
                    abs_info.maximum = _abs.get('maximum')
                    abs_info.fuzz = _abs.get('fuzz')
                    abs_info.flat = _abs.get('flat')
                    abs_info.resolution = _abs.get('resolution')

                    # Set the axis and the ABS info
                    uinput_abs_setup.code = _axis
                    uinput_abs_setup.absinfo = abs_info

                    # Call ioctl to make our abs setup ;)
                    fcntl.ioctl(self.fd, constants.uinput.UI_ABS_SETUP, uinput_abs_setup)

                continue

        # Setup the device prop bits
        for bit in range(constants.input.INPUT_PROP_CNT):
            if misc.utils.is_in_bitmask(self.info.get('prop'), bit):
                fcntl.ioctl(self.fd, constants.uinput.UI_SET_PROPBIT, bit)

        # This ioctl sets parameters for the input device to be created
        constants.globals.logger.info('Writing setup to kernel')
        fcntl.ioctl(self.fd, constants.uinput.UI_DEV_SETUP, self.usetup)

        # On UI_DEV_CREATE the kernel will create the device node for this
        # device. We can start listening to the event, otherwise it will
        # not notice the events we are about to send.
        constants.globals.logger.info('Creating the device node')
        fcntl.ioctl(self.fd, constants.uinput.UI_DEV_CREATE)

        self.ev_sync = structures.input.InputEvent(structures.time.Timeval(0, 0), 0, 0, 0)

    def emit(self, evs: list):
        """
        Send the signal by writing to the early configured
        file descriptor. File descriptor should be opened
        using 'os' module.
        """

        for evt in evs:
            ie = structures.input.InputEvent.from_buffer_copy(evt)
            # Write the event for file
            os.write(self.fd, ie)

        # Sync events written above
        os.write(self.fd, self.ev_sync)
        return None

    def destroy(self):
        """ Properly close the writer """
        fcntl.ioctl(self.fd, constants.uinput.UI_DEV_DESTROY)
        constants.globals.logger.info(f'Device {self.info["name"]} destroyed')
        os.close(self.fd)
        return None
