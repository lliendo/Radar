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
from socket import create_connection, SOL_SOCKET, SO_LINGER, error as SocketError
from select import select, error as SelectError
from struct import pack
from errno import EWOULDBLOCK, EAGAIN, EINTR


class ClientError(Exception):
    pass


class ClientReceiveError(Exception):
    pass


class ClientSendError(Exception):
    pass


class ClientDisconnected(Exception):
    pass


class ClientDataNotReady(Exception):
    pass


class ClientAbortError(Exception):
    pass


class Client(object):

    __metaclass__ = ABCMeta

    def __init__(self, address, port, socket=None, network_monitor_timeout=None, blocking_socket=True):
        self.address = address
        self.port = port
        self.socket = socket
        self.network_monitor_timeout = network_monitor_timeout
        self.blocking_socket = blocking_socket

    def connect(self):
        if self.is_connected():
            raise ClientError('Error - Client is already connected to {:}:{:}.'.format(self.address, self.port))

        try:
            self.socket = create_connection((self.address, self.port))
        except Exception as error:
            raise ClientError('Error - Can\'t connect to {:}:{:}. Details : {:}.'.format(self.address, self.port, error))

        if not self.blocking_socket:
            self.socket.setblocking(0)

        self.on_connect()

    def disconnect(self):
        if not self.is_connected():
            raise ClientError('Error - Client is not connected.')

        self.socket.close()
        self.socket = None
        self.on_disconnect()

    # Despite its name this method performs a TCP connection reset.
    def abort(self):
        if not self.is_connected():
            raise ClientError('Error - Client is not connected.')

        # Second parameter of pack means set on linger, the third parameter is
        # the linger timeout (0 in this case).
        self.socket.setsockopt(SOL_SOCKET, SO_LINGER, pack('ii', 1, 0))
        self.socket.close()
        self.socket = None
        self.on_abort()

    def _would_block(self, error_code):
        return (error_code == EWOULDBLOCK or error_code == EAGAIN) and \
            (self.socket.gettimeout() == 0)

    def _interrupted_by_signal(self, error_code):
        return error_code[0] == EINTR

    def send(self, data):
        try:
            sent_bytes = self.socket.send(data)
        # Can we do : except SocketError as (_, e): ?
        except SocketError as e:
            raise ClientSendError('Error - Couldn\'t send data. Details : {:}.'.format(e[1]))
        except TypeError:
            raise ClientSendError('Error - Couldn\'t send data (data not iterable).')

        return sent_bytes

    def receive(self, length):
        try:
            received_bytes = self.socket.recv(length)
        # Can we do : except SocketError as (error_code_, error_details): ?
        except SocketError as e:
            if self._would_block(e[0]):
                raise ClientDataNotReady('Error - Non blocking socket attempting read ahead.')

            raise ClientReceiveError('Error - Couldn\'t receive data from {:}:{:}. Details : {:}.'.format(
                self.address, self.port, e[1]))

        if len(received_bytes) == 0:
            raise ClientDisconnected()

        return received_bytes

    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def on_abort(self):
        pass

    def on_timeout(self):
        pass

    @abstractmethod
    def on_receive(self):
        pass

    # Yes, the error variable is not used in the default implementation however
    # it could be used when this behaviour is overrided.
    def on_receive_error(self, error):
        self.disconnect()

    def on_send_error(self, error):
        self.disconnect()

    def on_shutdown(self):
        self.disconnect()

    def is_stopped(self):
        return False

    def is_connected(self):
        return self.socket is not None

    def _process_message(self):
        try:
            self.on_receive()
        except ClientReceiveError as error:
            self.on_receive_error(error)
        except ClientSendError as error:
            self.on_send_error(error)
        except ClientDisconnected:
            self.disconnect()

    def _watch(self):
        ready_fds = []

        try:
            ready_fds, _, _ = select([self.socket], [], [], self.network_monitor_timeout)
        except SelectError as e:
            if not self._interrupted_by_signal(e):
                raise e

        return ready_fds

    def run(self):
        while (not self.is_stopped()) and self.is_connected():
            ready_fds = self._watch()

            if ready_fds:
                self._process_message()
            else:
                self.on_timeout()

        return self.is_stopped()

    def __eq__(self, other_client):
        return self.address == other_client.address
