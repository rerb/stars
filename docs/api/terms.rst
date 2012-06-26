.. _terminology:

Data Model & Terminology
========================

Every STARS submission is made up of `Credits`. Credits belong to `Credit
Sets`, which define a specific version of the STARS program
(eg. 1.0, 1.2, etc.). A STARS participant will submit documentation
for a subset of all credits in a credit set in order to determine their
rating.

Every credit includes one or more `Documentation Fields`. These fields
contain the data for every submission. Not all documentation fields
are required for a particular credit.


Institutions & Submission Sets
------------------------------

Every institution that submits to the STARS reporting system creates a
Submission Set. The Submission Set contains the credit set the
participant is submitting against as well as a variety of additional
information like submission dates, rating information, and other
metadata.

Example institution JSON data:

.. code-block:: javascript

    {
     id: 111,
     name: "University of Colorado at Boulder",
     charter_participant: true,
     country: "United States of America"
    }

Example submission set JSON data:

.. code-block:: javascript

    {
     id: 211,
     version: "1.1",
     date_submitted: "2011-10-24",
     rating: "Gold"
    }

.. Should we include an entity relationship or some other diagram here?

Documentation Fields
--------------------

Every credit includes a set of one or more `Documentation
Fields`. Each documentation field includes a label, the value for a
related submission and some additional metadata.

Example documentation field JSON data:

.. code-block:: javascript

    {
     id: 2112,
     value: "Eco-Reps",
    }

.. Should we include an entity relationship or some other diagram here?
