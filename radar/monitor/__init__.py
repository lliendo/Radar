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
from ..misc import RemoteControl


class MonitorError(Exception):
    pass


# TODO: Use sets & implement __hash__ to actually get rid of duplicated monitors !
# Also re-implement __eq__ without calling set.
class Monitor(RemoteControl):
    def __init__(self, addresses=[], checks=[], contacts=[], enabled=True):
        super(Monitor, self).__init__(enabled=enabled)
        # self.addresses = addresses
        # self.checks = checks
        # self.contacts = contacts

        self.addresses = set(addresses)
        self.checks = set(checks)
        self.contacts = set(contacts)

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
        self.active_clients = [c for c in self.active_clients if c['client'] != client]

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

    def poll(self, message_type):
        message = reduce(lambda l, m: l + m, [c.to_check_dict() for c in self.checks if c.enabled])

        if message:
            [c['client'].send_message(message_type, serialize_json(message)) for c in self.active_clients]

    # TODO: This is wrong. Can't identify to which hosts the checks belong to
    # (I only get ids but not the ids associated to a particular client).
    def to_dict(self):
        d = super(Monitor, self).to_dict(['id', 'enabled'])
        # d.update({
        #     'addresses': [a.to_dict() for a in self.addresses],
        #     'checks': [c.to_dict() for c in self.checks],
        #     'contacts': [c.to_dict() for c in self.contacts],
        # })

        d.update({
            'addresses': [a.to_dict() for a in self.addresses],
            'checks': [c.to_dict() for c in self.checks],
            'contacts': [c.to_dict() for c in self.contacts],
        })

        return d

    # def __eq__(self, other_monitor):
    #     return (set(self.addresses) == set(other_monitor.addresses)) and \
    #         (set(self._checks) == set(other_monitor._checks)) and \
    #         (set(self.contacts) == set(other_monitor.contacts))

    def __eq__(self, other_monitor):
        return (self.addresses == other_monitor.addresses) and (self._checks == other_monitor._checks) and \
            (self.contacts == other_monitor.contacts)

    def __hash__(self):
        return reduce(lambda l, m: l.__hash__() ^ m.__hash__(), self.addresses.union(self.checks).union(self.contacts))
