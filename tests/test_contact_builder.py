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
from StringIO import StringIO
from yaml import safe_load
from radar.config import ConfigError
from radar.config.server import ContactBuilder


class MockedContactBuilder(ContactBuilder):
    def _read_config(self, path):
        return safe_load(path)


class TestContactBuilder(TestCase):
    def test_repeated_contacts_are_excluded(self):
        f = StringIO("""
        - contact:
            name: A
            email: A

        - contact:
            name: B
            email: B

        - contact:
            name: A
            email: A

        - contact:
            name: B
            email: B
        """)

        self.assertEqual(len(MockedContactBuilder(f).build()), 2)

    @raises(ConfigError)
    def test_missing_name_raises_config_error(self):
        f = StringIO("""
        - contact:
            name: A
            email: A

        - contact:
            email: B
        """)

        MockedContactBuilder(f).build()

    @raises(ConfigError)
    def test_missing_email_raises_config_error(self):
        f = StringIO("""
        - contact:
            name: A
            email: A

        - contact:
            name: B
        """)

        MockedContactBuilder(f).build()
