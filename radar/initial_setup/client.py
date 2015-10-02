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
from ..platform_setup.client import UnixClientSetup, WindowsClientSetup


class ClientInitialSetup(InitialSetup):

    AVAILABLE_PLATFORMS = {
        'UNIX': UnixClientSetup,
        'Windows': WindowsClientSetup,
    }

    def _get_config_dict(self):
        return {
            'connect': {
                'to': 'Server address ? [{:}] ',
                'port': 'Server port ? [{:}] ',
            },

            'run as': {
                'user': 'User to run Radar client as ? [{:}] ',
                'group': 'Group to run Radar client as ? [{:}] ',
            },

            'log': {
                'to': 'Log file ? [{:}] ',
                'size': 'Log max size ? [{:}] ',
                'rotations': 'Log max rotations ? [{:}] ',
            },

            'enforce ownership': 'Enforce check ownership ? [{:}] ',
            'reconnect': 'Reconnect automatically to server ? [{:}] ',
            'pid file': 'Pid file ? [{:}] ',
            'checks': 'Checks directory ? [{:}] ',
        }

    def _create_directories(self, config):
        directories = [
            dirname(config['log']['to']),
            dirname(config['pid file']),
            config['checks'],
        ]

        [self._create_directory(d) for d in directories]
