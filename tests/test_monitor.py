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
from radar.misc import Address, AddressRange
from radar.check import Check, CheckGroup
from radar.contact import Contact, ContactGroup
from radar.monitor import Monitor, MonitorError
from radar.network.client import Client
from radar.protocol import Message


class DummyClient(Client):
    def on_receive(self):
        pass

    def send_message(self, message_type, message, message_options=Message.OPTIONS['NONE']):
        pass


class TestMonitor(TestCase):
    def setUp(self):
        self.dummy_client = DummyClient(address='192.168.0.1', port=10000)
        self.checks = [Check(name='Load average', path='load_average')]
        self.monitor = Monitor(
            addresses=[AddressRange('192.168.0.1 - 192.168.0.100')],
            checks=self.checks,
            contacts=[Contact(name='name', email='name@contact.org')]
        )

    def test_monitor_does_not_get_duplicates(self):
        address = Address('192.168.0.1')
        address_range = AddressRange('192.168.0.1 - 192.168.0.100')
        check = Check(name='Load average', path='load_average')
        check_group = CheckGroup(name='check group', checks=[check])
        contact = Contact(name='name', email='contact@contact.com')
        contact_group = ContactGroup(name='contact group', contacts=[contact])
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
        self.assertTrue(self.monitor.matches(self.dummy_client))

    def test_monitor_does_not_match_client_address(self):
        self.assertFalse(self.monitor.matches(DummyClient(address='192.168.0.101', port=10000)))

    def test_monitor_does_not_match_client_because_is_already_connected(self):
        self.monitor.add_client(self.dummy_client)
        self.assertFalse(self.monitor.matches(self.dummy_client))

    def test_add_client_succeeds(self):
        self.assertTrue(self.monitor.add_client(self.dummy_client))

    def test_add_client_fails(self):
        self.assertFalse(self.monitor.add_client(DummyClient(address='192.168.0.101', port=10000)))

    def test_remove_client_succeeds(self):
        self.monitor.add_client(self.dummy_client)
        self.assertEqual(len(self.monitor.active_clients), 1)
        self.assertTrue(self.monitor.remove_client(self.dummy_client))

    def test_remove_client_fails(self):
        self.assertFalse(self.monitor.remove_client(self.dummy_client))

    def test_monitors_are_equal(self):
        another_monitor = Monitor(
            addresses=[AddressRange('192.168.0.1 - 192.168.0.100')],
            checks=[Check(name='Load average', path='load_average')],
            contacts=[Contact(name='name', email='name@contact.org')]
        )
        self.assertEqual(self.monitor, another_monitor)

    def test_monitors_are_not_equal(self):
        another_monitor = Monitor(
            addresses=[AddressRange('192.168.0.0 - 192.168.0.100')],
            checks=[Check(name='Load average', path='load_average')]
        )
        self.assertNotEqual(self.monitor, another_monitor)

    def test_monitors_set(self):
        self.assertTrue(len(set([self.monitor, self.monitor])), 1)

    def test_monitor_updates_check_status(self):
        check_status = {'status': Check.STATUS['ERROR'], 'id': self.checks[0].id}
        self.monitor.add_client(self.dummy_client)
        updated_checks = self.monitor.update_checks(self.dummy_client, [check_status])
        self.assertEqual(list(self.monitor.active_clients[0]['checks']).pop().current_status, Check.STATUS['ERROR'])
        self.assertNotEqual(updated_checks, {})

    def test_monitor_does_not_update_check_status(self):
        check_status = {'status': Check.STATUS['ERROR'], 'id': self.checks[0].id + 1}
        self.monitor.add_client(self.dummy_client)
        updated_checks = self.monitor.update_checks(self.dummy_client, [check_status])
        self.assertEqual(list(self.monitor.active_clients[0]['checks']).pop().current_status, Check.STATUS['UNKNOWN'])
        self.assertEqual(updated_checks, {})

    def test_monitor_to_dict(self):
        self.monitor.add_client(self.dummy_client)
        d = self.monitor.to_dict()
        self.assertTrue('clients' in d)
        self.assertTrue('id' in d)
        self.assertTrue('enabled' in d)
        self.assertTrue('name' in d)
        self.assertEqual(type(d['clients']), list)

    def test_monitor_polls_clients(self):
        self.monitor.add_client(self.dummy_client)
        message = self.monitor.poll(Message.TYPE['CHECK'])
        [self.assertTrue(('path' in c) and ('id' in c)) for c in message]
        self.assertEqual(type(message), list)
