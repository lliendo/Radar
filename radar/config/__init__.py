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
        self.config = self._lower_config_keys(self._read_config(path) or {})
        self.logger = None

    # Merges the current config with a default config.
    def merge_config(self, default_config):
        try:
            self.config = self._merge_options(self.config, default_config)
        except AttributeError:
            raise ConfigError('Error - Wrong Radar main config format.')

    def _merge_options(self, source, destination):
        for key, value in source.items():
            if isinstance(value, dict):
                node = destination.setdefault(key, {})
                self._merge_options(value, node)
            else:
                destination[key] = value

        return destination

    # TODO: This is ugly and not woking properly !
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
        except (YAMLError, IOError) as e:
            raise ConfigError('Error - Couldn\'t parse YAML file : \'{:}\'. Details : {:}.'.format(path, e))

    def _filter_config(self, key):
        return [config for config in self.config if key in config]

    def build(self):
        pass

    def configure(self, *args):
        self.logger = RadarLogger(
            self.config['log']['to'], max_size=self.config['log']['size'],
            rotations=self.config['log']['rotations']
        )

    def tear_down(self):
        self.logger.shutdown()
