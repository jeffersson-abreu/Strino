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

import constants.uinput
import constants.ecodes
import structures.input
import constants.glob
import ctypes
import fcntl
import os


# noinspection PyTypeChecker
class VirtualDevice(object):
    def __init__(self, device_info):

        try:
            self.fd = os.open('/dev/uinput', os.O_RDWR | os.O_NONBLOCK)
        except Exception as err:
            constants.glob.logger.error('Error when openning uinput file')
            raise err

        self.events = device_info.pop('events')
        self.info = device_info

        constants.glob.logger.info(f'Emulating {self.info.get("name")}')

        # Prepare the setup and clean the memory space
        self.usetup = structures.input.UinputSetup()
        ctypes.memset(ctypes.addressof(self.usetup), 0, ctypes.sizeof(self.usetup))

        # Set the device phys
        fcntl.ioctl(self.fd, constants.uinput.UI_SET_PHYS, self.info.get('phys'))

        # Fill the struct with our virtual device information
        self.usetup.name = self.info['name'].encode()
        self.usetup.id.bustype = self.info['bustype']
        self.usetup.id.product = self.info['product']
        self.usetup.id.vendor = self.info['vendor']

        # For each event and codes [0, [1, 2, 3...]]
        for event, codes in self.events.items():

            # Set the event code bit
            fcntl.ioctl(self.fd, constants.uinput.UI_SET_EVBIT, event)

            if event == constants.ecodes.event_types.get("EV_SYN"):
                constants.glob.logger.info('Setting up event EV_SYN')

            if event == constants.ecodes.event_types.get("EV_MSC"):
                constants.glob.logger.info('Setting up event EV_MSC')
                for key in codes:
                    fcntl.ioctl(self.fd, constants.uinput.UI_SET_MSCBIT, key)
                continue

            if event == constants.ecodes.event_types.get("EV_LED"):
                constants.glob.logger.info('Setting up event EV_LED')
                for key in codes:
                    fcntl.ioctl(self.fd, constants.uinput.UI_SET_LEDBIT, key)
                continue

            if event == constants.ecodes.event_types.get("EV_KEY"):
                constants.glob.logger.info('Setting up event EV_KEY')
                for key in codes:
                    fcntl.ioctl(self.fd, constants.uinput.UI_SET_KEYBIT, key)
                continue

            if event == constants.ecodes.event_types.get("EV_REL"):
                constants.glob.logger.info('Setting up event EV_REL')

                for key in codes:
                    fcntl.ioctl(self.fd, constants.uinput.UI_SET_RELBIT, key)
                continue

            if event == constants.ecodes.event_types.get("EV_ABS"):
                constants.glob.logger.info('Setting up event EV_ABS')

                # Define all structures we gona use below
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

        # This ioctl sets parameters for the input device to be created
        constants.glob.logger.info('Writting setup to kernel')
        fcntl.ioctl(self.fd, constants.uinput.UI_DEV_SETUP, self.usetup)

        # On UI_DEV_CREATE the kernel will create the device node for this
        # device. We can start listening to the event, otherwise it will
        # not notice the events we are about to send.
        constants.glob.logger.info('Creating the device node')
        fcntl.ioctl(self.fd, constants.uinput.UI_DEV_CREATE)

    def emit(self, ev_type, ev_code, ev_value):
        """
        Send the signal by writing to the early configured
        file descriptor. File descriptor should be opened
        using 'os' module.
        :param ev_type: Any Linux event type described in input-event-codes header
        :param ev_code: Any Linux event code described in input-event-codes header
        :param ev_value: Event possible value
        :return: None
        """

        # Intantiate a timeval and input_event
        timeval = structures.time.Timeval(0, 0)
        input_event = structures.input.InputEvent()

        input_event.time = timeval
        input_event.type = ev_type
        input_event.code = ev_code
        input_event.value = ev_value

        # Write the event for file
        os.write(self.fd, input_event)
        return None

    def destroy(self):
        """ Properly close the writer """
        constants.glob.logger.info('Stopping device emulation')
        fcntl.ioctl(self.fd, constants.uinput.UI_DEV_DESTROY)
        os.close(self.fd)
        return None


class PhisicalDevice(object):
    def __init__(self, handler=None):

        # The system handler file
        self.handler = handler

    def read(self):
        input_event = structures.input.InputEvent()

        with open(self.handler, 'rb') as device:
            try:
                with open('/home/jeffersson/data.txt', 'w') as datafile:

                    while True:
                        data = device.read(ctypes.sizeof(input_event))
                        event = structures.input.InputEvent.from_buffer(bytearray(data))
                        print(event.time.tv_sec, event.time.tv_usec, event.type, event.code, event.value)
                        datafile.write(f'{event.type},{event.code},{event.value}\n')

            except KeyboardInterrupt:
                pass


__all__ = [
    'VirtualDevice',
    'PhisicalDevice'
]
