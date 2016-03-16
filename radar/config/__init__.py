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


from future.utils import listitems
from abc import ABCMeta
from errno import EEXIST
from io import open
from os import getpid, mkdir, remove
from os.path import dirname, isfile as file_exists
from yaml import safe_load, YAMLError
from ..logger import RadarLogger


class ConfigError(Exception):
    pass


# TODO: Add line numbers to config dictionaries, this allows
# to report configuration errors in a precise way.
# Check : http://stackoverflow.com/questions/13319067/parsing-yaml-return-with-line-number
class ConfigBuilder(object):

    __metaclass__ = ABCMeta

    def __init__(self, path):
        self.path = path
        self.config = self._lower_config_dict(self._read_config(path) or {})
        self.logger = None

    # Merges the current config with a default config.
    def merge_config(self, default_config):
        try:
            self.config = self._merge_options(self.config, default_config)
        except AttributeError:
            raise ConfigError('Error - Wrong Radar main config format.')

    def _merge_options(self, source, destination):
        for key, value in listitems(source):
            if isinstance(value, dict):
                node = destination.setdefault(key, {})
                self._merge_options(value, node)
            else:
                destination[key] = value

        return destination

    # Lowers down all keys of our config dictionary.
    def _lower_config_dict(self, obj):
        if type(obj) == dict:
            return {key.lower(): self._lower_config_dict(value) for key, value in obj.iteritems()}
        elif type(obj) == list:
            return [self._lower_config_dict(item) for item in obj]

        return obj

    def _read_config(self, path):
        try:
            with open(path) as fd:
                return safe_load(fd)
        except (YAMLError, IOError) as error:
            raise ConfigError('Error - Couldn\'t parse YAML file : \'{:}\'. Details : {:}.'.format(path, error))

    def _filter_config(self, key):
        return [config for config in self.config if key in config]

    def _create_dir(self, path):
        try:
            mkdir(path)
        except OSError as error:
            if error.errno != EEXIST:
                raise ConfigError('Error - Couldn\'t create directory : \'{:}\'. Details : {:}.'.format(
                    path, error.strerror))

    def _write_pidfile(self, pidfile):
        self._create_dir(dirname(pidfile))

        if file_exists(pidfile):
            raise ConfigError('Error - \'{:}\' exists. Process already running ?.'.format(pidfile))

        try:
            with open(pidfile, 'w') as fd:
                fd.write(u'{:}'.format(getpid()))
        except IOError as error:
            raise ConfigError('Error - Couldn\'t write pidfile \'{:}\'. Details : {:}.'.format(pidfile, error))


    def _delete_pidfile(self, pidfile):
        try:
            remove(pidfile)
        except OSError as error:
            raise ConfigError('Error - Couldn\'t delete pidfile \'{:}\'. Details {:}.'.format(pidfile, error))

    def build(self):
        pass

    def _configure_plugins(self):
        [plugin.configure() for plugin in self.plugins]

    def _shutdown_plugins(self):
        [plugin.on_shutdown() for plugin in self.plugins]

    def configure(self, *args):
        RadarLogger(
            self.config['log']['to'], max_size=self.config['log']['size'],
            rotations=self.config['log']['rotations']
        )
        self._write_pidfile(self.config['pid file'])
        self._configure_plugins()

    def tear_down(self):
        self._shutdown_plugins()
        self._delete_pidfile(self.config['pid file'])
        RadarLogger.shutdown()
