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


from functools import reduce
from ..misc import RemoteControl


class ContactError(Exception):
    pass


class Contact(RemoteControl):
    def __init__(self, id=None, name='', email='', phone='', enabled=True):
        super(Contact, self).__init__(id=id, enabled=enabled)

        if not name or not email:
            raise ContactError('Error - Missing name and/or email from contact definition.')

        self.name = name
        self.email = email
        self.phone = phone

    def to_dict(self):
        return super(Contact, self).to_dict(['id', 'name', 'email', 'phone', 'enabled'])

    def as_list(self):
        return [self]

    def __eq__(self, other_contact):
        return self.name == other_contact.name and self.email == other_contact.email and \
            self.phone == other_contact.phone

    def __hash__(self):
        return hash(self.name) ^ hash(self.email) ^ hash(self.phone)


class ContactGroup(RemoteControl):
    def __init__(self, name='', contacts=[], enabled=True):
        super(ContactGroup, self).__init__(enabled=enabled)

        if not name or not contacts:
            raise ContactError('Error - Missing name and/or contacts from contact group definition.')

        self.name = name
        self.contacts = set(contacts)

    def to_dict(self):
        d = super(ContactGroup, self).to_dict(['id', 'name', 'enabled'])
        d.update({'contacts': [c.to_dict() for c in self.contacts]})
        return d

    def as_list(self):
        return [c for c in self.contacts]

    def __eq__(self, other_contact_group):
        return self.name == other_contact_group.name \
            and self.contacts == other_contact_group.contacts

    def __hash__(self):
        if len(self.contacts) > 1:
            hashed = hash(self.name) ^ reduce(lambda l, m: l.__hash__() ^ m.__hash__(), self.contacts)
        else:
            hashed = hash(self.name) ^ list(self.contacts).pop().__hash__()

        return hashed
