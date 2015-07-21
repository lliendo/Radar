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


from . import NetworkMonitor, NetworkMonitorError


class IOCPMonitor(NetworkMonitor):
    def __new__(cls, *args, **kwargs):
        try:
            global CreateIoCompletionPort, GetQueuedCompletionStatus, CancelIo, INVALID_HANDLE_VALUE
            from win32file import CreateIoCompletionPort, GetQueuedCompletionStatus, CancelIo, INVALID_HANDLE_VALUE
        except ImportError:
            raise NetworkMonitorError('IOCPMonitor')

        return super(IOCPMonitor, cls).__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(IOCPMonitor, self).__init__(*args, **kwargs)
        self._fds = []
        self._iocp_monitor = CreateIoCompletionPort(INVALID_HANDLE_VALUE, None, 0, 0)
        self._register(self._server.socket)

    def _register(self, fd):
        # Is it possible to use the fd directly ?
        # CreateIoCompletionPort(fd.fileno(), self._iocp_monitor, 0, 0)
        CreateIoCompletionPort(fd.fileno(), self._iocp_monitor, fd.fileno(), 0)
        self._fds.append(fd)

    def on_disconnect(self, client):
        # Is it possible to use the fd directly ?
        CancelIo(client.socket.fileno())
        self._fds.remove(client.socket)

    def on_connect(self, client):
        self._register(client.socket)

    def watch(self):
        # Does overlapped contain my socket object, my fd ?
        _, _, ready_fileno, overlapped = GetQueuedCompletionStatus(self._iocp_monitor, int(self._timeout * 1000))
        super(IOCPMonitor, self)._watch([fd for fd in self._fds if fd.fileno() == ready_fileno])
