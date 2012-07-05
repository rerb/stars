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

/api/0.1/credits/...

Currently the STARS API supports several output formats:

 * json
 * jsonp
 * yaml
 * xml
 * html

To select a particular format use the format get parameter::

/api/0.1/credits/creditset/?format=json

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

/api/0.1/credits/creditset/

Sample Output (truncated):

.. code-block:: javascript

	{
		meta: {
			limit: 20,
			next: null,
			offset: 0,
			previous: null,
			total_count: 3
		},
		objects: [
			{
				categories: [
					{
						resource_uri: "/api/0.1/credits/category/1/",
						title: "Education & Research"
					},
					{
						resource_uri: "/api/0.1/credits/category/2/",
						title: "Operations"
					},
					...
				],
				release_date: "2010-11-02",
				resource_uri: "/api/0.1/credits/creditset/2/",
				version: "1.0"
			},
			{
				categories: [
					...
				],
				release_date: "2011-02-09",
				resource_uri: "/api/0.1/credits/creditset/4/",
				version: "1.1"
			},
			{
				...
				resource_uri: "/api/0.1/credits/creditset/5/",
				version: "1.2"
			}
		]
	}
	
**Access a Specific Credit Set**::

/api/0.1/credits/creditset/2/

Sample Output (truncated):

.. code-block:: javascript

	{
		categories: [
			{
				resource_uri: "/api/0.1/credits/category/1/",
				title: "Education & Research"
			},
			{
				resource_uri: "/api/0.1/credits/category/2/",
				title: "Operations"
			},
			...
		],
		release_date: "2010-11-02",
		resource_uri: "/api/0.1/credits/creditset/2/",
		version: "1.0"
	}

Categories
^^^^^^^^^^

Each Credit Set can contains several categories.

**Access a Specific Category**::

/api/0.1/credits/category/1/

Sample Output:

.. code-block:: javascript

	{
		abbreviation: "ER",
		creditset: {
			resource_uri: "/api/0.1/credits/creditset/2/",
			version: "1.0"
		},
		description: "<p>The Education &amp; Research category includes Co-Curricular Education, Curriculum, and Research sub-categories.</p>",
		id: 1,
		include_in_report: true,
		include_in_score: true,
		ordinal: 0,
		resource_uri: "/api/0.1/credits/category/1/",
		subcategories: [
			{
				resource_uri: "/api/0.1/credits/subcategory/1/",
				title: "Co-Curricular Education"
			},
			{
				resource_uri: "/api/0.1/credits/subcategory/3/",
				title: "Curriculum"
			},
			{
				resource_uri: "/api/0.1/credits/subcategory/5/",
				title: "Research"
			}
		],
		title: "Education & Research"
	}

Subcategories
^^^^^^^^^^^^^

And Categories contain Subcategories

**Access a Specific Subcategory**::

/api/0.1/credits/subcategory/1/

Sample Output (truncated):

.. code-block:: javascript

	{
		category: {
			resource_uri: "/api/0.1/credits/category/1/",
			title: "Education & Research"
		},
		credits: [
			{
			resource_uri: "/api/0.1/credits/credit/1/",
			title: "Student Sustainability Educators Program"
			},
			{
			resource_uri: "/api/0.1/credits/credit/2/",
			title: "Student Sustainability Outreach Campaign"
			},
			{
			resource_uri: "/api/0.1/credits/credit/3/",
			title: "Sustainability in New Student Orientation"
			},
			...
		],
		description: "<p>....</p>",
		ordinal: 0,
		resource_uri: "/api/0.1/credits/subcategory/1/",
		title: "Co-Curricular Education"
	}
	
Credits
^^^^^^^

And Subcategories contain Credits.

**Access a Specific Credit**::

/api/0.1/credits/credit/1/

Sample Output (truncated):

.. code-block:: javascript

	{
		applicability: "<p>This credit applies to all institutions.</p>",
		criteria: "...",
		documentation_fields: [
			{
			resource_uri: "/api/0.1/credits/field/2/",
			title: "Total number of degree-seeking students enrolled at the institution"
			},
			{
			resource_uri: "/api/0.1/credits/field/26/",
			title: "Program name (1st program)"
			},
			{
			resource_uri: "/api/0.1/credits/field/30/",
			title: "Number of students served by the program (1st program)"
			},
			...
		],
		identifier: "ER-1",
		measurement: "...",
		ordinal: 0,
		point_value: 5,
		resource_uri: "/api/0.1/credits/credit/1/",
		scoring: "...",
		subcategory: {
			resource_uri: "/api/0.1/credits/subcategory/1/",
			title: "Co-Curricular Education"
		},
		title: "Student Sustainability Educators Program",
		type: "t1"
	}
	
Documentation Fields
^^^^^^^^^^^^^^^^^^^^

Each credit is made up of Documentation Fields that can be accessed individually.

**Access a Specific Documentation Field**::

/api/0.1/credits/field/2/

Sample Output:

.. code-block:: javascript

	{
		credit: {
			resource_uri: "/api/0.1/credits/credit/1/",
			title: "Student Sustainability Educators Program"
		},
		inline_help_text: "",
		max_range: 500000,
		min_range: 0,
		ordinal: 0,
		required: "req",
		resource_uri: "/api/0.1/credits/field/2/",
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

Submissions are STARS Reports

**List of available Reports**::

/api/0.1/submissions/

Sample Output (truncated):

.. code-block:: javascript

	{
		meta: {
			limit: 20,
			next: "/api/0.1/submissions/?offset=20&limit=20&format=json",
			offset: 0,
			previous: null,
			total_count: 198
		},
		objects: [
			{
				categories: [
					{
						resource_uri: "/api/0.1/submissions/29/category/1/",
						title: "Education & Research"
					},
					{
						resource_uri: "/api/0.1/submissions/29/category/2/",
						title: "Operations"
					},
					{
						resource_uri: "/api/0.1/submissions/29/category/3/",
						title: "Planning, Administration & Engagement"
					},
					...
				],
				creditset: {
					resource_uri: "/api/0.1/credits/creditset/2/",
					version: "1.0"
				},
				date_submitted: "2010-09-13",
				institution: {
					name: "Pacific Lutheran University",
					resource_uri: "/api/0.1/institutions/25/"
				},
				pdf_report: "/media/secure/25/submission-29/pacific-lutheran-university-wa.pdf",
				presidents_letter: "/media/secure/25/letter/ltr%20STARS%20Steering%20Committee%2C%209-02-2010_1.pdf",
				rating: "Silver",
				resource_uri: "/api/0.1/submissions/29/",
				score: 45.0277598566308
			},
			{
				categories: [
					{
						resource_uri: "/api/0.1/submissions/64/category/1/",
						title: "Education & Research"
					},
					...
				],
				creditset: {
					resource_uri: "/api/0.1/credits/creditset/2/",
					version: "1.0"
				},
				date_submitted: "2011-07-29",
				institution: {
					name: "Arizona State University",
					resource_uri: "/api/0.1/institutions/21/"
				},
				pdf_report: "/media/secure/21/submission-64/arizona-state-university-az.pdf",
				presidents_letter: "/media/secure/21/submission-64/STARS%20Submission%20072211%20MMC%20Cover%20Ltr.pdf",
				rating: "Gold",
				resource_uri: "/api/0.1/submissions/64/",
				score: 66.9719298245614
			},
			...
		]
	}

**Access to a specific Report**::

/api/0.1/submissions/29/

Sample Output:

.. code-block:: javascript

	{
		categories: [
			{
				resource_uri: "/api/0.1/submissions/29/category/1/",
				title: "Education & Research"
			},
			{
				resource_uri: "/api/0.1/submissions/29/category/2/",
				title: "Operations"
			},
			{
				resource_uri: "/api/0.1/submissions/29/category/3/",
				title: "Planning, Administration & Engagement"
			},
			{
				resource_uri: "/api/0.1/submissions/29/category/4/",
				title: "Innovation"
			}
		],
		creditset: {
			resource_uri: "/api/0.1/credits/creditset/2/",
			version: "1.0"
		},
		date_submitted: "2010-09-13",
		institution: {
			name: "Pacific Lutheran University",
			resource_uri: "/api/0.1/institutions/25/"
		},
		pdf_report: "/media/secure/25/submission-29/pacific-lutheran-university-wa.pdf",
		presidents_letter: "/media/secure/25/letter/ltr%20STARS%20Steering%20Committee%2C%209-02-2010_1.pdf",
		rating: "Silver",
		resource_uri: "/api/0.1/submissions/29/",
		score: 45.0277598566308
	}
	
Category Submissions
^^^^^^^^^^^^^^^^^^^^

**Access to a specific Category**::

/api/0.1/submissions/29/category/1/

Sample Output (truncated):

.. code-block:: javascript

	{
		category: {
			resource_uri: "/api/0.1/credits/category/1/",
			title: "Education & Research"
		},
		resource_uri: "/api/0.1/submissions/29/category/1/",
		score: 25.875,
		subcategory_submissions: [
			{
				resource_uri: "/api/0.1/submissions/29/subcategory/1/",
				title: "Co-Curricular Education"
			},
			{
				resource_uri: "/api/0.1/submissions/29/subcategory/3/",
				title: "Curriculum"
			},
			{
				resource_uri: "/api/0.1/submissions/29/subcategory/5/",
				title: "Research"
			}
		],
		submissionset: {
			date_submitted: "2010-09-13",
			rating: "Silver",
			resource_uri: "/api/0.1/submissions/29/",
			title: null
		}
	}
	
Subcategories Submissions
^^^^^^^^^^^^^^^^^^^^^^^^^

**Access to a specific Subcategory**::

/api/0.1/submissions/29/subcategory/1/

Sample Output (truncated):

.. code-block:: javascript

	{
		category_submission: {
			resource_uri: "/api/0.1/submissions/29/category/1/",
			title: "Education & Research"
		},
		description: "",
		points: 12,
		resource_uri: "/api/0.1/submissions/29/subcategory/1/",
		subcategory: {
			resource_uri: "/api/0.1/credits/subcategory/1/",
			title: "Co-Curricular Education"
		},
		credit_submissions: [
			{
				resource_uri: "/api/0.1/submissions/29/credit/1/",
				title: "Student Sustainability Educators Program"
			},
			{
				resource_uri: "/api/0.1/submissions/29/credit/2/",
				title: "Student Sustainability Outreach Campaign"
			},
			{
				resource_uri: "/api/0.1/submissions/29/credit/3/",
				title: "Sustainability in New Student Orientation"
			},
			...
		]
	}

Credit Submissions
^^^^^^^^^^^^^^^^^^

**Access to a specific Credit**::

/api/0.1/submissions/29/credit/1/

Sample Output:

.. code-block:: javascript

	{
		assessed_points: 5,
		credit: {
			resource_uri: "/api/0.1/credits/credit/2/",
			title: "Student Sustainability Outreach Campaign"
		},
		documentation_fields: [
			{
			resource_uri: "/api/0.1/submissions/29/field/158/",
			title: "Does the institution hold a campaign that meets the criteria for this credit?"
			},
			{
			resource_uri: "/api/0.1/submissions/29/field/6/",
			title: "A brief description of the campaign(s)"
			},
			{
			resource_uri: "/api/0.1/submissions/29/field/7/",
			title: "A brief description of the measured positive impact(s) of the campaign(s)"
			},
			{
			resource_uri: "/api/0.1/submissions/29/field/5/",
			title: "The name of the campaign(s)"
			},
			{
			resource_uri: "/api/0.1/submissions/29/field/10/",
			title: "The website URL for the campaign"
			}
		],
		resource_uri: "/api/0.1/submissions/29/credit/2/",
		subcategory_submission: {
			resource_uri: "/api/0.1/submissions/29/subcategory/1/",
			title: "Co-Curricular Education"
		},
		submission_status: "c",
		title: "Student Sustainability Outreach Campaign"
	}
	
Documentation Fields
^^^^^^^^^^^^^^^^^^^^

**Access to a specific Credit**::

/api/0.1/submissions/29/field/5/

Sample Output:

.. code-block:: javascript

	{
		credit_submission: "/api/0.1/submissions/29/credit/2/",
		documentation_field: "/api/0.1/credits/field/5/",
		resource_uri: "/api/0.1/submissions/29/field/5/",
		value: "unPLUg All-Hall Energy Challenge"
	}