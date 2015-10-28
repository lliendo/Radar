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


from unittest import TestCase
from nose.tools import raises
from mock import MagicMock
from struct import pack, unpack, calcsize
from io import BytesIO
from radar.protocol import Message, MessageNotReady
from radar.network.client import ClientAbortError


class TestRadarProtocol(TestCase):
    def setUp(self):
        self.client = MagicMock()

    def _mock_receive(self, side_effect):
        self.client.receive = MagicMock(side_effect=side_effect)

    def _receive_header(self, message, header_format):
        try:
            message._receive_header(self.client)
        except MessageNotReady:
            self.assertEqual(message.header.tell(), calcsize(header_format))

        return message.header.getvalue()

    def test_header_reception(self):
        message = Message()
        self._mock_receive([
            pack('!B', Message.TYPE['CHECK']),
            pack('!B', Message.OPTIONS['NONE']),
            pack('!H', 2),
        ])

        self.assertEqual(
            unpack('!B', self._receive_header(message, '!B')),
            (Message.TYPE['CHECK'],)
        )
        self.assertEqual(
            unpack('!BB', self._receive_header(message, '!BB')),
            (Message.TYPE['CHECK'], Message.OPTIONS['NONE'], )
        )
        self.assertEqual(
            unpack('!BBH', self._receive_header(message, '!BBH')),
            (Message.TYPE['CHECK'], Message.OPTIONS['NONE'], 2)
        )

    def _receive(self, message, message_type, message_options, payload=''):
        self._mock_receive([
            pack('!BBH', message_type, message_options, len(payload)),
            pack('!{:}s'.format(len(payload)), payload)
        ])
        return message.receive(self.client)

    @raises(ClientAbortError)
    def test_receive_raises_error_due_to_invalid_message_type(self):
        message = Message()
        self._receive(message, max(Message.TYPE.values()) + 1, Message.OPTIONS['NONE'])

    @raises(ClientAbortError)
    def test_invalid_header_due_to_invalid_message_option(self):
        message = Message()
        self._receive(message, Message.TYPE['CHECK'], max(Message.OPTIONS.values()) + 1)

    @raises(ClientAbortError)
    def test_invalid_header_due_to_invalid_message_length(self):
        message = Message()
        self._receive(message, Message.TYPE['CHECK'], max(Message.OPTIONS.values()) + 1)

    def test_payload_reception(self):
        message = Message()
        message_type, payload = self._receive(message, Message.TYPE['CHECK'], Message.OPTIONS['NONE'], '{}')
        self.assertEqual(message_type, Message.TYPE['CHECK'])
        self.assertEqual(payload, '{}')
        self.assertEqual(message.header.getvalue(), BytesIO().getvalue())
        self.assertEqual(message.payload.getvalue(), BytesIO().getvalue())
