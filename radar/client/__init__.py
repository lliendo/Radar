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


from time import time
from threading import Thread, Event
from json import loads as deserialize_json, dumps as serialize_json
from queue import Empty as EmptyQueue
from ..logger import RadarLogger
from ..network.client import Client, ClientError
from ..protocol import Message, RadarMessage, RadarConsoleMessage


class RadarClientLite(Client):
    def __init__(self, *args, **kwargs):
        super(RadarClientLite, self).__init__(*args, **kwargs)
        self._message = RadarMessage()

    def on_receive(self):
        pass

    def send_message(self, message_type, message, message_options=Message.OPTIONS['NONE']):
        return self._message.send(self, message_type, message, message_options=message_options)

    def receive_message(self):
        return self._message.receive(self)


class RadarConsoleClient(RadarClientLite):
    def __init__(self, *args, **kwargs):
        super(RadarConsoleClient, self).__init__(*args, **kwargs)
        self._message = RadarConsoleMessage()


class RadarClient(RadarClientLite, Thread):

    NETWORK_MONITOR_TIMEOUT = 0.2
    CONNECT_DISCONNECT_INTERVAL = 0.5
    RECONNECT_DELAYS = [5, 15, 60]

    def __init__(self, platform_setup, input_queue, output_queue, stop_event=None):
        Thread.__init__(self)
        RadarClientLite.__init__(
            self,
            platform_setup.config['connect']['to'],
            platform_setup.config['connect']['port'],
            network_monitor_timeout=self.NETWORK_MONITOR_TIMEOUT,
            blocking_socket=False
        )
        self._reconnect = platform_setup.config['reconnect']
        self._input_queue = input_queue
        self._output_queue = output_queue
        self._delays = self.RECONNECT_DELAYS
        self._connect_timestamp = 0
        self.stop_event = stop_event or Event()

    def _sleep(self):
        self.stop_event.wait(self._delays[0])
        self._delays.append(self._delays[0])
        self._delays.pop(0)

    # If we get disconnected relatively fast (under the CONNECT_DISCONNECT_INTERVAL threshold)
    # then we should give up connecting at all. When server goes down the 'else' prevents
    # instant reconnection giving it time to fully shutdown its listen socket.
    def _should_give_up_reconnect(self):
        if time() - self._connect_timestamp < self.CONNECT_DISCONNECT_INTERVAL:
            self.stop_event.set()
            RadarLogger.log('Error - Radar client seems not to be allowed to connect to Radar server.')
        else:
            self.stop_event.wait(self.CONNECT_DISCONNECT_INTERVAL)

    def on_connect(self):
        RadarLogger.log('Connected to {:}:{:}.'.format(self.address, self.port))
        self._connect_timestamp = time()

    def on_disconnect(self):
        RadarLogger.log('Disconnected from {:}:{:}.'.format(self.address, self.port))
        self._should_give_up_reconnect()

    def connect(self):
        while not self.is_stopped() and not self.is_connected():
            try:
                super(RadarClient, self).connect()
            except ClientError as error:
                RadarLogger.log('{:} Falling back {:}s. Details: {:}.'.format(error, self._delays[0]))

                if self._reconnect:
                    self._sleep()
                else:
                    self.stop_event.set()

    def on_receive(self):
        message_type, message = self.receive_message()
        self._output_queue.put_nowait({
            'message_type': message_type,
            'message': deserialize_json(message),
        })

    def on_timeout(self):
        try:
            serialized_message = serialize_json(self._input_queue.get_nowait())
            self.send_message(RadarMessage.TYPE['CHECK REPLY'], serialized_message)
        except EmptyQueue:
            pass

    def is_stopped(self):
        return self.stop_event.is_set()

    def run(self):
        self.connect()

        while not self.is_stopped():
            super(RadarClient, self).run()
            self.connect()
