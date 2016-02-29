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
from mock import Mock, ANY
from radar.plugin import ServerPlugin, ServerPluginError
from radar.logger import RadarLogger
from radar.protocol import RadarMessage


class InvalidPlugin(ServerPlugin):
    pass


class DummyPlugin(ServerPlugin):
    PLUGIN_NAME = 'dummy'


class TestServerPlugin(TestCase):
    @raises(ServerPluginError)
    def test_server_plugin_raises_error_due_to_missing_name(self):
        InvalidPlugin()

    @raises(ServerPluginError)
    def test_run_raises_error_due_to_wrong_message_type(self):
        DummyPlugin().run(None, None, max(RadarMessage.TYPE.values()) + 1, None, None)

    def test_on_start_is_called_when_plugin_gets_configured(self):
        RadarLogger._shared_state['logger'] = Mock()
        dummy_plugin = DummyPlugin()
        dummy_plugin.on_start = Mock()
        dummy_plugin.configure()
        self.assertTrue(dummy_plugin.on_start.called)
        RadarLogger._shared_state['logger'].info.assert_called_with(ANY)
