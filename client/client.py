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

import networking.communication
import constants.globals
import asyncio
import time
import sys


class TCPClient(asyncio.Protocol):

    def __init__(self, loop=None):

        self.events = networking.communication.Events()
        self.transport = None
        self.loop = loop

    def connection_made(self, transport):
        addr, _ = transport.get_extra_info('peername')
        constants.globals.logger.info("Successful connect to server")
        self.transport = transport

    def data_received(self, data):
        # All communication is made by events. The
        # events are generated and handled by Events
        # class defined at module "networking"
        self.events.handle(data, self)

    def connection_lost(self, exc):
        constants.globals.logger.info('The server closed the connection')
        constants.globals.logger.info(f'Reason: {exc if exc is not None else "Unknown reason"}')
        self.loop.stop()
        sys.exit(1)


def connect_to(addr, port):
    """ Connect the client to the server """

    loop = asyncio.get_event_loop()

    while True:
        # This try to connect us to server that should be
        # waiting for connections in the most case. Once
        # there is a possibility that some connection error
        # occurs, the loop will try every 'X' seconds to
        # connect to it.

        try:
            constants.globals.logger.info(f"Trying to connect to server at {addr}:{port}")
            coro = loop.create_connection(lambda: TCPClient(loop=loop), addr, port)
            loop.run_until_complete(coro)

            # If connection is successful
            # stop the loop and go on
            break
        except ConnectionRefusedError:
            constants.globals.logger.info("Fail connecting to server")
            constants.globals.logger.info("Trying again in 5 secs")
            time.sleep(5)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        constants.globals.logger.info("Stopping the communication")
        loop.stop()


__all__ = [
    'TCPClient',
    'connect_to'
]
