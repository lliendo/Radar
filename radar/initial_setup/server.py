#!/usr/bin/env python

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


from os.path import dirname
from . import InitialSetup
from ..platform_setup.server import UnixServerSetup, WindowsServerSetup


class ServerInitialSetup(InitialSetup):

    AVAILABLE_PLATFORMS = {
        'UNIX': UnixServerSetup,
        'Windows': WindowsServerSetup,
    }

    def _get_config_dict(self):
        return {
            'listen': {
                'address': 'Listen address ? [{:}] ',
                'port': 'Listen on ? [{:}] ',
            },

            'run as': {
                'user': 'User to run Radar server as ? [{:}] ',
                'group': 'Group to run Radar server as ? [{:}] ',
            },

            'log': {
                'to': 'Log file ? [{:}] ',
                'size': 'Log max size ? [{:}] ',
                'rotations': 'Log max rotations ? [{:}] ',
            },

            'polling time': 'Polling time ? [{:}] ',
            'pid file': 'Pid file ? [{:}] ',
            'checks': 'Checks directory ? [{:}] ',
            'monitors': 'Monitors directory ? [{:}] ',
            'contacts': 'Contacts directory ? [{:}] ',
            'plugins': 'Plugins directory ? [{:}] ',
        }

    def _create_directories(self, config):
        directories = [
            dirname(config['log']['to']),
            dirname(config['pid file']),
            config['checks'],
            config['monitors'],
            config['contacts'],
            config['plugins'],
        ]

        [self._create_directory(d) for d in directories]
