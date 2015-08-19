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

        self.socket = create_connection((self.address, self.port))

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

        # First parameter of pack means set on linger, the other option is
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
        except SocketError, (_, error_details):
            raise ClientSendError('Error - Couldn\'t send data. Details : {:}.'.format(error_details))
        except TypeError:
            raise ClientSendError('Error - Couldn\'t send data (data not iterable).')

        return sent_bytes

    # TODO: Recheck that this is behaving as expected.
    # We're assuming that on a non-blocking socket recv does not read length
    # bytes if there are not at least length bytes... (e.g. we're doing
    # a recv(5) when there are actually only 3 bytes on the socket)
    # and hence those 3 bytes plus the next 2 would be available in the next
    # recv.
    def receive(self, length):
        try:
            received_bytes = self.socket.recv(length)
        except SocketError, (error_code, error_details):
            if self._would_block(error_code):
                raise ClientDataNotReady('Error - Non blocking socket attempting read ahead.')

            raise ClientReceiveError('Error - Couldn\'t receive data from {:}:{:}. Details : {:}.'.format(
                self.address, self.port, error_details))

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
        except ClientReceiveError, error:
            self.on_receive_error(error)
        except ClientSendError, error:
            self.on_send_error(error)
        except ClientDisconnected:
            self.disconnect()

    def _watch(self, fds):
        ready_fds = []

        try:
            ready_fds, _, _ = select(fds, [], [], self.network_monitor_timeout)
        except SelectError, e:
            if not self._interrupted_by_signal(e):
                raise e

        return ready_fds

    def __eq__(self, other_client):
        return self.address == other_client.address

    def run(self):
        while (not self.is_stopped()) and self.is_connected():
            ready_fds = self._watch([self.socket])

            if ready_fds:
                self._process_message()
            else:
                self.on_timeout()

        return self.is_stopped()
