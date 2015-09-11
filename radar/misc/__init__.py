# -*- coding: utf-8 -*-

"""
This file is part of Radar.

Radar is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Radar is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
Lesser GNU General Public License for more details.

You should have received a copy of the Lesser GNU General Public License
along with Radar. If not, see <http://www.gnu.org/licenses/>.

Copyright 2015 Lucas Liendo.
"""


from re import compile as compile_re
from socket import gethostbyname
from abc import ABCMeta


class AddressError(Exception):
    pass


class Address(object):
    def __init__(self, address):
        self.ip = self._validate(address.strip())
        self.n = self._to_int()

    def to_dict(self):
        return {'address': self.ip}

    def _resolve_hostname(self, hostname):
        try:
            return gethostbyname(hostname)
        except Exception:
            raise AddressError('Error - Invalid hostname or address : \'{:}\'.'.format(hostname))

    def _validate(self, address):
        regexp = compile_re('(\d{1,3}\.){3}\d{1,3}')

        try:
            if not regexp.match(address) or not all([int(octet) <= 255 for octet in address.split('.', 3)]):
                return self._resolve_hostname(address)
        except ValueError:
            raise AddressError('Error - Invalid host name or address : \'{:}\'.'.format(address))

        return address

    def _to_int(self):
        octets = [int(octet) for octet in self.ip.split('.', 3)]
        return sum([byte * pow(256, n) for n, byte in enumerate(reversed(octets))])

    def __eq__(self, other_address):
        if type(other_address) == Address:
            return self.n == other_address.n

        return self.n == Address(other_address).n

    def __hash__(self):
        return hash(self.ip) ^ hash(self.n)

    def __contains__(self, address):
        return self.__eq__(address)


class AddressRange(object):
    def __init__(self, address_range):
        self.start_ip, self.end_ip = self._validate(address_range.strip())

    def to_dict(self):
        return {
            'start address': self.start_ip.ip,
            'end address': self.end_ip.ip,
        }

    def _validate(self, address_range):
        start_ip, end_ip = [Address(a) for a in address_range.split('-', 1)]

        if start_ip.n >= end_ip.n:
            raise AddressError('Error - Start ip address is lower (or equal) than end ip address : \'{:} - {:}\'.'.format(
                start_ip.ip, end_ip.ip))

        return start_ip, end_ip

    def __eq__(self, other_address_range):
        if type(other_address_range) == AddressRange:
            return self.start_ip == other_address_range.start_ip and \
                self.end_ip == other_address_range.end_ip

        return self.start_ip.n == AddressRange(other_address_range).start_ip.n and \
            self.end_ip.n == AddressRange(other_address_range).end_ip.n

    def __hash__(self):
        return self.start_ip.__hash__() ^ self.end_ip.__hash__()

    def __contains__(self, address):
        if type(address) == Address:
            return self.start_ip.n <= address.n <= self.end_ip.n

        return self.start_ip.n <= Address(address).n <= self.end_ip.n


class SequentialIdGenerator(object):

    _shared_state = {'id': 1}

    def __init__(self):
        self.__dict__ = self._shared_state

    def generate(self):
        id = self._shared_state['id']
        self._shared_state['id'] += 1
        return id


# Mixin used heavily on server side. It provides a unique id and a silly
# enable/disable behaviour.
class Switchable(object):

    __metaclass__ = ABCMeta

    def __init__(self, id=None, enabled=True):
        self.id = id or SequentialIdGenerator().generate()
        self.enabled = enabled

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def to_dict(self, attrs):
        return {a: getattr(self, a) for a in attrs}
