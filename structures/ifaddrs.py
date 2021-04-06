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


import ctypes


class In6Addr(ctypes.Structure):
    """
    Data structure to hold a single IPV6
    address is defined as follows
    """

    _fields_ = [
        ('s6_addr', ctypes.c_uint8 * 16),   # IPV6 address
    ]


class SockAddrIn6(ctypes.Structure):
    """
    This structure is used to pass address
    information to the socket function call
    that requires network address information
    """

    _fields_ = [
        ('sin6_len', ctypes.c_uint8),           # Length of this structure
        ('sin6_family', ctypes.c_uint8),        # AF_INET6
        ('sin6_port', ctypes.c_uint16),         # Transport layer port
        ('sin6_flowinfo', ctypes.c_uint32),     # IPV6 flow information
        ('sin6_addr', In6Addr),                 # IPV6 address
    ]


class InAddr(ctypes.Structure):
    """
    Data structure to hold a single IPV4
    address is defined as follows
    """

    _fields_ = [
        ('s_addr', ctypes.c_ulong),   # IPV4 Load with inet_aton()
    ]


class SockAddrIn(ctypes.Structure):
    """
    This structure is used to pass address
    information to the socket function call
    that requires network address information
    """

    _fields_ = [
        ('sin_family', ctypes.c_short),     # E.g AF_INET
        ('sin_port', ctypes.c_ushort),      # E.g htons(3490)
        ('sin_addr', InAddr),               # Struct in_addr above
        ('sin_zero', ctypes.c_char * 8),    # Zero this if you want to
    ]


class Sockaddr(ctypes.Structure):
    _fields_ = [
        ('sa_family', ctypes.c_short),      # Address family
        ('sa_data', ctypes.c_char * 14)     # Up to 14 bytes of direct address
    ]


class _IfaIfu(ctypes.Union):
    """ Union support for Ifaddrs class """
    _fields_ = [
        ('ifu_broaddr', ctypes.POINTER(Sockaddr)),  # Broadcast address of interface
        ('ifu_dstaddr', ctypes.POINTER(Sockaddr)),  # Point-to-point destination address
    ]


class Ifaddrs(ctypes.Structure):
    """
    Describes a network interface in the local system
    """
    pass


# Because the structure has a pointer
# to  it self we need to set the fields
# and anonymous fields outside of it
Ifaddrs._anonymous_ = ("ifa_ifu",)
Ifaddrs._fields_ = [
    ('ifa_next', ctypes.POINTER(Ifaddrs)),      # Next item in list
    ('ifa_name', ctypes.c_char_p),              # Name of interface
    ('ifa_flags', ctypes.c_uint),               # Flags from SIOCGFFLAGS
    ('ifa_addr', ctypes.POINTER(Sockaddr)),     # Address of interface
    ('ifa_netmask', ctypes.c_uint16),           # Netmask of interface
    ('ifa_ifu', _IfaIfu),
    ('ifa_data', ctypes.c_void_p),              # Address specific data
]
