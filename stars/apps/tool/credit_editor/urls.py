from django.conf.urls.defaults import patterns, url
from django.views.decorators.cache import never_cache

from stars.apps.tool.credit_editor.views import *


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

    (r'^%sfields/$' % cr_prefix, never_cache(CreditReportingFields())),
    (r'^%sadd-field/$' % cr_prefix, AddReportingField()),
    (r'^%s(?P<field_id>\d+)/$' % cr_prefix, EditReportingField()),

    url(r'^%sapplicability/$' % cr_prefix,
        ApplicabilityReasons(),
        name="applicability-reason-list"),
    (r'^%sadd-reason/$' % cr_prefix, AddApplicabilityReason()),
    (r'^%sapplicability/(?P<reason_id>\d+)/$' % cr_prefix,
     EditApplicabilityReason()),
    url(r'^credits/applicabilityreason/(?P<pk>\d+)/delete/$',
        DeleteApplicabilityReason.as_view(),
        name="applicability-reason-delete"),

    (r'^%sformula/$' % cr_prefix, FormulaAndValidation()),
    (r'^%sformula/add-test-case/$' % cr_prefix, AddTestCase()),
    (r'^%sformula/(?P<test_id>\d+)/$' % cr_prefix, EditTestCase()),
    url(r'^%sformula/(?P<pk>\d+)/delete/$' % cr_prefix,
        DeleteTestCase.as_view(),
        name="test-case-delete"),
  )
