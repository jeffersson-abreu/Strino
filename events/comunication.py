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

import virtualize.devices
import constants.glob
import client.updates
import server.updates
import pickle
import sys


def generate_announcement_response(result=True):
    """
    Generate an event of a given type and encode data
    :param result: An boolean value
    :return: Encoded and packed data
    """
    return pickle.dumps({
        "name": "ANNOUNCEMENT_RESPONSE",
        "data": {
            "status": int(result),
            "devices": [device.info for device in server.updates.devices.values()]
        }
    })


def digest_announcement_response(data, protocol):
    """
    Handle announcement response
    :param protocol: asyncio.Protocol instance
    :param data: binary data
    :return: None
    """
    if data.get("status"):
        constants.glob.logger.info("Sync was successful")
        devices = data.get('devices')
        constants.glob.logger.info(f"Devices to emulate: {len(devices)}")
        for device in devices:
            device_name = device.get('name')
            constants.glob.logger.info(f"Name: {device_name}")
            d = virtualize.devices.VirtualDevice(device)
            client.updates.devices[device_name] = d

        return None

    constants.glob.logger.error("Something in sync went wrong")
    protocol.transport.close()
    sys.exit(1)


def generate_announcement(protocol) -> bytes:
    """
    Generate an event of announcement type and encode data
    :return: Encoded and packed data
    """
    constants.glob.logger.info(f"Client id is '{protocol.id}'")

    return pickle.dumps({
        "name": "ANNOUNCEMENT",
        "data": {
            "id": protocol.id
        }
    })


def digest_announcement(data, protocol):
    """
    Handle all clients announcements
    :param data: event binary data
    :param protocol: asyncio.Protocol instance
    :return: None
    """
    try:
        protocol.id = data.get("id")

        constants.glob.logger.info(f"Client '{protocol.id}' trying to sync")

        # Save the client transport
        server.updates.clients[protocol.id] = dict(protocol=protocol)

        constants.glob.logger.info(f"Sync with '{protocol.id}' was successful")

        # Generate an event announcement response to the client
        response = generate_announcement_response(result=True)
        protocol.transport.write(response)

    except Exception as exc:
        # Generate an event announcement response to the client
        constants.glob.logger.critical("Something went wrong when digesting announcement")
        constants.glob.logger.critical(f"{exc}")
        response = generate_announcement_response(result=False)
        protocol.transport.write(response)
        sys.exit(1)

    return None


def generate_device_event(data, device_name):
    """
    Generate an device event type and encode data
    :return: Encoded and packed data
    """

    return pickle.dumps({
        "name": "DEVICE_EVENT",
        "data": {
            "device": device_name,
            "event": data
        }
    })


def digest_device_event(data, *args):
    client.updates.events.put(data)


__all__ = [
    'generate_announcement_response',
    'digest_announcement_response',

    'generate_device_event',
    'digest_device_event',

    'generate_announcement',
    'digest_announcement'
]
