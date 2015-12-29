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
from ..client import RadarClientLite
from ..network.server import Server
from ..protocol import RadarConsoleMessage, MessageNotReady


class RadarServerConsoleError(Exception):
    pass


class RadarServerConsole(Server, Thread):

    Client = RadarClientLite
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
        self.stop_event = stop_event or Event()
        self._actions = {
            'list': self._list,
            'enable': self._enable,
            'disable': self._disable,
            'test': self._test,
        }

    def _enable(self, ids):
        print 'enabling {:}'.format(ids)

    def _disable(self, ids):
        print 'disabling {:}'.format(ids)

    def _test(self, ids):
        print 'testing {:}'.format(ids)

    def _list(self, ids):
        print 'listing {:}'.format(ids)

    def is_stopped(self):
        return self.stop_event.is_set()

    def _process_command(self, message):
        try:
            parsed_expression = parse(message['action']).body.pop()
            action = parsed_expression.value.func.id
            return self._actions[action]([arg.n for arg in parsed_expression.value.args])
        except SyntaxError as error:
            raise RadarServerConsoleError('Error - Couldn\'t parse command : \'{:}\'. Details : \'{:}\'.'.format(
                error.text.strip(), error.msg))
        except KeyError:
            raise RadarServerConsoleError('Error - Invalid command : \'{:}\'.'.format(action))

    def _reply_client(self, client, response):
        if response is not None:
            client.send_message(RadarConsoleMessage.TYPE['QUERY REPLY'], serialize_json(response))

    def on_receive(self, client):
        response = None

        try:
            message_type, message = client.receive_message()
            response = self._process_command(deserialize_json(message))
        except RadarServerConsoleError as error:
            response = {'action reply': error}
        except MessageNotReady:
            pass

        self._reply_client(client, response)
