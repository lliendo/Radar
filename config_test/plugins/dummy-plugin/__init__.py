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


from radar.plugin import ServerPlugin
from os.path import dirname


class DummyPlugin(ServerPlugin):

    PLUGIN_NAME = 'Dummy plugin'
    PLUGIN_CONFIG_FILE = dirname(__file__) + '/dummy.yml'

    def on_start(self):
        self._logger.log('Starting up.')

    def on_check_reply(self, address, port, checks, contacts):
        self._logger.log('Received check reply from {:}:{:}.'.format(address, port))

    def on_shutdown(self):
        self._logger.log('Shutting down.')
