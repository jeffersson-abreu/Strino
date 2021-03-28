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
import events.classes
import constants.glob
import server.updates
import virtualize
import asyncio


class TCPServer(asyncio.Protocol):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.events = events.classes.Events()
        self.transport = None
        self.id = None

    def connection_made(self, transport):
        addr, port = transport.get_extra_info('peername')
        constants.glob.logger.info(f'New connection from ({addr})')
        self.transport = transport

    def data_received(self, data):
        # All comunication is made by events. The
        # events are generated and handled by Events
        # class defined at module "events"
        self.events.handle(data, self)

    def connection_lost(self, exc) -> None:
        constants.glob.logger.info(f"Connection with '{self.id}' was lost")
        constants.glob.logger.info(f'Reason: {exc if exc is not None else "Unknown"}')

        # Remove the outgoing client from the clients list
        server.updates.clients.pop(self.id)

        # In case of all clients disconnect from the server so
        # set the focus back to us and release all devices
        if len(server.updates.clients) == 1:
            constants.glob.logger.info("Setting the focus back to the server")
            keys = list(server.updates.clients.keys())
            server.updates.focus = keys[0]  # Focus to the server

            for name, device in server.updates.devices.items():
                constants.glob.logger.info(f"Releasing {name}")
                device.release()


def start_server(addr, port, handlers=None):

    if handlers is not None:
        if isinstance(handlers, list):
            for handler in handlers:
                # Start the threads that read device events
                device = virtualize.devices.PhisicalDevice(handler)
                server.updates.devices[device.info.get('name')] = device
                p = Thread(target=device.read, daemon=True)
                p.start()

    # Start the responsible for send all events in queue to the focus client
    sd = Thread(target=server.updates.send_events, daemon=True)
    sd.start()

    constants.glob.logger.info(f"Starting server at {addr}:{port}")

    # Genetating default main server identification
    loop = asyncio.get_event_loop()
    identification = functions.utils.generate_random_id()
    server.updates.clients[identification] = {'transport': None}

    # Each client connection will create a new server instance
    # and all instance will be identified with the same id.
    # that means the server (instance) will have the same
    # id if the client connected to it
    coro = loop.create_server(TCPServer, addr, port)
    waiter = loop.run_until_complete(coro)
    constants.glob.logger.info(f"Server started successful")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        constants.glob.logger.info('Server stop required')
        for name, device in server.updates.devices.items():
            constants.glob.logger.info(f"Releasing {name}")
            device.release()

    # Close the server
    waiter.close()
    loop.run_until_complete(waiter.wait_closed())
    loop.close()

    constants.glob.logger.info('Server stopped successful')


__all__ = [
    'TCPServer',
    'start_server'
]
