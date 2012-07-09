.. _credits_api_endpoints:

The Credits API
===============

AASHE provides access to the STARS Technical Manual through the API in the form of
the **Credits API**, which allows you to navigate each CreditSet (version of STARS),
from the top level down through Categories, Subcategories, Credits, and Documentation
Fields.

.. note::

   This API is GET only.

Credit Sets
-----------

Credit Sets represent versions of STARS, such as 1.0 or 1.1.

List URI
^^^^^^^^
::

	/api/0.1/credits/creditset/

Sample Output (truncated):
^^^^^^^^^^^^^^^^^^^^^^^^^^

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
	
Object URI
^^^^^^^^^^
::

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
   
Properties
^^^^^^^^^^

+--------------+---------------------------------------------------------------+
| Property     | Description                                                   |
+==============+===============================================================+
| categories   | The list of category objects in this creditset and their URIs |
+--------------+---------------------------------------------------------------+
| release date | The date this version of STARS was released                   |
+--------------+---------------------------------------------------------------+
| resource_uri | The URI used to access this resource                          |
+--------------+---------------------------------------------------------------+
| version      | A string representation of the STARS version of this credits  |
+--------------+---------------------------------------------------------------+


Categories
----------

Each Credit Set can contains several categories.

Object URI
^^^^^^^^^^
::

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

Properties
^^^^^^^^^^

+-------------------+------------------------------------------------------------------------------------+
| Property          | Description                                                                        |
+===================+====================================================================================+
| abbreviation      | The short name for the category                                                    |
+-------------------+------------------------------------------------------------------------------------+
| creditset         | The parent creditset for this category                                             |
+-------------------+------------------------------------------------------------------------------------+
| description       | An HTML formatted description of the category                                      |
+-------------------+------------------------------------------------------------------------------------+
| include_in_report | Indicates if this is displayed in public reports                                   |
+-------------------+------------------------------------------------------------------------------------+
| include_in_score  | Indicates if the score for credits in this category factor in to the overall score |
+-------------------+------------------------------------------------------------------------------------+
| ordinal           | Used to order categories within a crediset                                         |
+-------------------+------------------------------------------------------------------------------------+
| resource_uri      | The URI used to access this resource                                               |
+-------------------+------------------------------------------------------------------------------------+
| subcategories     | Subcategories in this category and their URIs                                      |
+-------------------+------------------------------------------------------------------------------------+
| title             | The name of the category                                                           |
+-------------------+------------------------------------------------------------------------------------+

Subcategories
-------------

And Categories contain Subcategories

Object URI
^^^^^^^^^^
::

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

Properties
^^^^^^^^^^

+--------------+---------------------------------------------------+
| Property     | Description                                       |
+==============+===================================================+
| category     | The parent category for this subcategory          |
+--------------+---------------------------------------------------+
| credits      | Credits in this subcategory and their URIs        |
+--------------+---------------------------------------------------+
| description  | An HTML formatted description of this subcategory |
+--------------+---------------------------------------------------+
| ordinal      | Used to order subcategories within a category     |
+--------------+---------------------------------------------------+
| resource_uri | The URI used to access this resource              |
+--------------+---------------------------------------------------+
| title        | The name of this subcategory                      |
+--------------+---------------------------------------------------+
	
Credits
-------

And Subcategories contain Credits.

Object URI
^^^^^^^^^^
::

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

Properties
^^^^^^^^^^

+----------------------+-----------------------------------------------------------------------+
| Property             | Description                                                           |
+======================+=======================================================================+
| applicability        | HTML formatted text describing the applicability of this credit       |
+----------------------+-----------------------------------------------------------------------+
| criteria             | HTML formatted text describing the criteria for this credit           |
+----------------------+-----------------------------------------------------------------------+
| documentation_fields | The list of documentation fields in this credit along with their URIs |
+----------------------+-----------------------------------------------------------------------+
| identifier           | A short name for this credit                                          |
+----------------------+-----------------------------------------------------------------------+
| measurement          | HTML formatted text describing the measurements used in this credit   |
+----------------------+-----------------------------------------------------------------------+
| ordinal              | An integer used to order credits within a subcategory                 |
+----------------------+-----------------------------------------------------------------------+
| point_value          | The amount of points this credit is worth                             |
+----------------------+-----------------------------------------------------------------------+
| resource_uri         | The URI used to access this resource                                  |
+----------------------+-----------------------------------------------------------------------+
| scoring              | HTML formatted text describing how this credit is scored              |
+----------------------+-----------------------------------------------------------------------+
| subcategory          | The parent subcategory for this credit                                |
+----------------------+-----------------------------------------------------------------------+
| title                | The full name of this credit                                          |
+----------------------+-----------------------------------------------------------------------+
| type                 | The type, tier 1 or tier 2 of this credit                             |
+----------------------+-----------------------------------------------------------------------+
	
Documentation Fields
--------------------

Each credit is made up of Documentation Fields that can be accessed individually.

Object URI
^^^^^^^^^^
::

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

Properties
^^^^^^^^^^

+-------------------+----------------------------------------------------------------------------------------------------------------+
| Property          | Description                                                                                                    |
+===================+================================================================================================================+
| credit            | The parent credit for this documenation field and its URI                                                      |
+-------------------+----------------------------------------------------------------------------------------------------------------+
| inline_help_text  | Text that appears beside this field in the tool                                                                |
+-------------------+----------------------------------------------------------------------------------------------------------------+
| max_range         | The max value of this field for integer fields only                                                            |
+-------------------+----------------------------------------------------------------------------------------------------------------+
| min_range         | The min value of this field for integer fields only                                                            |
+-------------------+----------------------------------------------------------------------------------------------------------------+
| ordinal           | An integer used to order fields within a credit                                                                |
+-------------------+----------------------------------------------------------------------------------------------------------------+
| required          | req: Required or opt: Optional or cond: Conditionally Required (based on other fields)                         |
+-------------------+----------------------------------------------------------------------------------------------------------------+
| resource_uri      | The URI for this resource                                                                                      |
+-------------------+----------------------------------------------------------------------------------------------------------------+
| title             | The title of this field                                                                                        |
+-------------------+----------------------------------------------------------------------------------------------------------------+
| tooltip_help_text | Text that appears as a pop-up icon beside the field in the Reporting Tool                                      |
+-------------------+----------------------------------------------------------------------------------------------------------------+
| type              | The response type: 'text', 'long_text', 'numeric', 'boolean', 'choice', 'multichoice', 'url', 'date', 'upload' |
+-------------------+----------------------------------------------------------------------------------------------------------------+

