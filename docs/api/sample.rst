.. _sample-workflow:

Sample Workflow
===============

This outline is intended to be an example of a transaction from a
third party application accessing data for a specific Documentation
Field within a STARS Report. In this case the plan is to find out
what American University filled in for the description of their
Outdoor Program in Tier2-7.

1) Access the Institution
--------------------------

First, let's use :ref:`institutions_api_endpoints` to find the institution we're looking for.
For the sake of this example, let's assume that's American Unversity.

Endpoint
^^^^^^^^
::

	/api/0.1/institutions/

Truncated Response
^^^^^^^^^^^^^^^^^^

.. code-block:: javascript

	...
	{
		...
		current_report: {
			date_submitted: "2011-01-31",
			rating: "Gold",
			resource_uri: "/api/0.1/submissions/55/",
			version: "1.0"
		},
		name: "American University",
		...
	},
	...

2) Access the Submission
------------------------

Now that we know the URI for the `current_report` above, we can get closer to the field
in question using :ref:`submissions_api_endpoints`:

Endpoint
^^^^^^^^
::

	/api/0.1/submissions/55/

Truncated Response
^^^^^^^^^^^^^^^^^^

.. code-block:: javascript

	{
		category_submissions: [
			{
				resource_uri: "/api/0.1/submissions/55/category/1/",
				title: "Education & Research"
			},
			...
		],
		...
	}

3) Navigate down to the Documentation Field
-------------------------------------------

Now we can work our way down the :ref:`submissions_data_model` data model to find the
data we're looking for::

	/api/0.1/submissions/55/category/1/
	/api/0.1/submissions/55/subcategory/1/
	/api/0.1/submissions/55/credit/12/

Finally arriving at our field::

	/api/0.1/submissions/55/field/143/
	
Response
^^^^^^^^

.. code-block:: javascript

	{
		credit_submission: "/api/0.1/submissions/55/credit/12/",
		documentation_field: "/api/0.1/credits/field/143/",
		resource_uri: "/api/0.1/submissions/55/field/143/",
		value: "The Outdoors Club is dedicated to creating a stronger relationship between students and the environment, offering trips throughout the year, including hiking, biking, kayaking, and camping."
	}