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
from radar.config.server import ContactGroupBuilder
from radar.contact import Contact


class MockedContactGroupBuilder(ContactGroupBuilder):
    def _read_config(self, path):
        return safe_load(path)


class TestContactBuilder(TestCase):
    def test_repeated_contacts_group_are_excluded(self):
        f = StringIO("""
        - contact group:
            name: A
            contacts:
                - contact:
                    name: B
                    email: B

                - contact:
                    name: C
                    email: C

        - contact group:
            name: A
            contacts:
                - contact:
                    name: B
                    email: B

                - contact:
                    name: C
                    email: C
        """)

        contacts = [
            Contact(name='B', email='B'),
            Contact(name='C', email='C'),
        ]

        contact_group = MockedContactGroupBuilder(f).build(contacts)
        self.assertEqual(len(contact_group), 1)
        self.assertTrue(contacts[0] in contact_group[0].contacts)
        self.assertTrue(contacts[1] in contact_group[0].contacts)

    @raises(ConfigError)
    def test_non_existent_contact_raises_config_error(self):
        f = StringIO("""
        - contact group:
            name: A
            contacts:
                - contact:
                    name: B
                    email: B

                - contact:
                    name: C
        """)

        contacts = [
            Contact(name='B', email='B'),
        ]

        MockedContactGroupBuilder(f).build(contacts)

    def test_contacts_are_referenced(self):
        f = StringIO("""
        - contact group:
            name: A
            contacts:
                - contact:
                    name: B

                - contact:
                    name: C
        """)

        contacts = [
            Contact(name='B', email='B'),
            Contact(name='C', email='C'),
        ]

        contact_group = MockedContactGroupBuilder(f).build(contacts)
        self.assertEqual(len(contact_group[0].contacts), 2)
        self.assertTrue(contacts[0] in contact_group[0].contacts)
        self.assertTrue(contacts[1] in contact_group[0].contacts)
