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


from threading import Event
from queue import Queue
from . import RadarLauncher
from ..client_manager import ClientManager
from ..server import RadarServer, RadarServerPoller
from ..console import RadarServerConsole
from ..platform_setup.server import UnixServerSetup, WindowsServerSetup
from ..plugin import PluginManager


class RadarServerLauncher(RadarLauncher):

    PROGRAM_NAME = 'radar-server'
    PROGRAM_VERSION = '0.0.1'
    AVAILABLE_PLATFORMS = {
        'Unix': UnixServerSetup,
        'Windows': WindowsServerSetup,
    }

    def __init__(self):
        super(RadarServerLauncher, self).__init__()
        self._threads = self._build_threads()

    def _build_radar_server_console(self, client_manager, stop_event):
        radar_server_console_address = self._platform_setup.config['console']['address']
        return [
            RadarServerConsole(client_manager, self._platform_setup, stop_event=stop_event)
        ] if radar_server_console_address is not None else []

    def _build_threads(self):
        client_manager = ClientManager(self._platform_setup.monitors)
        queue = Queue()
        stop_event = Event()

        return [
            RadarServer(client_manager, self._platform_setup, queue, stop_event=stop_event),
            RadarServerPoller(client_manager, self._platform_setup, stop_event=stop_event),
            PluginManager(self._platform_setup.plugins, queue, stop_event=stop_event),
        ] + self._build_radar_server_console(client_manager, stop_event)

    def _start_and_join_threads(self):
        self._start_threads(self._threads[:1])

        while self._threads[0].is_alive() and not self._threads[0].is_listening():
            self._threads[0].join(self.THREAD_POLLING_TIME)

        # Only spawn remaining threads if the server is listening.
        if self._threads[0].is_alive():
            self._start_threads(self._threads[1:])
            self._join_threads()
