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


from abc import ABCMeta
from os.path import dirname
from . import InitialSetup
from ..platform_setup.server import UnixServerSetup, WindowsServerSetup


class UnixServerInitialSetup(object):
    def _get_config_dict(self):
        return {
            'run as': {
                'user': 'User to run Radar server as ? [{:}] ',
                'group': 'Group to run Radar server as ? [{:}] ',
            },

            'pid file': 'Pid file ? [{:}] ',
        }

    def _get_directories(self, config):
        return [
            dirname(config['pid file']),
        ]


# As there are no Windows platform specific options, the class is empty.
class WindowsServerInitialSetup(object):
    def _get_config_dict(self):
        return {}

    def _get_directories(self, config):
        return []


class ServerInitialSetup(InitialSetup):

    __metaclass__ = ABCMeta

    AVAILABLE_PLATFORMS = {
        'Unix': (UnixServerInitialSetup, UnixServerSetup),
        'Windows': (WindowsServerInitialSetup, WindowsServerSetup),
    }

    def _build_config_dict(self):
        config = {
            'listen': {
                'address': 'Listen address ? [{:}] ',
                'port': 'Listen on ? [{:}] ',
            },

            'log': {
                'to': 'Log file ? [{:}] ',
                'size': 'Log max size ? [{:}] ',
                'rotations': 'Log max rotations ? [{:}] ',
            },

            'console': {
                'address': 'Console listen address ? [{:}]',
                'port': 'Console listen port ? [{:}]',
                'allowed hosts': 'Console allowed hosts ? [{:}] (format: [IPv4 | IPv6 | HOSTNAME, IPv4 range | IPv6 range, ...])',
            },

            'polling time': 'Polling time ? [{:}] ',
            'checks': 'Checks directory ? [{:}] ',
            'monitors': 'Monitors directory ? [{:}] ',
            'contacts': 'Contacts directory ? [{:}] ',
            'plugins': 'Plugins directory ? [{:}] ',
        }

        config.update(self.user_setup._get_config_dict())

        return config

    def _create_directories(self, config):
        directories = [
            dirname(config['log']['to']),
            config['checks'],
            config['monitors'],
            config['contacts'],
            config['plugins'],
        ]

        for directory in directories + self.user_setup._get_directories(config):
            self._create_directory(directory)
