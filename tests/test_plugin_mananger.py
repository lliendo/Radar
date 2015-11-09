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
from mock import Mock, MagicMock, ANY
from radar.plugin import PluginManager, PluginManagerError, ServerPluginError
from radar.check import Check
from radar.contact import Contact
from radar.logger import RadarLogger


class TestPluginManager(TestCase):
    def setUp(self):
        RadarLogger._shared_state['logger'] = Mock()
        self.plugin_manager = PluginManager([Mock(), Mock()], Mock())
        self.contacts = [Contact(name='A', email='A'), Contact(name='B', email='B')]
        self.checks = [Check(name='A', path='A'), Check(name='B', path='B')]
        self.queue_message = {
            'address': None,
            'port': None,
            'message_type': None,
            'check_ids': [id(c) for c in self.checks],
            'contact_ids': [id(c) for c in self.contacts],
        }

    def test_run_plugin_logs_error(self):
        self.plugin_manager._plugins[0].run = MagicMock(side_effect=ServerPluginError())
        self.plugin_manager._run_plugins(self.queue_message)
        RadarLogger._shared_state['logger'].info.assert_called_with(ANY)

    def test_get_plugin_args(self):
        _, _, _, checks, contacts = self.plugin_manager._get_plugin_args(self.queue_message)
        self.assertEqual(type(checks), list)
        self.assertEqual(type(contacts), list)
        self.assertTrue(all([isinstance(c, Check) for c in checks]))
        self.assertTrue(all([isinstance(c, Contact) for c in contacts]))

    @raises(PluginManagerError)
    def test_get_plugin_args_raises_error(self):
        self.plugin_manager._get_plugin_args({})

    def test_dereference_ids(self):
        self.assertEqual(
            set(self.checks),
            set(self.plugin_manager._dereference([id(c) for c in self.checks]))
        )

    def test_plugin_does_not_run_because_is_disabled(self):
        self.plugin_manager._plugins[0].run = MagicMock()
        self.plugin_manager._plugins[0].enabled = False
        self.plugin_manager._run_plugins(self.queue_message)
        self.assertFalse(self.plugin_manager._plugins[0].run.called)

    def test_plugin_gets_called(self):
        self.plugin_manager._plugins[0].run = MagicMock()
        self.plugin_manager._plugins[1].run = MagicMock()
        self.plugin_manager._run_plugins(self.queue_message)
        self.assertTrue(all([p.run.called for p in self.plugin_manager._plugins]))
