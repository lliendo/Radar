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


from platform import system as platform_name
from os import mkdir
# from shutil import copyfile
from radar.platform_setup.server import LinuxServerSetup, WindowsServerSetup


class PlatformConfigError(Exception):
    pass


class PlatformServerConfig(object):

    AVAILABLE_PLATFORMS = {
        'Linux': LinuxServerSetup,
        'Windows': WindowsServerSetup,
    }

    def __init__(self):
        self.platform_name = platform_name()
        self.PlatformSetup = self._get_platform()

    def create_dir(self, path):
        mkdir(path)

    # def copy_main_config_file(self):
    #     copyfile()

    def configure_radar_directories(self):
        defaults = [
            ('Config directory path : [{:}] ? ', self.PlatformSetup.PLATFORM_CONFIG_PATH),
            ('Main config file path : [{:}] ? ', self.PlatformSetup.MAIN_CONFIG_PATH),
            ('Checks directory path : [{:}] ? ', self.PlatformSetup.PLATFORM_CONFIG['checks']),
            ('Contacts directory path : [{:}] ? ', self.PlatformSetup.PLATFORM_CONFIG['contacts']),
            ('Monitors directory path : [{:}] ? ', self.PlatformSetup.PLATFORM_CONFIG['monitors']),
            ('Plugins directory path : [{:}] ? ', self.PlatformSetup.PLATFORM_CONFIG['plugins']),
        ]

        for message, path in defaults:
            path = raw_input(message.format(path))

    def _get_platform(self):
        try:
            platform_setup = self.AVAILABLE_PLATFORMS[self.platform_name]
            print '\nDetected platform : {:}\n'.format(self.platform_name)
        except KeyError:
            raise PlatformConfigError('Error - Platform {:} is not currently supported.'.format(self.platform_name))

        return platform_setup

    def run(self):
        print 'Press enter for default value or input a custom one :'
        print '-----------------------------------------------------'
        self.configure_radar_directories()


if __name__ == '__main__':
    try:
        PlatformServerConfig().run()
    except Exception, e:
        print e
