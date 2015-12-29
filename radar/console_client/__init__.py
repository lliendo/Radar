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


from threading import Thread, Event
from queue import Empty as EmptyQueue
from ..client import RadarClientLite
from ..protocol import RadarConsoleMessage, MessageNotReady


class RadarClientConsoleError(Exception):
    pass


class RadarConsoleClient(RadarClientLite, Thread):

    NETWORK_MONITOR_TIMEOUT = 0.2

    def __init__(self, cli, input_queue, output_queue, stop_event):
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

    def _on_query_reply(self, message):
        self._output_queue.put(message)

    def on_receive(self):
        try:
            message_type, message = self.receive_message()
            self._actions[message_type](message)
        except MessageNotReady:
            pass
        except KeyError:
            print('Error - Invalid message type : {:}.'.format(message_type))

    def run(self):
        self.connect()

        while not self.is_stopped():
            super(RadarConsoleClient, self).run()


class RadarConsoleClientInput(Thread):

    COMMAND_PROMPT = '> '

    def __init__(self, input_queue, output_queue, stop_event):
        Thread.__init__(self)
        self._input_queue = input_queue
        self._output_queue = output_queue
        self.stop_event = stop_event

    def _write_output_queue(self, command):
        try:
            self._output_queue.put(command)
        except Exception as error:
            raise RadarClientConsoleError('Error - Couldn\'t run command : {:}. Details {:}.'.format(command, error))

    def _read_input_queue(self):
        try:
            print('\n{:}'.format(self._input_queue.get()))
        except Exception as error:
            raise RadarClientConsoleError('Error - Couldn\'t read input queue. Details {:}.'.format(error))

    def is_stopped(self):
        return self.stop_event.is_set()

    def run(self):
        while not self.is_stopped():
            try:
                self._write_output_queue(raw_input(self.COMMAND_PROMPT))
                self._read_input_queue()
            except RadarClientConsoleError as error:
                print(error)

        return self.is_stopped()
