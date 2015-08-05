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
from radar.contact import Contact, ContactGroup


class TestContactGroup(TestCase):
    def setUp(self):
        self.contact_group = ContactGroup(name='contact group', contacts=[Contact(name='contact', email='contact@contact.com')])

    def test_contact_group_default_values(self):
        self.assertNotEqual(self.contact_group.id, None)
        self.assertEqual(type(self.contact_group.contacts), set)
        self.assertNotEqual(len(self.contact_group.contacts), 0)
        self.assertEqual(self.contact_group.enabled, True)

    def test_contact_groups_are_equal(self):
        self.assertEqual(self.contact_group, ContactGroup(name='contact group', contacts=[Contact(name='contact', email='contact@contact.com')]))

    def test_contact_groups_are_not_equal(self):
        contact = Contact(name='contact', email='contact@contact.com')
        another_contact = Contact(name='another contact', email='another@contact.com')
        self.assertNotEqual(ContactGroup(name='contact group 1', contacts=[contact]), ContactGroup(name='contact group 2', contacts=[another_contact]))

    def test_contact_groups_set(self):
        contact = Contact(name='contact', email='contact@contact.com')
        another_contact = Contact(name='another contact', email='another@contact.com')
        self.assertEqual(len(set([ContactGroup(name='contact group 1', contacts=[contact, another_contact]), ContactGroup(name='contact group 1', contacts=[contact, another_contact])])), 1)
        self.assertEqual(len(set([ContactGroup(name='contact group 1', contacts=[contact]), ContactGroup(name='contact group 2', contacts=[another_contact])])), 2)

    def test_to_dict(self):
        d = self.contact_group.to_dict()
        keys = ['id', 'name', 'contacts', 'enabled']
        self.assertTrue(all([k in d for k in keys]))

    # def test_check_as_list(self):
    #     self.assertEqual(type(self.contact.as_list()), list)
    #     self.assertEqual(len(self.contact.as_list()), 1)
