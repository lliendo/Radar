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
from ..misc import Address, AddressRange
from ..check import Check, CheckGroup
from ..contact import Contact, ContactGroup
from ..monitor import Monitor, MonitorError
from ..network.client import Client


class DummyClient(Client):
    def on_receive(self):
        pass


class TestMonitor(TestCase):
    def test_monitor_does_not_get_duplicates(self):
        address = Address('192.168.0.1')
        address_range = AddressRange('192.168.0.1 - 192.168.0.100')
        check = Check(name='Load average', path='load_average')
        check_group = CheckGroup(checks=[check])
        contact = Contact(name='name', email='contact@contact.com')
        contact_group = ContactGroup(contacts=[contact])
        monitor = Monitor(
            addresses=[address, address, address_range, address_range],
            checks=[check, check, check_group, check_group],
            contacts=[contact, contact, contact_group, contact_group]
        )
        self.assertEqual(len(monitor.addresses), 2)
        self.assertEqual(len(monitor.checks), 2)
        self.assertEqual(len(monitor.contacts), 2)

    @raises(MonitorError)
    def test_monitor_raises_exception_due_to_missing_addresses(self):
        Monitor()

    @raises(MonitorError)
    def test_monitor_raises_exception_due_to_missing_checks(self):
        Monitor(addresses=[Address('192.168.0.1')])

    def test_monitor_matches_client(self):
        monitor = Monitor(addresses=[AddressRange('192.168.0.1 - 192.168.0.100')], checks=[Check(name='Load average', path='load_average')])
        self.assertTrue(monitor.matches(DummyClient(address='192.168.0.1', port=10000)))

    def test_monitor_does_not_match_client_address(self):
        monitor = Monitor(addresses=[AddressRange('192.168.0.1 - 192.168.0.100')], checks=[Check(name='Load average', path='load_average')])
        self.assertFalse(monitor.matches(DummyClient(address='192.168.0.101', port=10000)))

    def test_monitor_does_not_match_client_because_is_already_connected(self):
        dummy_client = DummyClient(address='192.168.0.1', port=10000)
        monitor = Monitor(addresses=[AddressRange('192.168.0.1 - 192.168.0.100')], checks=[Check(name='Load average', path='load_average')])
        monitor.add_client(dummy_client)
        self.assertFalse(monitor.matches(dummy_client))

    def test_add_client_succeeds(self):
        monitor = Monitor(addresses=[AddressRange('192.168.0.1 - 192.168.0.100')], checks=[Check(name='Load average', path='load_average')])
        self.assertTrue(monitor.add_client(DummyClient(address='192.168.0.1', port=10000)))

    def test_add_client_fails(self):
        monitor = Monitor(addresses=[AddressRange('192.168.0.1 - 192.168.0.100')], checks=[Check(name='Load average', path='load_average')])
        self.assertFalse(monitor.add_client(DummyClient(address='192.168.0.101', port=10000)))

    def test_remove_client(self):
        dummy_client = DummyClient(address='192.168.0.1', port=10000)
        monitor = Monitor(addresses=[AddressRange('192.168.0.1 - 192.168.0.100')], checks=[Check(name='Load average', path='load_average')])
        monitor.add_client(dummy_client)
        self.assertEqual(len(monitor.active_clients), 1)
        self.assertTrue(monitor.remove_client(dummy_client))

    def test_monitors_set(self):
        monitor = Monitor(addresses=[AddressRange('192.168.0.1 - 192.168.0.100')], checks=[Check(name='Load average', path='load_average')])
        duplicated_monitors = [monitor, monitor]
        self.assertTrue(len(set(duplicated_monitors)), 1)
