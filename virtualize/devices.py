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
    def __init__(self, capabilities: dict):

        self.fd = os.open('/dev/uinput', os.O_WRONLY | os.O_NONBLOCK)

        self.capabilities = capabilities

        # Intantiate a timeval and input_event
        self.timeval = structures.time.Timeval(0, 0)
        self.input_event = structures.input.InputEvent(self.timeval, 0, 0, 0)

        # Prepare the setup and clean the memory space
        usetup = structures.input.UinputSetup()
        ctypes.memset(ctypes.addressof(usetup), 0, ctypes.sizeof(usetup))

        for event_type, event_codes in self.capabilities['events'].items():
            ui_set = constants.uinput.uinput_sets.get(event_type)

            ev_key = constants.ecodes.event_types.get(event_type)

            try:
                if ui_set is not None:
                    print('\n\n' + event_type, ui_set, ev_key)
                    fcntl.ioctl(self.fd, ui_set, ev_key)
                    for code in event_codes:
                        print(event_type, ui_set, code)
                        fcntl.ioctl(self.fd, ui_set, code)
            except OSError:
                pass

        # Fill the struct with our virtual device information
        usetup.name = self.capabilities['name'].encode()
        usetup.id.bustype = self.capabilities['bustype']
        usetup.id.product = self.capabilities['product']
        usetup.id.vendor = self.capabilities['vendor']

        # This ioctl sets parameters for the input device to be created
        fcntl.ioctl(self.fd, constants.uinput.UI_DEV_SETUP(structures.input.UinputSetup), usetup)

        # On UI_DEV_CREATE the kernel will create the device node for this
        # device. We are inserting a pause here so that userspace has time
        # to detect, initialize the new device, and can start listening to
        # the event, otherwise it will not notice the event we are about
        # to send. This pause is only needed in our example code!
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


__all__ = [
    'VirtualDevice'
]
