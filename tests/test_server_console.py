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
from mock import Mock, MagicMock, patch, ANY
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

    @raises(RadarServerConsoleError)
    def test_process_command_fails_due_syntax_error(self):
        radar_server_console = self._get_patched_radar_server_console()
        radar_server_console._process_command({'action': '{'})

    @raises(RadarServerConsoleError)
    def test_process_command_fails_due_missing_action_keyword(self):
        radar_server_console = self._get_patched_radar_server_console()
        radar_server_console._process_command({})

    def test_enable_action_is_called(self):
        radar_server_console = self._get_patched_radar_server_console()
        radar_server_console._client_manager.enable = MagicMock(side_effect=[[], [1, 2, 3]])
        client = MagicMock()
        client.receive_message = MagicMock(side_effect=[
            (RadarConsoleMessage.TYPE['QUERY'], '{"action": "enable()"}'),
            (RadarConsoleMessage.TYPE['QUERY'], '{"action": "enable(1, 2, 3)"}'),
        ])
        client.send_message = MagicMock()
        radar_server_console.on_receive(client)
        radar_server_console._client_manager.enable.assert_called_with(ids=([],))
        client.send_message.assert_called_with(RadarConsoleMessage.TYPE['QUERY REPLY'], ANY)
        radar_server_console.on_receive(client)
        radar_server_console._client_manager.enable.assert_called_with(ids=([1, 2, 3],))
