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
from io import open
from os import getpid, mkdir
from os.path import dirname, isfile as file_exists
from signal import signal, SIGTERM, SIGINT
from platform import system as platform_name
from errno import EEXIST


class UnixSetupError(Exception):
    pass


class Platform(object):

    __metaclass__ = ABCMeta

    SUPPORTED_OS_TYPES = [
        'BSD',
        'Linux',
        'Windows'
    ]

    @staticmethod
    def get_platform_type():
        unixes = ['Linux', 'Darwin', 'FreeBSD', 'NetBSD', 'OpenBSD']
        platform = platform_name()
        return 'Unix' if platform in unixes else platform

    @staticmethod
    def get_os_type():
        bsds = ['Darwin', 'FreeBSD', 'NetBSD', 'OpenBSD']
        platform = platform_name()
        platform = 'BSD' if platform in bsds else platform
        return 'Unknown' if platform not in Platform.SUPPORTED_OS_TYPES else platform


class UnixSetup(object):

    __metaclass__ = ABCMeta

    def __new__(cls, *args, **kwargs):
        try:
            global chown, getpwnam, getgrnam, seteuid, setegid, setgroups
            from os import chown, seteuid, setegid, setgroups
            from pwd import getpwnam
            from grp import getgrnam
        except ImportError as e:
            raise UnixSetupError('Error - Couldn\'t import Unix permission functions. Details : {:}.'.format(e))

        return object.__new__(cls, *args, **kwargs)

    def _create_dir(self, path):
        try:
            mkdir(path)
        except OSError as e:
            if e.errno != EEXIST:
                raise UnixSetupError('Error - Couldn\'t create directory : \'{:}\'. Details : {:}.'.format(
                    path, e.strerror))

    def _write_pid_file(self, pidfile, user, group):
        self._create_dir(dirname(pidfile))

        if file_exists(pidfile):
            raise UnixSetupError('Error - \'{:}\' exists. Process already running ?.'.format(pidfile))

        try:
            with open(pidfile, 'w') as fd:
                fd.write(u'{:}'.format(getpid()))

            chown(pidfile, getpwnam(user).pw_uid, getgrnam(group).gr_gid)
        except IOError as e:
            raise UnixSetupError('Error - Couldn\'t write pidfile \'{:}\'. Details : {:}.'.format(pidfile, e))
        except OSError as e:
            raise UnixSetupError('Error - Couldn\'t change permissions for pidfile \'{:}\'. Details : {:}.'.format(pidfile, e))

    def _install_signal_handlers(self, launcher):
        signal(SIGTERM, launcher.stop)
        signal(SIGINT, launcher.stop)

    def _switch_process_owner(self, user, group):
        try:
            setgroups([])
            setegid(getgrnam(group).gr_gid)
            seteuid(getpwnam(user).pw_uid)
        except OSError as e:
            raise UnixSetupError('Error - Couldn\'t switch process owner \'{:}.{:}\'. Details {:}.'.format(
                user, group, e))
        except KeyError:
            raise UnixSetupError('Error - User or group \'{:}.{:}\' does not exist.'.format(user, group))


class WindowsSetup(object):

    __metaclass__ = ABCMeta

    def _install_signal_handlers(self, launcher):
        signal(SIGTERM, launcher.stop)
        signal(SIGINT, launcher.stop)
