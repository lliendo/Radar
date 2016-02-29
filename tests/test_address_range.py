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


from unittest import TestCase,skip
from nose.tools import raises
from radar.misc import IPV4Address, IPV4AddressRange, IPV6Address, IPV6AddressRange, AddressError


class TestIPV4AddressRange(TestCase):
    def setUp(self):
        self.start_ip = '192.168.0.1'
        self.end_ip = '192.168.0.100'
        self.address_range = IPV4AddressRange('{:} - {:}'.format(self.start_ip, self.end_ip))

    def test_address_range_integer_mappings(self):
        self.assertEqual(self.address_range.start_ip.ip, self.start_ip)
        self.assertEqual(self.address_range.start_ip.n, 3232235521)
        self.assertEqual(self.address_range.end_ip.ip, self.end_ip)
        self.assertEqual(self.address_range.end_ip.n, 3232235620)

    def test_addresses_are_included_in_address_range(self):
        [self.assertTrue(IPV4Address('192.168.0.' + str(i)) in self.address_range) for i in range(1, 100 + 1)]

    def test_addresses_are_not_included_in_address_range(self):
        self.assertFalse(IPV4Address('192.168.0.0') in self.address_range)
        self.assertFalse(IPV4Address('192.168.0.101') in self.address_range)

    def test_address_ranges_are_equal(self):
        self.assertEqual(
            IPV4AddressRange('{:} - {:}'.format(self.start_ip, self.end_ip)),
            self.address_range
        )

    def test_address_ranges_are_not_equal(self):
        self.assertNotEqual(self.address_range, IPV4AddressRange('192.168.0.1 - 192.168.0.101'))

    def test_address_range_and_string_address_range_are_equal(self):
        self.assertEqual(self.address_range, '{:} - {:}'.format(self.start_ip, self.end_ip))

    def test_address_range_and_string_address_range_are_not_equal(self):
        self.assertNotEqual(self.address_range, '192.168.0.1 - 192.168.0.101')

    def test_address_range_to_dict(self):
        d = self.address_range.to_dict()
        self.assertEqual(d['start address'], self.start_ip)
        self.assertEqual(d['end address'], self.end_ip)

    @raises(AddressError)
    def test_address_range_raises_address_error_exception(self):
        IPV4AddressRange('*invalid hostname* - 01')

    @raises(AddressError)
    def test_address_range_raises_address_error_due_to_inverted_addresses(self):
        IPV4AddressRange('192.168.0.100 - 192.168.0.1')


class TestIPV6AddressRange(TestCase):
    def setUp(self):
        self.start_ip = '2001:0db8:85a3:0000:0000:8a2e:0370:7334'
        self.end_ip = '2001:0db8:85a3:0000:1000:0:0:0'
        self.address_range = IPV6AddressRange('{:} - {:}'.format(self.start_ip, self.end_ip))

    def test_address_range_integer_mappings(self):
        self.assertEqual(self.address_range.start_ip.ip, self.start_ip)
        self.assertEqual(self.address_range.start_ip.n, 42540766452641154071740215577757643572L)
        self.assertEqual(self.address_range.end_ip.ip, self.end_ip)
        self.assertEqual(self.address_range.end_ip.n, 42540766452641154072892985152133660672L)

    def test_addresses_are_included_in_address_range(self):
        left_padding = lambda group: hex(group).strip('0x').ljust(4, '0')
        [self.assertTrue(IPV6Address('2001:0db8:85a3:0000:0000:8a2e:0370:{:}'.format(left_padding(group)) in self.address_range) for group in range(0x7334, 0xffff))]

    def test_addresses_are_not_included_in_address_range(self):
        self.assertFalse(IPV6Address('2001:0db8:85a3:0000:0000:8a2e:0370:7333') in self.address_range)
        self.assertFalse(IPV6Address('2001:0db8:85a3:0000:1000:0:0:1') in self.address_range)

    def test_address_ranges_are_equal(self):
        self.assertEqual(
            self.address_range,
            IPV6AddressRange('{:} - {:}'.format(self.start_ip, self.end_ip)),
        )

    def test_address_ranges_are_not_equal(self):
        self.assertNotEqual(
            self.address_range,
            IPV6AddressRange('2001:0db8:85a3:0000:0000:8a2e:0370:7334 - 2001:0db8:85a3:0000:1000:0:0:1')
        )

    def test_address_range_and_string_address_range_are_equal(self):
        self.assertEqual(
            self.address_range,
            '{:} - {:}'.format(self.start_ip, self.end_ip)
        )

    def test_address_range_and_string_address_range_are_not_equal(self):
        self.assertNotEqual(
            self.address_range,
            '{:} - {:}'.format(self.start_ip, '2001:0db8:85a3:0000:1000:0:0:1')
        )

    def test_address_range_to_dict(self):
        d = self.address_range.to_dict()
        self.assertEqual(d['start address'], '2001:0db8:85a3:0000:0000:8a2e:0370:7334')
        self.assertEqual(d['end address'], '2001:0db8:85a3:0000:1000:0:0:0')

    @skip('Needs to be worked out')
    @raises(AddressError)
    def test_address_range_raises_address_error_exception(self):
        IPV6AddressRange('*invalid hostname* - 01')

    @raises(AddressError)
    def test_address_range_raises_address_error_due_to_inverted_addresses(self):
        IPV6AddressRange('{:} - {:}'.format(self.end_ip, self.start_ip))
