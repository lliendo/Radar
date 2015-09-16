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


class EPollMonitor(NetworkMonitor):
    def __new__(cls, *args, **kwargs):
        try:
            global epoll, EPOLLIN
            from select import epoll, EPOLLIN
        except ImportError:
            raise NetworkMonitorError(cls.__name__)

        return super(EPollMonitor, cls).__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(EPollMonitor, self).__init__(*args, **kwargs)
        self._epoll_monitor = epoll()
        self._register(self._server.socket)

    def _register(self, fd):
        self._epoll_monitor.register(fd, EPOLLIN)

    def on_disconnect(self, client):
        self._epoll_monitor.unregister(client.socket)

    def on_connect(self, client):
        self._register(client.socket)

    def watch(self):
        ready_fds = [fd for (fd, _) in self._epoll_monitor.poll(self._timeout)]
        super(EPollMonitor, self)._watch(ready_fds)
