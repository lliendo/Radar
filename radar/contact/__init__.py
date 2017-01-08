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

Copyright 2015 - 2017 Lucas Liendo.
"""


from functools import reduce
from ..misc import Switchable


class ContactError(Exception):
    pass


class ContactGroupError(Exception):
    pass


class Contact(Switchable):

    """
    This class represents a person who can be contacted through its
    email or phone number.

    :param id: A unique integer that identifies a contact.
    :param name: A string containing a person's name.
    :param email: A string containing a person's email.
    :param phone: A string containing a person's mobile or phone number.
    :param enabled: A boolean indicating if the contact is enabled or not.
    """

    def __init__(self, id=None, name='', email='', phone='', enabled=True):
        super(Contact, self).__init__(id=id, enabled=enabled)

        if not name or not email:
            raise ContactError('Error - Missing name and/or email from contact definition.')

        self.name = name
        self.email = email
        self.phone = phone

    def to_dict(self):
        """
        Return the representation of a `Contact` as a dictionary.

        :return: A dictionary containing the following keys: id, name, email,
            phone and enabled.
        """

        return super(Contact, self).to_dict(['id', 'name', 'email', 'phone', 'enabled'])

    def __eq__(self, other_contact):
        """
        Compare if two contacts are the same. Two contacts are considered
        equal if their name, email and phone are the same.

        :param other_contact: A `Contact` object.
        :return: A boolean indicating if a `Contact` is equal to another one.
        """

        return self.name == other_contact.name and self.email == other_contact.email and \
            self.phone == other_contact.phone

    def __hash__(self):
        """
        Return the hash of a `Contact` object for comparison purposes taking
        into account its name, email and phone.

        :return: An integer value representing the hash of a `Contact`.
        """

        return hash(self.name) ^ hash(self.email) ^ hash(self.phone)


class ContactGroup(Switchable):

    """
    The ContactGroup class contains a collection of contacts.

    :param name: A string containing the name of the `ContactGroup`.
    :param contacts: A list containing `Contact` objects.
    :param enabled: A boolean indicating if the `ContactGroup` is enabled.
    """

    def __init__(self, name='', contacts=None, enabled=True):
        super(ContactGroup, self).__init__(enabled=enabled)

        if not name or not contacts:
            raise ContactGroupError('Error - Missing name and/or contacts from contact group definition.')

        self.name = name
        self.contacts = set(contacts) if contacts is not None else []

    def to_dict(self):
        """
        Return the representation of a `ContactGroup` as a dictionary.

        :return: A dictionary containing the following keys: id, name, enabled,
            and contacts.
        """

        d = super(ContactGroup, self).to_dict(['id', 'name', 'enabled'])
        d.update({'contacts': [c.to_dict() for c in self.contacts]})

        return d

    def as_list(self):
        """
        Construct a list containing all `Contacts` defined within this `ContactGroup`.

        :return: A list containing all contacts defined in a `ContactGroup`.
        """

        return [contact for contact in self.contacts]

    def __eq__(self, other_contact_group):
        """
        Compare if two contact groups are the same. Two contact groups are considered
        equal if their name and their respective contacts are the same.

        :param other_contact_groupd: A `ContactGroup` object.
        :return: A boolean indicating if a `ContactGroup` is equal to another one.
        """

        return self.name == other_contact_group.name \
            and self.contacts == other_contact_group.contacts

    def __hash__(self):
        """
        Return the hash of a `ContactGroup` object for comparison purposes taking
        into account its name and the hashes of its contacts.

        :return: An integer value representing the hash of a `ContactGroup`.
        """

        if len(self.contacts) > 1:
            hashed = hash(self.name) ^ reduce(lambda l, m: l.__hash__() ^ m.__hash__(), self.contacts)
        else:
            hashed = hash(self.name) ^ list(self.contacts).pop().__hash__()

        return hashed

    def enable(self, ids):
        """
        Enable one or more contacts.

        :param ids: A list containing the ids to be enabled. The list can
            include `Contact` and `ContactGroup` ids.
        :return: A list containing the ids of `Contact` and `ContactGroup`
            objects that were enabled.
        """

        return ([self.id] if super(ContactGroup, self).enable(ids=ids) else []) + \
            [contact.id for contact in self.contacts if contact.enable(ids=ids)]

    def disable(self, ids):
        """
        Disable one or more contacts.

        :param ids: A list containing contacts ids to be disabled. The list can
            include `Contact` and `ContactGroup` ids.
        :return: A list containing the ids `Contact` and `ContactGroup`
            objects that were disabled.
        """

        return ([self.id] if super(ContactGroup, self).disable(ids=ids) else []) + \
            [contact.id for contact in self.contacts if contact.disable(ids=ids)]
