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
from platform import system as platform_name
from os import chmod, makedirs
from errno import EEXIST
from stat import S_IRUSR, S_IWUSR, S_IXUSR


class InitialSetupError(Exception):
    pass


class InitialSetup(object):

    __metaclass__ = ABCMeta

    def __init__(self):
        self.platform_name = platform_name()
        self.PlatformSetup = self._get_platform_setup()

    def _get_platform_setup(self):
        try:
            PlatformSetup = self.AVAILABLE_PLATFORMS[self.platform_name]
            print '\nDetected platform : {:}\n'.format(self.platform_name)
        except KeyError:
            raise InitialSetupError('Error - Platform {:} is not currently supported.'.format(self.platform_name))

        return PlatformSetup

    def _configure(self, configuration):
        for k, (message, path) in configuration.iteritems():
            path = raw_input(message.format(path)) or path
            configuration[k] = (message, path)

        return configuration

    def _create_directory(self, path):
        try:
            makedirs(path)
        except OSError, e:
            if (e.errno != EEXIST):
                raise InitialSetupError('Error - Couldn\'t create : \'{:}\'. Details : {:}.'.format(path, e))

        try:
            chmod(path, S_IRUSR | S_IWUSR | S_IXUSR)
        except Exception, e:
            raise InitialSetupError('Error - Couldn\'t change permission of : \'{:}\' directory. Details : {:}.'.format(path, e))

    def _create_directories(self, configuration, directory_keys=[]):
        [self._create_directory(path) for k, (_, path) in configuration.iteritems() if k in directory_keys]

    def _read_template(self, path):
        with open(path, 'r') as fd:
            return fd.read()

    def _render_template(self, template, configuration):
        return template.format(*[v for _, (_, v) in configuration.iteritems()])

    def _save_template(self, template, path):
        with open(path, 'a') as fd:
            fd.write(template)

        try:
            chmod(path, S_IRUSR | S_IWUSR)
        except Exception, e:
            raise InitialSetupError('Error - Couldn\'t change permission of : \'{:}\' file. Details : {:}.'.format(path, e))

    def _print_header(self):
        print 'Press enter for default value or input a custom one :'
        print '-----------------------------------------------------\n'

    def _run(self, template_name):
        self._print_header()
        configuration = self._configure(self._get_default_configuration())
        self._create_directories(configuration, directory_keys=['platform config', 'checks', 'contacts', 'monitors', 'plugins'])
        template = self._read_template(self.TEMPLATES_PATH + '/{:}'.format(template_name))
        self._save_template(self._render_template(template, configuration), configuration['main config'][1])

    def run(self, template_name=''):
        try:
            self._run(template_name)
            print 'Done !'
        except KeyboardInterrupt:
            print '\n\nAborting configuration...'
        except Exception, e:
            print e
