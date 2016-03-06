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
from builtins import input
from io import open
from functools import reduce
from os.path import dirname
from os import chmod, makedirs
from errno import EEXIST
from stat import S_IRUSR, S_IWUSR, S_IXUSR
from yaml import dump as dump_yaml
from ..platform_setup import Platform


class InitialSetupError(Exception):
    pass


class InitialSetup(object):

    __metaclass__ = ABCMeta

    def __init__(self):
        self.user_setup, self.PlatformSetup = self._get_setup()

    def _get_setup(self):
        platform = Platform.get_platform_type()

        try:
            user_setup, platform_setup = self.AVAILABLE_PLATFORMS[platform]
            print('\nDetected platform : {:}\n'.format(platform))
        except KeyError:
            raise InitialSetupError('Error - Platform {:} is not currently supported.'.format(platform))

        return user_setup(), platform_setup

    def _read_value(self, console_message, default_value):
        correct_type = False
        inputted_value = ''

        while not correct_type:
            try:
                inputted_value = type(default_value)(input(console_message.format(default_value)) or default_value)
                correct_type = True
            except ValueError:
                pass

        return inputted_value

    def _read_config(self, config):
        for path in self._generate_dict_paths(config):
            console_message = self._read_dict_path(config, path)
            default_value = self._read_dict_path(self.PlatformSetup.PLATFORM_CONFIG, path)
            self._write_to_dict_path(config, path, self._read_value(console_message, default_value))

        return config

    # Generates all paths to all values of an arbitrary nested dictionary.
    def _generate_dict_paths(self, d, path=None):
        if not path:
            path = []

        if isinstance(d, dict):
            for x in list(d):
                local_path = path[:]
                local_path.append(x)

                for b in self._generate_dict_paths(d[x], local_path):
                    yield b
        else:
            yield path

    # Given a path of keys access the dictionary applying all those keys recursively.
    def _read_dict_path(self, d, path):
        return reduce(lambda d, k: d[k], path, d)

    # Given a path to an arbitrary nested dictionary, updates a value.
    def _write_to_dict_path(self, d, path, value):
        self._read_dict_path(d, path[:-1])[path[-1]] = value

    def _create_directory(self, path):
        try:
            makedirs(path, mode=0755)
            chmod(path, S_IRUSR | S_IWUSR | S_IXUSR)
        except OSError as error:
            if error.errno != EEXIST:
                raise InitialSetupError('Error - Couldn\'t create : \'{:}\'. Details : {:}.'.format(path, error))
        except Exception as error:
            raise InitialSetupError('Error - Couldn\'t change permission of : \'{:}\' directory. Details : {:}.'.format(path, error))

    def _save_yaml(self, config):
        console_message = 'Path to main config ? [{:}] '.format(self.PlatformSetup.MAIN_CONFIG_PATH)
        main_config_path = input(console_message) or self.PlatformSetup.MAIN_CONFIG_PATH
        self._create_directory(dirname(main_config_path))

        with open(main_config_path, 'w') as fd:
            fd.write(u'{:}'.format(dump_yaml(config, default_flow_style=False, indent=4, line_break='\n\n')))

    def _print_header(self):
        print('Press enter for default values or input a custom one :')
        print('------------------------------------------------------\n')

    def _run(self):
        self._print_header()
        config = self._read_config(self._build_config_dict())
        self._create_directories(config)
        self._save_yaml(config)

    def run(self):
        try:
            self._run()
            print('\nDone !\n')
        except KeyboardInterrupt:
            print('\n\nAborting configuration...')
        except Exception as error:
            print(error)
