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


from collections import OrderedDict
from os.path import dirname
from radar.initial_setup import InitialSetup
from radar.platform_setup.server import LinuxServerSetup, WindowsServerSetup


class ServerInitialSetup(InitialSetup):

    AVAILABLE_PLATFORMS = {
        'Linux': LinuxServerSetup,
        'Windows': WindowsServerSetup,
    }

    TEMPLATES_PATH = dirname(__file__) + '/templates'

    def _get_default_configuration(self):
        return OrderedDict([
            ('address', ('Listen address ? [{:}] ', self.PlatformSetup.PLATFORM_CONFIG['listen']['address'])),
            ('port', ('Port to listen on ? [{:}] ', self.PlatformSetup.PLATFORM_CONFIG['listen']['port'])),
            ('user', ('User to run Radar as ? [{:}] ', self.PlatformSetup.PLATFORM_CONFIG['run as']['user'])),
            ('group', ('Group to run Radas as ? [{:}] ', self.PlatformSetup.PLATFORM_CONFIG['run as']['group'])),
            ('polling time', ('Polling time ? [{:}] ', self.PlatformSetup.PLATFORM_CONFIG['polling time'])),
            ('platform config', ('Config directory path ? [{:}] ', self.PlatformSetup.PLATFORM_CONFIG_PATH)),
            ('main config', ('Main config file path ? [{:}] ', self.PlatformSetup.MAIN_CONFIG_PATH)),
            ('checks', ('Checks directory path ? [{:}] ', self.PlatformSetup.PLATFORM_CONFIG['checks'])),
            ('contacts', ('Contacts directory path ? [{:}] ', self.PlatformSetup.PLATFORM_CONFIG['contacts'])),
            ('monitors', ('Monitors directory path ? [{:}] ', self.PlatformSetup.PLATFORM_CONFIG['monitors'])),
            ('plugins', ('Plugins directory path ? [{:}] ', self.PlatformSetup.PLATFORM_CONFIG['plugins'])),
            ('pid file', ('Pid file ? [{:}] ', self.PlatformSetup.PLATFORM_CONFIG['pid file'])),
            ('log file', ('Log file ? [{:}] ', self.PlatformSetup.PLATFORM_CONFIG['log file'])),
        ])


if __name__ == '__main__':
    ServerInitialSetup().run(template_name='radar-server.templ')
