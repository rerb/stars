.. _endpoint_list:

All STARS API End-points
========================

Here is an itemized list of all the end-points in the STARS API along with their permissions and parameters. 

Profile
-------

get_rw_institutions - institutions you have read/write access to
get_snapshot_institutions - institutions who have opted to share snapshots with you

Credits (read-only)
-------------------

/credits/ - get list of all credit sets
/credits/<id>/ - get specific credit set
/credits/<id>/cat/ - get all the categories in a creditset
/credits/<id>/cat/<id>/ - get a specific category
/credits/<id>/cat/<id>/s/
/credits/<id>/cat/<id>/sub/<id>/
/credits/<id>/cat/<id>/sub/<id>/c/
/credits/<id>/cat/<id>/sub/<id>/c/<id>/
/credits/<id>/cat/<id>/sub/<id>/c/<id>/d/ - documentation field list
/credits/<id>/cat/<id>/sub/<id>/c/<id>/d/<id>/ - specific documentation field

/credits/creditset/<id>
/credits/categories/<id>
/credits/subcategories/<id>

Institutions
------------

/institutions/
/institutions/<id>/
/institutions/<id>/ss/ - submissionsets
/institutions/<id>/ss/<id>/
/institutions/<id>/ss/<id>/boundary/
/institutions/<id>/ss/<id>/

