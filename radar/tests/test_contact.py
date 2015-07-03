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
from ..contact import Contact


class TestContact(TestCase):
    def setUp(self):
        self.contact = Contact()

    def test_contact_default_values(self):
        self.assertNotEqual(self.contact.id, None)
        self.assertEqual(self.contact.name, '')
        self.assertEqual(self.contact.email, '')
        self.assertEqual(self.contact.phone, '')
        self.assertEqual(self.contact.enabled, True)

    def test_contacts_are_equal(self):
        self.assertEqual(self.contact, Contact())

    def test_contacts_are_not_equal(self):
        contact = Contact(name='contact', email='')
        another_contact = Contact(name='another contact', email='another@contact.com')
        self.assertNotEqual(contact, another_contact)

    def test_to_dict(self):
        d = Contact().to_dict()
        keys = ['id', 'name', 'email', 'phone']
        self.assertTrue(all([k in d for k in keys]))

    def test_check_as_list(self):
        self.assertEqual(type(self.contact.as_list()), list)
        self.assertEqual(len(self.contact.as_list()), 1)
