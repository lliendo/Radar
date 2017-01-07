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

    """
    Abstract class that is used as a base for plugin development.

    All plugins must inherit from this class and at least implement
    the `on_check_reply` method in order to perform any useful work.
    """

    def __init__(self):
        if not self.PLUGIN_NAME:
            raise ServerPluginError("Error - Plugin name not defined.")

        try:
            ConfigBuilder.__init__(self, self.PLUGIN_CONFIG_FILE)
            self.merge_config(self.DEFAULT_CONFIG)
        except ConfigError:
            self.config = self.DEFAULT_CONFIG

        Switchable.__init__(self, enabled=self.config.get('enabled', True))

        # Currently we only support check and test replies.
        self._message_actions = {
            RadarMessage.TYPE['CHECK REPLY']: self.on_check_reply,
            RadarMessage.TYPE['TEST REPLY']: self.on_test_reply,
        }

    @staticmethod
    def get_path(source_filename, config_filename):
        return join_path(dirname(source_filename), config_filename)

    def run(self, address, port, message_type, checks, contacts):
        """
        Run an action. Currently we only support a check reply and
        a test reply action.

        :param address: A string containing the source IP address.
        :param port: An integer representing the source port.
        :param message_type: A RadarMessage.TYPE value.
        :param checks: A list containing `Check` objects.
        :param contacts: A list containing `Contact` objects.
        """

        try:
            action = self._message_actions[message_type]
            action(address, port, checks, contacts)
        except KeyError:
            raise ServerPluginError("Error - Unrecognized message type : {}.".format(message_type))

    def log(self, message):
        """
        Method that can be used by the user to perform logging.
        """

        RadarLogger.log("Plugin '{}' v{}. {}".format(self.PLUGIN_NAME, self.PLUGIN_VERSION, message))

    def configure(self):
        """
        Configure this `Plugin` by calling the `on_start` method.
        """

        RadarLogger.log("Loading plugin : '{}' v{}.".format(self.PLUGIN_NAME, self.PLUGIN_VERSION))
        self.on_start()

    def on_start(self):
        """
        Implement this method to (optionally) initialize the plugin.
        """

    def on_check_reply(self, address, port, checks, contacts):
        """
        Implement this method to process a check reply.

        The implementation of this method is mandatory.
        """

        raise ServerPluginError("Error - Unimplemented `on_check_reply` method.")

    def on_test_reply(self, address, port, checks, contacts):
        """
        Implement this method to (optionally) process a test reply.
        """

    def on_shutdown(self):
        """
        Implement this method to (optionally) tear down the plugin.
        """

    def to_dict(self):
        return super(ServerPlugin, self).to_dict(['id', 'plugin_id', 'plugin_version', 'enabled'])

    def __eq__(self, other_plugin):
        """
        Compare if two plugins are the same. Two plugins are considered
        equal if their name and version are the same.

        :param other_plugin: A `Plugin` object.
        :return: A boolean indicating if this plugin is equal to another one.
        """

        return (self.PLUGIN_NAME == other_plugin.PLUGIN_NAME) and \
            (self.PLUGIN_VERSION == other_plugin.PLUGIN_VERSION)


class PluginManager(Thread):

    STOP_EVENT_TIMEOUT = 0.2

    """
    The PluginManager thread is responsible for executing all defined and enabled
    plugins.

    :param plugins: A list containing `Plugin` objects.
    :param queue: A `Queue` object used to receive upcoming messages from
        the RadarServer thread.
    :param stop_event: An `Event` object that is used to control thread
        termination.
    """

    def __init__(self, plugins, queue, stop_event=None):
        Thread.__init__(self)
        self._plugins = plugins
        self._queue = queue
        self.stop_event = stop_event or Event()

    def _dereference(self, ids):
        """
        Given a list of Python ids get their corresponding Python objects.
        We dereference ids, to avoid re-instantiating objects. We can actually
        do this because we're on the same process address space.

        :return: A list of Python objects.
        """

        return [cast(object_id, py_object).value for object_id in ids]

    def _get_plugin_args(self, message):
        """
        Construct a tuple with the data needed by every plugin to run.
        This method dereferences a list of Python ids to Python objects.

        :param message: A dictionary containing the following keys:
            address, port, message_type, check_ids and contact_ids.
        :return: A tuple containing the source IP addres, the source port, the message type,
            a list of `Check` objects and a list of `Contact` objects.
        """

        try:
            return (
                message['address'],
                message['port'],
                message['message_type'],
                self._dereference(message['check_ids']),
                self._dereference(message['contact_ids']),
            )
        except KeyError as error:
            raise PluginManagerError("Error - Couldn't process incoming message from queue. Missing key : '{}'.".format(error))

    def is_stopped(self):
        """
        Tell if the thread has been stopped.

        :return: A boolean indicating if the thread has been stopped.
        """

        return self.stop_event.is_set()

    def _run_plugin(self, plugin, address, port, message_type, checks, contacts):
        """
        Run a plugin. Each plugin is fed with:
            - The source IP address of the client who sent the check reply.
            - The source port of the client who sent the check reply.
            - The message type of the reply.
            - A list containing `Check` objects.
            - A list containing `Contact` objects.

        :param plugin: A `Plugin` object to be run.
        :param address: A string containing the source IP address.
        :param port: An integer representing the source port.
        :param message_type: A RadarMessage.TYPE value.
        :param checks: A list containing `Check` objects.
        :param contacts: A list containing `Contact` objects.
        """

        try:
            plugin.run(address, port, message_type, checks, contacts)
        except Exception as error:
            RadarLogger.log("Error - Plugin '{}' version '{}' raised an error. Details : {}.".format(
                plugin.PLUGIN_NAME, plugin.PLUGIN_VERSION, error))

    def _run_plugins(self, message):
        """
        Rrocess all defined and enabled plugins.

        :param message: A dictionary containing the following keys:
            address, port, message_type, check_ids and contact_ids.
        """

        plugin_args = self._get_plugin_args(message)

        for plugin in self._plugins:
            if plugin.enabled:
                self._run_plugin(plugin, *plugin_args)

    def run(self):
        """
        Run the PluginManager thread.

        This method scans a `Queue` object continuously and if a new message
        arrives it is passed to all defined plugins for further processing.
        """

        while not self.is_stopped():
            try:
                self._run_plugins(self._queue.get_nowait())
            except EmptyQueue:
                self.stop_event.wait(self.STOP_EVENT_TIMEOUT)
            except PluginManagerError as error:
                RadarLogger.log(error)
