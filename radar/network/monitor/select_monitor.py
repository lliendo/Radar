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


class SelectMonitor(NetworkMonitor):
    def __new__(cls, *args, **kwargs):
        try:
            from select import select
        except ImportError:
            raise NetworkMonitorError('SelectMonitor')

        return super(SelectMonitor, cls).__new__(cls, *args, **kwargs)

    def watch(self):
        fds = [self._server.socket] + [c.socket for c in self._server._clients]
        ready_fds, _, _ = select(fds, [], [], self._timeout)
        super(SelectMonitor, self)._watch(ready_fds)
