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


from unittest import TestCase, skip
from nose.tools import raises
from mock import Mock, MagicMock, patch
from json import dumps as serialize_json
from radar.protocol import RadarConsoleMessage
from radar.logger import RadarLogger
from radar.console import RadarServerConsole, RadarServerConsoleError
from radar.config.server import ServerConfig


class TestRadarServerConsole(TestCase):
    def setUp(self):
        RadarLogger._shared_state['logger'] = Mock()
        allowed_addresses = ['127.0.0.1', '10.0.0.1 - 10.0.0.10']
        self.platform_setup = Mock()
        self.platform_setup.config = ServerConfig.DEFAULT_CONFIG
        self.platform_setup.config['console']['address'] = '127.0.0.1'
        self.platform_setup.config['console']['allowed hosts'] = allowed_addresses

    # We get rid of the _listen & _get_network_monitor calls.
    def _get_patched_radar_server_console(self):
        with patch.object(RadarServerConsole, '_listen', return_value=None):
            with patch.object(RadarServerConsole, '_get_network_monitor', return_value=None):
                client_manager = MagicMock()
                return RadarServerConsole(client_manager, self.platform_setup)

    def _get_mocked_radar_client(self, side_effect):
        client = MagicMock()
        client.receive_message = MagicMock(side_effect=side_effect)
        client.send_message = MagicMock()

        return client

    @raises(RadarServerConsoleError)
    def test_process_command_fails_due_syntax_error(self):
        radar_server_console = self._get_patched_radar_server_console()
        radar_server_console._process_command({'action': '{'})

    @raises(RadarServerConsoleError)
    def test_process_command_fails_due_missing_action_keyword(self):
        radar_server_console = self._get_patched_radar_server_console()
        radar_server_console._process_command({})

    # We make sure that upon an action the respective client_manager action is
    # also triggered.
    def _test_on_receive_action_is_called(self, action, ids=[]):
        radar_server_console = self._get_patched_radar_server_console()
        setattr(radar_server_console._client_manager, action, MagicMock(side_effect=[ids]))
        serialized_action = serialize_json({
            'action': '{:}({:})'.format(action, ','.join([str(id) for id in ids]))
        })
        radar_client = self._get_mocked_radar_client([
            (RadarConsoleMessage.TYPE['QUERY'], serialized_action),
        ])
        radar_server_console.on_receive(radar_client)
        getattr(radar_server_console._client_manager, action).assert_called_with(ids=(ids,))

    def test_on_receive_enable_action_is_called(self):
        self._test_on_receive_action_is_called('enable')
        self._test_on_receive_action_is_called('enable', ids=[1, 2, 3])

    def test_on_receive_disable_action_is_called(self):
        self._test_on_receive_action_is_called('disable')
        self._test_on_receive_action_is_called('disable', ids=[1, 2, 3])

    def test_on_receive_list_action_is_called(self):
        self._test_on_receive_action_is_called('list')
        self._test_on_receive_action_is_called('list', ids=[1, 2, 3])

    @skip('The test action not yet implemented.')
    def test_on_receive_test_action_is_called(self):
        pass
