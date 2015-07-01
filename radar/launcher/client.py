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


from Queue import Queue
from . import RadarLauncher
from ..setup.client import LinuxClientSetup, WindowsClientSetup
from ..check_manager import CheckManager
from ..client import RadarClient


class RadarClientLauncher(RadarLauncher):

    PROGRAM_NAME = 'Radar client'
    PROGRAM_VERSION = '0.0.1'
    AVAILABLE_PLATFORMS = {
        'Linux': LinuxClientSetup,
        'Windows': WindowsClientSetup,
    }

    # TODO: Better names for queues?
    def __init__(self):
        super(RadarClientLauncher, self).__init__()
        queue_a, queue_b = Queue(), Queue()
        self._threads = [
            RadarClient(self._platform_setup, queue_a, queue_b),
            CheckManager(self._platform_setup, queue_b, queue_a),
        ]

    def _join_threads(self):
        while self._threads[0].is_alive() and not self._threads[0].is_connected():
            self._threads[0].join(self.THREAD_POLLING_TIME)

        # Only spawn remaining threads if the client got connected or if the
        # client is trying to reconnect.
        if self._threads[0].is_alive():
            self._start_threads(self._threads[1:])
            super(RadarClientLauncher, self)._join_threads()

    def run(self):
        self._platform_setup.logger.log('Starting radar client.')
        self._start_threads(self._threads[:1])
        self._join_threads()
        self._platform_setup.logger.log('Shutting down radar client.')
        self._platform_setup.tear_down(self)
