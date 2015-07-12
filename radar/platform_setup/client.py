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


from ..config.client import ClientConfig
from . import LinuxSetup


class LinuxClientSetup(ClientConfig, LinuxSetup):

    BASE_PATH = '/etc/radar/client'
    PLATFORM_CONFIG_PATH = BASE_PATH + '/config'
    MAIN_CONFIG_PATH = PLATFORM_CONFIG_PATH + '/radar.yml'
    PLATFORM_CONFIG = ClientConfig.DEFAULT_CONFIG
    PLATFORM_CONFIG.update({
        'pidfile': '/var/run/radar/client.pid',
        'log file': '/var/log/radar/client.log',
        'checks': '/usr/local/radar/client/checks'
    })

    def configure(self, launcher):
        super(LinuxClientSetup, self).configure()
        self._write_pid_file(self.config['pidfile'])
        self._install_signal_handlers(launcher)
        self._switch_process_owner(self.config['run as']['user'], self.config['run as']['group'])

    def tear_down(self, launcher):
        self._delete_pid_file(self.config['pidfile'])
        super(LinuxClientSetup, self).tear_down()


class WindowsClientSetup(ClientConfig):

    BASE_PATH = 'C:\\Program Files\\Radar\\Client'
    PLATFORM_CONFIG_PATH = BASE_PATH + '\\Config'
    MAIN_CONFIG_PATH = PLATFORM_CONFIG_PATH + '\\radar.yml'
    PLATFORM_CONFIG = ClientConfig.DEFAULT_CONFIG
    PLATFORM_CONFIG.update({
        'log file': BASE_PATH + '\\Log\\client.log',
    })

    # TODO : Enforce ownership is not currently available on Windows platforms.
    # Try to make this option available.
    def _disable_enforce_ownership(self):
        self.config['enforce ownership'] = False

    def configure(self, launcher):
        super(WindowsClientSetup, self).configure()
        self._disable_enforce_ownership()
