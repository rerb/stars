.. _institutions_api_endpoints:

Institutions API
================

AASHE provides access to all STARS Rated institutions through the API.
The most common use of this api is as a navigation tool to institutions'
Reports.

.. note::

   This API is GET only.

Institution
-----------

In v0.1 of the API, Institutions are currently rated STARS Institutions.

List URI
^^^^^^^^
::

	/api/0.1/institutions/

Sample Output (truncated)
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: javascript

	{
		meta: {
			limit: 20,
			next: "/api/0.1/institutions/?offset=20&limit=20&format=json",
			offset: 0,
			previous: null,
			total_count: 188
		},
		objects: [
			{
				city: "Decatur",
				country: "United States of America",
				current_report: {
					date_submitted: "2012-02-15",
					rating: "Silver",
					resource_uri: "/api/0.1/submissions/349/",
					version: "1.0"
				},
				is_member: true,
				name: "Agnes Scott College",
				postal_code: "30030-3797",
				resource_uri: "/api/0.1/institutions/286/",
				state: "GA"
			},
			{
				city: "Washington",
				country: "United States of America",
				current_report: {
					date_submitted: "2011-01-31",
					rating: "Gold",
					resource_uri: "/api/0.1/submissions/55/",
					version: "1.0"
				},
				is_member: true,
				name: "American University",
				postal_code: "20016-8001",
				resource_uri: "/api/0.1/institutions/54/",
				state: "DC"
			},
			...
		]
	}
	
Object URI
^^^^^^^^^^
::

	/api/0.1/institutions/286/
	
Sample Output
^^^^^^^^^^^^^

.. code-block:: javascript
	
	{
		city: "Decatur",
		country: "United States of America",
		current_report: {
			date_submitted: "2012-02-15",
			rating: "Silver",
			resource_uri: "/api/0.1/submissions/349/",
			version: "1.0"
		},
		is_member: true,
		name: "Agnes Scott College",
		postal_code: "30030-3797",
		resource_uri: "/api/0.1/institutions/286/",
		state: "GA"
	}
	
Properties
^^^^^^^^^^

+----------------+------------------------------------------------------+
| Property       | Description                                          |
+================+======================================================+
| city           | The city the institution is located in               |
+----------------+------------------------------------------------------+
| country        | The country the institution is located in            |
+----------------+------------------------------------------------------+
| current_report | The most recent submitted report by this institution |
+----------------+------------------------------------------------------+
| is_member      | AASHE Member Status                                  |
+----------------+------------------------------------------------------+
| name           | The formal name of the institution                   |
+----------------+------------------------------------------------------+
| postal_code    | The primary postal code for the institution          |
+----------------+------------------------------------------------------+
| resource_uri   | The URL for the current resource                     |
+----------------+------------------------------------------------------+
| state          | The state the institution is located in              |
+----------------+------------------------------------------------------+
