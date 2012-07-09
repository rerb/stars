.. _endpoint_list:

STARS API Endpoints
===================

Introduction
------------

A detailed list of all the STARS API RESTful endpoints, along with example input and output.
There are three major interfaces: Credits, Submissions, and Institutions. All
endpoints start with a prefix of the following format::

/api/<api_version>/<interface>/

For example, accessing the Credits interface for Version 0.1 of the API would look
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

All examples below ``json``.

.. toctree::
	:maxdepth: 2

	credits_api_endpoints
	institutions_api_endpoints
	submissions_api_endpoints
   
