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


from ast import parse
from json import loads as deserialize_json, dumps as serialize_json
from threading import Thread, Event
from ..logger import RadarLogger
from ..client import RadarConsoleClient
from ..network.server import Server
from ..protocol import RadarConsoleMessage, MessageNotReady
from ..config.server import AddressBuilder


class RadarServerConsoleError(Exception):
    pass


class RadarServerConsole(Server, Thread):

    Client = RadarConsoleClient
    NETWORK_MONITOR_TIMEOUT = 0.2

    def __init__(self, client_manager, platform_setup, stop_event=None):
        Thread.__init__(self)
        Server.__init__(
            self,
            platform_setup.config['console']['address'],
            platform_setup.config['console']['port'],
            network_monitor_timeout=self.NETWORK_MONITOR_TIMEOUT,
            blocking_socket=False,
        )
        self._client_manager = client_manager
        self._allowed_addresses = AddressBuilder(platform_setup.config['console']['allowed hosts']).build()
        self.stop_event = stop_event or Event()
        self._actions = {
            'help': self._help,
            'list': self._list,
            'enable': self._enable,
            'disable': self._disable,
            'test': self._test,
        }

    def accept_client(self, client):
        return any([client.address in address for address in self._allowed_addresses])

    def on_reject(self, client):
        RadarLogger.log('Console client {:}:{:} is not allowed to connect or is already conected.'.format(
            client.address, client.port))

    def _help(self, *unused):
        message = """
        help()                               Displays this help message.
        list()                               List all available Radar objects.
        enable() | enable(id [, id, ...])    Enable all Radar objects or the ones specified by their ids.
        disable() | disable(id [, id, ...])  Disable all Radar objects or the ones specified by their ids.
        test(id [, id, ...])                 Force test of specified Radar objects.
        quit() | Ctrl-D                      Exits the console client.
        """

        return message, []

    def _enable(self, *ids):
        enabled_objects = self._client_manager.enable(ids=ids) or 'All'
        message = '{:} objects are now enabled.'.format(enabled_objects)

        return message, enabled_objects

    def _disable(self, *ids):
        disabled_objects = self._client_manager.disable(ids=ids) or 'All'
        message = '{:} objects are now disabled.'.format(disabled_objects)

        return message, disabled_objects

    # TODO: Needs to be implemented.
    def _test(self, *ids):
        tested_objects = []
        message = 'Launched test for : {:} objects.'.format(tested_objects)

        return message, tested_objects

    def _list(self, *ids):
        return None, self._client_manager.list(ids=ids)

    def is_stopped(self):
        return self.stop_event.is_set()

    def _process_command(self, message):
        try:
            parsed_sentence = parse(message['action']).body.pop()
            action = parsed_sentence.value.func.id
            return self._actions[action]([arg.n for arg in parsed_sentence.value.args])
        except KeyError as error:
            raise RadarServerConsoleError('Error - Invalid message format. Misssing : \'{:}\' key.'.format(error.message))
        except (SyntaxError, AttributeError):
            raise RadarServerConsoleError('Error - Invalid command : \'{:}\'.'.format(message['action']))

    def _reply_client(self, client, response):
        client.send_message(RadarConsoleMessage.TYPE['QUERY REPLY'], serialize_json(response))

    def on_receive(self, client):
        try:
            message_type, message = client.receive_message()
            action_message, object_ids = self._process_command(deserialize_json(message))
            response = {'message': action_message, 'data': object_ids}
        except (ValueError, RadarServerConsoleError) as error:
            response = {'message': error.message, 'data': []}
        except MessageNotReady:
            pass

        self._reply_client(client, response)
