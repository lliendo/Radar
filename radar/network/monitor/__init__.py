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


from abc import ABCMeta, abstractmethod


class NetworkMonitorError(Exception):
    def __init__(self, network_monitor):
        self._network_monitor = network_monitor

    def __str__(self):
        return 'Error - \'{:}\' is not supported on this platform.'.format(self._network_monitor)


class NetworkMonitor(object):

    __metaclass__ = ABCMeta

    def __init__(self, server, timeout=None):
        self._server = server
        self._timeout = timeout

    def _client_arrived(self, fds):
        return self._server.socket.fileno() in fds

    def _client_ready(self, client, fds):
        return client.socket.fileno() in fds

    def _ready_clients(self, fds):
        return [c for c in self._server._clients if self._client_ready(c, fds)]

    def _watch(self, fds):
        if self._client_arrived(fds):
            client = self._server._accept()
            fds.remove(self._server.socket.fileno())

            if self._server.accept_client(client):
                self._server._on_connect(client)
            else:
                self._server._on_reject(client)

        self._server._serve_ready_clients(self._ready_clients(fds))

        if not fds:
            self._server.on_timeout()

    def on_connect(self, client):
        pass

    def on_disconnect(self, client):
        pass

    @abstractmethod
    def watch(self):
        pass
