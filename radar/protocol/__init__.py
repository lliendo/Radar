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
    MAX_PAYLOAD_SIZE = 2 ** (calcsize('H') * 8)  # We assume 8 bits per byte.
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

    def __init__(self):
        self._buffer = BytesIO()

    @staticmethod
    def get_type(message_type):
        return list(Message.TYPE)[list(Message.TYPE.values()).index(message_type)]

    def _read_buffer_chunk(self, offset, n_bytes):
        current_offset = self._buffer.tell()  # Save current offset.
        self._buffer.seek(offset)
        buffer_chunk = self._buffer.read(n_bytes)
        self._buffer.seek(current_offset)  # Restore offset.

        return buffer_chunk

    def _header_received(self):
        return self._buffer.tell() >= self.HEADER_SIZE

    # A '>=' here is less sensitive to an error than '=='. Should we be strict in
    # receiving exactly HEADER_SIZE + payload_size bytes ?
    def _payload_received(self):
        _, _, payload_size = self._read_header()
        return self._buffer.tell() >= self.HEADER_SIZE + payload_size

    def _read_header(self):
        return unpack(self.HEADER_FORMAT, self._read_buffer_chunk(0, self.HEADER_SIZE))

    def _read_payload(self):
        _, _, payload_size = self._read_header()
        return self._read_buffer_chunk(self.HEADER_SIZE, payload_size)

    def _pack(self, message_type, message_options, message):
        message_length = len(message)
        pack_format = (self.HEADER_FORMAT + self.PAYLOAD_FORMAT).format(message_length)
        return pack(pack_format, message_type, message_options, message_length, message)

    def _receive(self, received_chunk, read_chunk, client, n_bytes):
        if not received_chunk():
            try:
                self._buffer.write(client.receive(n_bytes))
            except ClientDataNotReady:
                raise MessageNotReady()

            if not received_chunk():
                raise MessageNotReady()

        return read_chunk()

    def _invalid_header(self):
        message_type, message_options, payload_size = self._read_header()
        return (message_type not in list(self.TYPE.values())) or \
            (message_options not in list(self.OPTIONS.values())) or payload_size == 0

    def _receive_header(self, client):
        message_type, _, _ = self._receive(
            self._header_received, self._read_header, client,
            self.HEADER_SIZE - self._buffer.tell()
        )

        if self._invalid_header():
            self._buffer = BytesIO()
            raise ClientAbortError()

        return message_type

    def _receive_payload(self, client):
        _, _, payload_size = self._read_header()
        payload = self._receive(
            self._payload_received, self._read_payload, client,
            self.HEADER_SIZE + payload_size - self._buffer.tell()
        )
        self._buffer = BytesIO()

        return payload

    def receive(self, client):
        return self._receive_header(client), self._receive_payload(client)

    def send(self, client, message_type, message, message_options=OPTIONS['NONE']):
        packed_message = self._pack(message_type, message_options, message)
        message_length = len(packed_message)
        sent_bytes = 0

        while sent_bytes < message_length:
            sent_bytes += client.send(packed_message[sent_bytes:message_length])

        return sent_bytes
