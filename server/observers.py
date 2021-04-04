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

from structures.input import InputEvent
from events.interfaces import Observer
from typing import AnyStr, Dict, List
import networking.communication
import constants.globals
import devices.physical
import constants.ecodes
import configparser
import asyncio
import os


class EventSender(Observer):
    """
    Send all events that occurs to the
    client in focus at the moment.
    """

    def __init__(self, *args, **kwargs):
        Observer.__init__(self, *args, **kwargs)

        # Networking events handler
        self.events = networking.communication.Events()

        self._identification = None
        self._transport = None

    def run(self) -> None:
        while True:
            data = self.queue.get()
            who, event = data.values()

            if who == 'PhysicalDevice':
                if self._identification is not 'StrinoServer' and self._identification is not None:
                    evt = self.events.generate("DEVICE_EVENT", event)
                    self._transport.write(evt)

            if who == 'FocusEvents':
                self._identification = event.get('identification')
                self._transport = event.get('transport')


class ShortcutListener(Observer):
    """
    Listen to events and try to match the keyboard
    shortcuts and notify all observers attached
    """

    def __init__(self, *args, **kwargs):
        Observer.__init__(self, *args, **kwargs)

        # Open shortcuts settings and load all of then
        self.path = os.path.join(constants.globals.BASE_DIR, 'etc/shortcuts.ini')
        shortcuts = configparser.ConfigParser()
        shortcuts.read(self.path)

        # Get all modifiers and map all shortcuts
        self.modifiers = self.get_all_modifiers(shortcuts)
        self.shortcuts = self.map(shortcuts)
        self.event = None
        self.modifier = 0

    @staticmethod
    def get_all_modifiers(shortcuts):
        """
         Get all modifiers in shortcuts
        :param shortcuts: Shortcuts read with configparser
        :return: A set containing modifiers keys
        """
        modifiers = set()
        for name in shortcuts:
            if name is not "DEFAULT":
                event = shortcuts[name]
                modifier = event.getint('modifier')
                modifiers.add(modifier)
        return modifiers

    @staticmethod
    def map(shortcuts) -> dict:
        """
        Map all shortcuts and generalize then to be
        readable as events. The default shortcut in
        shortcuts.ini sims like:

            [SHORTCUT_NAME]
            modifier = 29
            left = 105

        This functions map the shortcuts to something
        like:

            '29 105': 'SHORTCUT_NAME'

        :param shortcuts: Shortcuts read with configparser
        :return: dict of mapped shortcuts
        """
        events = dict()
        for name in shortcuts:
            if name is not "DEFAULT":
                shortcut = shortcuts[name]
                event = ' '.join(shortcut.get(key) for key in shortcut)
                events[event] = name
        return events

    def run(self) -> None:
        while True:
            data = self.queue.get()
            who, event = data.values()

            if who == "PhysicalDevice":
                data = event.get('data')

                for evt in data:
                    ie = InputEvent.from_buffer_copy(evt)
                    if ie.type == constants.ecodes.EV_KEY:
                        # In case of the key pressed is an modifier
                        if ie.code in self.modifiers:
                            if ie.value:  # Pressing
                                self.modifier = ie.code
                                continue

                            # Releasing
                            self.modifier = 0

                            # We just propagate the shortcut event
                            # when the modifier key is released to
                            # prevent bug that stuck devices
                            if self.event:
                                event = self.event
                                self.notify(event)
                                self.event = None
                            continue

                        if self.modifier:  # A modifier is pressed
                            if not ie.value:  # The key is being released

                                # Generate a key name as in "map" function defined above
                                keys = [str(self.modifier), str(ie.code)]
                                shortcut = ' '.join(keys)

                                # Check if shortcut name is in
                                # mapped shortcuts list
                                if shortcut in self.shortcuts:
                                    # Set the shortcut event to be sent on modifier key release
                                    self.event = {'name': self.shortcuts[shortcut]}


class FocusEvents(Observer):
    """
    Keep references of clients and notify
    all observers attached about changes
    """

    def __init__(self, *args, **kwargs):
        Observer.__init__(self, *args, **kwargs)

        # Define the clients data type
        self._clients: Dict[AnyStr, asyncio.BaseTransport] = {}

        # Generate the default identification and
        # pass it as default to the _client
        self.default_identification = "StrinoServer"
        self._focus = self.default_identification

        # Register the default identification key and transport
        self._clients[self.default_identification] = asyncio.BaseTransport()
        constants.globals.logger.info(f"Added {self.default_identification} as default focus")

    def register(self, name: AnyStr, transport: asyncio.BaseTransport):
        """ Register a client to send events """
        self._clients[name] = transport
        constants.globals.logger.info(f"Added {name} to sender list")

    def forget(self, name: AnyStr):
        """ Remove a client from list of clients """
        if name in self._clients:
            constants.globals.logger.info(f"Removing {name} from sender list")
            self._clients.pop(name)
            self.to_last_client()

    def to_last_client(self):
        """ Change the focus to the last client """
        if len(self._clients):
            identifications = list(self._clients.keys())
            identification = identifications[-1]
            self._focus = identification
            constants.globals.logger.info(f"Focus moved to {self._focus}")

            self.notify({
                'identification': self._focus,
                'transport': self._clients.get(self._focus)
            })

    def to_left(self):
        """ Change the focus to left """
        names = list(self._clients.keys())
        position = names.index(self._focus) - 1

        if position >= 0:
            try:
                self._focus = names[position]
                constants.globals.logger.info(f"Focus moved to {self._focus}")
                self.notify({
                    'identification': self._focus,
                    'transport': self._clients.get(self._focus)
                })

            except (ValueError, IndexError):
                pass

    def to_right(self):
        """ Change the focus to left """
        names = list(self._clients.keys())
        position = names.index(self._focus) + 1

        if position <= len(self._focus):
            try:
                self._focus = names[position]
                constants.globals.logger.info(f"Focus moved to {self._focus}")
                self.notify({
                    'identification': self._focus,
                    'transport': self._clients.get(self._focus)
                })
            except (ValueError, IndexError):
                pass

    def run(self) -> None:
        while True:
            data = self.queue.get()
            who, event = data.values()

            if who == "ShortcutListener":
                shortcut = event.get('name')

                if shortcut == "FOCUS_SWITCH_RIGHT":
                    self.to_right()

                if shortcut == "FOCUS_SWITCH_LEFT":
                    self.to_left()


class Grabber(Observer):
    """ Grab devices based on focus """

    def __init__(self, *args, **kwargs):
        Observer.__init__(self, *args, **kwargs)

        self._devices: List[devices.physical.PhysicalDevice] = []

    def get_devices(self) -> List[devices.physical.PhysicalDevice]:
        """ Return a list of devices we are watching for grab """
        return self._devices

    def add_device(self, device: devices.physical.PhysicalDevice) -> None:
        """
        Add devices to internal devices list
        :param device: PhysicalDevice instance
        :return: None
        """
        self._devices.append(device)
        return None

    def release_all(self):
        """ Release all devices in internal list """
        constants.globals.logger.info("Releasing all devices")
        for device in self._devices:
            if device.is_grabbed:
                device.release()

    def grab_all(self):
        """ Grab all devices in internal list """
        constants.globals.logger.info("Grabbing all devices")
        for device in self._devices:
            if not device.is_grabbed:
                device.grab()

    def run(self) -> None:
        while True:
            data = self.queue.get()
            who, event = data.values()

            if who == 'FocusEvents':
                if event.get('identification') == 'StrinoServer':
                    self.release_all()
                    continue

                self.grab_all()
