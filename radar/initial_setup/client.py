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
from ..platform_setup.client import UnixClientSetup, WindowsClientSetup


class UnixClientInitialSetup(object):
    def _get_config_dict(self):
        return {
            'run as': {
                'user': 'User to run Radar client as ? [{:}] ',
                'group': 'Group to run Radar client as ? [{:}] ',
            },

            'pid file': 'Pid file ? [{:}] ',
        }

    def _get_directories(self, config):
        return [
            dirname(config['pid file']),
        ]


class WindowsClientInitialSetup(object):
    def _get_config_dict(self):
        return {
            'run as': {
                'user': 'User to run Radar client as ? [{:}] ',
            },
        }

    def _get_directories(self, config):
        return []


class ClientInitialSetup(InitialSetup):

    __metaclass__ = ABCMeta

    AVAILABLE_PLATFORMS = {
        'Unix': (UnixClientInitialSetup, UnixClientSetup),
        'Windows': (WindowsClientInitialSetup, WindowsClientSetup),
    }

    def _build_config_dict(self):
        config = {
            'connect': {
                'to': 'Server address ? [{:}] ',
                'port': 'Server port ? [{:}] ',
            },

            'log': {
                'to': 'Log file ? [{:}] ',
                'size': 'Log max size ? [{:}] ',
                'rotations': 'Log max rotations ? [{:}] ',
            },

            'enforce ownership': 'Enforce check ownership ? [{:}] ',
            'reconnect': 'Reconnect automatically to server ? [{:}] ',
            'checks': 'Checks directory ? [{:}] ',
        }

        config.update(self.user_setup._get_config_dict())

        return config

    def _create_directories(self, config):
        directories = [
            dirname(config['log']['to']),
            config['checks'],
        ]

        [self._create_directory(d) for d in directories + self.user_setup._get_directories(config)]
