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

from events.interfaces import Subject
import constants.globals
import constants.ecodes
import constants.input
import misc.utils
import structures
import ctypes
import fcntl
import sys
import os


# noinspection PyTypeChecker
class PhysicalDevice(Subject):
    """ Represents a physical device on the system """

    def __init__(self, handler, *args, **kwargs):
        Subject.__init__(self, *args, **kwargs)

        self.handler_path = handler
        self.handler = self._open(handler, os.O_RDWR)

        # Get device capabilities and device information
        self.capabilities = self._get_capabilities()
        self.info = self._get_info()
        self.info['events'] = self.capabilities

        # Keep a direct reference of our name
        self.name = self.info.get('name')

        self.is_grabbed = False

    @staticmethod
    def _open(file, flags):
        """ Open the handle file device """

        try:
            return os.open(file, flags)
        except Exception as error:
            constants.globals.logger.fatal("Error while opening device handler file")
            constants.globals.logger.fatal(error.__class__)
            sys.exit(127)

    def grab(self):
        """ Grab the device events visibility only for us """
        fcntl.ioctl(self.handler, constants.input.EVIOCGRAB, 1)
        self.is_grabbed = True

    def release(self):
        """ Revoke the access to device """
        fcntl.ioctl(self.handler, constants.input.EVIOCREVOKE, 0)
        self.is_grabbed = False

    def _get_info(self) -> dict:
        """
        Get Device information by a given file descriptor
        :return: Dict containing information about device handled by file
        """

        # Create the string buffer to make future ioctl calls
        name = ctypes.create_string_buffer(constants.input.MAX_NAME_SIZE)
        phys = ctypes.create_string_buffer(constants.input.MAX_NAME_SIZE)
        uniq = ctypes.create_string_buffer(constants.input.MAX_NAME_SIZE)

        prop = ctypes.create_string_buffer(constants.input.INPUT_PROP_CNT // 8)
        fcntl.ioctl(self.handler, constants.input.EVIOCGPROP(prop), prop)

        # Instantiate a struct input_id and and
        # clean (fill 0) memory of it's address
        iid = structures.input.InputId()
        ctypes.memset(ctypes.addressof(iid), 0, ctypes.sizeof(iid))

        # Get the file ID (type, vendor, product, version)
        fcntl.ioctl(self.handler, constants.input.EVIOCGID, iid)

        # Get the device name
        fcntl.ioctl(self.handler, constants.input.EVIOCGNAME, name)

        # Some devices do not have a physical topology associated with them
        fcntl.ioctl(self.handler, constants.input.EVIOCGPHYS, phys)

        try:
            # Some kernels have started reporting bluetooth controller MACs as phys.
            # This lets us get the real physical address. As with phys, it may be blank.
            fcntl.ioctl(self.handler, constants.input.EVIOCGUNIQ, uniq)
        except IOError:
            pass

        constants.globals.logger.info(f'Device name is "{name.value.decode()}"')

        return {
            'bustype': iid.bustype,
            'vendor': iid.vendor,
            'product': iid.product,
            'version': iid.version,
            'name': name.value.decode(),
            'phys': phys.value.decode(),
            'unique': uniq.value.decode(),
            'prop': prop.raw,
        }

    def _get_capabilities(self) -> dict:
        """
        Return all device events supported and keys related
        :return: Dict with device capabilities
        """

        constants.globals.logger.info(f'Trying to get device information')

        # Create char arrays to be filed in ioctl calls. This char's
        # array a will handle events and key codes related to event
        cd_bits = ctypes.create_string_buffer(constants.ecodes.KEY_MAX // 8 + 1)
        ev_bits = ctypes.create_string_buffer(constants.ecodes.EV_MAX // 8 + 1)

        capabilities = dict()

        # Fill 0 (clean) the memory space of ev_bits and call ioctl to get bits of
        # all event codes supported by device so we can build the device capabilities
        constants.globals.logger.info(f'Trying to get all events supported by the device')
        ctypes.memset(ctypes.addressof(ev_bits), 0, ctypes.sizeof(ev_bits))
        fcntl.ioctl(self.handler, constants.input.EVIOCGBIT(0, ev_bits), ev_bits)

        # Build a dictionary of the device's capabilities
        for ev_type in range(0, constants.ecodes.EV_MAX):
            if misc.utils.is_in_bitmask(ev_bits.raw, ev_type):

                try:
                    # Fill 0 (clean) the memory space of cd_bits and call ioctl to get all
                    # related event codes so we can build a list of codes handled by event
                    ctypes.memset(ctypes.addressof(cd_bits), 0, ctypes.sizeof(cd_bits))
                    fcntl.ioctl(self.handler, constants.input.EVIOCGBIT(ev_type, cd_bits), cd_bits)
                except OSError:
                    # Sometime an argument error occurs we
                    # just break the loop and keep going
                    break

                keyname = ev_type

                # if no error occurs so add the event key
                capabilities[keyname] = []

                for ev_code in range(0, constants.ecodes.KEY_MAX):
                    if misc.utils.is_in_bitmask(cd_bits.raw, ev_code):

                        if ev_type == constants.ecodes.event_types['EV_ABS']:
                            abs_info = structures.input.ABSInfo()

                            # At this point we just check if event type is EV_ABS so clean the memory
                            # space of the instance of ABSInfo defined above and call the kernel to
                            # give us info about ABS device capabilities
                            ctypes.memset(ctypes.addressof(abs_info), 0, ctypes.sizeof(abs_info))
                            fcntl.ioctl(self.handler, constants.input.EVIOCGABS(ev_code), abs_info)

                            _abs = {
                                'value': abs_info.value,
                                'minimum': abs_info.minimum,
                                'maximum': abs_info.maximum,
                                'fuzz': abs_info.fuzz,
                                'flat': abs_info.flat,
                                'resolution': abs_info.resolution
                            }

                            # Get the event list and save the ABS
                            # dict in a tuple numbered by event...
                            # Eg: (00, _abs)
                            event = capabilities[keyname]
                            event.append((ev_code, _abs))

                        else:
                            # Just append the event code to event type key
                            capabilities[keyname].append(ev_code)

        for key in capabilities.keys():
            for name, code in constants.ecodes.event_types.items():
                if key == code:
                    constants.globals.logger.info(f'Supported event: {name}')

        return capabilities

    def read(self):
        """
        This is the heart of any communication between
        physic and virtual device that is being simulated
        at the other point. Here we just read the events
        and notify all observers attached to us about the
        event
        """

        # Buffer size to read at time
        buffer_length = ctypes.sizeof(structures.input.InputEvent)
        event_list: [structures.input.InputEvent] = []

        while True:
            try:
                # We need a blocking read as well to not
                # spend machine power in a reading loop
                buffer = os.read(self.handler, buffer_length)
            except OSError:
                # When releasing device from grab the read
                # operation throws an OSError exception, so
                # just reopen the handler and keep going
                self.handler = self._open(self.handler_path, os.O_RDWR)
                continue

            # We instantiate an structure input_event and fill with
            # buffer to check if event is different of EV_SYNC.
            ie = structures.input.InputEvent.from_buffer_copy(buffer)

            if ie.type:

                # Event is not EV_SYNC so append
                # to list and continue the loop
                event_list.append(buffer)
                continue

            # At this point the event is EV_SYNC then
            # we notify all observers attached to us
            self.notify({
                'data': event_list[:],
                'name': self.name
            })

            # Should I comment? ;)
            event_list.clear()
