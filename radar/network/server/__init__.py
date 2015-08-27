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
from platform import system as platform_name
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SOMAXCONN, error as SocketError
from ..monitor.select_monitor import SelectMonitor
from ..monitor.poll_monitor import PollMonitor
from ..monitor.epoll_monitor import EPollMonitor
from ..monitor.kqueue_monitor import KQueueMonitor
from ..monitor.iocp_monitor import IOCPMonitor
from ..client import ClientReceiveError, ClientSendError, ClientDisconnected, ClientAbortError, Client as BaseClient


class ServerListenError(Exception):
    pass


class ServerAcceptError(Exception):
    pass


class ServerPlatformError(Exception):
    pass


class ServerError(Exception):
    pass


class Server(object):

    __metaclass__ = ABCMeta

    # TODO: Make IOCPMonitor work.
    AVAILABLE_PLATFORM_MONITORS = {
        'BSD': [KQueueMonitor, PollMonitor, SelectMonitor],
        'Linux': [EPollMonitor, PollMonitor, SelectMonitor],
        'Windows': [SelectMonitor],
        'Unknown': [SelectMonitor],
    }

    Client = None

    def __init__(self, address, port, network_monitor=None, network_monitor_timeout=None, blocking_socket=True):
        self.blocking_socket = blocking_socket
        self.socket = None
        self._clients = []
        self._listen(address, port)
        self.network_monitor = network_monitor or self._get_network_monitor(network_monitor_timeout)

    def _get_platform_name(self):
        bsds = ['Darwin', 'FreeBSD', 'NetBSD', 'OpenBSD']
        platform = platform_name()
        platform = 'BSD' if platform in bsds else platform
        return 'Unknown' if platform not in self.AVAILABLE_PLATFORM_MONITORS.keys() else platform

    def _get_network_monitor(self, network_monitor_timeout):
        platform = self._get_platform_name()

        for NetworkMonitor in self.AVAILABLE_PLATFORM_MONITORS[platform]:
            try:
                return NetworkMonitor(self, network_monitor_timeout)
            except KeyError:
                raise ServerPlatformError('Error - Platform : \'{:}\' is not available.'.format(platform))
            except AttributeError:
                pass

        raise ServerPlatformError('Error - No available network monitor for platform : \'{:}\'.'.format(platform))

    def accept_client(self, client):
        return True

    def _on_connect(self, client):
        self.network_monitor.on_connect(client)
        self._clients.append(client)
        self.on_connect(client)

    def on_connect(self, client):
        pass

    def _on_reject(self, client):
        self.on_reject(client)
        client.disconnect()

    def on_reject(self, client):
        pass

    def disconnect(self, client):
        self.network_monitor.on_disconnect(client)
        self.on_disconnect(client)
        self._clients.remove(client)
        client.disconnect()

    def on_disconnect(self, client):
        pass

    def _on_abort(self, client):
        self.network_monitor.on_disconnect(client)
        self.on_abort(client)
        self._clients.remove(client)
        client.abort()

    def on_abort(self, client):
        pass

    def on_timeout(self):
        pass

    @abstractmethod
    def on_receive(self, client):
        pass

    def on_shutdown(self):
        [c.disconnect() for c in self._clients]
        self.socket.close()
        self.socket = None

    def is_stopped(self):
        return False

    def is_listening(self):
        return self.socket is not None

    def on_receive_error(self, client, error):
        self.remove_client(client)

    def on_send_error(self, client, error):
        self.remove_client(client)

    def _listen(self, address, port):
        try:
            self.socket = socket(AF_INET, SOCK_STREAM)
            self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

            if not self.blocking_socket:
                self.socket.setblocking(0)

            self.socket.bind((address, port))
            self.socket.listen(SOMAXCONN)
        except SocketError, (_, e):
            raise ServerListenError('Error - Couldn\'t not listen on : {:}/{:}. Details : {:}.'.format(address, port, e))

    def _accept(self):
        try:
            client_socket, (address, port) = self.socket.accept()
        except SocketError, (_, e):
            raise ServerAcceptError('Error - Couldn\'t accept new client. Details : {:}.'.format(e))

        if not self.blocking_socket:
            client_socket.setblocking(0)

        if (self.Client is None) or (not issubclass(self.Client, BaseClient)):
            raise ServerError('Error - Wrong \'Client\' subclass or \'Client\' subclass not defined.')

        return self.Client(address, port, socket=client_socket, blocking_socket=self.blocking_socket)

    def _serve_ready_clients(self, clients):
        for c in clients:
            try:
                self.on_receive(c)
            except ClientReceiveError, error:
                self.on_receive_error(c, error)
            except ClientSendError, error:
                self.on_send_error(c, error)
            except ClientDisconnected:
                self.disconnect(c)
            except ClientAbortError:
                self._on_abort(c)

    def run(self):
        while not self.is_stopped():
            self.network_monitor.watch()

        self.on_shutdown()

        return self.is_stopped()
