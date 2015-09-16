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
from os import getpid, remove, mkdir
from os.path import dirname, isfile as file_exists
from signal import signal, SIGTERM, SIGINT
from errno import EEXIST


class UnixSetupError(Exception):
    pass


class UnixSetup(object):

    __metaclass__ = ABCMeta

    def __new__(cls, *args, **kwargs):
        try:
            global getpwnam, getgrnam, seteuid, setegid
            from os import seteuid, setegid
            from pwd import getpwnam
            from grp import getgrnam
        except ImportError:
            raise UnixSetupError('')

        return object.__new__(cls, *args, **kwargs)

    def _create_dir(self, path):
        try:
            mkdir(path)
        except OSError, e:
            if e.errno != EEXIST:
                raise UnixSetupError('Error - Couldn\'t create directory : \'{:}\'. Details : {:}.'.format(
                    path, e.strerror))

    def _write_pid_file(self, pidfile):
        self._create_dir(dirname(pidfile))

        if file_exists(pidfile):
            raise UnixSetupError('Error - \'{:}\' exists. Process already running ?.'.format(pidfile))

        try:
            with open(pidfile, 'w') as fd:
                fd.write(str(getpid()))
        except IOError, e:
            raise UnixSetupError('Error - Couldn\'t write pidfile \'{:}\'. Details : {:}.'.format(pidfile, e))

    def _install_signal_handlers(self, launcher):
        signal(SIGTERM, launcher.stop)
        signal(SIGINT, launcher.stop)

    def _switch_process_owner(self, user, group):
        try:
            seteuid(getpwnam(user).pw_uid)
            setegid(getgrnam(group).gr_gid)
        except OSError, e:
            raise UnixSetupError('Error - Couldn\'t switch process owner \'{:}.{:}\'. Details {:}.'.format(
                user, group, e))
        except KeyError:
            raise UnixSetupError('Error - User or group \'{:}.{:}\' does not exist.'.format(user, group))

    def _delete_pid_file(self, pidfile):
        try:
            remove(pidfile)
        except OSError, e:
            raise UnixSetupError(('Error - Couldn\'t delete pidfile \'{:}\'. Details {:}.').format(pidfile, e))


class WindowsSetup(object):

    __metaclass__ = ABCMeta

    def _install_signal_handlers(self, launcher):
        signal(SIGTERM, launcher.stop)
        signal(SIGINT, launcher.stop)
