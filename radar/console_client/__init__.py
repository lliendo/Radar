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


from json import dumps as serialize_json, loads as deserialize_json
from threading import Thread, Event
from queue import Empty as EmptyQueue
from pprint import pprint
from ..client import RadarClientLite
from ..protocol import RadarConsoleMessage, MessageNotReady
from ..network.client import ClientError


class RadarConsoleClientError(Exception):
    pass


class RadarConsoleClientQuit(Exception):
    pass


class RadarConsoleClientEmptyInput(Exception):
    pass


class RadarConsoleClient(RadarClientLite, Thread):

    NETWORK_MONITOR_TIMEOUT = 0.2

    def __init__(self, cli, input_queue, output_queue, stop_event=None):
        Thread.__init__(self)
        RadarClientLite.__init__(
            self,
            cli.address,
            cli.port,
            network_monitor_timeout=self.NETWORK_MONITOR_TIMEOUT,
            blocking_socket=False
        )
        self._input_queue = input_queue
        self._output_queue = output_queue
        self.stop_event = stop_event or Event()
        self._actions = {
            RadarConsoleMessage.TYPE['QUERY REPLY']: self._on_query_reply,
        }

    def on_timeout(self):
        try:
            self.send_message(RadarConsoleMessage.TYPE['QUERY'], self._input_queue.get_nowait())
        except EmptyQueue:
            pass

    def on_disconnect(self):
        self.stop_event.set()
        print('\n\nError - Got disconnect from server. Was Radar server shut down ?')

    def _on_query_reply(self, message):
        self._output_queue.put(message)

    def on_receive(self):
        try:
            message_type, message = self.receive_message()
            self._actions[message_type](message)
        except KeyError:
            print('Error - Invalid message type : {:}.'.format(message_type))
        except MessageNotReady:
            pass

    def is_stopped(self):
        return self.stop_event.is_set()

    def run(self):
        try:
            self.connect()
            super(RadarConsoleClient, self).run()
        except ClientError as error:
            print(error)

        return self.is_stopped()


class RadarConsoleClientInput(Thread):

    COMMAND_PROMPT = '> '
    WRAPPED_COMMANDS = {
        'quit()': RadarConsoleClientQuit,
        '': RadarConsoleClientEmptyInput,
    }

    def __init__(self, input_queue, output_queue, stop_event=None):
        Thread.__init__(self)
        self._input_queue = input_queue
        self._output_queue = output_queue
        self.stop_event = stop_event or Event()

    def _write_output_queue(self, command):
        try:
            self._output_queue.put(serialize_json({'action': command}))
        except Exception as error:
            raise RadarConsoleClientError('Error - Couldn\'t run command : {:}. Details {:}.'.format(command, error))

    def _print_reply(self, response):
        try:
            if type(response['message']) == unicode:
                print(response['message'])
            else:
                pprint(response['data'])
        except KeyError:
            raise RadarConsoleClientError('Error - Wrong JSON format. Missing \'message\' or \'data\' key.')

    def _read_input_queue(self):
        try:
            self._print_reply(deserialize_json(self._input_queue.get()))
        except Exception as error:
            raise RadarConsoleClientError('Error - Couldn\'t read input queue. Details {:}.'.format(error))

    def _read_input(self):
        try:
            command = raw_input(self.COMMAND_PROMPT)
            raise self.WRAPPED_COMMANDS[command]()
        except EOFError:
            raise RadarConsoleClientQuit()
        except KeyError:
            return command

    def is_stopped(self):
        return self.stop_event.is_set()

    def run(self):
        while not self.is_stopped():
            try:
                self._write_output_queue(self._read_input())
                self._read_input_queue()
            except RadarConsoleClientQuit:
                self.stop_event.set()
            except RadarConsoleClientError as error:
                print(error)
            except RadarConsoleClientEmptyInput:
                pass

        return self.is_stopped()
