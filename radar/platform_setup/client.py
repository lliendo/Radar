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

Copyright 2015 - 2017 Lucas Liendo.
"""


from copy import deepcopy
from ..config.client import ClientConfig
from . import UnixSetup, WindowsSetup


class UnixClientSetup(ClientConfig, UnixSetup):

    BASE_PATH = '/etc/radar/client'
    PLATFORM_CONFIG_PATH = BASE_PATH + '/config'
    MAIN_CONFIG_PATH = PLATFORM_CONFIG_PATH + '/main.yml'
    PLATFORM_CONFIG = deepcopy(ClientConfig.DEFAULT_CONFIG)
    PLATFORM_CONFIG.update({
        'pid file': '/var/run/radar-client.pid',
        'checks': '/usr/local/radar/client/checks'
    })
    PLATFORM_CONFIG['log']['to'] = '/var/log/radar-client.log'

    """
    The UnixClientSetup class performs the configuration and
    setup of a Radar client on a Unix platform.

    This class also defines all default paths to files and
    directories needed during setup.
    """

    def configure(self, launcher):
        """
        Perform client configuration and Unix setup.

        :param launcher: A `RadarLauncher` object.
        :return: A `UnixClientSetup` object.
        """

        ClientConfig.configure(self)
        UnixSetup.configure(self, launcher)

        return self


class WindowsClientSetup(ClientConfig, WindowsSetup):

    BASE_PATH = 'C:\\Program Files\\Radar\\Client'
    PLATFORM_CONFIG_PATH = BASE_PATH + '\\Config'
    MAIN_CONFIG_PATH = PLATFORM_CONFIG_PATH + '\\main.yml'
    PLATFORM_CONFIG = deepcopy(ClientConfig.DEFAULT_CONFIG)
    PLATFORM_CONFIG.update({
        'checks': PLATFORM_CONFIG_PATH + '\\Checks',
    })
    PLATFORM_CONFIG['log']['to'] = BASE_PATH + '\\Log\\radar-client.log'

    """
    The WindowsClientSetup class performs the configuration and
    setup of a Radar client on a Windows platform.

    This class also defines all default paths to files and
    directories needed during setup.
    """

    def configure(self, launcher):
        """
        Perform client configuration and Windows setup.

        :param launcher: A `RadarLauncher` object.
        :return: A `WindowsClientSetup` object.
        """

        ClientConfig.configure(self)
        WindowsSetup.configure(self, launcher)

        return self
