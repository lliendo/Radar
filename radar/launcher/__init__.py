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
from platform import system as platform_name
from argparse import ArgumentParser


class CLIError(Exception):
    pass


class RadarLauncherError(Exception):
    pass


class CLI(object):
    def __init__(self, program_name='', version=''):
        self._program_name = program_name
        self._version = version
        self._options = self._build_parser().parse_args()

    def __getattr__(self, option):
        try:
            return getattr(self._options, option)
        except AttributeError:
            raise CLIError('Error - Option: \'{:}\' does not exist.'.format(option))

    def _build_parser(self):
        parser = ArgumentParser(prog=self._program_name)
        parser.add_argument('-c', '--config', dest='main_config', action='store', required=True)
        parser.add_argument('-v', '--version', action='version', version=self._version)

        return parser


class RadarLauncher(object):

    __metaclass__ = ABCMeta

    PROGRAM_NAME = ''
    PROGRAM_VERSION = ''
    THREAD_POLLING_TIME = 0.2
    AVAILABLE_PLATFORMS = {}

    def __init__(self):
        cli = CLI(program_name=self.PROGRAM_NAME, version=self.PROGRAM_VERSION)
        self._platform_setup = self._setup_platform(cli.main_config)

    def _get_platform_name(self):
        unixes = ['Linux', 'Darwin', 'FreeBSD', 'NetBSD', 'OpenBSD']
        platform = platform_name()
        return 'UNIX' if platform in unixes else platform

    def _setup_platform(self, path):
        platform = self._get_platform_name()

        try:
            PlatformSetup = self.AVAILABLE_PLATFORMS[platform]
            platform_setup = PlatformSetup(path).build()
        except KeyError:
            raise RadarLauncherError('Error - Platform : \'{:}\' is not available.'.format(platform))

        platform_setup.configure(self)

        return platform_setup

    def _start_threads(self, threads):
        [t.start() for t in threads]

    def _join_threads(self):
        while any([t.is_alive() for t in self._threads]):
            [t.join(self.THREAD_POLLING_TIME) for t in self._threads if t.is_alive()]

    def stop(self, *args):
        [t.stop_event.set() for t in self._threads]

    @abstractmethod
    def run(self):
        pass
