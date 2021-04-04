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
from threading import Thread
import constants.globals
import server.observers
from typing import List
import devices.physical
import misc.utils
import asyncio


class TCPServer(asyncio.Protocol):

    def __init__(self, focus: server.observers.FocusEvents, devinfo: List, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Generate an unique identification to the connection
        self.identification = misc.utils.generate_random_id()
        self.events = networking.communication.Events()
        self.devinfo = devinfo
        self.transport = None
        self.focus = focus

    def connection_made(self, transport):
        addr, _ = transport.get_extra_info('peername')
        constants.globals.logger.info(f'New connection from {addr}')
        constants.globals.logger.info(f'Connection identified as {self.identification}')
        self.focus.register(self.identification, transport)
        event = self.events.generate("CREATE_DEVICE", self.devinfo)
        self.transport = transport
        transport.write(event)

    def data_received(self, data):
        # All communication is made by events. The
        # events are generated and handled by Events
        # class defined at module "networking"
        self.events.handle(data)

    def connection_lost(self, exc) -> None:
        constants.globals.logger.info(f"Connection with '{self.identification}' was lost")
        constants.globals.logger.info(f'Reason: {exc if exc is not None else "Unknown reason"}')

        # Remove the outgoing client from the clients list
        self.focus.forget(self.identification)
        self.transport.close()


def start_server(addr, port, handlers: List):

    # Instantiate observers
    shortcut = server.observers.ShortcutListener()
    sender = server.observers.EventSender()
    focus = server.observers.FocusEvents()
    grabber = server.observers.Grabber()

    # This is the most important thing using
    # observers, the way we attach then each
    # others resume all the program fluxing
    focus.attach(grabber)
    focus.attach(sender)

    # TODO: Remove in a future release when focus
    #       gonna change based on mouse pointer
    shortcut.attach(focus)

    devices_info = list()

    for handler in handlers:
        # Start the threads that read device events
        device = devices.physical.PhysicalDevice(handler)

        # Fill devices info
        devices_info.append(device.info)

        # Once again we attach the observers to
        # devices. The observers can be attached
        # to each other and also to classes that
        # inherits from "Subject" interface
        device.attach(shortcut)
        device.attach(sender)

        # Add the device to grabber list
        grabber.add_device(device)

        # Start device reading events as daemon
        p = Thread(target=device.read, daemon=True)
        p.start()

    # Generating default main loop
    loop = asyncio.get_event_loop()

    # Each client connection will create a new server instance
    constants.globals.logger.info(f"Starting server at {addr}:{port}")
    coro = loop.create_server(lambda: TCPServer(focus, devices_info), addr, port)
    waiter = loop.run_until_complete(coro)
    constants.globals.logger.info(f"Server started successful")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        constants.globals.logger.info('Server stop required')
        grabber.release_all()

        # Close the server
        waiter.close()
        loop.run_until_complete(waiter.wait_closed())
        loop.close()

        constants.globals.logger.info('Server stopped successful')


__all__ = [
    'TCPServer',
    'start_server'
]
