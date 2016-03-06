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


from queue import Empty as EmptyQueue
from abc import ABCMeta
from ctypes import cast, py_object
from functools import reduce
from os.path import dirname, join as join_path
from threading import Thread, Event
from ..logger import RadarLogger
from ..config import ConfigBuilder, ConfigError
from ..misc import Switchable
from ..protocol import RadarMessage


class ServerPluginError(Exception):
    pass


class PluginManagerError(Exception):
    pass


class ServerPlugin(ConfigBuilder, Switchable):

    __metaclass__ = ABCMeta

    PLUGIN_NAME = ''
    PLUGIN_VERSION = '0.0.1'
    PLUGIN_CONFIG_FILE = ''
    DEFAULT_CONFIG = {}

    def __init__(self):
        if not self.PLUGIN_NAME:
            raise ServerPluginError('Error - Plugin name not defined.')

        try:
            ConfigBuilder.__init__(self, self.PLUGIN_CONFIG_FILE)
            self.merge_config(self.DEFAULT_CONFIG)
        except ConfigError:
            self.config = self.DEFAULT_CONFIG

        Switchable.__init__(self, enabled=self.config.get('enabled', True))
        self._message_actions = {
            RadarMessage.TYPE['CHECK REPLY']: self.on_check_reply,
            RadarMessage.TYPE['TEST REPLY']: self.on_test_reply,
        }

    @staticmethod
    def get_path(source_filename, config_filename):
        return join_path(dirname(source_filename), config_filename)

    def run(self, address, port, message_type, checks, contacts):
        try:
            action = self._message_actions[message_type]
            action(address, port, checks, contacts)
        except KeyError:
            raise ServerPluginError('Error - Unrecognized message type : {:}.'.format(message_type))

    def log(self, message):
        RadarLogger.log('Plugin \'{:}\' v{:}. {:}'.format(self.PLUGIN_NAME, self.PLUGIN_VERSION, message))

    def configure(self):
        RadarLogger.log('Loading plugin : \'{:}\' v{:}.'.format(self.PLUGIN_NAME, self.PLUGIN_VERSION))
        self.on_start()

    def on_start(self):
        """ Implement this method to initialize the plugin. """
        pass

    def on_check_reply(self, address, port, checks, contacts):
        """ Implement this method to process a check reply. """
        pass

    def on_test_reply(self, address, port, checks, contacts):
        """ Implement this method to process a test reply. """
        pass

    def on_shutdown(self):
        """ Implement this method to tear down the plugin. """
        pass

    def to_dict(self):
        return super(ServerPlugin, self).to_dict(['id', 'plugin_id', 'plugin_version', 'enabled'])

    def __eq__(self, other_plugin):
        return (self.PLUGIN_NAME == other_plugin.PLUGIN_NAME) and \
            (self.PLUGIN_VERSION == other_plugin.PLUGIN_VERSION)


class PluginManager(Thread):

    STOP_EVENT_TIMEOUT = 0.2

    def __init__(self, plugins, queue, stop_event=None):
        Thread.__init__(self)
        self._plugins = plugins
        self._queue = queue
        self.stop_event = stop_event or Event()

    # We dereference ids, to avoid re-instantiating objects. We can actually
    # do this because we're on the same process address space.
    def _dereference(self, ids):
        return [cast(object_id, py_object).value for object_id in ids]

    def _flatten(self, list_of_lists):
        return reduce(lambda l, m: l + m, list_of_lists)

    def _get_plugin_args(self, message):
        try:
            return (
                message['address'],
                message['port'],
                message['message_type'],
                self._flatten([check_ids.as_list() for check_ids in self._dereference(message['check_ids'])]),
                self._flatten([contact_ids.as_list() for contact_ids in self._dereference(message['contact_ids'])]),
            )
        except KeyError as error:
            raise PluginManagerError('Error - Couldn\'t process incoming message from queue. Missing key : \'{:}\'.'.format(error))

    def is_stopped(self):
        return self.stop_event.is_set()

    def _run_plugin(self, plugin, address, port, message_type, checks, contacts):
        try:
            plugin.run(address, port, message_type, checks, contacts)
        except Exception as error:
            RadarLogger.log('Error - Plugin \'{:}\' version \'{:}\' raised an error. Details : {:}.'.format(
                plugin.PLUGIN_NAME, plugin.PLUGIN_VERSION, error))

    def _run_plugins(self, queue_message):
        plugin_args = self._get_plugin_args(queue_message)
        [self._run_plugin(plugin, *plugin_args) for plugin in self._plugins if plugin.enabled]

    def run(self):
        while not self.is_stopped():
            try:
                self._run_plugins(self._queue.get_nowait())
            except EmptyQueue:
                self.stop_event.wait(self.STOP_EVENT_TIMEOUT)
            except PluginManagerError as error:
                RadarLogger.log(error)
