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


from unittest import TestCase
from nose.tools import raises
from ..misc import Address, AddressError, AddressRange


class TestAddressRange(TestCase):
    def test_address_range_integer_mappings(self):
        address_range = AddressRange('192.168.0.1 - 192.168.0.100')
        self.assertEqual(address_range.start_ip.ip, '192.168.0.1')
        self.assertEqual(address_range.start_ip.n, 3232235521)
        self.assertEqual(address_range.end_ip.ip, '192.168.0.100')
        self.assertEqual(address_range.end_ip.n, 3232235620)

    def test_addresses_are_included_in_address_range(self):
        address_range = AddressRange('192.168.0.1 - 192.168.0.100')
        [self.assertTrue(Address('192.168.0.' + str(i)) in address_range) for i in range(1, 100 + 1)]

    def test_addresses_are_not_included_in_address_range(self):
        address_range = AddressRange('192.168.0.1 - 192.168.0.100')
        self.assertFalse(Address('192.168.0.0') in address_range)
        self.assertFalse(Address('192.168.0.101') in address_range)

    def test_address_ranges_are_equal(self):
        self.assertEqual(AddressRange('192.168.0.1 - 192.168.0.100'), AddressRange('192.168.0.1 - 192.168.0.100'))

    def test_address_ranges_are_not_equal(self):
        self.assertNotEqual(AddressRange('192.168.0.1 - 192.168.0.100'), AddressRange('192.168.0.1 - 192.168.0.101'))

    def test_address_range_and_string_address_range_are_equal(self):
        self.assertEqual(AddressRange('192.168.0.1 - 192.168.0.100'), '192.168.0.1 - 192.168.0.100')

    def test_address_range_and_string_address_range_are_not_equal(self):
        self.assertNotEqual(AddressRange('192.168.0.1 - 192.168.0.100'), '192.168.0.1 - 192.168.0.101')

    def test_address_range_to_dict(self):
        d = AddressRange('192.168.0.1 - 192.168.0.100').to_dict()
        self.assertEqual(d['start address'], '192.168.0.1')
        self.assertEqual(d['end address'], '192.168.0.100')

    @raises(AddressError)
    def test_address_range_raises_address_error_exception(self):
        Address('*invalid hostname* - 01')

    @raises(AddressError)
    def test_address_range_raises_address_error_due_to_inverted_addresses(self):
        AddressRange('192.168.0.100 - 192.168.0.1')
