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
from mock import Mock, ANY
from radar.misc import IPV4Address, IPV4AddressRange
from radar.check import Check
from radar.monitor import Monitor
from radar.client_manager import ClientManager
from radar.client import RadarClientLite
from radar.logger import RadarLogger
from radar.protocol import Message


class TestClientManager(TestCase):
    def setUp(self):
        RadarLogger._shared_state['logger'] = Mock()
        self.check = Check(name='dummy', path='dummy_check.py')
        addresses = [
            IPV4AddressRange('10.0.0.1 - 10.0.0.10'),
            IPV4AddressRange('10.0.0.20 - 10.0.0.30'),
            IPV4Address('10.0.0.40'),
        ]
        self.monitors = [Monitor(addresses=[a], checks=[self.check]) for a in addresses]
        self.client_manager = ClientManager(self.monitors)

    def test_client_manager_matches_any_monitor(self):
        clients = [
            RadarClientLite('10.0.0.5', 10000),
            RadarClientLite('10.0.0.25', 10000),
            RadarClientLite('10.0.0.40', 10000),
        ]
        self.assertTrue(all([self.client_manager.matches_any_monitor(c) for c in clients]))

    def test_client_manager_does_not_match_any_monitor(self):
        clients = [
            RadarClientLite('10.0.0.0', 10000),
            RadarClientLite('10.0.0.15', 10000),
        ]
        matches_result = [self.client_manager.matches_any_monitor(c) for c in clients]
        self.assertTrue(all(matches_result) or not any(matches_result))

    def test_client_manager_process_message_fails(self):
        self.client_manager.process_message(
            RadarClientLite('10.0.0.1', 10000),
            max(Message.TYPE.values()) + 1,
            ''
        )
        RadarLogger._shared_state['logger'].info.assert_called_with(ANY)

    def test_client_manager_updates_check(self):
        client = RadarClientLite('10.0.0.1', 10000)
        self.client_manager.register(client)
        active_client = list(self.monitors[0].active_clients).pop()
        check = list(active_client['checks'])[0]

        # We verify initial status and then perform 2 check updates.
        self.assertEqual(check.current_status, Check.STATUS['UNKNOWN'])
        self.assertEqual(check.previous_status, Check.STATUS['UNKNOWN'])

        self.client_manager._update_checks(client, [{'id': self.check.id, 'status': Check.STATUS['OK']}])
        self.assertEqual(check.current_status, Check.STATUS['OK'])

        self.client_manager._update_checks(client, [{'id': self.check.id, 'status': Check.STATUS['WARNING']}])
        self.assertEqual(check.current_status, Check.STATUS['WARNING'])
        self.assertEqual(check.previous_status, Check.STATUS['OK'])

    def test_client_manager_does_not_update_check_due_to_wrong_id(self):
        client = RadarClientLite('10.0.0.1', 10000)
        self.client_manager.register(client)
        active_client = list(self.monitors[0].active_clients).pop()
        check = list(active_client['checks'])[0]

        self.client_manager._update_checks(client, [{'id': self.check.id + 1, 'status': Check.STATUS['OK']}])
        self.assertNotEqual(check.current_status, Check.STATUS['OK'])

    def test_client_manager_does_not_update_check_due_to_disabled_monitor(self):
        client = RadarClientLite('10.0.0.1', 10000)
        self.client_manager.register(client)
        active_client = list(self.monitors[0].active_clients).pop()
        check = list(active_client['checks'])[0]
        self.monitors[0].disable()

        self.client_manager._update_checks(client, [{'id': self.check.id, 'status': Check.STATUS['OK']}])
        self.assertNotEqual(check.current_status, Check.STATUS['OK'])
