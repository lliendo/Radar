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
from yaml.error import YAMLError
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

    def _set_default_config(self):
        try:
            [self.config.setdefault(k, self.PLATFORM_CONFIG[k]) for k in self.PLATFORM_CONFIG.keys()]
        except AttributeError:
            raise ConfigError('Error - Wrong Radar main config format.')

    def _lower_config_keys(self, config):
        if type(config) == list:
            return [self._lower_config_keys(d) for d in config]

        for k in config.keys():
            if type(config[k]) == dict:
                lowered = self._lower_config_keys(config.pop(k))
            elif type(config[k]) == list and all([type(e) == str for e in config[k]]):
                lowered = config.pop(k)
            elif type(config[k]) == list:
                lowered = [self._lower_config_keys(d) for d in config[k]]
            else:
                lowered = config.pop(k)

            config[k.lower()] = lowered

        return config

    def _read_config(self, path):
        try:
            with open(path) as fd:
                return safe_load(fd)
        except (YAMLError, IOError), e:
            raise ConfigError('Error - Couldn\'t parse YAML file : \'{:}\'. Details : {:}.'.format(path, e))

    def _filter_config(self, key):
        return [config for config in self.config if key in config]

    @abstractmethod
    def build(self):
        pass

    def configure(self, *args):
        self.logger = RadarLogger(self.config['log file'])

    def tear_down(self):
        self.logger.shutdown()
