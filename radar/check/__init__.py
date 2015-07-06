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
from shlex import split as split_args
from subprocess import Popen, PIPE
from ..misc import RemoteControl


class CheckError(Exception):
    pass


class Check(RemoteControl):

    STATUS = {
        'ERROR': -1,
        'OK': 0,
        'WARNING': 1,
        'SEVERE': 2,
        'UNKNOWN': 3,
        'TIMEOUT': 4,
    }

    def __new__(cls, *args, **kwargs):
        try:
            global getpwnam
            from pwd import getpwnam
        except ImportError:
            pass

        return super(Check, cls).__new__(cls, *args, **kwargs)

    def __init__(self, id=None, name='', path='', args='',
                 status=STATUS['UNKNOWN'], previous_status=STATUS['UNKNOWN'],
                 details='', data=None, enabled=True):
        super(Check, self).__init__(id=id, enabled=enabled)
        self.name = name
        self.path = path
        self.args = args
        self.status = status
        self.previous_status = previous_status
        self.details = details
        self.data = data

    # TODO: Add me to __init__().
    def _validate(self):
        if self.path == '':
            raise CheckError('Error - Missing \'path\' from check definition.')

    def update_status(self, check_status):
        updated = False

        try:
            if (self.id == check_status['id']) and (check_status['status'] in self.STATUS.values()) and self.enabled:
                self.previous_status = self.status
                self.status = check_status['status']
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
            raise CheckError('Error - Invalid status value : \'{:}\'.')

    @property
    def check_status(self):
        return Check.get_status(self.status)

    @property
    def previous_check_status(self):
        return Check.get_status(self.previous_status)

    def to_dict(self):
        return super(Check, self).to_dict([
            'id', 'name', 'path', 'args', 'status', 'previous_status',
            'details', 'data', 'enabled',
        ])

    def to_check_dict(self):
        d = super(Check, self).to_dict(['id', 'path'])

        if self.args:
            d.update({'args': self.args})

        return [d]

    def to_check_reply_dict(self):
        d = super(Check, self).to_dict(['id', 'status'])

        if self.details:
            d.update({'details': self.details})

        if self.data:
            d.update({'data': self.data})

        return d

    def _deserialize_output(self, output):
        try:
            d = {k.lower(): v for k, v in deserialize_json(output).iteritems() if k.lower() in ['status', 'details', 'data']}
            d.update({
                'status': self.STATUS[d['status'].upper()],
                'id': self.id,
            })
        except ValueError, e:
            raise CheckError('Error - Couldn\'t parse JSON from check output. Details : {:}'.format(e))
        except KeyError:
            raise CheckError('Error - Missing or invalid \'status\' from check output.')

        return d

    def _owned_by_user(self, user):
        try:
            return getpwnam(user).pw_uid == stat(self.path)['st_uid']
        except KeyError:
            raise CheckError('Error - User : \'{:}\' doesn\'t exist.'.format(user))

    def _owned_by_group(self, group):
        try:
            return getpwnam(group).pw_gid == stat(self.path)['st_gid']
        except KeyError:
            raise CheckError('Error - Group : \'{:}\' doesn\'t exist.'.format(group))

    def _owned_by(self, user, group):
        return self._owned_by_user(user) and self._owned_by_group(group)

    def _call_popen(self, user, group, enforce_ownership):
        if enforce_ownership and not self._owned_by(user, group):
            raise CheckError('Error - \'{:}\' is not owned by user : {:} / group : {:}.'.format(
                self.path, user, group))

        return Popen([self.path] + split_args(self.args), stdout=PIPE).communicate()[0]

    def run(self, user, group, enforce_ownership):
        try:
            output = self._call_popen(user, group, enforce_ownership)
            deserialized_output = self._deserialize_output(output)
            self.update_status(deserialized_output)
        except (OSError, CheckError), e:
            self.status = self.STATUS['ERROR']
            self.details = str(e)

        return self

    def as_list(self):
        return [self]

    def __eq__(self, other_check):
        return self.name == other_check.name and self.path == other_check.path and \
            self.args == other_check.args

    def __hash__(self):
        return hash(self.name) ^ hash(self.path) ^ hash(self.args)


class CheckGroup(RemoteControl):
    def __init__(self, name='', checks=[], enabled=True):
        super(CheckGroup, self).__init__(enabled=enabled)
        self.name = name
        self.checks = set(checks)

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
