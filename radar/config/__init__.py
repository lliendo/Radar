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


from abc import ABCMeta, abstractmethod
from yaml import safe_load
from ..logger import RadarLogger


class ConfigError(Exception):
    pass


# TODO: Add line numbers to config dictionaries, this allows
# to report configuration errors in a precise way.
# Check : http://stackoverflow.com/questions/13319067/parsing-yaml-return-with-line-number
# Also move YAML parsing to another class, so it may be used alse by ServerPlugin class.
class ConfigBuilder(object):

    __metaclass__ = ABCMeta

    def __init__(self, path):
        self.path = path
        self.config = self._lower_config_keys(self._read_config(path))
        self.logger = None

    def _lower_config_keys(self, config):
        if type(config) == list:
            return [self._lower_config_keys(d) for d in config]

        for k in config.keys():
            if type(config[k]) == dict:
                config[k.lower()] = self._lower_config_keys(config.pop(k))
            elif type(config[k]) == list and all([type(e) == str for e in config[k]]):
                config[k.lower()] = config.pop(k)
            elif type(config[k]) == list:
                config[k.lower()] = [self._lower_config_keys(d) for d in config[k]]
            else:
                config[k.lower()] = config.pop(k)

        return config

    # TODO: Add YAML exception catch.
    def _read_config(self, path):
        try:
            with open(path) as fd:
                return safe_load(fd)
        except IOError, e:
            raise ConfigError('Error - Couldn\'t open config file : \'{:}\'. Details : {:}.'.format(path, e))

    def _filter_config(self, key):
        return [config for config in self.config if key in config]

    @abstractmethod
    def build(self):
        pass

    def configure(self):
        self.logger = RadarLogger(self.config['log file'])

    def tear_down(self):
        self.logger.shutdown()
