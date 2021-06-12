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
import numpy as np
from tqdm import tqdm


class SchedulingModule():

    def __init__(self, targets):
        """
        Initialisation function for the scheduling module.

        Parameters
        ----------
        targets : list
            List of targets.

        Returns
        -------
        None.

        """

        # Store targets
        self.targets = targets

        # Declare empty variables
        self.contacts = None
        self.scheduled_contacts = None

    def combine_contacts(self):
        """
        Function to combine contacts from all the targets into one list.

        Returns
        -------
        contacts : list
            List of all contacts.

        """

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
        contacts = self.contacts
        contact_key = operator.attrgetter("end")
        contacts.sort(key=contact_key)

        # Shift the contacts by using a dummy element as the original
        # algorithm assumes indexing from one
        contacts_shift = [None] + contacts

        # Calculate predecessors
        pred = np.zeros(len(contacts_shift), dtype="uintc")
        # Loop through each contact
        for i, contact in enumerate(tqdm(contacts_shift, "Calculating Predecessors")):
            # Skip dummy element
            if i == 0:
                continue

            # Loop through preceeding contacts, working backwards from the
            # current contact
            for j in range(i-1, 0, -1):
                # Extract second contact
                second_contact = contacts_shift[j]

                # Update predecessor if it does not intersect with the contact
                if contact.start >= second_contact.end:
                    pred[i] = j
                    break

        # Calculate schedule
        benefit = np.zeros(len(contacts_shift))
        optimal_contacts = [[]] + [None] * (len(contacts))

        # Iterate through subproblems
        for i, contact in enumerate(tqdm(contacts_shift, "Scheduling")):
            # Skip dummy element
            if i == 0:
                continue

            # Calculate previous benefit
            benefit_previous = benefit[i-1]

            # Calculate new benefit
            benefit_new = benefit[pred[i]] + contact.benefit

            # Update benefit
            benefit[i] = max(benefit_previous, benefit_new)

            # Update included contacts
            optimal_contacts_previous = optimal_contacts[i-1]
            optimal_contacts_new = optimal_contacts[pred[i]] + [i]
            if benefit_new > benefit_previous:
                optimal_contacts[i] = optimal_contacts_new
            else:
                optimal_contacts[i] = optimal_contacts_previous

        # Extract optimal benefit and contacts
        benefit_optimal = benefit[-1]
        scheduled_contacts = [contacts_shift[i] for i in optimal_contacts[-1]]

        # Store scheduled_contacts
        self.scheduled_contacts = scheduled_contacts

        return scheduled_contacts, benefit_optimal
