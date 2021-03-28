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

# This itens that can chage their values
# any time during the program execution

import constants.glob
import queue

# Devices emulated
devices = {}

# Events received queue
events = queue.SimpleQueue()


def exec_from_queue():
    """
    Get events from queue and execute
    then by emmiting to emulated device
    """
    constants.glob.logger.error("Starting dequeue thread")

    while True:
        try:
            # Try to get events from queue. This is a
            # blocking operation so if nothing in queue
            # the threads wait until new data comes
            event = events.get()
            name = event.get('device')
            evt_list = event.get('event')
            device = devices.get(name)
            device.emit(evt_list)

        except Exception as error:
            constants.glob.logger.error("Error happens in 'exec_from_queue' thread")
            constants.glob.logger.error(f"Error: {error}")
            continue
