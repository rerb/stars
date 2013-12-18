from django.conf.urls.defaults import patterns, url

from stars.apps.tool.credit_editor.views import *
# from stars.apps.tool.credit_editor.forms import *


# Define some prefixes here to keep the clutter down.
cs_prefix = "(?P<creditset_id>\d+)/"
ct_prefix = cs_prefix + "(?P<category_id>\d+)/"
sb_prefix = ct_prefix + "(?P<subcategory_id>\d+)/"
cr_prefix = sb_prefix + "(?P<credit_id>\d+)/"


urlpatterns = patterns(
    'stars.apps.tool.credit_editor.views',

    (r'^$', 'home'),

    # Creditsets
    (r'^add-creditset/$', AddCreditset()),
    (r'^%s$' % cs_prefix, CreditsetDetail()),
    # (r'^%sdelete/$' % cs_prefix, DeleteCreditset()),

    # Categories
    (r'^%sadd-category/$' % cs_prefix, AddCategory()),
    (r'^%s$' % ct_prefix, CategoryDetail()),
    # (r'^%sdelete/$' % ct_prefix, DeleteCategory()),

    # Subcategories
    (r'^%sadd-subcategory/$' % ct_prefix, AddSubcategory()),
    (r'^%s$' % sb_prefix, SubcategoryDetail()),
    # (r'^%sdelete/$' % sb_prefix, DeleteSubcategory()),

    # Credits
    (r'^%sadd-credit/$' % sb_prefix, AddT1Credit()),
    (r'^%sadd-t2-credit/$' % sb_prefix, AddT2Credit()),
    (r'^%s$' % cr_prefix, CreditDetail()),

    (r'^%sfields/$' % cr_prefix, CreditReportingFields()),
    (r'^%sadd-field/$' % cr_prefix, AddReportingField()),
    (r'^%s(?P<field_id>\d+)/$' % cr_prefix, EditReportingField()),

    (r'^%sapplicability/$' % cr_prefix, ApplicabilityReasons()),
    (r'^%sadd-reason/$' % cr_prefix, AddApplicabilityReason()),
    (r'^%sapplicability/(?P<reason_id>\d+)/$' % cr_prefix,
     EditApplicabilityReason()),

    (r'^%sformula/$' % cr_prefix, FormulaAndValidation()),
    (r'^%sformula/add-test-case/$' % cr_prefix, AddTestCase()),
    (r'^%sformula/(?P<test_id>\d+)/$' % cr_prefix, EditTestCase()),
    url(r'^%sformula/(?P<pk>\d+)/delete/$' % cr_prefix,
        DeleteTestCase.as_view(),
        name="test-case-delete"),

  #     (r'^add-units/$', 'add_units'),
  #
      # (r'^(?P<creditset_id>\d+)/$', 'credit_set_detail'),
  #     (r'^(?P<creditset_id>\d+)/ratings/$', 'credit_set_ratings'),
  #     (r'^(?P<creditset_id>\d+)/ratings/(?P<rating_id>\d+)/delete/$', 'delete_rating'),
  #     (r'^(?P<creditset_id>\d+)/add-category/$', 'add_category'),
  #     (r'^(?P<creditset_id>\d+)/confirm-unlock/$', 'credit_set_confirm_unlock'),
  #     (r'^(?P<creditset_id>\d+)/locked/$', 'credit_set_locked'),
  #     (r'^(?P<creditset_id>\d+)/(?P<category_id>\d+)/$', 'category_detail'),
  #     (r'^(?P<creditset_id>\d+)/(?P<category_id>\d+)/delete/$', 'delete_category'),
  #     (r'^(?P<creditset_id>\d+)/(?P<category_id>\d+)/add-subcategory/$', 'add_subcategory'),
  #     (r'^(?P<creditset_id>\d+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/delete/$', 'delete_subcategory'),
  #     (r'^(?P<creditset_id>\d+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/add-credit/$', 'add_credit'),
  #     (r'^(?P<creditset_id>\d+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/add-t2-credit/$', 'add_t2_credit'),
  #     (r'^(?P<creditset_id>\d+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/$', 'credit_detail'),
  #     (r'^(?P<creditset_id>\d+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/delete/$', 'delete_credit'),
  #     (r'^(?P<creditset_id>\d+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/formula/$', 'credit_formula'),
  #     (r'^(?P<creditset_id>\d+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/formula/add-test/$', 'add_formula_test_case'),
  #     (r'^(?P<creditset_id>\d+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/formula/(?P<test_case_id>\d+)/$', 'formula_test_case'),
  #     (r'^(?P<creditset_id>\d+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/formula/(?P<test_case_id>\d+)/delete/$', 'delete_formula_test_case'),
  #     (r'^(?P<creditset_id>\d+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/add-field/$', 'add_field'),
  #     (r'^(?P<creditset_id>\d+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/fields/$', 'credit_fields'),
  #     (r'^(?P<creditset_id>\d+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/applicability/$', 'credit_applicability'),
  #     (r'^(?P<creditset_id>\d+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/applicability/(?P<reason_id>\d+)/$', 'edit_applicability'),
  #     (r'^(?P<creditset_id>\d+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/applicability/(?P<reason_id>\d+)/delete/$', 'delete_applicability'),
  #     (r'^(?P<creditset_id>\d+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/(?P<field_id>\d+)/$', 'field_detail'),
  #     (r'^(?P<creditset_id>\d+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/(?P<field_id>\d+)/delete/$', 'delete_field'),
  #     (r'^(?P<creditset_id>\d+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/(?P<field_id>\d+)/change_field_type/$', 'change_field_type'),
  #     (r'^(?P<creditset_id>\d+)/(?P<category_id>\d+)/(?P<subcategory_id>\d+)/(?P<credit_id>\d+)/(?P<field_id>\d+)/choice/(?P<choice_id>\d+)/delete/$', 'delete_choice'),
  )
