#!/usr/bin/env python

"""
MIT License

Copyright (c) 2020-2021 Max Hallgarten La Casta

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

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
