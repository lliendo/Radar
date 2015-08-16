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


class PollMonitor(NetworkMonitor):
    def __new__(cls, *args, **kwargs):
        try:
            global poll, POLLIN
            from select import poll, POLLIN
        except ImportError:
            raise NetworkMonitorError('PollMonitor')

        return super(PollMonitor, cls).__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(PollMonitor, self).__init__(*args, **kwargs)
        self._poll_monitor = poll()
        self._register(self._server.socket)

    def _register(self, fd):
        self._poll_monitor.register(fd, POLLIN)

    def on_disconnect(self, client):
        self._poll_monitor.unregister(client.socket)

    def on_connect(self, client):
        self._register(client.socket)

    def watch(self):
        ready_fds = [fd for (fd, _) in self._poll_monitor.poll(int(self._timeout * 1000))]
        super(PollMonitor, self)._watch(ready_fds)
