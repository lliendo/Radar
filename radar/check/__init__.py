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


from functools import reduce
from json import loads as deserialize_json
from os import stat
from os.path import join as join_path, isabs as is_absolute_path
from shlex import split as split_args
from subprocess import Popen, PIPE
from ..misc import Switchable


class CheckError(Exception):
    pass


class CheckGroupError(Exception):
    pass


class Check(Switchable):

    STATUS = {
        'ERROR': -1,
        'OK': 0,
        'WARNING': 1,
        'SEVERE': 2,
        'UNKNOWN': 3,
        'TIMEOUT': 4,
    }

    def __init__(self, id=None, name='', path='', args='', details='', data=None, enabled=True, platform_setup=None):
        super(Check, self).__init__(id=id, enabled=enabled)

        if not name or not path:
            raise CheckError('Error - Missing name and/or path from check definition.')

        self.name = name
        self.path = path
        self.args = args
        self.details = details
        self.data = data
        self.current_status = self.STATUS['UNKNOWN']
        self.previous_status = self.STATUS['UNKNOWN']
        self._platform_setup = platform_setup

    def _update_matches(self, check_status):
        return (self.id == check_status['id']) and (check_status['status'] in self.STATUS.values()) and \
            self.enabled

    def update_status(self, check_status):
        updated = False

        try:
            if self._update_matches(check_status):
                self.previous_status = self.current_status
                self.current_status = check_status['status']
                self.details = check_status.get('details', '')
                self.data = check_status.get('data', None)
                updated = True
        except KeyError:
            raise CheckError('Error - Can\'t update check\'s status. Missing id and/or status from check reply.')

        return updated

    @staticmethod
    def get_status(status):
        try:
            return Check.STATUS.keys()[Check.STATUS.values().index(status)]
        except ValueError:
            raise CheckError('Error - Invalid status value : \'{:}\'.'.format(status))

    def to_dict(self):
        return super(Check, self).to_dict([
            'id', 'name', 'path', 'args', 'current_status', 'previous_status',
            'details', 'data', 'enabled',
        ])

    def to_check_dict(self):
        d = super(Check, self).to_dict(['id', 'path'])

        if self.args:
            d.update({'args': self.args})

        return [d]

    def to_check_reply_dict(self):
        d = {
            'id': self.id,
            'status': self.current_status,
        }

        if self.details:
            d.update({'details': self.details})

        if self.data:
            d.update({'data': self.data})

        return d

    def _deserialize_output(self, output):
        try:
            valid_fields = ['status', 'details', 'data']
            d = {k.lower(): v for k, v in deserialize_json(output).iteritems() if k.lower() in valid_fields}
            d.update({
                'status': self.STATUS[d['status'].upper()],
                'id': self.id,
            })
        except ValueError as e:
            raise CheckError('Error - Couldn\'t parse JSON from check output. Details : {:}'.format(e))
        except KeyError:
            raise CheckError('Error - Missing or invalid \'status\' from check output.')

        return d

    def _build_absolute_path(self):
        checks_directory = self._platform_setup.PLATFORM_CONFIG['checks']
        return [self.path if is_absolute_path(self.path) else join_path(checks_directory, self.path)]

    def _split_args(self):
        return split_args(self.args)

    def _call_popen(self):
        absolute_path = self._build_absolute_path()
        filename = absolute_path[len(absolute_path) - 1]

        if self._platform_setup.config['enforce ownership'] and not self._owned_by_stated_user(filename):
            raise CheckError('Error - \'{:}\' is not owned by user : {:} / group : {:}.'.format(
                filename,
                self._platform_setup.config['run as']['user'],
                self._platform_setup.config['run as']['group']
            ))

        try:
            return Popen(absolute_path + self._split_args(), stdout=PIPE).communicate()[0]
        except OSError as e:
            raise CheckError('Error - Couldn\'t run : {:} check. Details : {:}'.format(absolute_path, e))

    def run(self):
        try:
            deserialized_output = self._deserialize_output(self._call_popen())
            self.update_status(deserialized_output)
        except CheckError as e:
            self.current_status = self.STATUS['ERROR']
            self.details = str(e)

        return self

    def as_list(self):
        return [self]

    def __eq__(self, other_check):
        return self.name == other_check.name and self.path == other_check.path and \
            self.args == other_check.args

    def __hash__(self):
        return hash(self.name) ^ hash(self.path) ^ hash(self.args)


class UnixCheck(Check):
    def __new__(cls, *args, **kwargs):
        try:
            global getpwnam
            from pwd import getpwnam
        except ImportError:
            pass

        return super(UnixCheck, cls).__new__(cls, *args, **kwargs)

    def _owned_by_user(self, filename):
        user = self._platform_setup.config['run as']['user']

        try:
            return getpwnam(user).pw_uid == stat(filename).st_uid
        except KeyError:
            raise CheckError('Error - User : \'{:}\' doesn\'t exist.'.format(user))

    def _owned_by_group(self, filename):
        group = self._platform_setup.config['run as']['group']

        try:
            return getpwnam(group).pw_gid == stat(filename).st_gid
        except KeyError:
            raise CheckError('Error - Group : \'{:}\' doesn\'t exist.'.format(group))

    def _owned_by_stated_user(self, filename):
        return self._owned_by_user(filename) and self._owned_by_group(filename)


class WindowsCheck(Check):
    def __new__(cls, *args, **kwargs):
        try:
            global FindExecutable, FindExecutableError, GetFileSecurity, LookupAccountSid, OWNER_SECURITY_INFORMATION
            from win32security import GetFileSecurity, LookupAccountSid, OWNER_SECURITY_INFORMATION
            from win32api import FindExecutable
            from pywintypes import error as FindExecutableError
        except ImportError:
            pass

        return super(WindowsCheck, cls).__new__(cls, *args, **kwargs)

    def _find_interpreter(self, filename):
        try:
            return FindExecutable(filename)
        except FindExecutableError as e:
            raise CheckError('Error - Couldn\'t find executable for : {:}. Details : {:}.'.format(filename, e))

    # If the file isn't just executable we need to know who interprets this filetype,
    # otherwise popen fails.
    def _build_absolute_path(self):
        absolute_path = super(WindowsCheck, self)._build_absolute_path().pop()
        _, interpreter = self._find_interpreter(absolute_path)
        executable = [interpreter, absolute_path]

        if interpreter == absolute_path:
            executable.pop()

        return executable

    def _owned_by_user(self, filename):
        try:
            security_descriptor = GetFileSecurity(filename, OWNER_SECURITY_INFORMATION)
            user, _, _ = LookupAccountSid(None, security_descriptor.GetSecurityDescriptorOwner())
            return user == self._platform_setup.config['run as']['user']
        except MemoryError as e:
            raise CheckError('Error - Couldn\'t get owner of : {:}. Details : {:}.'.format(filename, e))

    def _owned_by_stated_user(self, filename):
        return self._owned_by_user(filename)

    def _split_args(self):
        return split_args(self.args, posix=False)


class CheckGroup(Switchable):
    def __init__(self, name='', checks=None, enabled=True):
        super(CheckGroup, self).__init__(enabled=enabled)

        if not name or not checks:
            raise CheckGroupError('Error - Missing name and/or checks from check group definition.')

        self.name = name
        self.checks = set(checks) if checks is not None else []

    def update_status(self, check_status):
        return any([c.update_status(check_status) for c in self.checks])

    def to_dict(self):
        d = super(CheckGroup, self).to_dict(['id', 'name', 'enabled'])
        d.update({'checks': [c.to_dict() for c in self.checks]})
        return d

    def to_check_dict(self):
        return reduce(lambda l, m: l + m, [c.to_check_dict() for c in self.checks])

    def as_list(self):
        return [c for c in self.checks]

    def __eq__(self, other_check_group):
        return self.name == other_check_group.name and self.checks == other_check_group.checks

    def __hash__(self):
        if len(self.checks) > 1:
            hashed = hash(self.name) ^ reduce(lambda l, m: l.__hash__() ^ m.__hash__(), self.checks)
        else:
            hashed = hash(self.name) ^ list(self.checks).pop().__hash__()

        return hashed
