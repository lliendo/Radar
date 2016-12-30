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

Copyright 2015 - 2017 Lucas Liendo.
"""


from errno import EINTR
from abc import ABCMeta
from argparse import ArgumentParser
from ..logger import RadarLogger
from ..platform_setup import Platform


class CLIError(Exception):
    pass


class RadarLauncherError(Exception):
    pass


class CLI(object):
    """
    Command Line Interface.

    Construct a CLI object that allows to retrieve arbitrary command
    line options.

    :param default_main_config_path: The default path to the main configuration
        file provided the user didn't supply one.
    :param program_name: Optional keyword argument that specifies the name
        of the program to be shown on the command line.
    :param version: Optional keyword argument that specifies the version
        of the program to be shown from the command line.
    """

    def __init__(self, default_main_config_path, program_name='', version=''):
        self._program_name = program_name
        self._version = version
        self._options = self._build_parser(default_main_config_path).parse_args()

    def __getattr__(self, option):
        """
        Retrieve an arbitrary command line option value or raise a
        CLIError exception if the specified option does not exist.

        :param option: The name of the command line option to be read.
        :return: A string containing the value of the specified option.
        """

        try:
            return getattr(self._options, option)
        except AttributeError:
            raise CLIError("Error - Option: '{}' does not exist.".format(option))

    def _build_parser(self, default_main_config_path):
        """
        Construct the command line argument parser.

        :param default_main_config_path: The default path to the main configuration
            file if the user does not specify one.
        :return: An `ArgumentParser` object.
        """

        parser = ArgumentParser(prog=self._program_name)
        parser.add_argument('-c', '--config', dest='main_config', action='store', default=default_main_config_path, required=False)
        parser.add_argument('-v', '--version', action='version', version=self._version)

        return parser


class RadarLauncher(object):

    __metaclass__ = ABCMeta

    PROGRAM_NAME = ''
    PROGRAM_VERSION = ''
    THREAD_POLLING_TIME = 0.2
    AVAILABLE_PLATFORMS = {}

    """
    Abstract launcher class used by both Radar server and client launchers.

    The RadarLauncher is responsible for starting, joining and stopping
    all Radar threads for both client and server.
    """

    def __init__(self):
        cli = CLI(self._get_default_main_config_path(), program_name=self.PROGRAM_NAME, version=self.PROGRAM_VERSION)
        self._platform_setup = self._setup_platform(cli.main_config)
        self._threads = []

    def _get_default_main_config_path(self):
        """
        Retrieve the default main configuration file depending the platform
        we are running on.
        """

        return self.AVAILABLE_PLATFORMS[Platform.get_platform_type()].MAIN_CONFIG_PATH

    def _setup_platform(self, main_config_path):
        """
        Construct a PlatformSetup object.

        :param main_config_path: The path to the main configuration file.
        :return: A PlatformSetup object.
        """

        platform = Platform.get_platform_type()

        try:
            platform_setup_class = self.AVAILABLE_PLATFORMS[platform]
            platform_setup = platform_setup_class(main_config_path).build().configure(self)
        except KeyError:
            raise RadarLauncherError("Error - Platform : '{}' is not available.".format(platform))

        return platform_setup

    def _start_threads(self, threads):
        """
        Start all Radar threads.

        :param threads: A list of threads to be started.
        """

        for thread in threads:
            thread.start()

    def _join_threads(self):
        """
        Join all Radar threads that are alive.
        """

        while any([thread.is_alive() for thread in self._threads]):
            for thread in self._threads:
                if thread.is_alive():
                    thread.join(self.THREAD_POLLING_TIME)

    def stop(self, *args):
        """
        Stop all Radar threads by setting `stop_event`.
        """

        for thread in self._threads:
            thread.stop_event.set()

    def _resume_interrupted_call(self, error):
        """
        Try to re-join the threads one more time for graceful termination
        only if we receive an EINTR error.

        :param error: The exception to compare its value.
        """

        if error.errno != EINTR:
            raise error

        self._join_threads()

    def _start_and_join_threads(self):
        """
        Abstract method to be implemented by concrete sub-classes.
        """

    def run(self):
        """
        Start and join all Radar threads.
        """

        try:
            RadarLogger.log('Starting {}.'.format(self.PROGRAM_NAME))
            self._start_and_join_threads()
        except IOError as error:
            self._resume_interrupted_call(error)
        except Exception as error:
            RadarLogger.log('Error - {} raised an error. Details : {}.'.format(self.__class__.__name__, error))
        finally:
            RadarLogger.log('Shutting down {}.'.format(self.PROGRAM_NAME))
            self._platform_setup.tear_down()
