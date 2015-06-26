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


from Queue import Full as FullQueue
from datetime import datetime, timedelta
from json import loads as deserialize_json
from threading import Thread, Event
from ..client import RadarClientLite
from ..network.server import Server
from ..protocol import MessageNotReady


class ServerPollerError(object):
    pass


class RadarServer(Server, Thread):

    Client = RadarClientLite
    NETWORK_MONITOR_TIMEOUT = 0.2

    def __init__(self, client_manager, platform_setup, queue):
        Thread.__init__(self)
        Server.__init__(
            self,
            platform_setup.config['listen']['address'],
            platform_setup.config['listen']['port'],
            network_monitor_timeout=self.NETWORK_MONITOR_TIMEOUT,
            blocking_socket=False,
        )
        self._client_manager = client_manager
        self._logger = platform_setup.logger
        self._plugins = platform_setup.plugins
        self._queue = queue
        self.stop_event = Event()

    def accept_client(self, client):
        return self._client_manager.matches_any_monitor(client)

    def on_reject(self, client):
        self._logger.log('Client {:}:{:} is not allowed to connect or is already conected.'.format(
            client.address, client.port))

    def on_connect(self, client):
        self._client_manager.register(client)
        self._logger.log('Client {:}:{:} got connected.'.format(client.address, client.port))

    def on_disconnect(self, client):
        self._client_manager.unregister(client)
        self._logger.log('Client {:}:{:} got disconnected.'.format(client.address, client.port))

    def on_abort(self, client):
        self._client_manager.unregister(client)
        self._logger.log('Error - Client {:}:{:} sent an unknown message. Resetting connection.'.format(
            client.address, client.port))

    def _write_queue(self, client, message_type, updated_checks):
        queue_message = {
            'client_address': client.address,
            'client_port': client.port,
            'message_type': message_type,
            'check_ids': [id(c) for c in updated_checks['checks']],
            'contact_ids': [id(c) for c in updated_checks['contacts']]
        }

        try:
            self._queue.put_nowait(queue_message)
        except FullQueue, e:
            self._logger.log('Error - Couldn\'t write to queue. Details : {:}.'.format(e))

    def on_receive(self, client):
        try:
            message_type, message = client.receive_message()
            deserialized_message = deserialize_json(message)
            updated_checks = self._client_manager.process_message(client, message_type, deserialized_message)
            [self._write_queue(client, message_type, uc) for uc in updated_checks]
        except MessageNotReady:
            pass

    def on_receive_error(self, client, error):
        self._client_manager.unregister(client)
        self._logger.log('Error - While receiving data from client {:}:{:}. Details: {:}'.format(
            client.address, client.port, error))

    def is_stopped(self):
        return self.stop_event.is_set()


class RadarServerPoller(Thread):
    def __init__(self, client_manager, platform_setup):
        Thread.__init__(self)
        self._client_manager = client_manager
        self._logger = platform_setup.logger
        self._polling_time = self._validate(platform_setup.config['polling time'])
        self.stop_event = Event()

    def _validate(self, polling_time):
        try:
            if float(polling_time) < 1:
                raise ServerPollerError('Error - Polling time must be greater than 1 sec.')
        except ValueError:
            raise ServerPollerError('Error - \'{:}\' is not a valid polling time.'.format(polling_time))

        return float(polling_time)

    def _log_next_poll(self):
        time = (datetime.now() + timedelta(0, self._polling_time)).strftime('%H:%M:%S')
        self._logger.log('Next scheduled poll at : {:}.'.format(time))

    def run(self):
        while not self.is_stopped():
            self._client_manager.poll()
            self._log_next_poll()
            self.stop_event.wait(self._polling_time)

    def is_stopped(self):
        return self.stop_event.is_set()


class RadarServerRC(Thread):
    def __init__(self, client_manager, platform_setup):
        Thread.__init__(self)
        self._client_manager = client_manager
        self._logger = platform_setup.logger
        self._token = platform_setup.token
        self.stop_event = Event()

    def enable(self, ids=[]):
        pass

    def disable(self, ids=[]):
        pass

    def test(self, ids=[]):
        pass

    def list(self, ids=[]):
        pass

    def run(self):
        while not self.is_stopped():
            pass

    def is_stopped(self):
        return self.stop_event.is_set()
