The Submissions API
===================

AASHE provides access to the STARS Reports through the API in the form of
the **Submissions API**, which allows you to navigate each Report, from the
top level down through Categories, Subcategories, Credits, and responses to
Documentation Fields.

Submissions
-----------

Submissions are STARS Reports

List URI
^^^^^^^^
::

	/api/0.1/submissions/

Sample Output (truncated)
^^^^^^^^^^^^^^^^^^^^^^^^^

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

Object URI
^^^^^^^^^^
::

	/api/0.1/submissions/29/

Sample Output
^^^^^^^^^^^^^

.. code-block:: javascript

	{
		category_submissions: [
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

Properties
^^^^^^^^^^

+----------------------+------------------------------------------------------------------+
| Property             | Description                                                      |
+======================+==================================================================+
| category_submissions | A list of categories in this submission                          |
+----------------------+------------------------------------------------------------------+
| creditset            | The version of STARS this submission used                        |
+----------------------+------------------------------------------------------------------+
| date_submitted       | The date this submission was finalized                           |
+----------------------+------------------------------------------------------------------+
| institution          | The submitting institution                                       |
+----------------------+------------------------------------------------------------------+
| pdf_report           | The URI of the pdf versino of this report                        |
+----------------------+------------------------------------------------------------------+
| presidents_letter    | The URI of the pdf letter from the president of this institution |
+----------------------+------------------------------------------------------------------+
| rating               | The rating received for this submission                          |
+----------------------+------------------------------------------------------------------+
| resource_uri         | The URI used to access this resource                             |
+----------------------+------------------------------------------------------------------+
| score                | The score recieved for this submission (null if Reporter)        |
+----------------------+------------------------------------------------------------------+

	
Category Submissions
--------------------

Object URI
^^^^^^^^^^
::

	/api/0.1/submissions/29/category/1/

Sample Output (truncated)
^^^^^^^^^^^^^^^^^^^^^^^^^

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

Properties
^^^^^^^^^^

+-------------------------+--------------------------------------------------------+
| Property                | Description                                            |
+=========================+========================================================+
| category                | The parent category in the specific STARS Creditset    |
+-------------------------+--------------------------------------------------------+
| resource_uri            | The URI used to access this resource                   |
+-------------------------+--------------------------------------------------------+
| score                   | The score received in this category (null if Reporter) |
+-------------------------+--------------------------------------------------------+
| subcategory_submissions | Subcategories in this category submisison              |
+-------------------------+--------------------------------------------------------+
| submissionset           | The parent submission set                              |
+-------------------------+--------------------------------------------------------+

Subcategories Submissions
-------------------------

Object URI
^^^^^^^^^^
::

	/api/0.1/submissions/29/subcategory/1/

Sample Output (truncated)
^^^^^^^^^^^^^^^^^^^^^^^^^

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

Properties
^^^^^^^^^^

+---------------------+---------------------------------------------------------------+
| Property            | Description                                                   |
+=====================+===============================================================+
| category_submission | The parent category for this subcategory submission           |
+---------------------+---------------------------------------------------------------+
| description         | Optional description of the subcategory from the institution  |
+---------------------+---------------------------------------------------------------+
| points              | The points achieved in this subcategory                       |
+---------------------+---------------------------------------------------------------+
| resource_uri        | The URI used to access this resource                          |
+---------------------+---------------------------------------------------------------+
| subcategory         | The parent subcategory in this version of STARS and the URI   |
+---------------------+---------------------------------------------------------------+
| credit_submissions  | The list of credit submissions in this subcategory submission |
+---------------------+---------------------------------------------------------------+

Credit Submissions
------------------

Object URI
^^^^^^^^^^
::

	/api/0.1/submissions/29/credit/1/

Sample Output
^^^^^^^^^^^^^

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

Properties
^^^^^^^^^^

+------------------------+----------------------------------------------------------+
| Property               | Description                                              |
+========================+==========================================================+
| assessed_points        | The points assessed for this credit submission           |
+------------------------+----------------------------------------------------------+
| credit                 | The parent credit in this version of STARS and the URI   |
+------------------------+----------------------------------------------------------+
| documentation_fields   | The list of documentation fields in this credit          |
+------------------------+----------------------------------------------------------+
| resource_uri           | The URI to access this resource                          |
+------------------------+----------------------------------------------------------+
| subcategory_submission | The parent subcategory submission in this submission set |
+------------------------+----------------------------------------------------------+
| submission_status      | c: Complete, na: Not Applicable, np: Not Pursuing        |
+------------------------+----------------------------------------------------------+
| title                  | The title of this credit                                 |
+------------------------+----------------------------------------------------------+
	
Documentation Fields
--------------------


Object URI
^^^^^^^^^^
::

	/api/0.1/submissions/29/field/5/

Sample Output
^^^^^^^^^^^^^

.. code-block:: javascript

	{
		credit_submission: "/api/0.1/submissions/29/credit/2/",
		documentation_field: "/api/0.1/credits/field/5/",
		resource_uri: "/api/0.1/submissions/29/field/5/",
		value: "unPLUg All-Hall Energy Challenge"
	}

Properties
^^^^^^^^^^

+--------------------+----------------------------------------------------------------------------+
| Property           | Description                                                                |
+====================+============================================================================+
| credit_submission  | The parent credit containing this field                                    |
+--------------------+----------------------------------------------------------------------------+
| documenation_field | The parent documentation_field in the creditset (working version of STARS) |
+--------------------+----------------------------------------------------------------------------+
| resources_uri      | The URI for this resouce                                                   |
+--------------------+----------------------------------------------------------------------------+
| value              | The value submitted by the institution for this field                      |
+--------------------+----------------------------------------------------------------------------+
