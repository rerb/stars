.. _sample-workflow:

Sample Workflow
===============

This outline is intended to be an example of a transaction from a
third party application accessing data for a specific Documentation
Field within a STARS Report.

Acquiring the Institution Handle
--------------------------------

To access a report, the Client first needs to get the unique numeric
ID for the institution.

Look-up ID with search query
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Search based on `Name` field. Example input::

    name: "Colorado"

This request will be made to ``http://api.aashe.org/stars/institutions/search/?query=Colorado``

The response value is a list of handles for institutions matching the
query. Example JSON response data:

.. code-block:: javascript

    [
     {
      id: 111,
      name: "University of Colorado at Boulder"
     },
     {
      id: 112,
      name: "Colorado State University"
     }
    ]

Get all institutions query
^^^^^^^^^^^^^^^^^^^^^^^^^^

Returns a data structure similar to the response above, but with all
available STARS institutions. The application can store & process this
list locally to obtain necessary IDs.

This request can be made to ``http://api.aashe.org/stars/institutions/all/``


Getting a Handle for the Specific Submission Set
------------------------------------------------

Once the Client has the ID of the Institution they’re interested in,
they can access related Submission Sets.

Institutions can have multiple Submission Sets. For example, they may
have submitted for a STARS Rating in 2010 and then again
in 2011. These are unique submissions sets. This also applies to
Submission Sets that are finalized for submission to the Common Data
Set.

Latest Submission Set Query
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Get latest published submission set for an institution with
ID 111. Example input::

    id: 111

This request will be made to ``http://api.aashe.org/stars/institutions/111/submissionsets/latest/``

The response value is the latest submission set that has been publish
by the institution. Example JSON response data:

.. code-block:: javascript

    {
     id: 211,
     version: "1.1",
     date_submitted: "2011-10-24",
     rating: "Gold"
    }

All Submission Sets for an Institution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Get all submission sets an institution has submitted. The application
can store and process this list locally. Example input::

    id: 111

This request will be made to ``http://api.aashe.org/stars/institutions/111/submissionsets/``.

The response value is all submission sets for the institution
ID. Example JSON response data:

.. code-block:: javascript

    [
     {
      id: 210,
      version: "1.0",
      date_submitted: "2010-12-11",
      rating: "Silver"
     },
     {
      id: 211,
      version: "1.1",
      date_submitted: "2011-10-24",
      rating: "Gold"
     }
    ]


Accessing Data from the Specific Documentation Field
----------------------------------------------------

Access values for a Documentation Field on a specific submission
set. Required parameters include category, subcategory, credit, and
documentation field. 

Get data for a specific documentation field on a submission
set. Example input::

    SubmissionSetId: 211
    CategoryId: 1
    SubcategoryId: 1
    CreditId: 1
    DocumentationFieldId: 2

This request will be made to
``http://api.aashe.org/stars/submissions/211/1/1/1/2/``.

The response value is the data for the documentation field on this
credit for the specific submission. Example JSON response data:

.. code-block:: javascript

    {
     id: 2112,
     value: "Eco-Reps"
    }

