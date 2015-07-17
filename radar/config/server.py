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
from functools import reduce
from os import walk, stat
from os.path import join
from stat import S_ISREG
from . import ConfigBuilder, ConfigError
from ..check import Check, CheckGroup
from ..contact import Contact, ContactGroup
from ..monitor import Monitor
from ..misc import Address, AddressRange, AddressError
from ..class_loader import ClassLoader
from ..plugin import ServerPlugin


class ContactBuilder(ConfigBuilder):

    TAG = 'contact'
    GROUP_TAG = 'contact group'

    def _build_contact(self, contact):
        contact = contact[self.TAG]

        return Contact(
            name=contact['name'],
            email=contact['email'],
            phone=contact.get('phone', ''),
            enabled=contact.get('enabled', True)
        )

    def _build_contacts(self, contacts):
        return [self._build_contact(c) for c in contacts]

    def _build_contact_group(self, contact_group):
        contact_group = contact_group[self.GROUP_TAG]

        return ContactGroup(
            name=contact_group['name'],
            contacts=self._build_contacts(contact_group['contacts']),
            enabled=contact_group.get('enabled', True)
        )

    def _build_contact_groups(self, contact_groups):
        return set([self._build_contact_group(cg) for cg in contact_groups])

    def build(self):
        try:
            contacts_config = self._filter_config(self.TAG)
            contacts = list(self._build_contacts(contacts_config))
        except KeyError, e:
            raise ConfigError('Error - Missing \'{:}\' while creating contact from \'{:}\'.'.format(e.args[0], self.path))

        try:
            contact_groups_config = self._filter_config(self.GROUP_TAG)
            contact_groups = list(self._build_contact_groups(
                contact_groups_config))
        except KeyError, e:
            raise ConfigError('Error - Missing \'{:}\' while creating contact team from \'{:}\'.'.format(e.args[0], self.path))

        return contacts + contact_groups


class CheckBuilder(ConfigBuilder):

    TAG = 'check'
    GROUP_TAG = 'check group'

    def _build_check(self, check):
        check = check[self.TAG]

        return Check(
            name=check['name'],
            path=check['path'],
            args=check.get('args', ''),
            enabled=check.get('enabled', True)
        )

    def _build_checks(self, checks):
        return [self._build_check(c) for c in checks]

    def _build_check_group(self, check_group):
        check_group = check_group[self.GROUP_TAG]

        return CheckGroup(
            name=check_group['name'],
            checks=self._build_checks(check_group['checks']),
            enabled=check_group.get('enabled', True)
        )

    def _build_check_groups(self, check_groups):
        return set([self._build_check_group(cg) for cg in check_groups])

    def build(self):
        try:
            checks_config = self._filter_config(self.TAG)
            checks = list(self._build_checks(checks_config))
        except KeyError, e:
            raise ConfigError('Error - Missing \'{:}\' while creating check from {:}.'.format(e.args[0], self.path))

        try:
            check_groups_config = self._filter_config(self.GROUP_TAG)
            check_groups = list(self._build_check_groups(check_groups_config))
        except KeyError, e:
            raise ConfigError('Error - Missing \'{:}\' while creating check group from {:}.'.format(e.args[0], self.path))

        return checks + check_groups


class MonitorBuilder(ConfigBuilder):

    TAG = 'monitor'

    def __init__(self, path, checks, contacts):
        super(MonitorBuilder, self).__init__(path)
        self.checks = checks
        self.contacts = contacts

    def _build_address(self, address):
        for A in [Address, AddressRange]:
            try:
                return A(address)
            except AddressError, e:
                error = e

        raise error

    def _build_monitor(self, monitor):
        monitor = monitor[self.TAG]

        return Monitor(
            name=monitor.get('name', ''),
            addresses=[self._build_address(address) for address in monitor['hosts']],
            checks=[c for c in self.checks if c.name in monitor['watch']],
            contacts=[c for c in self.contacts if c.name in monitor['notify']],
            enabled=monitor.get('enabled', True)
        )

    def _build_monitors(self, monitors):
        return set([self._build_monitor(m) for m in monitors])

    def build(self):
        try:
            monitors_config = self._filter_config(self.TAG)
            monitors = list(self._build_monitors(monitors_config))
        except KeyError, e:
            raise ConfigError('Error - Missing \'{:}\' while creating monitor from {:}.'.format(e.args[0], self.path))

        return monitors


class ServerConfig(ConfigBuilder):

    __metaclass__ = ABCMeta

    DEFAULT_CONFIG = {
        'listen': {
            'address': '',
            'port': 3333,
        },

        'run as': {
            'user': 'radar',
            'group': 'radar',
        },

        'polling time': 300,
    }

    def __init__(self, path=None):
        super(ServerConfig, self).__init__(path or self.MAIN_CONFIG_PATH)
        self._set_default_config()
        self.monitors = []
        self.plugins = []

    def _search_files(self, path):
        files = [join(root, f) for root, _, files in walk(path) for f in files]
        return [f for f in files if S_ISREG(stat(f).st_mode)]

    def _build_contacts(self):
        files = self._search_files(self.config['contacts'])
        return reduce(lambda l, m: l + m, [ContactBuilder(f).build() for f in files])

    def _build_checks(self):
        files = self._search_files(self.config['checks'])
        return reduce(lambda l, m: l + m, [CheckBuilder(f).build() for f in files])

    def _build_monitors(self):
        checks = self._build_checks()
        contacts = self._build_contacts()
        files = self._search_files(self.config['monitors'])
        return reduce(lambda l, m: l + m, [MonitorBuilder(f, checks, contacts).build() for f in files])

    def _load_plugins(self):
        plugin_classes = ClassLoader(self.config['plugins']).get_classes(subclass=ServerPlugin)
        return set([P() for P in plugin_classes])

    def build(self):
        self.monitors = self._build_monitors()
        self.plugins = self._load_plugins()
        return self
