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


from queue import Queue
from threading import Event
from argparse import ArgumentParser
from . import CLI, RadarLauncher
from ..console_client import RadarConsoleClient, RadarConsoleClientInput
from ..config.server import ServerConfig


class RadarConsoleClientCLI(CLI):
    def __init__(self, program_name='', version=''):
        self._program_name = program_name
        self._version = version
        self._options = self._build_parser().parse_args()

    def _build_parser(self):
        parser = ArgumentParser(prog=self._program_name)
        parser.add_argument(
            '-a', '--address', dest='address', action='store',
            default=ServerConfig.DEFAULT_CONFIG['console']['address']
        )
        parser.add_argument(
            '-p', '--port', dest='port', action='store',
            default=ServerConfig.DEFAULT_CONFIG['console']['port']
        )
        parser.add_argument('-v', '--version', action='version', version=self._version)

        return parser


class RadarConsoleClientLauncher(RadarLauncher):

    PROGRAM_NAME = 'radar-console-client'
    PROGRAM_VERSION = '0.0.1'

    def __init__(self):
        cli = RadarConsoleClientCLI(program_name=self.PROGRAM_NAME, version=self.PROGRAM_VERSION)
        self._threads = self._build_threads(cli)

    def _build_threads(self, cli):
        queue_a, queue_b = Queue(), Queue()
        stop_event = Event()

        return [
            RadarConsoleClient(cli, queue_a, queue_b, stop_event=stop_event),
            RadarConsoleClientInput(queue_b, queue_a, stop_event=stop_event),
        ]

    def _start_and_join_threads(self):
        self._start_threads(self._threads[:1])

        while self._threads[0].is_alive() and not self._threads[0].is_connected():
            self._threads[0].join(self.THREAD_POLLING_TIME)

        # Only spawn remaining threads if the client got connected or if the
        # client is trying to reconnect.
        if self._threads[0].is_alive():
            self._start_threads(self._threads[1:])
            self._join_threads()

    def run(self):
        try:
            self._start_and_join_threads()
        except IOError as error:
            self._resume_interrupted_call(error)
        except Exception as error:
            print('Error - {:} raised an error. Details : {:}.'.format(self.__class__.__name__, error))
