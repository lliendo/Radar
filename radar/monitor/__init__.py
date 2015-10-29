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


from json import dumps as serialize_json
from copy import deepcopy
from functools import reduce
from ..logger import RadarLogger
from ..misc import Switchable
from ..network.client import ClientSendError


class MonitorError(Exception):
    pass


class Monitor(Switchable):
    def __init__(self, name='', addresses=None, checks=None, contacts=None, enabled=True):
        super(Monitor, self).__init__(enabled=enabled)
        self.name = name
        self.addresses = set(addresses) if addresses is not None else []
        self.checks = set(checks) if checks is not None else []
        self.contacts = set(contacts) if contacts is not None else []
        self.active_clients = []
        self._validate()

    def _validate(self):
        try:
            attr = [attr for attr in ['addresses', 'checks'] if not getattr(self, attr)].pop()
            raise MonitorError('Error - Missing \'{:}\' from monitor definition.'.format(attr))
        except IndexError:
            pass

    def matches(self, new_client):
        return (new_client not in [c['client'] for c in self.active_clients]) and \
            any([new_client.address in a for a in self.addresses])

    def add_client(self, client):
        added = False

        if self.matches(client):
            self.active_clients.append({
                'client': client,
                'checks': deepcopy(self.checks),
                'contacts': deepcopy(self.contacts),
            })
            added = True

        return added

    def remove_client(self, client):
        removed = False
        pre_remove_clients_count = len(self.active_clients)

        self.active_clients = [c for c in self.active_clients if c['client'] != client]

        if len(self.active_clients) < pre_remove_clients_count:
            removed = True

        return removed

    def update_checks(self, client, statuses):
        updated = {}

        try:
            active_client = [c for c in self.active_clients if c['client'] == client].pop()
            updated_checks = [c for c in active_client['checks'] for s in statuses if c.update_status(s)]

            if updated_checks:
                updated['checks'] = set(updated_checks)
                updated['contacts'] = set([c for c in active_client['contacts'] if c.enabled])
        except IndexError:
            pass

        return updated

    def _poll_client(self, client, message_type, message):
        try:
            client.send_message(message_type, serialize_json(message))
        except ClientSendError as e:
            RadarLogger.log(e)

    def poll(self, message_type):
        message = reduce(lambda l, m: l + m, [c.to_check_dict() for c in self.checks if c.enabled])
        [self._poll_client(c['client'], message_type, message) for c in self.active_clients]

        return message

    def _active_client_to_dict(self, active_client):
        return {
            'address': active_client['client'].address,
            'checks': [c.to_dict() for c in active_client['checks']],
            'contacts': [c.to_dict() for c in active_client['contacts']],
        }

    def to_dict(self):
        d = super(Monitor, self).to_dict(['id', 'name', 'enabled'])
        d.update({
            'clients': [self._active_client_to_dict(c) for c in self.active_clients]
        })

        return d

    def __eq__(self, other_monitor):
        return (self.addresses == other_monitor.addresses) and (self.checks == other_monitor.checks) and \
            (self.contacts == other_monitor.contacts)

    def __hash__(self):
        sets_union = self.addresses.union(self.checks).union(self.contacts)
        return hash(self.name) ^ reduce(lambda l, m: l.__hash__() ^ m.__hash__(), sets_union)
