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
from os.path import join as join_path
from stat import S_ISREG
from copy import deepcopy
from . import ConfigBuilder, ConfigError
from ..check import Check, CheckGroup, CheckError, CheckGroupError
from ..contact import Contact, ContactGroup, ContactError, ContactGroupError
from ..monitor import Monitor
from ..misc import Address, AddressRange, AddressError, SequentialIdGenerator
from ..class_loader import ClassLoader
from ..plugin import ServerPlugin


class ContactBuilder(ConfigBuilder):

    TAG = 'contact'

    def _build_contact(self, contact):
        return Contact(enabled=contact[ContactBuilder.TAG].get('enabled', True), **contact[ContactBuilder.TAG])

    def _build_contacts(self, contacts):
        return set([self._build_contact(c) for c in contacts])

    def build(self):
        try:
            return list(self._build_contacts(self._filter_config(self.TAG)))
        except ContactError as e:
            raise ConfigError(str(e) + ' File {:}'.format(self.path))


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
            contact = super(ContactGroupBuilder, self)._build_contact(contact)
        except ContactError:
            contact = self._copy_contact(contact['contact']['name'], defined_contacts)

        return contact

    def _build_contacts(self, contacts, defined_contacts):
        return [self._build_contact(c, defined_contacts) for c in contacts]

    def _build_contact_group(self, contact_group, defined_contacts):
        contact_group = contact_group[ContactGroupBuilder.TAG]

        return ContactGroup(
            name=contact_group['name'],
            contacts=self._build_contacts(contact_group['contacts'], defined_contacts),
            enabled=contact_group.get('enabled', True)
        )

    def _build_contact_groups(self, contact_groups, defined_contacts):
        try:
            return set([self._build_contact_group(cg, defined_contacts) for cg in contact_groups])
        except TypeError:
            raise ConfigError('Error - Invalid contact group format.')

    def build(self, defined_contacts):
        try:
            return list(self._build_contact_groups(self._filter_config(ContactGroupBuilder.TAG), defined_contacts))
        except ContactGroupError as e:
            raise ConfigError(str(e) + ' File {:}'.format(self.path))


class CheckBuilder(ConfigBuilder):

    TAG = 'check'

    def _build_check(self, check):
        return Check(enabled=check.get('enabled', True), **check[CheckBuilder.TAG])

    def _build_checks(self, checks):
        return set([self._build_check(c) for c in checks])

    def build(self):
        try:
            return list(self._build_checks(self._filter_config(CheckBuilder.TAG)))
        except CheckError as e:
            raise ConfigError(str(e) + ' File {:}'.format(self.path))


class CheckGroupBuilder(CheckBuilder):

    TAG = 'check group'

    def _copy_check(self, check_name, defined_checks):
        try:
            check = deepcopy([c for c in defined_checks if c.name == check_name].pop())
            check.id = SequentialIdGenerator().generate()
        except IndexError:
            raise ConfigError('Error - Check \'{:}\' does not exist.'.format(check_name))

        return check

    def _build_check(self, check, defined_checks):
        try:
            check = super(CheckGroupBuilder, self)._build_check(check)
        except CheckError:
            check = self._copy_check(check['check']['name'], defined_checks)

        return check

    def _build_checks(self, checks, defined_checks):
        return [self._build_check(c, defined_checks) for c in checks]

    def _build_check_group(self, check_group, defined_checks):
        check_group = check_group[CheckGroupBuilder.TAG]

        return CheckGroup(
            name=check_group['name'],
            checks=self._build_checks(check_group['checks'], defined_checks),
            enabled=check_group.get('enabled', True)
        )

    def _build_check_groups(self, check_groups, defined_checks):
        try:
            return set([self._build_check_group(cg, defined_checks) for cg in check_groups])
        except TypeError:
            raise ConfigError('Error - Invalid check group format.')

    def build(self, defined_checks):
        try:
            return list(self._build_check_groups(self._filter_config(CheckGroupBuilder.TAG), defined_checks))
        except CheckGroupError as e:
            raise ConfigError(str(e) + ' File {:}'.format(self.path))


# TODO: When merging with updated 'ipv6-support' branch, also remove _build_address()
# method from MonitorBuilder and use the AddressBuilder.
class AddressBuilder(object):
    def __init__(self, addresses):
        self._addresses = addresses

    def _build_address(self, address):
        for A in [Address, AddressRange]:
            try:
                return A(address)
            except AddressError as error:
                address_error = error

        raise address_error

    def build(self):
        return [self._build_address(address) for address in self._addresses]


class MonitorBuilder(ConfigBuilder):

    TAG = 'monitor'

    def _build_address(self, address):
        for A in [Address, AddressRange]:
            try:
                return A(address)
            except AddressError as e:
                error = e

        raise error

    def _build_monitor(self, monitor, checks, contacts):
        monitor = monitor[self.TAG]

        return Monitor(
            name=monitor.get('name', ''),
            addresses=[self._build_address(address) for address in monitor['hosts']],
            checks=[c for c in checks if c.name in monitor['watch']],
            contacts=[c for c in contacts if c.name in monitor['notify']],
            enabled=monitor.get('enabled', True)
        )

    def _build_monitors(self, monitors, checks, contacts):
        return set([self._build_monitor(m, checks, contacts) for m in monitors])

    def build(self, checks, contacts):
        try:
            monitors_config = self._filter_config(self.TAG)
            monitors = list(self._build_monitors(monitors_config, checks, contacts))
        except KeyError as e:
            raise ConfigError('Error - Missing \'{:}\' while creating monitor from {:}.'.format(e.args[0], self.path))
        except TypeError as e:
            raise ConfigError('Error - Either hosts, checks or contacts are not a YAML list in monitor definition. File : {:}.'.format(
                e.args[0], self.path))

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

        'console': {
            'address': None,
            'port': 3334,
            'allowed hosts': [],
        },

        'polling time': 300,
    }

    def __init__(self, path=None):
        super(ServerConfig, self).__init__(path or self.MAIN_CONFIG_PATH)
        self.merge_config(self.PLATFORM_CONFIG)
        self.monitors = []
        self.plugins = []

    def _search_files(self, path):
        files = [join_path(root, f) for root, _, files in walk(path) for f in files]
        return [f for f in files if S_ISREG(stat(f).st_mode)]

    def _build_and_reduce(self, Builder, files, builder_args=None):
        builder_args = builder_args if builder_args is not None else []
        return reduce(lambda l, m: l + m, [Builder(f).build(*builder_args) for f in files])

    def _build_contacts(self):
        files = self._search_files(self.config['contacts'])

        try:
            contacts = self._build_and_reduce(ContactBuilder, files)
            contact_groups = self._build_and_reduce(ContactGroupBuilder, files, builder_args=[contacts])
        except TypeError:
            return []

        return contacts + contact_groups

    def _build_checks(self):
        files = self._search_files(self.config['checks'])

        try:
            checks = self._build_and_reduce(CheckBuilder, files)
            check_groups = self._build_and_reduce(CheckGroupBuilder, files, builder_args=[checks])
        except TypeError:
            raise ConfigError('Error - No defined checks could be found.')

        return checks + check_groups

    def _build_monitors(self, checks, contacts):
        files = self._search_files(self.config['monitors'])

        try:
            return self._build_and_reduce(MonitorBuilder, files, builder_args=[checks, contacts])
        except TypeError:
            raise ConfigError('Error - No defined monitors could be found.')

    def _load_plugins(self):
        plugin_classes = ClassLoader(self.config['plugins']).get_classes(subclass=ServerPlugin)
        return set([P() for P in plugin_classes])

    def build(self):
        self.monitors = self._build_monitors(self._build_checks(), self._build_contacts())
        self.plugins = self._load_plugins()
        return self
