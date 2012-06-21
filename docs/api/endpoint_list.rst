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

/credits/creditset/ - get list of all credit sets
/credits/creditset/<id>/ - specific credit set
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
/submissions/<submission-set-id>/ - specific submission set
/submissions/<submission-set-id>/category/ - list of all categories for specific submission set
/submissions/<submission-set-id>/category/<category-id>/ - specific category for specific submission set
/submissions/<submission-set-id>/subcategory/
/submissions/<submission-set-id>/subcategory/<subcategory-id>/
/submissions/<submission-set-id>/credit/
/submissions/<submission-set-id>/credit/<credit-id>/
/submissions/<submission-set-id>/field/
/submissions/<submission-set-id>field/<field-id>/

Search
------
(future dev)

/search/institutions/
/search/credit/
