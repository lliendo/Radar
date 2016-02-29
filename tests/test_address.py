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
from socket import AF_INET, AF_INET6
from nose.tools import raises
from radar.misc import AddressError, Address, IPV4Address, IPV6Address


class TestIPV4Address(TestCase):
    def test_address_contains_itself(self):
        address = IPV4Address('0.0.0.0')
        self.assertTrue(address in IPV4Address('0.0.0.0'))

    def test_address_does_not_contain_itself(self):
        self.assertFalse(IPV4Address('0.0.0.0') in IPV4Address('0.0.0.1'))

    def test_addresses_are_equal(self):
        self.assertEqual(IPV4Address('0.0.0.0'), IPV4Address('0.0.0.0'))

    def test_addresses_are_not_equal(self):
        self.assertNotEqual(IPV4Address('0.0.0.0'), IPV4Address('0.0.0.1'))

    def test_address_to_dict(self):
        self.assertTrue(IPV4Address('0.0.0.0').to_dict()['address'], '0.0.0.0')

    def test_address_and_string_address_are_equal(self):
        self.assertEqual(IPV4Address('0.0.0.0'), '0.0.0.0')

    def test_address_and_string_address_are_not_equal(self):
        self.assertNotEqual(IPV4Address('0.0.0.0'), '0.0.0.1')

    def test_detect_address(self):
        self.assertEqual(Address.detect_version('0.0.0.0'), AF_INET)

    @raises(AddressError)
    def test_detect_address_raises_address_error(self):
        Address.detect_version('invalid address')

    @raises(AddressError)
    def test_address_raises_address_exception(self):
        IPV4Address('invalid hostname*')


class TestIPV6Address(TestCase):
    def test_address_contains_itself(self):
        address = IPV6Address('::')
        self.assertTrue(address in IPV6Address('::'))

    def test_full_address(self):
        self.assertEqual(IPV6Address('2001:0db8:85a3:0000:0000:8a2e:0370:7334').n, 42540766452641154071740215577757643572L)

    def test_shortened_address(self):
        self.assertEqual(IPV6Address('2001:db8:85a3:0:0:8a2e:370:7334').n, 42540766452641154071740215577757643572L)

    def test_compact_address(self):
        self.assertEqual(IPV6Address('2001:db8:85a3::8a2e:370:7334').n, 42540766452641154071740215577757643572L)

    def test_compact_address_2(self):
        self.assertEqual(IPV6Address('::ffff:c000:0280').n, 281473902969472)

    def test_compact_address_3(self):
        self.assertEqual(IPV6Address('::1').n, 1)

    def test_detect_address(self):
        self.assertEqual(Address.detect_version('::'), AF_INET6)
