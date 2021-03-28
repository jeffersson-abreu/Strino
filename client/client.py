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

from threading import Thread
import functions.utils
import constants.glob
import events.classes
import client.updates
import asyncio
import time


class TCPClient(asyncio.Protocol):

    def __init__(self, loop=None):

        self.id = functions.utils.generate_random_id()
        self.events = events.classes.Events()
        self.transport = None
        self.loop = loop

    def connection_made(self, transport):
        self.transport = transport
        # Afeter conecting to the server starts the sync process by
        # creating an announcement event and then send it to server
        event = self.events.generate('ANNOUNCEMENT', self)
        self.transport.write(event)

    def data_received(self, data):
        # All comunication is made by events. The
        # events are generated and handled by Events
        # class defined at module "events"
        self.events.handle(data, self)

    def connection_lost(self, exc):
        constants.glob.logger.info('The server closed the connection')
        constants.glob.logger.info(f'Reason: {exc if exc is not None else "Unknown"}')

        # Destroy all virtualized devices
        for name in client.updates.devices.keys():
            d = client.updates.devices.get(name)
            d.destroy()

        self.loop.stop()


def connect_to(addr='127.0.0.1', port=4000):
    """ Connect the client to the server """

    loop = asyncio.get_event_loop()

    # The loop bellow try to connect us to server that
    # should be waiting for connections in the most case.
    # Once there is a possibility that some connection
    # error occurs, the loop will try every 'X' seconds
    # to connect to it.
    while True:
        try:
            constants.glob.logger.info(f"Trying to connect to server at {addr}:{port}")
            coro = loop.create_connection(lambda: TCPClient(loop=loop), addr, port)
            loop.run_until_complete(coro)
            # If connection is successful
            # stop the loop and go on
            break
        except ConnectionRefusedError:
            constants.glob.logger.info("Fail connecting to server")
            constants.glob.logger.info("Trying again in 5 secs")
            time.sleep(5)

    # Start the dequeue thread responsible for execute all events
    p = Thread(target=client.updates.exec_from_queue, daemon=True)
    p.start()

    constants.glob.logger.info("Successful connect to server")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        constants.glob.logger.info("Stopping the comunication")
        for name in client.updates.devices.keys():
            device = client.updates.devices.get(name)
            device.destroy()
        loop.stop()


__all__ = [
    'TCPClient',
    'connect_to'
]
