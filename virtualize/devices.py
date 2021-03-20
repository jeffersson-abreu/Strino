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
import structures.input
import ctypes
import fcntl
import os


# noinspection PyTypeChecker
class VirtualDevice(object):
    def __init__(self, device_info):

        if not isinstance(device_info, dict):
            raise ValueError('VirtualDevice should receive a dict event capabilities.')

        self.fd = os.open('/dev/uinput', os.O_WRONLY | os.O_NONBLOCK)

        self.events = device_info.pop('events')
        self.info = device_info

        # Intantiate a timeval and input_event
        self.timeval = structures.time.Timeval(0, 0)
        self.input_event = structures.input.InputEvent(self.timeval, 0, 0, 0)
        ctypes.memset(ctypes.addressof(self.input_event), 0, ctypes.sizeof(self.input_event))

        # Prepare the setup and clean the memory space
        usetup = structures.input.UinputSetup()
        ctypes.memset(ctypes.addressof(usetup), 0, ctypes.sizeof(usetup))

        # Set the device phys
        fcntl.ioctl(self.fd, constants.uinput.UI_SET_PHYS, self.info.get('phys'))

        # Fill the struct with our virtual device information
        usetup.name = self.info['name'].encode()
        usetup.id.bustype = self.info['bustype']
        usetup.id.product = self.info['product']
        usetup.id.vendor = self.info['vendor']

        # For each event and codes [0, [1, 2, 3...]]
        for event, codes in self.events.items():

            # Set the event code bit
            fcntl.ioctl(self.fd, constants.uinput.UI_SET_EVBIT, event)

            if event == constants.ecodes.event_types.get("EV_KEY"):
                for key in codes:
                    fcntl.ioctl(self.fd, constants.uinput.UI_SET_KEYBIT, key)
                continue

            if event == constants.ecodes.event_types.get("EV_REL"):
                for key in codes:
                    fcntl.ioctl(self.fd, constants.uinput.UI_SET_RELBIT, key)
                continue

            if event == constants.ecodes.event_types.get("EV_ABS"):

                for key in codes:
                    # (0 {value: 0, minimum: 0, maximum: 0, flat: 0, fuzz: 0, resolution: 0})
                    _axis, _abs = key

                    abs_info = structures.input.ABSInfo()
                    # ctypes.memset(ctypes.addressof(self.abs_info), 0, ctypes.sizeof(self.abs_info))

                    abs_info.value = int(_abs.get('value'))
                    abs_info.minimum = int(_abs.get('minimum'))
                    abs_info.maximum = int(_abs.get('maximum'))
                    abs_info.fuzz = int(_abs.get('fuzz'))
                    abs_info.flat = int(_abs.get('flat'))
                    abs_info.resolution = int(_abs.get('resolution'))

                    # Todo: Figure out the "invalid argument error" in kernel call
                    fcntl.ioctl(self.fd, constants.input.EVIOCSABS(_axis), abs_info)

                continue

        # This ioctl sets parameters for the input device to be created
        fcntl.ioctl(self.fd, constants.uinput.UI_DEV_SETUP(structures.input.UinputSetup), usetup)

        # On UI_DEV_CREATE the kernel will create the device node for this
        # device. We can start listening to the event, otherwise it will
        # not notice the events we are about to send.
        fcntl.ioctl(self.fd, constants.uinput.UI_DEV_CREATE)

    def write(self, ev_type, ev_code, ev_value):
        """
        Send the signal by writing to the early configured
        file descriptor. File descriptor should be opened
        using 'os' module.
        :param ev_type: Any Linux event type described in input-event-codes header
        :param ev_code: Any Linux event code described in input-event-codes header
        :param ev_value: Event possible value
        :return: None
        """

        ctypes.memset(ctypes.addressof(self.input_event), 0, ctypes.sizeof(self.input_event))

        self.input_event.type = ev_type
        self.input_event.code = ev_code
        self.input_event.ev_value = ev_value

        # Write the event for file
        os.write(self.fd, self.input_event)
        return None

    def destroy(self):
        """ Properly close the writer """
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
                while True:
                    data = device.read(ctypes.sizeof(input_event))
                    event = structures.input.InputEvent.from_buffer(bytearray(data))
                    print(event.time.tv_sec, event.time.tv_usec, event.type, event.code, event.value)
            except KeyboardInterrupt:
                pass


__all__ = [
    'VirtualDevice',
    'PhisicalDevice'
]
