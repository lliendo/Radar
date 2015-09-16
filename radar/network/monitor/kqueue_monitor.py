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


class KQueueMonitor(NetworkMonitor):
    def __new__(cls, *args, **kwargs):
        try:
            global kqueue, kevent, KQ_EV_ENABLE, KQ_FILTER_READ, KQ_EV_ADD, KQ_EV_DELETE
            from select import kqueue, kevent, KQ_EV_ENABLE, KQ_FILTER_READ, KQ_EV_ADD, KQ_EV_DELETE
        except ImportError:
            raise NetworkMonitorError(cls.__name__)

        return super(KQueueMonitor, cls).__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(KQueueMonitor, self).__init__(*args, **kwargs)
        self._kernel_queue = kqueue()
        self._register(self._server.socket)

    def _register(self, fd):
        self._kernel_queue.control([kevent(fd, KQ_FILTER_READ, KQ_EV_ADD | KQ_EV_ENABLE)], 0)

    def on_disconnect(self, client):
        self._kernel_queue.control([kevent(client.socket, KQ_FILTER_READ, KQ_EV_DELETE)], 0)

    def on_connect(self, client):
        self._register(client.socket)

    def watch(self):
        ready_fds = [e.ident for e in self._kernel_queue.control(None, 1, self._timeout)]
        super(KQueueMonitor, self)._watch(ready_fds)
