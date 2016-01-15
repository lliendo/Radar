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


from ..logger import RadarLogger
from ..protocol import RadarMessage
from ..check import Check


class ClientManager(object):
    def __init__(self, monitors):
        self._monitors = monitors
        self._message_actions = {
            RadarMessage.TYPE['CHECK REPLY']: self._on_check_reply,
            RadarMessage.TYPE['TEST REPLY']: self._on_test_reply,
        }

    def matches_any_monitor(self, client):
        return any([m.matches(client) for m in self._monitors])

    def _update_checks(self, client, statuses):
        updated_checks = [m.update_checks(client, statuses) for m in self._monitors if m.enabled]
        return [uc for uc in updated_checks if uc]

    def register(self, client):
        [m.add_client(client) for m in self._monitors]

    def unregister(self, client):
        [m.remove_client(client) for m in self._monitors]

    def poll(self, message_type=RadarMessage.TYPE['CHECK']):
        [m.poll(message_type) for m in self._monitors if m.enabled]

    def _log_reply(self, client, message_type, check):
        check['status'] = Check.get_status(check['status'])
        RadarLogger.log('{:} from {:}:{:} -> {:}'.format(
            RadarMessage.get_type(message_type), client.address, client.port,
            check)
        )
        check['status'] = Check.STATUS[check['status']]

    def _log_incoming_message(self, client, message_type, message):
        [self._log_reply(client, message_type, check) for check in message]

    def _on_check_reply(self, client, message_type, message):
        self._log_incoming_message(client, message_type, message)
        return self._update_checks(client, message)

    # Yes, is the same as above ! This implementation may change in the future.
    def _on_test_reply(self, client, message_type, message):
        return self._on_check_reply(client, message_type, message)

    def process_message(self, client, message_type, message):
        updated_checks = []

        try:
            action = self._message_actions[message_type]
            updated_checks = action(client, message_type, message)
        except KeyError:
            RadarLogger.log('Error - Client {:}:{:} sent unknown message id \'{:}\'.'.format(
                client.address, client.port, message_type))

        return updated_checks

    def to_dict(self):
        return {'monitors': [monitor.to_dict() for monitor in self._monitors]}

    def enable(self, ids=None):
        [monitor.enable(ids=ids) for monitor in self._monitors]

    def disable(self, ids=None):
        [monitor.disable(ids=ids) for monitor in self._monitors]
