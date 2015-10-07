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
from . import ConfigBuilder


class ClientConfig(ConfigBuilder):

    __metaclass__ = ABCMeta

    DEFAULT_CONFIG = {
        'connect': {
            'to': 'localhost',
            'port': 3333,
        },

        'run as': {
            'user': 'radar',
            'group': 'radar',
        },

        'log': {
            'to': '',
            'size': 100,
            'rotations': 5,
        },

        'enforce ownership': True,
        'reconnect': True,
    }

    def __init__(self, path=None):
        super(ClientConfig, self).__init__(path or self.MAIN_CONFIG_PATH)
        self.merge_config(self.PLATFORM_CONFIG)

    def build(self):
        return self
