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


from copy import deepcopy
from ..config.server import ServerConfig
from . import UnixSetup, WindowsSetup


class SetupError(Exception):
    pass


class UnixServerSetup(ServerConfig, UnixSetup):

    BASE_PATH = '/etc/radar/server'
    PLATFORM_CONFIG_PATH = BASE_PATH + '/config'
    MAIN_CONFIG_PATH = PLATFORM_CONFIG_PATH + '/main.yml'
    PLATFORM_CONFIG = deepcopy(ServerConfig.DEFAULT_CONFIG)
    PLATFORM_CONFIG.update({
        'checks': PLATFORM_CONFIG_PATH + '/checks',
        'contacts': PLATFORM_CONFIG_PATH + '/contacts',
        'monitors': PLATFORM_CONFIG_PATH + '/monitors',
        'plugins': '/usr/local/radar/server/plugins',
        'pid file': '/var/run/radar-server.pid',
    })
    PLATFORM_CONFIG['log']['to'] = '/var/log/radar-server.log'

    # TODO: Can we get rid of the duplicated _configure & shutdown methods ?
    def _configure_plugins(self):
        [plugin.configure() for plugin in self.plugins]

    def _shutdown_plugins(self):
        [plugin.on_shutdown() for plugin in self.plugins]

    def configure(self, launcher):
        ServerConfig.configure(self)
        UnixSetup.configure(self, launcher)
        self._configure_plugins()

        return self

    def tear_down(self):
        self._shutdown_plugins()
        super(UnixServerSetup, self).tear_down()


class WindowsServerSetup(ServerConfig, WindowsSetup):

    BASE_PATH = 'C:\\Program Files\\Radar\\Server'
    PLATFORM_CONFIG_PATH = BASE_PATH + '\\Config'
    MAIN_CONFIG_PATH = PLATFORM_CONFIG_PATH + '\\main.yml'
    PLATFORM_CONFIG = deepcopy(ServerConfig.DEFAULT_CONFIG)
    PLATFORM_CONFIG.update({
        'checks': PLATFORM_CONFIG_PATH + '\\Checks',
        'contacts': PLATFORM_CONFIG_PATH + '\\Contacts',
        'monitors': PLATFORM_CONFIG_PATH + '\\Monitors',
        'plugins': PLATFORM_CONFIG_PATH + '\\Plugins',
    })
    PLATFORM_CONFIG['log']['to'] = BASE_PATH + '\\Log\\radar-server.log'

    def _configure_plugins(self):
        [plugin.configure() for plugin in self.plugins]

    def _shutdown_plugins(self):
        [plugin.on_shutdown() for plugin in self.plugins]

    def configure(self, launcher):
        super(WindowsServerSetup, self).configure()
        self._configure_plugins()
        self._install_signal_handlers(launcher)

        return self

    def tear_down(self):
        self._shutdown_plugins()
        super(WindowsServerSetup, self).tear_down()
