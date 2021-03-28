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
import functions.system
import constants.ecodes
import structures.input
import constants.glob
import server.updates
import configparser
import pickle
import ctypes
import fcntl
import sys
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
        self.usetup.id.product = self.info['product']
        self.usetup.id.vendor = self.info['vendor']

        # Set our bus diferent from the original info because now
        # we are emulating the device so set bus as virtual
        self.usetup.id.bustype = constants.input.BUS_VIRTUAL

        # TODO: set FF bits

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

            if event == constants.ecodes.event_types.get("EV_SND"):
                constants.glob.logger.info('Not supported EV_SND yet!')
                continue

            if event == constants.ecodes.event_types.get("EV_SW"):
                constants.glob.logger.info('Setting up event EV_SW')
                for key in codes:
                    fcntl.ioctl(self.fd, constants.uinput.UI_SET_SWBIT, key)
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

        # Setup the device prop bits
        for bit in range(constants.input.INPUT_PROP_CNT):
            if functions.system.test_bit(self.info.get('prop'), bit):
                fcntl.ioctl(self.fd, constants.uinput.UI_SET_PROPBIT, bit)

        # This ioctl sets parameters for the input device to be created
        constants.glob.logger.info('Writting setup to kernel')
        fcntl.ioctl(self.fd, constants.uinput.UI_DEV_SETUP, self.usetup)

        # On UI_DEV_CREATE the kernel will create the device node for this
        # device. We can start listening to the event, otherwise it will
        # not notice the events we are about to send.
        constants.glob.logger.info('Creating the device node')
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
        constants.glob.logger.info(f'Device {self.info["name"]} destroyed')
        os.close(self.fd)
        return None


class PhisicalDevice(object):
    """ Represents a phisical device on the system """
    def __init__(self, handler=None):

        self.handler_path = handler

        # Get device capabilities and device informations
        self.capabilities = functions.system.get_device_capabilities(handler)
        self.info = functions.system.get_device_info(handler)

        # Size of the buffer to read
        self.buffer_size = ctypes.sizeof(structures.input.InputEvent)
        self.handler = None

        # If the device is a keyboard so we bind the
        # shortcut keys used to switch between screens
        self.bind_keys = self.is_keyboard()

        config = configparser.ConfigParser()
        config.read('settings.ini')

        keys = config['SCREEN_SWITCH_KEYS']

        self.modifier_key = keys.getint('modifier')
        self.modifier_state = False

        self.right_key = keys.getint('right')
        self.left_key = keys.getint('left')

        self.pos = 0

        self.open()

    def is_keyboard(self):
        """
        Assert if device is a keyboard. We
        consider a keyboard according to the
        data above. So we use the original IBM
        with min 83 keys.

        Original IBM PC Keyboard (1981) - 83 keys
        Updated IBM PC Keyboard (1984) - 84 keys
        AT Keyboard - 84 keys
        AT Enhanced Keyboard - 101 keys
        US Traditional Keyboard - 101 keys
        Enhanced European Keyboard - 102 keys
        Windows Keyboard - 104 keys
        Windows-based Laptop Keyboard - 86 keys

        """
        if constants.ecodes.EV_KEY in self.capabilities.keys():
            keys = self.capabilities.get(constants.ecodes.EV_KEY)
            if len(keys) >= 83:  # See the docs above ;)
                return True

        # We are not a keyboard
        return False

    def grab(self):
        """ Grab the device events visibility only for us """
        try:
            fcntl.ioctl(self.handler, constants.input.EVIOCGRAB, 1)
        except OSError:
            pass

    def release(self):
        """ Revoke the access to device """
        try:
            fcntl.ioctl(self.handler, constants.input.EVIOCREVOKE, 0)
        except OSError:
            pass

        self.open()

    def open(self):
        """ Open the handle file device """
        try:
            self.handler = os.open(self.handler_path, os.O_RDWR)
        except FileNotFoundError:
            constants.glob.logger.error("Error openning device handler file")
            sys.exit(1)

    def read(self):
        """
        This is the heart of any comunication between
        phisic and virtual device that is being simulated
        at the other point. Here we just read the events
        and put it in a queue to be sent to device
        """

        # Device (phisical) name
        device = self.info.get('name')

        # We need a event list because some events, like EV_ABS
        # need two events (before sync) to work properly
        ev_list = list()

        while True:
            try:
                # We need a blocking read as well to not
                # spend machine power in a reading loop
                buffer = os.read(self.handler, self.buffer_size)
            except OSError:
                # When releasing device from grab the read
                # operation throws an OSError exception,
                # so just stop the loop and keep going
                continue

            # Put any event in queue is conditioned to
            # the existence of clients to receive it
            if len(server.updates.clients) > 1:

                # We instantiate an structure input_event and fill with
                # buffer to check if event is diferent of EV_SYNC.
                ie = structures.input.InputEvent.from_buffer_copy(buffer)
                # print(ie.type, ie.code, ie.value)

                if ie.type:

                    if ie.type == constants.ecodes.EV_KEY:

                        if ie.code == self.modifier_key:
                            self.modifier_state = ie.value
                            ev_list.append(buffer)
                            continue

                        if ie.code == self.left_key:
                            if self.modifier_state:
                                if ie.value:
                                    if self.pos > 0:
                                        self.pos -= 1
                                        server.updates.change_focus(self.pos)

                        if ie.code == self.right_key:
                            if self.modifier_state:
                                if ie.value:
                                    if self.pos < len(server.updates.clients):
                                        self.pos += 1
                                        server.updates.change_focus(self.pos)

                    # Event is not EV_SYNC so append
                    # to list and continue the loop
                    ev_list.append(buffer)
                    continue

                # At this point the event is EV_SYNC so
                # we add The list of events to queue
                server.updates.events.put(
                    pickle.dumps({
                        "name": "DEVICE_EVENT",
                        "data": {
                            "device": device,
                            "event": ev_list
                        }
                    })
                )

            # Should I comment? ;)
            ev_list.clear()


__all__ = [
    'VirtualDevice',
    'PhisicalDevice'
]
