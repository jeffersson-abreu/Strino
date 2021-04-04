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

import devices.virtual
import pickle


def generate_create_device(info) -> bytes:
    """
    Generate a "create device" event
    :return: Encoded and packed data
    """

    return pickle.dumps({
        "name": "CREATE_DEVICE",
        "data": info
    })


def digest_create_device(info, protocol):
    """
    Handle all clients announcements
    :param protocol: asyncio.Protocol instance
    :param info: event information
    :return: None
    """
    virtual_devices = {}
    for devinfo in info:
        device = devices.virtual.VirtualDevice(devinfo)
        virtual_devices[device.name] = device

    setattr(protocol, 'devices', virtual_devices)
    return None


def generate_device_event(data):
    """
    Generate an device event type and encode data
    :return: Encoded and packed data
    """

    return pickle.dumps({
        "name": "DEVICE_EVENT",
        "data": data
    })


def digest_device_event(data, protocol):
    """
     Digest device events received from server
    :param data: Dictionary data
    :param protocol: asyncio.Protocol instance
    :return: None
    """
    name = data.get('name')
    device = protocol.devices.get(name)
    if device is not None:
        device.emit(data.get('data'))


__all__ = [
    'generate_device_event',
    'digest_device_event',

    'generate_create_device',
    'generate_create_device',
    'generate_create_device',
    'generate_create_device',
    'digest_create_device'
]
