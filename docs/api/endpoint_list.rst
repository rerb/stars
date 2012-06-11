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
/credits/<id>/ - specific credit set
/credits/category/ - list of all categories
/credits/category/<id>/ - specific category
/credits/subcategory/
/credits/subcategory/<id>/
/credits/credit/
/credits/credit/<id>/
/credits/field/
/credits/field/<id>/

Institutions
------------

/institutions/
/institutions/<id>/

Submissions
-----------

/submissions/ - list of all submission sets (per auth)
/submissions/<id>/ - specific submission set
/submissions/category/
/submissions/category/<id>/
/submissions/subcategory/
/submissions/subcategory/<id>/
/submissions/credit/
/submissions/credit/<id>/
/submissions/field/
/submissions/field/<id>/

Search
------
(future dev)

/search/institutions/
/search/credit/

