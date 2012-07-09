.. _using-stars-api:

Using the STARS API
===================

The STARS API is a dedicated, RESTful API for accessing STARS submission
data. There are a few important things to know before using the STARS
API which are explained below.

Getting Access
--------------

AASHE requires that all programs using the API authenticate with an **API key** and **username**.
To request an API Key please contact the STARS team at stars@aashe.org. API Access will only be
provided to STARS Participants and AASHE Members at this time.

Currently all data is READ-ONLY, so all users will have the same access level. As future versions of
the API develop we will provide controlled write access to pre-submission STARS data as granted
by each institution. For now only GET requests are accepted.

.. _data_model:

Data Model and Structure
------------------------

The three APIs: :ref:`credits_api_endpoints`, :ref:`institutions_api_endpoints`, and :ref:`submissions_api_endpoints`
use resources that model the underlying STARS data.

Credits
^^^^^^^

Resources in :ref:`credits_api_endpoints` mimic the Technical Manual

* CreditSet - Versions of STARS
	* Category
		* Subcategory
			* Credit
				* Documentation Field
				
Institutions
^^^^^^^^^^^^

:ref:`institutions_api_endpoints` only has Institution Resources, but the resource contains
information about the institution including the URI of their STARS Report Resource in :ref:`submissions_api_endpoints`.

.. _submissions_data_model:

Submissions
^^^^^^^^^^^

Resources in :ref:`submissions_api_endpoints` tie directly to Credit Sets in :ref:`credits_api_endpoints`.

* Submission Set - A STARS Report
	* Category Submission
		* Subcategory Submission
			* Credit
				* Field

RESTful Interface
-----------------

The STARS API was designed to be as flexible as possible. This is why we chose to release it as
a RESTful interface. Each query of the API is simply an HTTP request (so far only GET) to a URI
where you can work with STARS data, for example::

	/api/0.1/credits/credisets/

will give you a list of all the versions of STARS. See :ref:`credits_api_endpoints` for specifics.
