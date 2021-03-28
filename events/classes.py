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

from events.comunication import *
import constants.glob
import pickle
import json
import sys


class Events(object):
    """ Represents a system event """
    def __init__(self):

        # All events should have a generate and a digest
        # callback function to keep a nice communication
        self._events = {
            "ANNOUNCEMENT": {
                "generate": generate_announcement,
                "digest": digest_announcement
            },

            "ANNOUNCEMENT_RESPONSE": {
                "generate": generate_announcement_response,
                "digest": digest_announcement_response
            },

            "DEVICE_EVENT": {
                "generate": generate_device_event,
                "digest": digest_device_event
            }
        }

    def handle(self, data, protocol):
        """
        Handle an event in hole application
        :param protocol: asyncio.Protocol instance
        :param data: Binary event
        :return: None
        """

        try:
            event = pickle.loads(data)
            event_name = event.get("name")
            event_data = event.get("data")
        except Exception as exc:
            constants.glob.logger.warning("Error receiving event")
            constants.glob.logger.warning(exc)
            return False

        # Check if the received event is listed as valid
        if self.is_valid(event_name):

            # Get all event callbacks and choose the digest one
            event_callables = self._events.get(event_name)
            callback = event_callables.get("digest")

            # Call a digest callback with
            # binary event data received
            callback(event_data, protocol)

    def generate(self, event_name: str, *args, **kwargs):
        """
        Generate any valid event in hole application
        :param event_name: String containing a valid event name
        :return: Return encoded data except on error that will return None
        """

        if self.is_valid(event_name):

            # Get all event callbacks and choose the generate
            event_callables = self._events.get(event_name)
            callback = event_callables.get("generate")

            # Generate callback
            event = callback(*args, **kwargs)
            return event

        constants.glob.logger.critical(f"Event {event_name} is not recognized")
        constants.glob.logger.info(f"Exiting now")
        # Return None if the event is not valid
        sys.exit(1)

    def is_valid(self, event_name: str):
        """
        Assert if a given event is listed in a particular event names list
        :param event_name: String containing a valid event name
        :return: Bool
        """
        if event_name in self._events.keys():
            return True
        return False


__all__ = [
    'Events'
]
