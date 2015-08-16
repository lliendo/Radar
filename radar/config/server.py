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
from copy import deepcopy
from . import ConfigBuilder, ConfigError
from ..check import Check, CheckGroup
from ..contact import Contact, ContactGroup, ContactError
from ..monitor import Monitor
from ..misc import Address, AddressRange, AddressError, SequentialIdGenerator
from ..class_loader import ClassLoader
from ..plugin import ServerPlugin


class ContactBuilder(ConfigBuilder):

    TAG = 'contact'

    def _build_contact(self, contact):
        return Contact(enabled=contact[self.TAG].get('enabled', True), **contact[self.TAG])

    def _build_contacts(self, contacts):
        return set([self._build_contact(c) for c in contacts])

    def build(self):
        try:
            return list(self._build_contacts(self._filter_config(self.TAG)))
        except KeyError, e:
            raise ConfigError('Error - Missing \'{:}\' while creating contact from \'{:}\'.'.format(e.args[0], self.path))


class ContactGroupBuilder(ContactBuilder):

    TAG = 'contact group'

    def _copy_contact(self, contact_name, defined_contacts):
        try:
            contact = deepcopy([c for c in defined_contacts if c.name == contact_name].pop())
            contact.id = SequentialIdGenerator().generate()
        except IndexError:
            raise ConfigError('Error - Contact \'{:}\' does not exist.'.format(contact_name))

        return contact

    def _build_contact(self, contact, defined_contacts):
        try:
            contact = Contact(enabled=contact['contact'].get('enabled', True), **contact['contact'])
        except ContactError:
            contact = self._copy_contact(contact['contact']['name'], defined_contacts)

        return contact

    def _build_contacts(self, contacts, defined_contacts):
        return [self._build_contact(c, defined_contacts) for c in contacts]

    def _build_contact_group(self, contact_group, defined_contacts):
        contact_group = contact_group[self.TAG]

        return ContactGroup(
            name=contact_group['name'],
            contacts=self._build_contacts(contact_group['contacts'], defined_contacts),
            enabled=contact_group.get('enabled', True)
        )

    def _build_contact_groups(self, contact_groups, defined_contacts):
        return set([self._build_contact_group(cg, defined_contacts) for cg in contact_groups])

    def build(self, defined_contacts):
        try:
            return list(self._build_contact_groups(self._filter_config(self.TAG), defined_contacts))
        except KeyError, e:
            raise ConfigError('Error - Missing \'{:}\' while creating contact group from \'{:}\'.'.format(e.args[0], self.path))


class CheckBuilder(ConfigBuilder):

    TAG = 'check'

    def _build_check(self, check):
        return Check(enabled=check.get('enabled', True), **check[self.TAG])

    def _build_checks(self, checks):
        return set([self._build_check(c) for c in checks])

    def build(self):
        try:
            return list(self._build_checks(self._filter_config(self.TAG)))
        except KeyError, e:
            raise ConfigError('Error - Missing \'{:}\' while creating check from {:}.'.format(e.args[0], self.path))


class CheckGroupBuilder(CheckBuilder):

    TAG = 'check group'

    def _copy_check(self, check_name, defined_checks):
        try:
            check = deepcopy([c for c in defined_checks if c.name == check_name].pop())
            check.id = SequentialIdGenerator().generate()
        except IndexError:
            raise ConfigError('Error - Check \'{:}\' does not exist.'.format(contact_name))

        return check

    def _build_check(self, check, defined_checks):
        try:
            check = Check(enabled=check['check'].get('enabled', True), **check['check'])
        except ContactError:
            check = self._copy_check(check['check']['name'], defined_checks)

        return check

    def _build_checks(self, checks, defined_checks):
        return [self._build_check(c, defined_checks) for c in checks]

    def _build_check_group(self, check_group, defined_checks):
        check_group = check_group[self.TAG]

        return CheckGroup(
            name=check_group['name'],
            checks=self._build_checks(check_group['checks'], defined_checks),
            enabled=check_group.get('enabled', True)
        )

    def _build_check_groups(self, check_groups, defined_checks):
        return set([self._build_check_group(cg, defined_checks) for cg in check_groups])

    def build(self, defined_checks):
        try:
            return list(self._build_check_groups(self._filter_config(self.TAG), defined_checks))
        except KeyError, e:
            raise ConfigError('Error - Missing \'{:}\' while creating check group from {:}.'.format(e.args[0], self.path))


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
            'address': 'localhost',
            'port': 3333,
        },

        'run as': {
            'user': 'radar',
            'group': 'radar',
        },

        'log': {
            'to': '',
            'size': 100,
            'rotations': 5,
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
        contacts = reduce(lambda l, m: l + m, [ContactBuilder(f).build() for f in files])
        contact_groups = reduce(lambda l, m: l + m, [ContactGroupBuilder(f).build(contacts) for f in files])

        return contacts + contact_groups

    def _build_checks(self):
        files = self._search_files(self.config['checks'])
        checks = reduce(lambda l, m: l + m, [CheckBuilder(f).build() for f in files])
        check_groups = reduce(lambda l, m: l + m, [CheckGroupBuilder(f).build(checks) for f in files])

        return checks + check_groups

    def _build_monitors(self, contacts, checks):
        files = self._search_files(self.config['monitors'])
        return reduce(lambda l, m: l + m, [MonitorBuilder(f, checks, contacts).build() for f in files])

    def _load_plugins(self):
        plugin_classes = ClassLoader(self.config['plugins']).get_classes(subclass=ServerPlugin)
        return set([P() for P in plugin_classes])

    def build(self):
        self.monitors = self._build_monitors(self._build_contacts(), self._build_checks())
        self.plugins = self._load_plugins()
        return self
