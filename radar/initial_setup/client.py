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
from . import InitialSetup
from ..platform_setup.client import LinuxClientSetup, WindowsClientSetup


class ClientInitialSetup(InitialSetup):

    AVAILABLE_PLATFORMS = {
        'Linux': LinuxClientSetup,
        'Windows': WindowsClientSetup,
    }

    TEMPLATES_PATH = dirname(__file__) + '/templates'

    # This is ugly.
    def _get_default_configuration(self):
        return OrderedDict([
            ('address', ('Connect address ? [{:}] ', self.PlatformSetup.PLATFORM_CONFIG['connect']['to'])),
            ('port', ('Port to connect to ? [{:}] ', self.PlatformSetup.PLATFORM_CONFIG['connect']['port'])),
            ('user', ('User to run Radar client as ? [{:}] ', self.PlatformSetup.PLATFORM_CONFIG['run as']['user'])),
            ('group', ('Group to run Radar client as ? [{:}] ', self.PlatformSetup.PLATFORM_CONFIG['run as']['group'])),
            ('enforce ownership', ('Enforce check ownership ? [{:}] ', self.PlatformSetup.PLATFORM_CONFIG['enforce ownership'])),
            ('reconnect', ('Reconnect automatically to server ? [{:}] ', self.PlatformSetup.PLATFORM_CONFIG['reconnect'])),
            ('platform config', ('Config directory path ? [{:}] ', self.PlatformSetup.PLATFORM_CONFIG_PATH)),
            ('main config', ('Main config file path ? [{:}] ', self.PlatformSetup.MAIN_CONFIG_PATH)),
            ('checks', ('Checks directory path ? [{:}] ', self.PlatformSetup.PLATFORM_CONFIG['checks'])),
            ('pid file', ('Pid file ? [{:}] ', self.PlatformSetup.PLATFORM_CONFIG['pid file'])),
            ('log file', ('Log file ? [{:}] ', self.PlatformSetup.PLATFORM_CONFIG['log file'])),
        ])
