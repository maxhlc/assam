#!/usr/bin/env python

import operator


class SchedulingModule():

    def __init__(self, targets):
        # TODO: docstring

        # Store targets
        self.targets = targets

    def combine_contacts(self):
        # TODO: docstring

        # Extract contacts
        contacts = [contact
                    for target in self.targets
                    for contact in target.contacts]

        # Store contacts
        self.contacts = contacts

        # Return contacts
        return contacts

    def simple_dynamic_schedule(self):
        # TODO: docstring

        # Sort list of contacts by end time
        contact_key = operator.attrgetter("end")
        self.contacts.sort(key=contact_key)

        # Calculate predecessors

        # Calculate schedule

        return self.contacts
