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

# This items that can change their values
# any time during the program execution

import constants.glob
import queue

devices = {}    # Devices capabilities
clients = {}    # Clients information
focus = None    # Client at focus now

# This is a simple first-in first-out
# queue that handle the devices events
# to be sent by the sender thread to the
# focus client defined above.
events = queue.SimpleQueue()


def send_events():
    """ Send the events to the client  """
    constants.glob.logger.info("Starting sender thread")

    # Instantiate client and protocol to be
    # visible by the body of while loop
    client, protocol = None, None

    while True:
        # Try to get events from queue. This is a
        # blocking operation so if nothing in queue
        # the threads wait until new data comes
        event = events.get()

        # Only if the focus has changed we get the
        # transport. This increase the performance.
        if client != focus:
            client = clients.get(focus)
            protocol = client.get('protocol')

        # Send the event
        if protocol is not None:
            protocol.transport.write(event)


def change_focus(pos):
    global focus

    all_clients = len(clients)

    if pos == 0:
        for device in devices.values():
            device.release()
    else:
        for device in devices.values():
            device.grab()

    if pos <= all_clients:
        ids = list(clients.keys())
        focus = ids[pos]
        print(f'Focus changed to {ids[pos]}')
