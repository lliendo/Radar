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


from io import BytesIO
from struct import pack, unpack, calcsize
from ..network.client import ClientDataNotReady, ClientAbortError


class MessageNotReady(Exception):
    pass


class Message(object):

    HEADER_FORMAT = '!BBH'
    HEADER_SIZE = calcsize(HEADER_FORMAT)
    MAX_PAYLOAD_SIZE = 65536
    PAYLOAD_FORMAT = '{:}s'

    TYPE = {
        'TEST': 0,
        'TEST REPLY': 1,
        'CHECK': 2,
        'CHECK REPLY': 3,
    }

    OPTIONS = {
        'NONE': 0x00,
        'COMPRESS': 0x01,
    }

    # TODO: Use just one buffer ?
    def __init__(self):
        self.header = BytesIO()
        self.payload = BytesIO()

    @staticmethod
    def get_type(message_type):
        return Message.TYPE.keys()[Message.TYPE.values().index(message_type)]

    def _header_received(self):
        return len(self.header.getvalue()) == self.HEADER_SIZE

    def _payload_received(self, payload_size):
        return len(self.payload.getvalue()) == payload_size

    def _unpack_header(self, header):
        return unpack(self.HEADER_FORMAT, header)

    def _unpack_payload(self, payload, payload_size):
        return unpack(('!' + self.PAYLOAD_FORMAT).format(payload_size), payload)

    def _pack(self, message_type, message_options, message):
        message_length = len(message)
        pack_format = (self.HEADER_FORMAT + self.PAYLOAD_FORMAT).format(message_length)
        return pack(pack_format, message_type, message_options, message_length, message)

    # TODO: Better way ? _receive_header & _receive_payload are the same...
    # Will it help to use a single buffer ?
    def _receive_header(self, client):
        if not self._header_received():
            try:
                received_bytes = client.receive(self.HEADER_SIZE - len(self.header.getvalue()))
                self.header.write(received_bytes)
            except ClientDataNotReady:
                raise MessageNotReady()

            if not self._header_received():
                raise MessageNotReady()

        return self.header.getvalue()

    def _receive_payload(self, client, payload_size):
        if not self._payload_received(payload_size):
            try:
                received_bytes = client.receive(payload_size - len(self.payload.getvalue()))
                self.payload.write(received_bytes)
            except ClientDataNotReady:
                raise MessageNotReady()

            if not self._payload_received(payload_size):
                raise MessageNotReady()

        return self.payload.getvalue()

    def _reset_buffers(self):
        self.header = BytesIO()
        self.payload = BytesIO()

    def receive(self, client):
        message_type, message_options, payload_size = self._unpack_header(self._receive_header(client))
        payload = self._receive_payload(client, payload_size)
        self._reset_buffers()

        if message_type not in self.TYPE.values():
            raise ClientAbortError()

        return message_type, payload

    def send(self, client, message_type, message, message_options=OPTIONS['NONE']):
        packed_message = self._pack(message_type, message_options, message)
        message_length = len(packed_message)
        sent_bytes = 0

        while sent_bytes < message_length:
            sent_bytes += client.send(packed_message[sent_bytes:message_length])

        return sent_bytes
