.. _endpoint_list:

STARS API Endpoints
===================

Introduction
------------

A detailed list of all the STARS API RESTful endpoints, along with example input and output.
There are three major interfaces: Credits, Submissions, and Institutions. All
endpoints start with a prefix of the following format::

/api/<api_version>/<interface>/

For example, accessing the Credits interface for Version 1.0 of the API would look
like this::

/api/v1/credits/...

Currently the STARS API supports several output formats:

 * json
 * jsonp
 * yaml
 * xml
 * html

To select a particular format use the format get parameter::

/api/v1/credits/creditset/?format=json

All examples below use ``json``.

The Credits API
---------------

AASHE provides access to the STARS Technical Manual through the API in the form of
the **Credits API**, which allows you to navigate each CreditSet (version of STARS),
from the top level down through Categories, Subcategories, Credits, and Documentation
Fields.

Credit Sets
^^^^^^^^^^^

Credit Sets represent versions of STARS, such as 1.0 or 1.1.

**List of available Credit Sets**::

/api/v1/credits/creditset/

Sample Output (truncated):

.. code-block:: javascript

	{
		meta:
			{
				limit: 20,
				next: null,
				offset: 0,
				previous: null,
				total_count: 4
			},
		objects: [
			{
				categories:	[
					"/api/v1/credits/category/1/",
					"/api/v1/credits/category/2/",
					"/api/v1/credits/category/3/",
					"/api/v1/credits/category/4/"
				],
				id: "2",
				release_date: "2010-11-02",
				resource_uri: "/api/v1/credits/creditset/2/",
				version: "1.0"
			},
			...
		]
	}
	
**Access a Specific Credit Set**::

/api/v1/credits/creditset/2/

Sample Output:

.. code-block:: javascript

	{
		categories: [
			"/api/v1/credits/category/1/",
			"/api/v1/credits/category/2/",
			"/api/v1/credits/category/3/",
			"/api/v1/credits/category/4/"
		],
		id: "2",
		release_date: "2010-11-02",
		resource_uri: "/api/v1/credits/creditset/2/",
		version: "1.0"
	}

Categories
^^^^^^^^^^

Each Credit Set can contains several categories.

**Access a Specific Category**::

/api/v1/credits/category/1/

Sample Output:

.. code-block:: javascript

	{
		abbreviation: "ER",
		creditset: "/api/v1/credits/creditset/2/",
		description: "<p>The Education &amp; Research category includes Co-Curricular Education, Curriculum, and Research sub-categories.</p>",
		id: "1",
		include_in_report: true,
		include_in_score: true,
		ordinal: 0,
		resource_uri: "/api/v1/credits/category/1/",
		subcategories: [
			"/api/v1/credits/subcategory/1/",
			"/api/v1/credits/subcategory/3/",
			"/api/v1/credits/subcategory/5/"
		],
		title: "Education & Research"
	}

Subcategories
^^^^^^^^^^^^^

And Categories contain Subcategories

**Access a Specific Subcategory**::

/api/v1/credits/subcategory/1/

Sample Output (truncated):

.. code-block:: javascript

	{
		category: "/api/v1/credits/category/1/",
		credits: [
			"/api/v1/credits/credit/1/",
			"/api/v1/credits/credit/2/",
			"/api/v1/credits/credit/3/",
			...
		],
		description: "<p>This subcategory...</p>",
		id: "1",
		ordinal: 0,
		resource_uri: "/api/v1/credits/subcategory/1/",
		title: "Co-Curricular Education"
	}
	
Credits
^^^^^^^

And Subcategories contain Credits.

**Access a Specific Credit**::

/api/v1/credits/credit/1/

Sample Output (truncated):

.. code-block:: javascript

	{
		applicability: "<p>...</p>",
		criteria: "<p>...</p>",
		documentation_fields: [
			"/api/v1/credits/field/2/",
			"/api/v1/credits/field/26/",
			"/api/v1/credits/field/30/",
			...
		],
		id: "1",
		identifier: "ER-1",
		measurement: "<p>...</p>",
		number: 1,
		ordinal: 0,
		point_value: 5,
		resource_uri: "/api/v1/credits/credit/1/",
		scoring: "<p>...</p>",
		subcategory: "/api/v1/credits/subcategory/1/",
		title: "Student Sustainability Educators Program",
		type: "t1"
	}

Documentation Fields
^^^^^^^^^^^^^^^^^^^^

Each credit is made up of Documentation Fields that can be accessed individually.

**Access a Specific Documentation Field**::

/api/v1/credits/field/2/

Sample Output:

.. code-block:: javascript

	{
		credit: "/api/v1/credits/credit/1/",
		id: "2",
		inline_help_text: "",
		max_range: 500000,
		min_range: 0,
		ordinal: 0,
		required: "req",
		resource_uri: "/api/v1/credits/field/2/",
		title: "Total number of degree-seeking students enrolled at the institution",
		tooltip_help_text: "",
		type: "numeric"
	}
	
The Submissions API
-------------------

AASHE provides access to the STARS Reports through the API in the form of
the **Submissions API**, which allows you to navigate each Report, from the
top level down through Categories, Subcategories, Credits, and responses to
Documentation Fields.

Submissions
^^^^^^^^^^^

Submissions represent STARS Reports

**List of available Reports**::

/api/v1/submissions/submissionset/

Sample Output (truncated):

.. code-block:: javascript

