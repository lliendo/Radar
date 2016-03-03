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


from re import compile as compile_regexp, IGNORECASE
from socket import gethostbyname, getaddrinfo, gaierror as GAIError
from abc import ABCMeta, abstractmethod


class AddressError(Exception):
    pass


class Address(object):

    __metaclass__ = ABCMeta

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

    @abstractmethod
    def _validate(self, address):
        pass

    def _to_int(self, n_groups=4, bits=8, base=10):
        groups = [int(group, base=base) for group in self.ip.split(self.SEPARATOR, n_groups - 1)]
        return sum([group * pow(pow(2, bits), n) for n, group in enumerate(reversed(groups))])

    @abstractmethod
    def __eq__(self, other_address):
        pass

    def __hash__(self):
        return hash(self.ip) ^ hash(self.n)

    def __contains__(self, address):
        return self.__eq__(address)

    @staticmethod
    def detect_version(address):
        try:
            protocol_version, _, _, _, _ = getaddrinfo(address, 0).pop()
            return protocol_version
        except GAIError:
            raise AddressError('Error - Couldn\'t detect ip address version for address : \'{:}\'.'.format(address))


class IPV4Address(Address):

    SEPARATOR = '.'

    def _invalid_octets(self, address):
        return not all([int(octet) <= 255 for octet in address.split(self.SEPARATOR, 3)])

    def _validate(self, address):
        ipv4_pattern = compile_regexp(r'(\d{1,3}\.){3}\d{1,3}')

        try:
            if not ipv4_pattern.match(address) or self._invalid_octets(address):
                return self._resolve_hostname(address)
        except ValueError:
            raise AddressError('Error - Invalid host name or ipv4 address : \'{:}\'.'.format(address))

        return address

    def __eq__(self, other_address):
        if type(other_address) == IPV4Address:
            return self.n == other_address.n

        return self.n == IPV4Address(other_address).n


class IPV6Address(Address):

    SEPARATOR = ':'
    GROUPS = 8

    def _compact_address(self, address):
        return len([group for group in address.split(self.SEPARATOR) if group != '']) != self.GROUPS

    def _fill_address(self, address):
        filled_address = address.split(self.SEPARATOR)

        # If a '::' is present at the beginning or at the end of the address
        # then after splitting, a double '' appears in filled_address.
        if filled_address.count('') > 1:
            filled_address.pop(filled_address.index(''))

        i = filled_address.index('')
        filled_address.pop(i)
        [filled_address.insert(i, '0') for n in range(0, self.GROUPS - len(filled_address))]

        return self.SEPARATOR.join(filled_address)

    def _validate(self, address):
        invalid_ipv6_pattern = compile_regexp(r'(\:\:)+')

        if len(invalid_ipv6_pattern.findall(address)) > 1:
            raise AddressError('Error - Invalid host name or ipv6 address : \'{:}\'.'.format(address))

        if address != '::' and self._compact_address(address):
            address = self._fill_address(address)
        elif address == '::':
            address = '0:0:0:0:0:0:0:0'

        ipv6_pattern = compile_regexp(r'([0-9a-f]{1,4}\:){7}[0-9a-f]{1,4}', IGNORECASE)

        try:
            if not ipv6_pattern.match(address):
                return self._resolve_hostname(address)
        except ValueError:
            raise AddressError('Error - Invalid host name or ipv6 address : \'{:}\'.'.format(address))

        return address

    def _to_int(self):
        return super(IPV6Address, self)._to_int(n_groups=self.GROUPS, bits=16, base=16)

    def __eq__(self, other_address):
        if type(other_address) == IPV6Address:
            return self.n == other_address.n

        return self.n == IPV6Address(other_address).n


class AddressRange(object):

    __metaclass__ = ABCMeta

    SEPARATOR = '-'
    AddressClass = None

    def __init__(self, address_range):
        self.start_ip, self.end_ip = self._validate(address_range.strip())

    def to_dict(self):
        return {
            'start address': self.start_ip.ip,
            'end address': self.end_ip.ip,
        }

    def _validate(self, address_range):
        start_ip, end_ip = [self.AddressClass(a) for a in address_range.split(self.SEPARATOR, 1)]

        if start_ip.n >= end_ip.n:
            raise AddressError('Error - Start ip address is lower (or equal) than end ip address : \'{:} - {:}\'.'.format(
                start_ip.ip, end_ip.ip))

        return start_ip, end_ip

    def __hash__(self):
        return self.start_ip.__hash__() ^ self.end_ip.__hash__()

    def __contains__(self, address):
        if type(address) == self.AddressClass:
            return self.start_ip.n <= address.n <= self.end_ip.n

        return self.start_ip.n <= self.AddressClass(address).n <= self.end_ip.n


class IPV4AddressRange(AddressRange):

    AddressClass = IPV4Address

    def __eq__(self, other_address_range):
        if type(other_address_range) == IPV4AddressRange:
            return self.start_ip == other_address_range.start_ip and \
                self.end_ip == other_address_range.end_ip

        return self.start_ip.n == IPV4AddressRange(other_address_range).start_ip.n and \
            self.end_ip.n == IPV4AddressRange(other_address_range).end_ip.n


class IPV6AddressRange(AddressRange):

    AddressClass = IPV6Address

    def __eq__(self, other_address_range):
        if type(other_address_range) == IPV6AddressRange:
            return self.start_ip == other_address_range.start_ip and \
                self.end_ip == other_address_range.end_ip

        return self.start_ip.n == IPV6AddressRange(other_address_range).start_ip.n and \
            self.end_ip.n == IPV6AddressRange(other_address_range).end_ip.n


class SequentialIdGenerator(object):

    _shared_state = {'id': 1}

    def __init__(self):
        self.__dict__ = self._shared_state

    def generate(self):
        _id = self._shared_state['id']
        self._shared_state['id'] += 1
        return _id


# Mixin used heavily on server side. It provides a unique id and a silly
# enable/disable behaviour.
class Switchable(object):

    __metaclass__ = ABCMeta

    def __init__(self, id=None, enabled=True):
        self.id = id or SequentialIdGenerator().generate()
        self.enabled = enabled

    # We enable/disable ourselves only if our id is present in the ids list or
    # if the list does not exist.
    def _switch(self, ids, to_value=True):
        switched = False

        try:
            if self.id in ids:
                self.enabled = to_value
                switched = True
        except TypeError:
            self.enabled = to_value
            switched = True

        return switched

    def enable(self, ids=None):
        return self._switch(ids)

    def disable(self, ids=None):
        return self._switch(ids, to_value=False)

    def to_dict(self, attrs):
        return {a: getattr(self, a) for a in attrs}
